<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Hidden;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['nombre', 'apellido', 'correo', 'telefono', 'password', 'rol', 'estado'])]
#[Hidden(['password'])]
class Usuario extends Model
{
    public const ROLES = ['administrador', 'coordinador', 'vendedor'];
    public const ESTADOS = ['activo', 'inactivo'];

    protected $table = 'usuarios';

    public function tokens(): HasMany
    {
        return $this->hasMany(ApiToken::class);
    }

    public function prospectosAsignados(): HasMany
    {
        return $this->hasMany(Prospecto::class, 'vendedor_id');
    }

    public function interesesAsignados(): HasMany
    {
        return $this->hasMany(Interes::class, 'vendedor_id');
    }

    public function comisiones(): HasMany
    {
        return $this->hasMany(Comision::class, 'vendedor_id');
    }

    public function interaccionesRegistradas(): HasMany
    {
        return $this->hasMany(Interaccion::class, 'usuario_id');
    }

    public function recordatorios(): HasMany
    {
        return $this->hasMany(Recordatorio::class, 'usuario_id');
    }

}
