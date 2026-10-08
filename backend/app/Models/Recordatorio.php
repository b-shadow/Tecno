<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['prospecto_id', 'interes_id', 'usuario_id', 'fecha_programada', 'fecha_realizada', 'descripcion', 'estado'])]
class Recordatorio extends Model
{
    public const ESTADOS = ['Pendiente', 'Realizada', 'Atrasada', 'Cancelado'];

    protected $table = 'recordatorios';

    protected function casts(): array
    {
        return [
            'fecha_programada' => 'datetime',
            'fecha_realizada' => 'datetime',
        ];
    }

    public function prospecto(): BelongsTo
    {
        return $this->belongsTo(Prospecto::class);
    }

    public function interes(): BelongsTo
    {
        return $this->belongsTo(Interes::class);
    }

    public function usuario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class);
    }
}
