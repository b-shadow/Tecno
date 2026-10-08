<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['solicitud_compra_id', 'orden_pago_id', 'monto', 'codigo_qr', 'estado', 'fecha_generacion', 'fecha_validacion', 'observacion_validacion'])]
class Pago extends Model
{
    public const ESTADOS = ['Pendiente de pago', 'En revision', 'Pago aprobado', 'Pago rechazado'];

    protected function casts(): array
    {
        return [
            'monto' => 'decimal:2',
            'fecha_generacion' => 'datetime',
            'fecha_validacion' => 'datetime',
        ];
    }

    public function solicitudCompra(): BelongsTo
    {
        return $this->belongsTo(SolicitudCompra::class);
    }

    public function ordenPago(): BelongsTo
    {
        return $this->belongsTo(OrdenPago::class);
    }

    public function comprobantes(): HasMany
    {
        return $this->hasMany(ComprobantePago::class);
    }
}
