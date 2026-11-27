<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class WebhookEventoStripe extends Model
{
    protected $table = 'webhook_eventos_stripe';

    protected $primaryKey = 'stripe_evento';

    public $incrementing = false;

    protected $keyType = 'string';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'nro_transaccion' => 'integer',
            'livemode' => 'boolean',
            'procesado_en' => 'datetime',
        ];
    }

    public function transaccion(): BelongsTo
    {
        return $this->belongsTo(TransaccionStripe::class, 'nro_transaccion', 'nro_transaccion');
    }
}
