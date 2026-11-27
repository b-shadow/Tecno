<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class InscripcionComercial extends Model
{
    protected $table = 'inscripciones_comerciales';

    protected $primaryKey = 'nro_solicitud';

    public $incrementing = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return ['fecha_confirmacion' => 'datetime'];
    }

    public function solicitudCompra(): BelongsTo
    {
        return $this->belongsTo(SolicitudCompra::class, 'nro_solicitud', 'nro_solicitud');
    }

    public function exportaciones(): HasMany
    {
        return $this->hasMany(Exportacion::class, 'nro_solicitud', 'nro_solicitud');
    }
}
