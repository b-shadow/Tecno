<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;

class Notificacion extends Model
{
    protected $table = 'notificaciones';

    protected $primaryKey = 'nro_notificacion';

    protected $guarded = [];

    protected function casts(): array
    {
        return ['fecha_envio' => 'datetime'];
    }
}
