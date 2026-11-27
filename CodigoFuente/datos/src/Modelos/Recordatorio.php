<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Recordatorio extends Model
{
    protected $table = 'recordatorios';

    protected $primaryKey = 'nro_recordatorio';

    protected $guarded = [];

    public const ESTADOS = ['Pendiente', 'Realizada', 'Atrasada', 'Cancelado'];

    protected function casts(): array
    {
        return ['fecha_programada' => 'datetime', 'fecha_realizada' => 'datetime', 'notificado' => 'boolean'];
    }

    public function interes(): BelongsTo
    {
        return $this->belongsTo(Interes::class, 'nro_tarjeta', 'nro_tarjeta');
    }

    public function usuario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'usuario_correo', 'correo');
    }
}
