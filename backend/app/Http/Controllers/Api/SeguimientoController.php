<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\SeguimientoService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use App\Models\Interes;
use App\Models\Recordatorio;
use App\Models\Usuario;

class SeguimientoController extends Controller
{
    public function registrarInteraccion(Request $request, Interes $interes, SeguimientoService $service): JsonResponse
    {
        return $service->registrarInteraccion($request, $interes);
    }

    public function recordatorios(Request $request, SeguimientoService $service): JsonResponse
    {
        return $service->recordatorios($request);
    }

    public function crearRecordatorio(Request $request, Interes $interes, SeguimientoService $service): JsonResponse
    {
        return $service->crearRecordatorio($request, $interes);
    }

    public function completarRecordatorio(Request $request, Recordatorio $recordatorio, SeguimientoService $service): JsonResponse
    {
        return $service->completarRecordatorio($request, $recordatorio);
    }

    public function cancelarRecordatorio(Request $request, Recordatorio $recordatorio, SeguimientoService $service): JsonResponse
    {
        return $service->cancelarRecordatorio($request, $recordatorio);
    }

    public function comisiones(Request $request, SeguimientoService $service): JsonResponse
    {
        return $service->comisiones($request);
    }

    public function resumenComisiones(Request $request, SeguimientoService $service): JsonResponse
    {
        return $service->resumenComisiones($request);
    }

    public function pagarComisiones(Usuario $vendedor, SeguimientoService $service): JsonResponse
    {
        return $service->pagarComisiones($vendedor);
    }

    public function configuracionComision(SeguimientoService $service): JsonResponse
    {
        return $service->configuracionComision();
    }

    public function actualizarConfiguracionComision(Request $request, SeguimientoService $service): JsonResponse
    {
        return $service->actualizarConfiguracionComision($request);
    }

    public function inscripciones(Request $request, SeguimientoService $service): JsonResponse
    {
        return $service->inscripciones($request);
    }
}
