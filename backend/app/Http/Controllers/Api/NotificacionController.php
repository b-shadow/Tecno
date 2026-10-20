<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Notificacion;
use App\Models\Prospecto;
use App\Models\Usuario;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Mail;
use Illuminate\Validation\ValidationException;

class NotificacionController extends Controller
{
    public function enviarCorreo(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $data = $request->validate([
            'usuario_id' => ['nullable', 'exists:usuarios,id'],
            'destinatario' => ['nullable', 'email'],
            'tipo' => ['required', 'string', 'max:120'],
            'mensaje' => ['required', 'string'],
        ]);

        $usuarioDestino = isset($data['usuario_id']) ? Usuario::query()->find($data['usuario_id']) : null;
        $destinatario = $data['destinatario'] ?? $usuarioDestino?->correo;

        if (! $destinatario) {
            throw ValidationException::withMessages([
                'destinatario' => 'Debe indicar un correo destinatario o un usuario con correo registrado.',
            ]);
        }
        if ($usuario->rol === 'vendedor') {
            $esPropio = $usuarioDestino?->id === $usuario->id || mb_strtolower($destinatario) === mb_strtolower($usuario->correo);
            $esProspectoAsignado = Prospecto::query()->whereRaw('lower(correo) = ?', [mb_strtolower($destinatario)])
                ->whereHas('intereses', fn ($query) => $query->where('vendedor_id', $usuario->id))->exists();
            abort_if(! $esPropio && ! $esProspectoAsignado, 403, 'Solo puede notificar a sus prospectos asignados o a su propia cuenta.');
        }

        $estado = 'enviada';

        try {
            Mail::raw($data['mensaje'], function ($message) use ($destinatario, $data): void {
                $message->to($destinatario)->subject($data['tipo']);
            });
        } catch (\Throwable) {
            $estado = 'fallida';
        }

        $notificacion = Notificacion::query()->create([
            'usuario_id' => $data['usuario_id'] ?? null,
            'destinatario' => $destinatario,
            'tipo' => $data['tipo'],
            'mensaje' => $data['mensaje'],
            'estado' => $estado,
            'fecha_envio' => now(),
        ]);

        return response()->json(['notificacion' => $notificacion->load('usuario')], 201);
    }

    public function listarNotificaciones(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $notificaciones = Notificacion::query()
            ->with('usuario')
            ->when($usuario->rol === 'vendedor', fn ($query) => $query->where('usuario_id', $usuario->id))
            ->latest('fecha_envio')
            ->get();

        return response()->json(['notificaciones' => $notificaciones]);
    }

    public function marcarLeida(Request $request, Notificacion $notificacion): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        abort_if(
            $usuario->rol === 'vendedor' && $notificacion->usuario_id !== $usuario->id,
            403,
            'No tiene permisos para actualizar esta notificacion.'
        );

        $notificacion->update(['estado' => 'leida']);

        return response()->json(['notificacion' => $notificacion->load('usuario')]);
    }
}
