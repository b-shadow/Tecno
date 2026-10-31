<?php

namespace App\Negocio;

use App\Http\Requests\Seguridad\AsignarPermisoRequest;
use App\Http\Requests\Seguridad\BitacoraRequest;
use Datos\DSeguridad;
use Datos\Modelos\Permiso;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Carbon;
use Illuminate\Validation\ValidationException;

/** Capa de negocio — enunciados 2 y 4: matriz de acceso rol × recurso (menú dinámico) y bitácora de auditoría. */
class NSeguridad
{
    public function __construct(private readonly DSeguridad $seguridad)
    {
    }

    public function matriz(): JsonResponse
    {
        return response()->json($this->seguridad->matriz() + ['niveles' => array_keys(Permiso::NIVELES)]);
    }

    public function asignar(AsignarPermisoRequest $r): JsonResponse
    {
        $datos = $r->validated();
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
        NAcceso::olvidar();

        return response()->json(['mensaje' => 'Permiso actualizado.']);
    }

    public function bitacora(BitacoraRequest $r): JsonResponse
    {
        $filtros = $r->query();
        if (! empty($filtros['desde'])) {
            $filtros['desde'] = Carbon::parse($filtros['desde'], 'America/La_Paz')->startOfDay()->utc();
        }
        if (! empty($filtros['hasta'])) {
            $filtros['hasta'] = Carbon::parse($filtros['hasta'], 'America/La_Paz')->endOfDay()->utc();
        }

        return response()->json(['registros' => $this->seguridad->bitacora($filtros)]);
    }

    public function resumen(): JsonResponse
    {
        return response()->json($this->seguridad->resumen(now()->subDays(30)));
    }
}
