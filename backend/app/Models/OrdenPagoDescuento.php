<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['orden_pago_id', 'descuento_id', 'porcentaje', 'monto'])]
class OrdenPagoDescuento extends Model
{
    protected $table = 'orden_pago_descuentos';

    protected function casts(): array
    {
        return [
            'porcentaje' => 'decimal:2',
            'monto' => 'decimal:2',
        ];
    }

    public function descuento(): BelongsTo
    {
        return $this->belongsTo(Descuento::class);
    }
}
