<?php

namespace App\Services;

use App\Exceptions\ReglaNegocioException;
use Datos\Modelos\Exportacion;
use Datos\Modelos\Usuario;
use Datos\Repositorios\ExportacionRepository;
use Illuminate\Support\Collection;

/** Caso de uso de exportación y consulta de matrículas hacia el SIS. */
class ExportacionService
{
    public function __construct(private readonly ExportacionRepository $exportaciones)
    {
    }

    public function pendientes(Usuario $usuario): Collection
    {
        return $this->exportaciones->exportables($usuario, $this->modulosACargo($usuario));
    }

    public function exportar(Usuario $usuario): array
    {
        $filas = $this->exportaciones->exportarPendientes($usuario, $this->modulosACargo($usuario));

        return [
            'mensaje' => count($filas) ? count($filas).' matrícula(s) exportadas.' : 'No hay matrículas pendientes de enviar.',
            'archivo' => 'alumnos_inscritos_'.now()->format('Ymd_His').'.csv',
            'filas' => $filas,
        ];
    }

    /** RF1.3: el coordinador solo registra el resultado de exportaciones de sus programas. */
    public function registrarResultado(Usuario $usuario, int $numero, array $datos): Exportacion
    {
        ReglaNegocioException::si(! $this->historial($usuario)->contains('nro_exportacion', $numero), 'Esta exportación no está dentro de sus programas.', 403);

        return $this->exportaciones->registrarResultado($numero, $datos);
    }

    public function historial(Usuario $usuario): Collection
    {
        return $this->exportaciones->historial($usuario, $this->modulosACargo($usuario));
    }

    private function modulosACargo(Usuario $usuario): ?array
    {
        return $usuario->rol === 'coordinador' ? AlcanceService::modulosACargo($usuario)->all() : null;
    }
}
