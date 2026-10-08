<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['usuario_id', 'prospecto_id', 'fecha_exportacion', 'estado', 'respuesta'])]
class Exportacion extends Model
{
    protected $table = 'exportaciones';

    protected function casts(): array
    {
        return ['fecha_exportacion' => 'datetime'];
    }

    public function usuario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class);
    }

    public function prospecto(): BelongsTo
    {
        return $this->belongsTo(Prospecto::class);
    }
}
