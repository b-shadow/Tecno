<?php

namespace App\Services;

use Datos\Modelos\Notificacion;
use Datos\Modelos\Usuario;
use Datos\Repositorios\NotificacionRepository;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Mail;

/** Reglas de negocio y entrega de notificaciones del CRM. */
class NotificacionService
{
    public function __construct(private readonly NotificacionRepository $notificaciones)
    {
    }

    public function enviar(Usuario $usuario, array $datos): array
    {
        if ($usuario->rol === 'vendedor') {
            $esPropio = strcasecmp($datos['destinatario'], $usuario->correo) === 0;
            $esDeCartera = $this->notificaciones->prospectoAsignadoA($datos['destinatario'], $usuario->correo);

            if (! $esPropio && ! $esDeCartera) {
                abort(403, 'Solo puede escribir a prospectos de su cartera.');
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

        return [$estado, $notificacion];
    }

    public function listar(Usuario $usuario): Collection
    {
        return $this->notificaciones->listar($usuario);
    }

    public function marcarLeida(Usuario $usuario, int $numero): Notificacion
    {
        $notificacion = $this->notificaciones->obtener($numero);

        abort_if(
            $usuario->rol !== 'administrador' && $notificacion->usuario_correo !== $usuario->correo,
            403,
            'No puede modificar esta notificación.',
        );

        return $this->notificaciones->marcarLeida($notificacion);
    }
}
