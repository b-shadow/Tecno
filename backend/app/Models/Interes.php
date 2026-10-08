<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['prospecto_id', 'vendedor_id', 'external_modulo_id', 'external_anuncio_id', 'programa_nombre', 'modulo_nombre', 'modulo_descripcion', 'precio', 'estado', 'fecha', 'fecha_asignacion', 'ultima_actividad_en', 'proximo_contacto', 'observacion'])]
class Interes extends Model
{
    public const ESTADOS = ['Nuevo', 'Contactado', 'Interesado', 'Pago enviado', 'En revision', 'Convertido', 'Perdido'];

    protected $table = 'intereses';

    protected function casts(): array
    {
        return [
            'fecha' => 'datetime',
            'fecha_asignacion' => 'datetime',
            'ultima_actividad_en' => 'datetime',
            'proximo_contacto' => 'datetime',
        ];
    }

    public function prospecto(): BelongsTo
    {
        return $this->belongsTo(Prospecto::class);
    }

    public function vendedor(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'vendedor_id');
    }

    public function interacciones(): HasMany
    {
        return $this->hasMany(Interaccion::class);
    }

    public function recordatorios(): HasMany
    {
        return $this->hasMany(Recordatorio::class);
    }

    public function ordenesPago(): HasMany
    {
        return $this->hasMany(OrdenPago::class);
    }
}
