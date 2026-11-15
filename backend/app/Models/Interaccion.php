<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasOneThrough;

#[Fillable(['interes_id', 'usuario_id', 'tipo', 'descripcion', 'resultado', 'fecha'])]
class Interaccion extends Model
{
    public const TIPOS = ['WhatsApp', 'Llamada', 'Correo electronico', 'Reunion', 'Nota comercial', 'Orden de pago enviada', 'Pago informado', 'Compra validada', 'Orden finalizada'];

    protected $table = 'interacciones';

    protected function casts(): array
    {
        return ['fecha' => 'datetime'];
    }

    public function prospecto(): HasOneThrough
    {
        return $this->hasOneThrough(Prospecto::class, Interes::class, 'id', 'id', 'interes_id', 'prospecto_id');
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
