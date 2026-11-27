<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Exportacion\RegistrarResultadoRequest;
use Datos\DExportacion;
use Datos\Modelos\Usuario;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Collection;

/** Capa de negocio — CU6: matriculados pendientes, exportación al SIS y su resultado. */
class NExportacion
{
    public function __construct(private readonly DExportacion $exportaciones)
    {
    }

    public function pendientes(ConsultaRequest $r): JsonResponse
    {
        $usuario = $r->usuario();
        $inscripciones = $this->exportaciones->exportables($usuario, $this->modulosACargo($usuario));

        return response()->json(['total' => $inscripciones->count(), 'inscripciones' => $inscripciones]);
    }

    public function exportar(ConsultaRequest $r): JsonResponse
    {
        $usuario = $r->usuario();
        $filas = $this->exportaciones->exportarPendientes($usuario, $this->modulosACargo($usuario));

        return response()->json([
            'mensaje' => count($filas) ? count($filas).' matrícula(s) exportadas.' : 'No hay matrículas pendientes de enviar.',
            'archivo' => 'alumnos_inscritos_'.now()->format('Ymd_His').'.csv',
            'filas' => $filas,
        ]);
    }

    /** RF1.3: el coordinador solo registra el resultado de exportaciones de sus programas. */
    public function registrarResultado(RegistrarResultadoRequest $r, int $exportacion): JsonResponse
    {
        ReglaNegocioException::si(! $this->historialDe($r->usuario())->contains('nro_exportacion', $exportacion),
            'Esta exportación no está dentro de sus programas.', 403);
        $resultado = $this->exportaciones->registrarResultado($exportacion, $r->validated());

        return response()->json(['mensaje' => 'Resultado registrado.', 'exportacion' => $resultado]);
    }

    public function historial(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['exportaciones' => $this->historialDe($r->usuario())]);
    }

    private function historialDe(Usuario $usuario): Collection
    {
        return $this->exportaciones->historial($usuario, $this->modulosACargo($usuario));
    }

    private function modulosACargo(Usuario $usuario): ?array
    {
        return $usuario->rol === 'coordinador' ? NAlcance::modulosACargo($usuario)->all() : null;
    }
}
