<?php

namespace App\Repositories;

use App\Models\Comision;
use App\Models\InscripcionComercial;
use App\Models\Interaccion;
use App\Models\Interes;
use App\Models\Recordatorio;
use App\Models\Usuario;
use App\Repositories\AlcanceRepository;
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

    public function resumenComisiones(): Collection
    {
        return DB::table('usuarios as u')->leftJoin('comisiones as c', 'c.vendedor_correo', '=', 'u.correo')
            ->where('u.rol', 'vendedor')->groupBy('u.correo', 'u.nombre', 'u.apellido')->orderBy('u.nombre')
            ->selectRaw("u.correo, u.nombre, u.apellido, count(c.nro_solicitud) as cursos_vendidos, coalesce(sum(c.monto),0) as comision_total,
                coalesce(sum(c.monto) filter (where c.estado = 'Pendiente'),0) as comision_pendiente")
            ->get();
    }

    public function pagarComisiones(string $correo): int
    {
        return Comision::query()->where('vendedor_correo', $correo)->where('estado', 'Pendiente')
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
