<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;

class Bitacora extends Model
{
    protected $table = 'bitacora';

    protected $primaryKey = 'nro_registro';

    public $timestamps = false;

    protected $guarded = [];

    public const EVENTOS = ['login_exitoso', 'login_fallido', 'logout', 'visita', 'acceso_denegado'];

    protected function casts(): array
    {
        return ['fecha' => 'datetime'];
    }
}
