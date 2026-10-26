<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Seguimiento\ActualizarComisionRequest;
use App\Http\Requests\Seguimiento\CompletarRecordatorioRequest;
use App\Http\Requests\Seguimiento\CrearRecordatorioRequest;
use App\Http\Requests\Seguimiento\RegistrarInteraccionRequest;
use App\Services\SeguimientoService;
use Datos\Modelos\Interes;
use Datos\Modelos\Recordatorio;
use Datos\Modelos\Usuario;
use Illuminate\Http\JsonResponse;

/** CU7 (interacciones y recordatorios) y CU6 (inscripciones y comisiones): delega en SeguimientoService. */
class SeguimientoController extends Controller
{
    public function __construct(private readonly SeguimientoService $seguimiento)
    {
    }

    public function registrarInteraccion(RegistrarInteraccionRequest $r, Interes $interes): JsonResponse
    {
        $interaccion = $this->seguimiento->registrarInteraccion($r->usuario(), $interes, $r->validated());

        return response()->json(['mensaje' => 'Interacción registrada.', 'interaccion' => $interaccion], 201);
    }

    public function recordatorios(ConsultaRequest $r): JsonResponse
    {
        $recordatorios = $this->seguimiento->recordatorios($r->usuario(), $r->query('estado'), $r->query('desde'), $r->query('hasta'));

        return response()->json(['recordatorios' => $recordatorios]);
    }

    public function crearRecordatorio(CrearRecordatorioRequest $r, Interes $interes): JsonResponse
    {
        $recordatorio = $this->seguimiento->crearRecordatorio($r->usuario(), $interes, $r->validated());

        return response()->json(['mensaje' => 'Actividad agendada.', 'recordatorio' => $recordatorio], 201);
    }

    public function completarRecordatorio(CompletarRecordatorioRequest $r, Recordatorio $recordatorio): JsonResponse
    {
        $this->seguimiento->completarRecordatorio($r->usuario(), $recordatorio, $r->validated('resultado'));

        return response()->json(['mensaje' => 'Actividad marcada como realizada.']);
    }

    public function cancelarRecordatorio(ConsultaRequest $r, Recordatorio $recordatorio): JsonResponse
    {
        $this->seguimiento->cancelarRecordatorio($r->usuario(), $recordatorio);

        return response()->json(['mensaje' => 'Actividad cancelada.']);
    }

    public function comisiones(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['comisiones' => $this->seguimiento->comisiones($r->usuario()), 'porcentaje' => $this->seguimiento->porcentajeComision()]);
    }

    public function resumenComisiones(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['vendedores' => $this->seguimiento->resumenComisiones($r->usuario())]);
    }

    public function pagarComisiones(ConsultaRequest $r, Usuario $vendedor): JsonResponse
    {
        $total = $this->seguimiento->pagarComisiones($r->usuario(), $vendedor);

        return response()->json(['mensaje' => $total ? "{$total} comisión(es) marcadas como pagadas." : 'No había comisiones pendientes.']);
    }

    public function configuracionComision(): JsonResponse
    {
        return response()->json(['porcentaje' => $this->seguimiento->porcentajeComision()]);
    }

    public function actualizarConfiguracionComision(ActualizarComisionRequest $r): JsonResponse
    {
        $porcentaje = $this->seguimiento->actualizarPorcentajeComision($r->usuario(), (float) $r->validated('porcentaje'));

        return response()->json(['mensaje' => 'Porcentaje de comisión actualizado.', 'porcentaje' => $porcentaje]);
    }

    public function inscripciones(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['inscripciones' => $this->seguimiento->inscripciones($r->usuario())]);
    }
}
