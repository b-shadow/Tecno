<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['pago_id', 'archivo', 'nombre_archivo', 'mime', 'remitente', 'hora_pago', 'fecha_envio', 'observacion', 'estado_revision'])]
class ComprobantePago extends Model
{
    protected $table = 'comprobantes_pago';

    protected function casts(): array
    {
        return [
            'fecha_envio' => 'datetime',
            'hora_pago' => 'datetime',
        ];
    }

    public function pago(): BelongsTo
    {
        return $this->belongsTo(Pago::class);
    }
}
