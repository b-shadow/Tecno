<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Exportacion\RegistrarResultadoRequest;
use App\Services\ExportacionService;
use Illuminate\Http\JsonResponse;

/** CU6: matriculados pendientes, exportación al SIS y su resultado. */
class ExportacionController extends Controller
{
    public function __construct(private readonly ExportacionService $exportaciones)
    {
    }

    public function pendientes(ConsultaRequest $r): JsonResponse
    {
        $inscripciones = $this->exportaciones->pendientes($r->usuario());

        return response()->json(['total' => $inscripciones->count(), 'inscripciones' => $inscripciones]);
    }

    public function exportar(ConsultaRequest $r): JsonResponse
    {
        return response()->json($this->exportaciones->exportar($r->usuario()));
    }

    public function registrarResultado(RegistrarResultadoRequest $r, int $exportacion): JsonResponse
    {
        $resultado = $this->exportaciones->registrarResultado($r->usuario(), $exportacion, $r->validated());

        return response()->json(['mensaje' => 'Resultado registrado.', 'exportacion' => $resultado]);
    }

    public function historial(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['exportaciones' => $this->exportaciones->historial($r->usuario())]);
    }
}
