<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Cuota extends Model
{
    protected $table = 'cuotas';

    // Clave compuesta: Eloquent no la maneja; se consulta y actualiza con where() sobre sus dos columnas.
    protected $primaryKey = null;

    public $incrementing = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return ['monto' => 'decimal:2', 'fecha_vencimiento' => 'date:Y-m-d', 'fecha_pago' => 'datetime', 'nro_cuota' => 'integer'];
    }

    public function metodo(): BelongsTo
    {
        return $this->belongsTo(MetodoPago::class, 'nro_metodo', 'nro_metodo');
    }
}
