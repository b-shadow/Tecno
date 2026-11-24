<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Pago\AprobarCuotaRequest;
use App\Http\Requests\Pago\CambiarEstadoMetodoRequest;
use App\Http\Requests\Pago\CrearOrdenRequest;
use App\Http\Requests\Pago\PagarConTarjetaRequest;
use App\Http\Requests\Pago\RechazarCuotaRequest;
use App\Http\Requests\Pago\RegistrarComprobanteRequest;
use App\Http\Requests\Pago\RegistrarMetodoRequest;
use App\Services\PagoService;
use Datos\Modelos\ComprobantePago;
use Datos\Modelos\Interes;
use Datos\Modelos\MetodoPago;
use Datos\Modelos\OrdenPago;
use Datos\Modelos\Prospecto;
use Illuminate\Http\JsonResponse;

/** CU6 y enunciado 10: recibe la petición, la valida (FormRequest) y delega en PagoService. */
class PagoController extends Controller
{
    public function __construct(private readonly PagoService $pagos)
    {
    }

    public function descuentos(): JsonResponse
    {
        return response()->json(['descuentos' => $this->pagos->descuentos()]);
    }

    public function metodos(ConsultaRequest $r, Prospecto $prospecto): JsonResponse
    {
        return response()->json(['metodos' => $this->pagos->metodos($r->usuario(), $prospecto), 'marcas' => PagoService::MARCAS]);
    }

    public function registrarMetodo(RegistrarMetodoRequest $r, Prospecto $prospecto): JsonResponse
    {
        $metodo = $this->pagos->registrarMetodo($r->usuario(), $prospecto, $r->validated());

        return response()->json(['mensaje' => 'Método de pago registrado.', 'metodo' => $metodo], 201);
    }

    public function cambiarEstadoMetodo(CambiarEstadoMetodoRequest $r, MetodoPago $metodo): JsonResponse
    {
        $estado = $r->validated('estado');
        $metodo = $this->pagos->cambiarEstadoMetodo($r->usuario(), $metodo, $estado);

        return response()->json(['mensaje' => $estado === 'activo' ? 'Método activado.' : 'Método desactivado.', 'metodo' => $metodo]);
    }

    public function ordenes(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['ordenes' => $this->pagos->ordenes($r->usuario())]);
    }

    public function crearOrden(CrearOrdenRequest $r, Interes $interes): JsonResponse
    {
        $orden = $this->pagos->crearOrden($r->usuario(), $interes, $r->validated());

        return response()->json(['mensaje' => 'Orden de pago generada.', 'orden' => $orden], 201);
    }

    public function cuotas(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['cuotas' => $this->pagos->cuotas($r->usuario(), $r->query('estado'))]);
    }

    public function registrarComprobante(RegistrarComprobanteRequest $r, OrdenPago $orden, int $cuota): JsonResponse
    {
        $this->pagos->registrarComprobante($r->usuario(), $orden, $cuota, $r->validated());

        return response()->json(['mensaje' => 'Comprobante enviado a revisión.'], 201);
    }

    public function pagarConTarjeta(PagarConTarjetaRequest $r, OrdenPago $orden, int $cuota): JsonResponse
    {
        $transaccion = $this->pagos->pagarConTarjeta($r->usuario(), $orden, $cuota, (int) $r->validated('nro_metodo'));

        return response()->json([
            'mensaje' => "Cobro registrado por la pasarela simulada ({$transaccion}). Coordinación debe validarlo.",
            'transaccion' => $transaccion,
        ]);
    }

    public function aprobar(AprobarCuotaRequest $r, OrdenPago $orden, int $cuota): JsonResponse
    {
        $faltantes = $this->pagos->aprobar($r->usuario(), $orden, $cuota, $r->validated('observacion'));
        $mensaje = $cuota === 1 && ! $faltantes ? 'Pago aprobado. El prospecto quedó matriculado (Convertido).' : 'Pago aprobado.';

        return response()->json(['mensaje' => $mensaje, 'faltantes_conversion' => $faltantes]);
    }

    public function rechazar(RechazarCuotaRequest $r, OrdenPago $orden, int $cuota): JsonResponse
    {
        $this->pagos->rechazar($r->usuario(), $orden, $cuota, $r->validated('observacion'));

        return response()->json(['mensaje' => 'Comprobante rechazado. El vendedor verá el motivo.']);
    }

    public function comprobante(ConsultaRequest $r, ComprobantePago $comprobante): JsonResponse
    {
        return response()->json(['comprobante' => $this->pagos->comprobante($r->usuario(), $comprobante)]);
    }
}
