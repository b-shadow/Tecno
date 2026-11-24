<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Seguridad\AsignarPermisoRequest;
use App\Http\Requests\Seguridad\BitacoraRequest;
use App\Services\SeguridadService;
use Illuminate\Http\JsonResponse;

/** Enunciados 2 y 4: matriz de acceso rol × recurso (menú dinámico) y bitácora de auditoría. */
class SeguridadController extends Controller
{
    public function __construct(private readonly SeguridadService $seguridad)
    {
    }

    public function matriz(): JsonResponse
    {
        return response()->json($this->seguridad->matriz());
    }

    public function asignar(AsignarPermisoRequest $r): JsonResponse
    {
        $this->seguridad->asignar($r->validated());

        return response()->json(['mensaje' => 'Permiso actualizado.']);
    }

    public function bitacora(BitacoraRequest $r): JsonResponse
    {
        return response()->json(['registros' => $this->seguridad->bitacora($r->query())]);
    }

    public function resumen(): JsonResponse
    {
        return response()->json($this->seguridad->resumen());
    }
}
