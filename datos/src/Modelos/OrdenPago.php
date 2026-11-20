<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;

class OrdenPago extends Model
{
    protected $table = 'ordenes_pago';

    protected $primaryKey = 'nro_orden';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'subtotal' => 'decimal:2',
            'descuento_total' => 'decimal:2',
            'total' => 'decimal:2',
            'fecha_generacion' => 'datetime',
            'fecha_anulacion' => 'datetime',
        ];
    }

    public function interes(): BelongsTo
    {
        return $this->belongsTo(Interes::class, 'nro_tarjeta', 'nro_tarjeta');
    }

    public function vendedor(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'vendedor_correo', 'correo');
    }

    public function anuladaPor(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'anulada_por', 'correo');
    }

    public function items(): HasMany
    {
        return $this->hasMany(SolicitudCompra::class, 'nro_orden', 'nro_orden');
    }

    public function descuentos(): HasMany
    {
        return $this->hasMany(OrdenPagoDescuento::class, 'nro_orden', 'nro_orden');
    }

    public function pago(): HasOne
    {
        return $this->hasOne(Pago::class, 'nro_orden', 'nro_orden');
    }

    public function cuotas(): HasMany
    {
        return $this->hasMany(Cuota::class, 'nro_orden', 'nro_orden')->orderBy('nro_cuota');
    }

    public function transaccionesStripe(): HasMany
    {
        return $this->hasMany(TransaccionStripe::class, 'nro_orden', 'nro_orden')->orderByDesc('nro_transaccion');
    }
}
