<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Prospecto extends Model
{
    protected $table = 'prospectos';

    protected $primaryKey = 'documento';

    protected $keyType = 'string';

    public $incrementing = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return ['fecha_registro' => 'datetime'];
    }

    public function intereses(): HasMany
    {
        return $this->hasMany(Interes::class, 'documento', 'documento');
    }

    public function metodosPago(): HasMany
    {
        return $this->hasMany(MetodoPago::class, 'documento', 'documento');
    }

    public function transaccionesStripe(): HasMany
    {
        return $this->hasMany(TransaccionStripe::class, 'documento', 'documento');
    }
}
