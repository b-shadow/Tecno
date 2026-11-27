<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;

class Recurso extends Model
{
    protected $table = 'recursos';

    protected $primaryKey = 'codigo';

    protected $keyType = 'string';

    public $incrementing = false;

    public $timestamps = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return ['publico' => 'boolean', 'visitas' => 'integer', 'orden' => 'integer'];
    }
}
