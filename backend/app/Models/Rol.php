<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Rol extends Model
{
    protected $table = 'roles';

    protected $primaryKey = 'nombre';

    protected $keyType = 'string';

    public $incrementing = false;

    protected $guarded = [];
}
