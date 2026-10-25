<?php

namespace App\Services;

use App\Models\Permiso;
use App\Repositories\SeguridadRepository;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;
use Illuminate\Support\Carbon;
use Illuminate\Validation\ValidationException;

/** Reglas de negocio para la matriz RBAC y las consultas de auditoría. */
class SeguridadService
{
    public function __construct(private readonly SeguridadRepository $seguridad)
    {
    }

    public function matriz(): array
    {
        return $this->seguridad->matriz() + ['niveles' => array_keys(Permiso::NIVELES)];
    }

    public function asignar(array $datos): void
    {
        if ($datos['rol'] === 'administrador'
            && in_array($datos['recurso_codigo'], ['matriz', 'usuarios'], true)
            && ($datos['acceso'] ?? null) !== 'eliminacion') {
            throw ValidationException::withMessages([
                'acceso' => 'El administrador debe conservar acceso total a Usuarios y Matriz de acceso.',
            ]);
        }

        $this->seguridad->guardarPermiso(
            ['rol' => $datos['rol'], 'recurso_codigo' => $datos['recurso_codigo']],
            $datos['acceso'] ?? null,
        );
        Acceso::olvidar();
    }

    public function bitacora(array $filtros): LengthAwarePaginator
    {
        if (! empty($filtros['desde'])) {
            $filtros['desde'] = Carbon::parse($filtros['desde'], 'America/La_Paz')->startOfDay()->utc();
        }
        if (! empty($filtros['hasta'])) {
            $filtros['hasta'] = Carbon::parse($filtros['hasta'], 'America/La_Paz')->endOfDay()->utc();
        }

        return $this->seguridad->bitacora($filtros);
    }

    public function resumen(): array
    {
        return $this->seguridad->resumen(now()->subDays(30));
    }
}
