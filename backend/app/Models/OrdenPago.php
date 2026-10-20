<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;
use Illuminate\Database\Eloquent\Relations\HasOneThrough;

#[Fillable(['interes_id', 'vendedor_id', 'subtotal', 'descuento_total', 'total', 'estado', 'fecha_generacion'])]
class OrdenPago extends Model
{
    protected $table = 'ordenes_pago';

    protected function casts(): array
    {
        return [
            'subtotal' => 'decimal:2',
            'descuento_total' => 'decimal:2',
            'total' => 'decimal:2',
            'fecha_generacion' => 'datetime',
        ];
    }

    public function interes(): BelongsTo
    {
        return $this->belongsTo(Interes::class);
    }

    public function prospecto(): HasOneThrough
    {
        return $this->hasOneThrough(Prospecto::class, Interes::class, 'id', 'id', 'interes_id', 'prospecto_id');
    }

    public function vendedor(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'vendedor_id');
    }

    public function items(): HasMany
    {
        return $this->hasMany(SolicitudCompra::class);
    }

    public function descuentos(): HasMany
    {
        return $this->hasMany(OrdenPagoDescuento::class);
    }

    public function pago(): HasOne
    {
        return $this->hasOne(Pago::class);
    }
}
