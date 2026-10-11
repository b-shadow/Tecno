<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['prospecto_id', 'solicitud_compra_id', 'fecha_confirmacion', 'estado'])]
class InscripcionComercial extends Model
{
    protected $table = 'inscripciones_comerciales';

    protected function casts(): array
    {
        return ['fecha_confirmacion' => 'datetime'];
    }

    public function prospecto(): BelongsTo
    {
        return $this->belongsTo(Prospecto::class);
    }

    public function solicitudCompra(): BelongsTo
    {
        return $this->belongsTo(SolicitudCompra::class);
    }
}
