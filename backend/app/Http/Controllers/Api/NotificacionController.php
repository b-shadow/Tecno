<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Notificacion;
use App\Models\Prospecto;
use App\Services\Alcance;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Mail;

/** CU7: avisos por correo al prospecto o al equipo, con su registro. */
class NotificacionController extends Controller
{
    public function enviar(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $data = $request->validate([
            'destinatario' => ['required', 'email', 'max:160'],
            'tipo' => ['required', 'string', 'max:120'],
            'mensaje' => ['required', 'string', 'min:3', 'max:5000'],
        ], [], ['tipo' => 'asunto']);

        if ($usuario->rol === 'vendedor') {
            $propio = strcasecmp($data['destinatario'], $usuario->correo) === 0;
            $suProspecto = Alcance::prospectos(Prospecto::query()->whereRaw('lower(correo) = ?', [mb_strtolower($data['destinatario'])]), $usuario)->exists();
            abort_unless($propio || $suProspecto, 403, 'Solo puede escribir a prospectos de su cartera.');
        }

        try {
            Mail::raw($data['mensaje'], fn ($m) => $m->to($data['destinatario'])->subject($data['tipo']));
            $estado = 'enviada';
        } catch (\Throwable) {
            $estado = 'fallida';
        }

        $notificacion = Notificacion::query()->create($data + ['usuario_correo' => $usuario->correo, 'estado' => $estado, 'fecha_envio' => now()]);

        return response()->json(['mensaje' => $estado === 'enviada' ? 'Correo enviado.' : 'No se pudo enviar el correo; quedó registrado como fallido.', 'notificacion' => $notificacion], 201);
    }

    public function index(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        return response()->json(['notificaciones' => Notificacion::query()
            ->when($usuario->rol !== 'administrador', fn ($q) => $q->where('usuario_correo', $usuario->correo))
            ->orderByDesc('fecha_envio')->limit(200)->get()]);
    }

    public function marcarLeida(Request $request, Notificacion $notificacion): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if($usuario->rol !== 'administrador' && $notificacion->usuario_correo !== $usuario->correo, 403, 'No puede modificar esta notificación.');
        $notificacion->update(['estado' => 'leida']);

        return response()->json(['notificacion' => $notificacion]);
    }
}
