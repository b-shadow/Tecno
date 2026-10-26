<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Reporte\ListadoRequest;
use App\Services\ReporteService;
use Illuminate\Http\JsonResponse;

/** CU8 (enunciado 8): dashboard, estadísticas porcentuales y reportes (listados). */
class ReporteController extends Controller
{
    private const FILTROS = ['desde', 'hasta', 'vendedor', 'programa', 'estado', 'buscar'];

    public function __construct(private readonly ReporteService $reportes)
    {
    }

    public function dashboard(ConsultaRequest $r): JsonResponse
    {
        return response()->json($this->reportes->dashboard($r->usuario()));
    }

    public function estadisticas(ConsultaRequest $r): JsonResponse
    {
        return response()->json($this->reportes->estadisticas($r->usuario(), $r->only(self::FILTROS)));
    }

    public function listado(ListadoRequest $r): JsonResponse
    {
        return response()->json($this->reportes->listado($r->usuario(), $r->only(['tipo', ...self::FILTROS])));
    }

    public function estadisticasVendedor(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['estadisticas' => $this->reportes->estadisticasVendedor($r->usuario())]);
    }
}
