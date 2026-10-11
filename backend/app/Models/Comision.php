<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['vendedor_id', 'venta_id', 'porcentaje', 'monto', 'estado', 'fecha_pago'])]
class Comision extends Model
{
    protected $table = 'comisiones';

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
        return $this->belongsTo(SolicitudCompra::class, 'venta_id');
    }
}
