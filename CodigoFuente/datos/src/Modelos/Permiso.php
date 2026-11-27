<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;

class Permiso extends Model
{
    protected $table = 'permisos';

    // Clave compuesta: Eloquent no la maneja; se consulta y actualiza con where() sobre sus dos columnas.
    protected $primaryKey = null;

    public $incrementing = false;

    protected $guarded = [];

    /** lectura < modificacion < eliminacion: cada nivel incluye a los anteriores. */
    public const NIVELES = ['lectura' => 1, 'modificacion' => 2, 'eliminacion' => 3];
}
