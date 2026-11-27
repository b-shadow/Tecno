<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasOne;

class SolicitudCompra extends Model
{
    protected $table = 'solicitudes_compra';

    protected $primaryKey = 'nro_solicitud';

    protected $guarded = [];

    protected function casts(): array
    {
        return ['fecha' => 'datetime', 'precio_acordado' => 'decimal:2'];
    }

    public function ordenPago(): BelongsTo
    {
        return $this->belongsTo(OrdenPago::class, 'nro_orden', 'nro_orden');
    }

    public function inscripcion(): HasOne
    {
        return $this->hasOne(InscripcionComercial::class, 'nro_solicitud', 'nro_solicitud');
    }

    public function comision(): HasOne
    {
        return $this->hasOne(Comision::class, 'nro_solicitud', 'nro_solicitud');
    }
}
