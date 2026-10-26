<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Pago extends Model
{
    protected $table = 'pagos';

    protected $primaryKey = 'nro_orden';

    public $incrementing = false;

    protected $guarded = [];

    public const ESTADOS = ['Pendiente de pago', 'En revision', 'Pago aprobado', 'Pago rechazado'];

    protected function casts(): array
    {
        return ['fecha_validacion' => 'datetime'];
    }

    public function ordenPago(): BelongsTo
    {
        return $this->belongsTo(OrdenPago::class, 'nro_orden', 'nro_orden');
    }

    public function comprobantes(): HasMany
    {
        return $this->hasMany(ComprobantePago::class, 'nro_orden', 'nro_orden');
    }
}
