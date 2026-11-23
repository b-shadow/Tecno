<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\ExportacionService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/** Adaptador HTTP de matrículas y exportaciones al SIS. */
class ExportacionController extends Controller
{
    public function pendientes(Request $request, ExportacionService $service): JsonResponse
    {
        $inscripciones = $service->pendientes($request->attributes->get('auth_usuario'));

        return response()->json(['total' => $inscripciones->count(), 'inscripciones' => $inscripciones]);
    }

    public function exportar(Request $request, ExportacionService $service): JsonResponse
    {
        return response()->json($service->exportar($request->attributes->get('auth_usuario')));
    }

    public function registrarResultado(Request $request, int $exportacion, ExportacionService $service): JsonResponse
    {
        $datos = $request->validate([
            'estado' => ['required', 'in:recibida,error'],
            'respuesta' => ['nullable', 'string', 'max:2000'],
        ]);

        return response()->json([
            'mensaje' => 'Resultado registrado.',
            'exportacion' => $service->registrarResultado($exportacion, $datos),
        ]);
    }

    public function historial(Request $request, ExportacionService $service): JsonResponse
    {
        return response()->json([
            'exportaciones' => $service->historial($request->attributes->get('auth_usuario')),
        ]);
    }
}
