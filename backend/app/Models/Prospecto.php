<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasManyThrough;

#[Fillable(['nombre', 'apellido', 'documento', 'correo', 'telefono', 'profesion', 'ubicacion', 'estado', 'fecha_registro'])]
class Prospecto extends Model
{
    public const ESTADOS = ['Nuevo', 'Contactado', 'Interesado', 'En proceso', 'Convertido', 'Perdido'];

    protected function casts(): array
    {
        return ['fecha_registro' => 'datetime'];
    }

    public function intereses(): HasMany
    {
        return $this->hasMany(Interes::class);
    }

    public function ordenesPago(): HasManyThrough
    {
        return $this->hasManyThrough(OrdenPago::class, Interes::class);
    }

    public function interacciones(): HasManyThrough
    {
        return $this->hasManyThrough(Interaccion::class, Interes::class);
    }

    public function recordatorios(): HasManyThrough
    {
        return $this->hasManyThrough(Recordatorio::class, Interes::class);
    }

}
