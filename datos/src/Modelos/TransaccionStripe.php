<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class TransaccionStripe extends Model
{
    protected $table = 'transacciones_stripe';

    protected $primaryKey = 'nro_transaccion';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'nro_orden' => 'integer',
            'nro_cuota' => 'integer',
            'monto_esperado' => 'decimal:2',
            'monto_centavos' => 'integer',
            'monto_confirmado' => 'decimal:2',
            'livemode' => 'boolean',
            'confirmado_en' => 'datetime',
        ];
    }

    public function orden(): BelongsTo
    {
        return $this->belongsTo(OrdenPago::class, 'nro_orden', 'nro_orden');
    }

    public function prospecto(): BelongsTo
    {
        return $this->belongsTo(Prospecto::class, 'documento', 'documento');
    }

    public function usuario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'usuario_correo', 'correo');
    }
}
