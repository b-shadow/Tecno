<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;

class ComprobantePago extends Model
{
    protected $table = 'comprobantes_pago';

    protected $primaryKey = 'nro_comprobante';

    protected $guarded = [];

    protected $hidden = ['archivo'];

    protected function casts(): array
    {
        return ['fecha_envio' => 'datetime', 'hora_pago' => 'datetime', 'nro_cuota' => 'integer'];
    }
}
