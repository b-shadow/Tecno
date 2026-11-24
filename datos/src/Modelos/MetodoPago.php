<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class MetodoPago extends Model
{
    protected $table = 'metodos_pago';

    protected $primaryKey = 'nro_metodo';

    protected $guarded = [];

    public const TIPOS = ['Tarjeta', 'QR', 'Transferencia'];

    public function prospecto(): BelongsTo
    {
        return $this->belongsTo(Prospecto::class, 'documento', 'documento');
    }
}
