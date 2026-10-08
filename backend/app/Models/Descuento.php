<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;

#[Fillable(['nombre', 'codigo', 'porcentaje', 'estado'])]
class Descuento extends Model
{
    protected $table = 'descuentos';

    protected function casts(): array
    {
        return ['porcentaje' => 'decimal:2'];
    }
}
