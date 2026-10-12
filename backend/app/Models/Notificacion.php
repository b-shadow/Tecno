<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['usuario_id', 'destinatario', 'tipo', 'mensaje', 'estado', 'fecha_envio'])]
class Notificacion extends Model
{
    protected $table = 'notificaciones';

    protected function casts(): array
    {
        return ['fecha_envio' => 'datetime'];
    }

    public function usuario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class);
    }
}
