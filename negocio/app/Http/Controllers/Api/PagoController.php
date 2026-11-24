<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\PagoService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Datos\Modelos\ComprobantePago;
use Datos\Modelos\Interes;
use Datos\Modelos\MetodoPago;
use Datos\Modelos\OrdenPago;
use Datos\Modelos\Prospecto;

class PagoController extends Controller
{
    public function descuentos(PagoService $service): JsonResponse
    {
        return $service->descuentos();
    }

    public function metodos(Request $request, Prospecto $prospecto, PagoService $service): JsonResponse
    {
        return $service->metodos($request, $prospecto);
    }

    public function registrarMetodo(Request $request, Prospecto $prospecto, PagoService $service): JsonResponse
    {
        return $service->registrarMetodo($request, $prospecto);
    }

    public function cambiarEstadoMetodo(Request $request, MetodoPago $metodo, PagoService $service): JsonResponse
    {
        return $service->cambiarEstadoMetodo($request, $metodo);
    }

    public function ordenes(Request $request, PagoService $service): JsonResponse
    {
        return $service->ordenes($request);
    }

    public function crearOrden(Request $request, Interes $interes, PagoService $service): JsonResponse
    {
        return $service->crearOrden($request, $interes);
    }

    public function cuotas(Request $request, PagoService $service): JsonResponse
    {
        return $service->cuotas($request);
    }

    public function registrarComprobante(Request $request, OrdenPago $orden, int $cuota, PagoService $service): JsonResponse
    {
        return $service->registrarComprobante($request, $orden, $cuota);
    }

    public function pagarConTarjeta(Request $request, OrdenPago $orden, int $cuota, PagoService $service): JsonResponse
    {
        return $service->pagarConTarjeta($request, $orden, $cuota);
    }

    public function aprobar(Request $request, OrdenPago $orden, int $cuota, PagoService $service): JsonResponse
    {
        return $service->aprobar($request, $orden, $cuota);
    }

    public function rechazar(Request $request, OrdenPago $orden, int $cuota, PagoService $service): JsonResponse
    {
        return $service->rechazar($request, $orden, $cuota);
    }

    public function comprobante(Request $request, ComprobantePago $comprobante, PagoService $service): JsonResponse
    {
        return $service->comprobante($request, $comprobante);
    }
}
