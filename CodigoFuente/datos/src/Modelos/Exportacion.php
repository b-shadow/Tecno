<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Exportacion extends Model
{
    protected $table = 'exportaciones';

    protected $primaryKey = 'nro_exportacion';

    protected $guarded = [];

    protected function casts(): array
    {
        return ['fecha_exportacion' => 'datetime'];
    }

    public function usuario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'usuario_correo', 'correo');
    }
}
