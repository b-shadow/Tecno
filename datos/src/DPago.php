<?php

namespace Datos;

use Datos\Modelos\CatalogoCache;
use Datos\Modelos\ComprobantePago;
use Datos\Modelos\Cuota;
use Datos\Modelos\Descuento;
use Datos\Modelos\Interaccion;
use Datos\Modelos\Interes;
use Datos\Modelos\MetodoPago;
use Datos\Modelos\OrdenPago;
use Datos\Modelos\Pago;
use Datos\Modelos\Prospecto;
use Datos\Modelos\Usuario;
use Datos\DAlcance;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Consultas y escrituras persistentes del módulo de pagos. */
class DPago
{
    // Registros de la ruta por su identificador (404 si no existen): el negocio no consulta modelos por su cuenta.
    public function prospecto(string $documento): Prospecto { return Prospecto::query()->findOrFail($documento); }
    public function metodo(int $numero): MetodoPago { return MetodoPago::query()->findOrFail($numero); }
    public function interes(int $numero): Interes { return Interes::query()->findOrFail($numero); }
    public function orden(int $numero): OrdenPago { return OrdenPago::query()->findOrFail($numero); }
    public function comprobante(int $numero): ComprobantePago { return ComprobantePago::query()->findOrFail($numero); }

    public function transaccion(callable $operacion): mixed { return DB::transaction($operacion); }
    public function descuentos(): Collection { return Descuento::query()->where('estado', 'activo')->orderBy('nombre')->get(); }
    public function metodos(Prospecto $prospecto): Collection { return $prospecto->metodosPago()->orderByDesc('nro_metodo')->get(); }
    public function crearMetodo(array $datos): MetodoPago { return MetodoPago::query()->create($datos); }
    public function actualizarMetodo(MetodoPago $metodo, array $datos): void { $metodo->update($datos); }

    public function ordenes(Usuario $usuario): Collection
    {
        return OrdenPago::query()->whereHas('interes', fn ($q) => DAlcance::intereses($q, $usuario))
            ->with('interes.prospecto', 'vendedor:correo,nombre,apellido', 'items', 'descuentos.descuento', 'pago', 'cuotas.metodo')
            ->orderByDesc('nro_orden')->get();
    }

    public function modulos(array $codigos): Collection { return CatalogoCache::query()->with('programa')->whereIn('codigo', $codigos)->get(); }
    public function descuentosPorCodigo(array $codigos): Collection { return Descuento::query()->whereIn('codigo', $codigos)->get(); }
    public function crearOrden(array $datos): OrdenPago { return OrdenPago::query()->create($datos); }
    public function insertarDescuentosOrden(array $filas): void { if ($filas) DB::table('orden_pago_descuentos')->insert($filas); }
    public function actualizarOrden(OrdenPago $orden, array $datos): void { $orden->update($datos); }
    public function insertarItems(OrdenPago $orden, array $filas): void { foreach ($filas as $fila) $orden->items()->create($fila); }
    public function insertarCuotas(array $filas): void { if ($filas) Cuota::query()->insert($filas); }
    public function crearPago(array $datos): Pago { return Pago::query()->create($datos); }
    public function registrarInteraccion(Interes $interes, array $datos): Interaccion { return $interes->interacciones()->create($datos); }
    public function actualizarInteres(Interes $interes, array $datos): void { $interes->update($datos); }
    public function ordenCompleta(OrdenPago $orden): OrdenPago { return $orden->load('items', 'descuentos.descuento', 'pago', 'cuotas'); }

    public function cuotas(Usuario $usuario, ?string $estado): Collection
    {
        return Cuota::query()->join('ordenes_pago as o', 'o.nro_orden', '=', 'cuotas.nro_orden')
            ->join('intereses as i', 'i.nro_tarjeta', '=', 'o.nro_tarjeta')
            ->join('prospectos as p', 'p.documento', '=', 'i.documento')
            ->join('usuarios as v', 'v.correo', '=', 'o.vendedor_correo')
            ->tap(fn ($q) => DAlcance::intereses($q, $usuario, 'i'))
            ->when($estado, fn ($q, $valor) => $q->where('cuotas.estado', $valor))
            ->orderByRaw("cuotas.estado = 'En revision' desc")->orderBy('cuotas.fecha_vencimiento')
            ->select('cuotas.*', 'o.total as total_orden', 'o.nro_tarjeta', 'i.programa_nombre', 'i.modulo_nombre',
                DB::raw("p.nombre || ' ' || p.apellido as prospecto"), 'p.documento', 'p.telefono',
                DB::raw("v.nombre || ' ' || v.apellido as vendedor"))->get()
            ->map(function ($cuota) {
                $cuota->comprobantes = ComprobantePago::query()->where('nro_orden', $cuota->nro_orden)
                    ->where(fn ($q) => $q->where('nro_cuota', $cuota->nro_cuota)
                        ->orWhere(fn ($s) => $s->whereNull('nro_cuota')->whereRaw('? = 1', [$cuota->nro_cuota])))
                    ->orderByDesc('nro_comprobante')->get();
                return $cuota;
            });
    }

    public function cuotaBloqueada(int $orden, int $numero): ?object
    {
        return DB::table('cuotas')->where('nro_orden', $orden)->where('nro_cuota', $numero)->lockForUpdate()->first();
    }
    public function crearComprobante(array $datos): ComprobantePago { return ComprobantePago::query()->create($datos); }
    public function metodoActivo(string $documento, int $numero, ?string $tipo = null): ?MetodoPago
    {
        return MetodoPago::query()->whereKey($numero)->where('documento', $documento)->where('estado', 'activo')
            ->when($tipo, fn ($q, $valor) => $q->where('tipo', $valor))->first();
    }

    /** Orden de la tarjeta con su 1.ª cuota todavía abierta (pendiente o en revisión), como en el P1. */
    public function ordenAbierta(int $nroTarjeta): ?object
    {
        return DB::table('ordenes_pago as op')->join('pagos as pg', 'pg.nro_orden', '=', 'op.nro_orden')
            ->where('op.nro_tarjeta', $nroTarjeta)->whereIn('pg.estado', ['Pendiente de pago', 'En revision'])
            ->select('op.nro_orden', 'pg.estado')->first();
    }
    public function metodoConProspecto(MetodoPago $metodo): MetodoPago { return $metodo->loadMissing('prospecto'); }
    public function interesDeOrden(OrdenPago $orden): Interes { return $orden->loadMissing('interes.prospecto')->interes; }
    public function cambiarEstadoCuota(int $orden, int $numero, string $estado, array $extra = []): void
    {
        $extra = array_filter($extra, fn ($valor) => $valor !== null);
        if ($numero === 1) Pago::query()->whereKey($orden)->update(['estado' => $estado, 'updated_at' => now()]
            + (in_array($estado, ['Pago aprobado', 'Pago rechazado'], true)
                ? ['fecha_validacion' => now(), 'observacion_validacion' => $extra['observacion'] ?? null] : []));
        Cuota::query()->where('nro_orden', $orden)->where('nro_cuota', $numero)->update(['estado' => $estado, 'updated_at' => now()]
            + ($estado === 'Pago aprobado' ? ['fecha_pago' => now()] : []) + $extra);
    }
    public function actualizarComprobantes(int $orden, int $cuota, string $estado, ?string $observacion = null): void
    {
        $query = ComprobantePago::query()->where('nro_orden', $orden)->where('nro_cuota', $cuota)->where('estado_revision', 'En revision');
        $datos = ['estado_revision' => $estado, 'updated_at' => now()];
        if ($observacion !== null) $datos['observacion'] = $observacion;
        $query->update($datos);
    }
    public function interesBloqueado(int $numero): Interes { return Interes::query()->lockForUpdate()->findOrFail($numero); }
    public function ordenDeComprobante(int $numero): OrdenPago { return OrdenPago::query()->with('interes')->findOrFail($numero); }
    public function prospectoEnCartera(Prospecto $prospecto, Usuario $usuario): bool
    {
        return DAlcance::prospectos(Prospecto::query()->whereKey($prospecto->documento), $usuario)->exists();
    }
}
