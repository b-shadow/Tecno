<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Datos\Modelos\Bitacora;
use Datos\Modelos\Permiso;
use App\Services\SeguridadService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

/** Adaptador HTTP de la matriz de acceso y la bitácora. */
class SeguridadController extends Controller
{
    public function matriz(SeguridadService $service): JsonResponse
    {
        return response()->json($service->matriz());
    }

    public function asignar(Request $request, SeguridadService $service): JsonResponse
    {
        $datos = $request->validate([
            'rol' => ['required', 'exists:roles,nombre'],
            'recurso_codigo' => ['required', Rule::exists('recursos', 'codigo')->where('publico', false)],
            'acceso' => ['nullable', Rule::in(array_keys(Permiso::NIVELES))],
        ], [], ['recurso_codigo' => 'recurso']);

        $service->asignar($datos);

        return response()->json(['mensaje' => 'Permiso actualizado.']);
    }

    public function bitacora(Request $request, SeguridadService $service): JsonResponse
    {
        $request->validate([
            'evento' => ['nullable', Rule::in(Bitacora::EVENTOS)],
            'desde' => ['nullable', 'date'],
            'hasta' => ['nullable', 'date', 'after_or_equal:desde'],
            'usuario' => ['nullable', 'string', 'max:160'],
            'ip' => ['nullable', 'string', 'max:45'],
        ], [], ['desde' => 'fecha inicial', 'hasta' => 'fecha final']);

        return response()->json(['registros' => $service->bitacora($request->query())]);
    }

    public function resumen(SeguridadService $service): JsonResponse
    {
        return response()->json($service->resumen());
    }
}
