<?php

namespace Datos;

use Datos\Modelos\Notificacion;
use Datos\Modelos\Prospecto;
use Datos\Modelos\Usuario;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Collection;

/** Persistencia de notificaciones y comprobaciones de cartera relacionadas. */
class DNotificacion
{
    public function prospectoAsignadoA(string $correo, string $vendedor): bool
    {
        return Prospecto::query()
            ->whereRaw('lower(correo) = ?', [mb_strtolower($correo)])
            ->whereHas('intereses', fn ($intereses) => $intereses->where('vendedor_correo', $vendedor))
            ->exists();
    }

    public function crear(array $datos): Notificacion
    {
        return Notificacion::query()->create($datos);
    }

    public function existeNotificacionEnviada(string $destinatario, string $tipo, string $referencia): bool
    {
        return Notificacion::query()
            ->whereRaw('lower(destinatario) = ?', [mb_strtolower($destinatario)])
            ->where('tipo', $tipo)
            ->where('estado', 'enviada')
            ->where('mensaje', 'ilike', DAlcance::escaparLike($referencia))
            ->exists();
    }

    public function listar(Usuario $usuario): Collection
    {
        return Notificacion::query()
            ->when($usuario->rol !== 'administrador', fn ($query) => $query->where('usuario_correo', $usuario->correo))
            ->orderByDesc('fecha_envio')
            ->limit(200)
            ->get();
    }

    public function obtener(int $numero): Notificacion
    {
        return Notificacion::query()->findOrFail($numero);
    }

    public function marcarLeida(Notificacion $notificacion): Notificacion
    {
        $notificacion->update(['estado' => 'leida']);

        return $notificacion->refresh();
    }
}
