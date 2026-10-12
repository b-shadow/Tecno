<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['orden_pago_id', 'solicitud_compra_id', 'external_modulo_id', 'programa_nombre', 'modulo_nombre', 'modulo_descripcion', 'precio'])]
class OrdenPagoItem extends Model
{
    protected $table = 'orden_pago_items';

    protected function casts(): array
    {
        return ['precio' => 'decimal:2'];
    }

    public function ordenPago(): BelongsTo
    {
        return $this->belongsTo(OrdenPago::class);
    }

    public function solicitudCompra(): BelongsTo
    {
        return $this->belongsTo(SolicitudCompra::class);
    }
}
