<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class MovimientoInteres extends Model
{
    protected $table = 'movimientos_interes';

    protected $primaryKey = 'nro_movimiento';

    public $timestamps = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return ['fecha' => 'datetime'];
    }

    public function usuario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'usuario_correo', 'correo');
    }
}
