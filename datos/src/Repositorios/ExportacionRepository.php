<?php

namespace Datos\Repositorios;

use Datos\Modelos\Exportacion;
use Datos\Modelos\InscripcionComercial;
use Datos\Modelos\Usuario;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Persistencia de matrículas y exportaciones al SIS. */
class ExportacionRepository
{
    public function exportables(Usuario $usuario, ?array $modulosACargo): Collection
    {
        return $this->consultaExportables($usuario, $modulosACargo)->get();
    }

    public function exportarPendientes(Usuario $usuario, ?array $modulosACargo): array
    {
        return DB::transaction(function () use ($usuario, $modulosACargo): array {
            DB::table('inscripciones_comerciales')->orderBy('nro_solicitud')->lockForUpdate()->get();
            $filas = [];

            foreach ($this->consultaExportables($usuario, $modulosACargo)->get() as $inscripcion) {
                $solicitud = $inscripcion->solicitudCompra;
                $prospecto = $solicitud->ordenPago->interes->prospecto;
                $fila = [
                    'nombres' => $prospecto->nombre,
                    'apellidos' => $prospecto->apellido,
                    'ci' => $prospecto->documento,
                    'telefono' => $prospecto->telefono,
                    'profesion' => $prospecto->profesion,
                    'ubicacion' => $prospecto->ubicacion,
                    'correo' => $prospecto->correo,
                    'programa' => $solicitud->programa_nombre,
                    'modulo' => $solicitud->modulo_nombre,
                    'codigo_modulo' => $solicitud->modulo_codigo,
                    'precio_acordado' => $solicitud->precio_acordado,
                    'fecha_inscripcion' => optional($inscripcion->fecha_confirmacion)->toDateTimeString(),
                ];
                $filas[] = $fila;

                Exportacion::query()->create([
                    'nro_solicitud' => $inscripcion->nro_solicitud,
                    'usuario_correo' => $usuario->correo,
                    'fecha_exportacion' => now(),
                    'estado' => 'exportada',
                    'respuesta' => json_encode($fila, JSON_UNESCAPED_UNICODE),
                ]);
            }

            return $filas;
        });
    }

    public function registrarResultado(int $numero, array $datos): Exportacion
    {
        $exportacion = Exportacion::query()->findOrFail($numero);
        $exportacion->update($datos);

        return $exportacion->refresh();
    }

    public function historial(Usuario $usuario, ?array $modulosACargo): Collection
    {
        return Exportacion::query()
            ->whereExists(fn ($query) => $query->from('solicitudes_compra as s')
                ->join('ordenes_pago as o', 'o.nro_orden', '=', 's.nro_orden')
                ->join('intereses as i', 'i.nro_tarjeta', '=', 'o.nro_tarjeta')
                ->whereColumn('s.nro_solicitud', 'exportaciones.nro_solicitud')
                ->when($usuario->rol === 'coordinador', fn ($subquery) => $subquery->whereIn('i.modulo_codigo', $modulosACargo ?? [])))
            ->with('usuario:correo,nombre,apellido')
            ->orderByDesc('fecha_exportacion')
            ->get();
    }

    private function consultaExportables(Usuario $usuario, ?array $modulosACargo): Builder
    {
        return InscripcionComercial::query()
            ->with('solicitudCompra.ordenPago.interes.prospecto')
            ->whereHas('solicitudCompra.ordenPago.interes', fn ($query) => $query
                ->when($usuario->rol === 'vendedor', fn ($scope) => $scope->where('vendedor_correo', $usuario->correo))
                ->when($usuario->rol === 'coordinador', fn ($scope) => $scope->whereIn('modulo_codigo', $modulosACargo ?? [])))
            ->whereDoesntHave('exportaciones', fn ($query) => $query->whereIn('estado', ['preparada', 'exportada', 'recibida']));
    }
}
