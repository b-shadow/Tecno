<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['solicitud_compra_id', 'fecha_confirmacion', 'estado'])]
class InscripcionComercial extends Model
{
    protected $table = 'inscripciones_comerciales';

    protected function casts(): array
    {
        return ['fecha_confirmacion' => 'datetime'];
    }

    public function solicitudCompra(): BelongsTo
    {
        return $this->belongsTo(SolicitudCompra::class);
    }

    public function exportaciones(): HasMany
    {
        return $this->hasMany(Exportacion::class);
    }

    /** El alumno es el prospecto de la orden a la que pertenece la venta inscrita. */
    public function alumno(): ?Prospecto
    {
        return $this->solicitudCompra?->ordenPago?->prospecto;
    }
}
