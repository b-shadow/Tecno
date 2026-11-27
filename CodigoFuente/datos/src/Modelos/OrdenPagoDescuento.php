<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class OrdenPagoDescuento extends Model
{
    protected $table = 'orden_pago_descuentos';

    // Clave compuesta: Eloquent no la maneja; se consulta y actualiza con where() sobre sus dos columnas.
    protected $primaryKey = null;

    public $incrementing = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return ['porcentaje' => 'decimal:2', 'monto' => 'decimal:2'];
    }

    public function descuento(): BelongsTo
    {
        return $this->belongsTo(Descuento::class, 'descuento_codigo', 'codigo');
    }
}
