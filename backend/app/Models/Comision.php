<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Facades\DB;

#[Fillable(['vendedor_id', 'solicitud_compra_id', 'porcentaje', 'monto', 'estado', 'fecha_pago'])]
class Comision extends Model
{
    protected $table = 'comisiones';

    public static function porcentajeVigente(): float
    {
        return (float) (DB::table('configuraciones')->where('clave', 'comision_porcentaje')->value('valor') ?? 2);
    }

    public static function registrar(int $ventaId, int $vendedorId, float $precio): self
    {
        $porcentaje = self::porcentajeVigente();

        return self::query()->firstOrCreate(['solicitud_compra_id' => $ventaId], [
            'vendedor_id' => $vendedorId,
            'porcentaje' => $porcentaje,
            'monto' => round($precio * $porcentaje / 100, 2),
            'estado' => 'Pendiente',
        ]);
    }

    protected function casts(): array
    {
        return [
            'porcentaje' => 'decimal:2',
            'monto' => 'decimal:2',
            'fecha_pago' => 'datetime',
        ];
    }

    public function vendedor(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'vendedor_id');
    }

    public function venta(): BelongsTo
    {
        return $this->belongsTo(SolicitudCompra::class, 'solicitud_compra_id');
    }
}
