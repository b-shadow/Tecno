<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasOne;

#[Fillable([
    'orden_pago_id',
    'external_anuncio_id',
    'external_modulo_id',
    'programa_nombre',
    'modulo_nombre',
    'modulo_descripcion',
    'anuncio_titulo',
    'precio_acordado',
    'estado',
    'fecha',
])]
class SolicitudCompra extends Model
{
    protected $table = 'solicitudes_compra';

    protected function casts(): array
    {
        return [
            'fecha' => 'datetime',
            'precio_acordado' => 'decimal:2',
        ];
    }

    public function ordenPago(): BelongsTo
    {
        return $this->belongsTo(OrdenPago::class);
    }

    public function inscripcionComercial(): HasOne
    {
        return $this->hasOne(InscripcionComercial::class);
    }

    public function comision(): HasOne
    {
        return $this->hasOne(Comision::class);
    }
}
