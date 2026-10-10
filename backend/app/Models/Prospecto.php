<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['nombre', 'apellido', 'documento', 'correo', 'telefono', 'profesion', 'ubicacion', 'estado', 'vendedor_id', 'fecha_registro'])]
class Prospecto extends Model
{
    public const ESTADOS = ['Nuevo', 'Contactado', 'Interesado', 'En proceso', 'Convertido', 'Perdido'];

    protected function casts(): array
    {
        return ['fecha_registro' => 'datetime'];
    }

    public function vendedor(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'vendedor_id');
    }

    public function intereses(): HasMany
    {
        return $this->hasMany(Interes::class);
    }

    public function solicitudesCompra(): HasMany
    {
        return $this->hasMany(SolicitudCompra::class);
    }

    public function interacciones(): HasMany
    {
        return $this->hasMany(Interaccion::class);
    }

    public function recordatorios(): HasMany
    {
        return $this->hasMany(Recordatorio::class);
    }

}
