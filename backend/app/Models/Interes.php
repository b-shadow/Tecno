<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Interes extends Model
{
    protected $table = 'intereses';

    protected $primaryKey = 'nro_tarjeta';

    protected $guarded = [];

    /** RF3.2: columnas del tablero Kanban (CU4), en orden. */
    public const ESTADOS = ['Nuevo', 'En Contacto', 'Seguimiento', 'Promesa de Pago', 'Convertido', 'Perdido'];

    protected function casts(): array
    {
        return ['fecha' => 'datetime', 'fecha_asignacion' => 'datetime', 'ultima_actividad_en' => 'datetime', 'proximo_contacto' => 'datetime', 'precio' => 'decimal:2'];
    }

    public function prospecto(): BelongsTo
    {
        return $this->belongsTo(Prospecto::class, 'documento', 'documento');
    }

    public function vendedor(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'vendedor_correo', 'correo');
    }

    public function modulo(): BelongsTo
    {
        return $this->belongsTo(CatalogoCache::class, 'modulo_codigo', 'codigo');
    }

    public function interacciones(): HasMany
    {
        return $this->hasMany(Interaccion::class, 'nro_tarjeta', 'nro_tarjeta');
    }

    public function recordatorios(): HasMany
    {
        return $this->hasMany(Recordatorio::class, 'nro_tarjeta', 'nro_tarjeta');
    }

    public function movimientos(): HasMany
    {
        return $this->hasMany(MovimientoInteres::class, 'nro_tarjeta', 'nro_tarjeta');
    }

    public function ordenesPago(): HasMany
    {
        return $this->hasMany(OrdenPago::class, 'nro_tarjeta', 'nro_tarjeta');
    }
}
