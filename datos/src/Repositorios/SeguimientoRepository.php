<?php

namespace Datos\Repositorios;

use Datos\Modelos\Comision;
use Datos\Modelos\InscripcionComercial;
use Datos\Modelos\Interaccion;
use Datos\Modelos\Interes;
use Datos\Modelos\Recordatorio;
use Datos\Modelos\Usuario;
use Datos\Repositorios\AlcanceRepository;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Consultas y persistencia del seguimiento comercial y las comisiones. */
class SeguimientoRepository
{
    public function transaccion(callable $operacion): mixed
    {
        return DB::transaction($operacion);
    }

    public function registrarInteraccion(Interes $interes, array $datos): Interaccion
    {
        return $interes->interacciones()->create($datos);
    }

    public function actualizarInteres(Interes $interes, array $datos): void
    {
        $interes->update($datos);
    }

    public function cargarInteraccion(Interaccion $interaccion): Interaccion
    {
        return $interaccion->load('usuario:correo,nombre,apellido');
    }

    public function listarRecordatorios(Usuario $usuario, ?string $estado, $desde, $hasta): Collection
    {
        Recordatorio::query()->where('estado', 'Pendiente')->where('fecha_programada', '<', now()->subHours(24))
            ->update(['estado' => 'Atrasada']);

        return Recordatorio::query()
            ->whereHas('interes', fn ($q) => AlcanceRepository::intereses($q, $usuario))
            ->with('interes.prospecto:documento,nombre,apellido,telefono', 'usuario:correo,nombre,apellido')
            ->when($estado, fn ($q, $valor) => $q->where('estado', $valor))
            ->when($desde, fn ($q, $valor) => $q->where('fecha_programada', '>=', $valor))
            ->when($hasta, fn ($q, $valor) => $q->where('fecha_programada', '<', $valor))
            ->orderBy('fecha_programada')->get();
    }

    public function crearRecordatorio(Interes $interes, array $datos)
    {
        return $interes->recordatorios()->create($datos);
    }

    public function buscarRecordatorioBloqueado(int $numero): Recordatorio
    {
        return Recordatorio::query()->with('interes')->lockForUpdate()->findOrFail($numero);
    }

    public function cargarInteresRecordatorio(Recordatorio $recordatorio): Recordatorio
    {
        return $recordatorio->loadMissing('interes');
    }

    public function insertarInteraccion(array $datos): Interaccion
    {
        return Interaccion::query()->create($datos);
    }

    public function recordatorio(Recordatorio $recordatorio, array $datos): void
    {
        $recordatorio->update($datos);
    }

    public function comisiones(Usuario $usuario): Collection
    {
        return Comision::query()
            ->whereHas('venta.ordenPago.interes', fn ($q) => AlcanceRepository::intereses($q, $usuario))
            ->with('vendedor:correo,nombre,apellido', 'venta.ordenPago.interes.prospecto:documento,nombre,apellido')
            ->orderByDesc('created_at')->get();
    }

    /** Totales por vendedor contando solo las comisiones dentro del alcance de quien consulta (RF1.3). */
    public function resumenComisiones(Usuario $usuario): Collection
    {
        $porVendedor = $this->comisiones($usuario)->groupBy('vendedor_correo');

        return Usuario::query()->where('rol', 'vendedor')->orderBy('nombre')->get(['correo', 'nombre', 'apellido'])
            ->map(function (Usuario $v) use ($porVendedor) {
                $suyas = $porVendedor->get($v->correo, collect());

                return (object) [
                    'correo' => $v->correo, 'nombre' => $v->nombre, 'apellido' => $v->apellido,
                    'cursos_vendidos' => $suyas->count(),
                    'comision_total' => round($suyas->sum(fn ($c) => (float) $c->monto), 2),
                    'comision_pendiente' => round($suyas->where('estado', 'Pendiente')->sum(fn ($c) => (float) $c->monto), 2),
                ];
            });
    }

    public function pagarComisiones(string $correo, Usuario $usuario): int
    {
        return Comision::query()->where('vendedor_correo', $correo)->where('estado', 'Pendiente')
            ->whereHas('venta.ordenPago.interes', fn ($q) => AlcanceRepository::intereses($q, $usuario))
            ->update(['estado' => 'Pagada', 'fecha_pago' => now()]);
    }

    public function porcentajeComision(): float
    {
        return Comision::porcentajeVigente();
    }

    public function actualizarPorcentajeComision(string $valor, string $correo): void
    {
        DB::table('configuraciones')->updateOrInsert(['clave' => 'comision_porcentaje'], [
            'valor' => $valor, 'actualizado_por' => $correo, 'updated_at' => now(),
        ]);
    }

    public function inscripciones(Usuario $usuario): Collection
    {
        return InscripcionComercial::query()
            ->whereHas('solicitudCompra.ordenPago.interes', fn ($q) => AlcanceRepository::intereses($q, $usuario))
            ->with('solicitudCompra.ordenPago.interes.prospecto', 'solicitudCompra.ordenPago.vendedor:correo,nombre,apellido', 'exportaciones')
            ->orderByDesc('fecha_confirmacion')->get();
    }
}
