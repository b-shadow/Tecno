<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class MotivoPerdida extends Model
{
    protected $table = 'motivos_perdida';

    protected $primaryKey = 'nombre';

    protected $keyType = 'string';

    public $incrementing = false;

    public $timestamps = false;

    protected $guarded = [];

    public const CATEGORIAS = ['Económico', 'Horario', 'Incompatibilidad', 'Contacto', 'Otro'];
}
