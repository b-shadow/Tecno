<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Notificacion\EnviarNotificacionRequest;
use Datos\DNotificacion;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Mail;

/** Capa de negocio — CU7: correos enviados desde el CRM y su registro. */
class NNotificacion
{
    public function __construct(private readonly DNotificacion $notificaciones)
    {
    }

    public function enviar(EnviarNotificacionRequest $r): JsonResponse
    {
        $usuario = $r->usuario();
        $datos = $r->validated();
        if ($usuario->rol === 'vendedor') {
            $esPropio = strcasecmp($datos['destinatario'], $usuario->correo) === 0;
            $esDeCartera = $this->notificaciones->prospectoAsignadoA($datos['destinatario'], $usuario->correo);

            if (! $esPropio && ! $esDeCartera) {
                throw new ReglaNegocioException('Solo puede escribir a prospectos de su cartera.', 403);
            }
        }

        try {
            Mail::raw($datos['mensaje'], fn ($mensaje) => $mensaje->to($datos['destinatario'])->subject($datos['tipo']));
            $estado = 'enviada';
        } catch (\Throwable) {
            $estado = 'fallida';
        }

        $notificacion = $this->notificaciones->crear($datos + [
            'usuario_correo' => $usuario->correo,
            'estado' => $estado,
            'fecha_envio' => now(),
        ]);

        return response()->json([
            'mensaje' => $estado === 'enviada' ? 'Correo enviado.' : 'No se pudo enviar el correo; quedó registrado como fallido.',
            'notificacion' => $notificacion,
        ], 201);
    }

    public function index(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['notificaciones' => $this->notificaciones->listar($r->usuario())]);
    }

    public function marcarLeida(ConsultaRequest $r, int $notificacion): JsonResponse
    {
        $usuario = $r->usuario();
        $registro = $this->notificaciones->obtener($notificacion);

        ReglaNegocioException::si(
            $usuario->rol !== 'administrador' && $registro->usuario_correo !== $usuario->correo,
            'No puede modificar esta notificación.',
            403,
        );

        return response()->json(['notificacion' => $this->notificaciones->marcarLeida($registro)]);
    }
}
