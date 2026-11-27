<?php

namespace App\Negocio;

use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Reporte\ListadoRequest;
use Datos\DReporte;
use Datos\Modelos\Interes;
use Illuminate\Http\JsonResponse;

/** Capa de negocio — CU8 (enunciado 8): dashboard, estadísticas porcentuales y reportes (listados). */
class NReporte
{
    private const FILTROS = ['desde', 'hasta', 'vendedor', 'programa', 'estado', 'buscar'];

    public function __construct(private readonly DReporte $reportes)
    {
    }

    public function dashboard(ConsultaRequest $r): JsonResponse
    {
        $usuario = $r->usuario();
        $dias = collect(range(13, 0))->map(fn ($n) => now()->subDays($n)->toDateString());
        $datos = $this->reportes->dashboard($usuario, $dias, NAcceso::permite($usuario, 'bitacora'));

        return response()->json([
            'indicadores' => $datos['indicadores'],
            'embudo' => $this->porcentajes($datos['embudo'], Interes::ESTADOS),
            'ingresos_por_dia' => $this->serie($dias, $datos['ingresos_por_dia']),
            'ventas_por_programa' => $this->porcentajes($datos['ventas_por_programa']),
            'visitas_por_pagina' => $datos['visitas_por_pagina'],
            ...(isset($datos['accesos']) ? ['accesos' => [
                'exitosos' => $this->serie($dias, $datos['accesos']['exitosos']),
                'fallidos' => $this->serie($dias, $datos['accesos']['fallidos']),
                'denegados_semana' => $datos['accesos']['denegados_semana'],
            ]] : []),
        ]);
    }

    public function estadisticas(ConsultaRequest $r): JsonResponse
    {
        $datos = $this->reportes->estadisticas($r->usuario(), $r->only(self::FILTROS));
        $porVendedor = $datos['conversion_por_vendedor']->map(fn ($fila) => (array) $fila + [
            'tasa_conversion' => $fila->total ? round($fila->convertidos * 100 / $fila->total, 1) : 0,
        ]);

        return response()->json([
            'embudo' => $this->porcentajes($datos['embudo'], Interes::ESTADOS),
            'perdidas_por_categoria' => $this->porcentajes($datos['perdidas_por_categoria']),
            'perdidas_por_motivo' => $this->porcentajes($datos['perdidas_por_motivo']),
            'origen_de_leads' => $this->porcentajes($datos['origen_de_leads']),
            'conversion_por_vendedor' => $porVendedor,
        ]);
    }

    public function listado(ListadoRequest $r): JsonResponse
    {
        $usuario = $r->usuario();
        $datos = $this->reportes->listado($usuario, $r->only(['tipo', ...self::FILTROS]));

        return response()->json([
            ...$datos,
            'columnas' => collect($datos['columnas'])->map(fn ($etiqueta, $clave) => ['key' => $clave, 'label' => $etiqueta])->values(),
            'vendedores' => $usuario->rol === 'vendedor' ? [] : $this->reportes->vendedores(),
        ]);
    }

    public function estadisticasVendedor(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['estadisticas' => $this->reportes->estadisticasVendedor($r->usuario()->correo)]);
    }

    private function porcentajes($conteos, ?array $orden = null): array
    {
        $conteos = collect($conteos)->map(fn ($valor) => (int) $valor);
        $etiquetas = $orden ?? $conteos->sortDesc()->keys()->all();
        $suma = max($conteos->sum(), 1);

        return array_map(fn ($etiqueta) => [
            'etiqueta' => $etiqueta,
            'total' => $conteos[$etiqueta] ?? 0,
            'porcentaje' => round(($conteos[$etiqueta] ?? 0) * 100 / $suma, 1),
        ], $etiquetas);
    }

    private function serie($dias, $valores): array
    {
        return $dias->map(fn ($dia) => ['dia' => $dia, 'total' => (float) ($valores[$dia] ?? 0)])->all();
    }
}
