<?php

namespace App\Repositories;

use App\Models\Comision;
use App\Models\InscripcionComercial;
use App\Models\Interes;
use App\Models\Interaccion;
use App\Models\OrdenPago;
use Illuminate\Support\Facades\DB;

/** Persistencia de las matrículas y movimientos generados al convertir una tarjeta. */
class ConversionRepository
{
    public function datosConversion(Interes $interes): array
    {
        $interes->loadMissing('prospecto');

        return [$interes->prospecto, $this->ordenAprobada($interes)];
    }

    public function ordenAprobada(Interes $interes): ?OrdenPago
    {
        return OrdenPago::query()->with('items')
            ->where('nro_tarjeta', $interes->nro_tarjeta)
            ->whereExists(fn ($q) => $q->select(DB::raw(1))->from('pagos')
                ->whereColumn('pagos.nro_orden', 'ordenes_pago.nro_orden')->where('pagos.estado', 'Pago aprobado'))
            ->latest('nro_orden')->first();
    }

    public function registrarInscripcionesYComisiones(OrdenPago $orden): void
    {
        foreach ($orden->items as $item) {
            InscripcionComercial::query()->firstOrCreate(
                ['nro_solicitud' => $item->nro_solicitud], ['fecha_confirmacion' => now()],
            );
            Comision::registrar($item->nro_solicitud, $orden->vendedor_correo, (float) $item->precio_acordado);
        }
    }

    public function registrarInteraccion(Interes $interes, array $datos): void
    {
        Interaccion::query()->create(['nro_tarjeta' => $interes->nro_tarjeta] + $datos);
    }

    public function actualizarConversion(Interes $interes, array $datosInteres, string $estadoProspecto): void
    {
        $interes->update($datosInteres);
        $interes->prospecto->update(['estado' => $estadoProspecto]);
    }
}
