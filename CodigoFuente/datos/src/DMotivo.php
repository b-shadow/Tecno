<?php

namespace Datos;

use Datos\Modelos\Interes;
use Datos\Modelos\MotivoPerdida;
use Illuminate\Support\Collection;

/** Acceso de persistencia a motivos de pérdida y sus referencias. */
class DMotivo
{
    public function listarConUsos(): Collection
    {
        $usos = Interes::query()
            ->whereNotNull('motivo_perdida')
            ->groupBy('motivo_perdida')
            ->selectRaw('motivo_perdida, count(*) as total')
            ->pluck('total', 'motivo_perdida');

        return MotivoPerdida::query()
            ->orderBy('categoria')
            ->orderBy('nombre')
            ->get()
            ->map(fn (MotivoPerdida $motivo) => $motivo->toArray() + [
                'usos' => (int) ($usos[$motivo->nombre] ?? 0),
            ]);
    }

    public function existeNombre(string $nombre, ?string $excepto = null): bool
    {
        return MotivoPerdida::query()
            ->where('nombre', $nombre)
            ->when($excepto !== null, fn ($query) => $query->where('nombre', '!=', $excepto))
            ->exists();
    }

    public function crear(array $datos): MotivoPerdida
    {
        return MotivoPerdida::query()->create($datos);
    }

    public function obtener(string $nombre): MotivoPerdida
    {
        return MotivoPerdida::query()->findOrFail($nombre);
    }

    public function estaEnUso(string $nombre): bool
    {
        return Interes::query()->where('motivo_perdida', $nombre)->exists();
    }

    public function actualizar(MotivoPerdida $motivo, array $datos): MotivoPerdida
    {
        $motivo->update($datos);

        return $motivo->refresh();
    }

    public function eliminar(MotivoPerdida $motivo): void
    {
        $motivo->delete();
    }
}
