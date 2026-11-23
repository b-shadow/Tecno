<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\ReporteService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/** Adaptador HTTP para los reportes del negocio. */
class ReporteController extends Controller
{
    public function dashboard(Request $request, ReporteService $service): JsonResponse
    {
        return response()->json($service->dashboard($request->attributes->get('auth_usuario')));
    }

    public function estadisticas(Request $request, ReporteService $service): JsonResponse
    {
        return response()->json($service->estadisticas(
            $request->attributes->get('auth_usuario'),
            $request->only(['desde', 'hasta', 'vendedor', 'programa', 'estado', 'buscar']),
        ));
    }

    public function listado(Request $request, ReporteService $service): JsonResponse
    {
        $request->validate([
            'tipo' => ['required', 'in:tarjetas,pagos,matriculas,comisiones,perdidas,vendedores'],
            'desde' => ['nullable', 'date'],
            'hasta' => ['nullable', 'date', 'after_or_equal:desde'],
            'vendedor' => ['nullable', 'email'],
            'programa' => ['nullable', 'string', 'max:255'],
            'estado' => ['nullable', 'string', 'max:40'],
            'buscar' => ['nullable', 'string', 'max:120'],
        ], [], ['desde' => 'fecha inicial', 'hasta' => 'fecha final']);

        return response()->json($service->listado(
            $request->attributes->get('auth_usuario'),
            $request->only(['tipo', 'desde', 'hasta', 'vendedor', 'programa', 'estado', 'buscar']),
        ));
    }

    public function estadisticasVendedor(Request $request, ReporteService $service): JsonResponse
    {
        return response()->json([
            'estadisticas' => $service->estadisticasVendedor($request->attributes->get('auth_usuario')),
        ]);
    }
}
