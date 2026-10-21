<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Usuario extends Model
{
    protected $table = 'usuarios';

    protected $primaryKey = 'correo';

    protected $keyType = 'string';

    public $incrementing = false;

    protected $guarded = [];

    public const ROLES = ['administrador', 'coordinador', 'vendedor'];

    public const ESTADOS = ['activo', 'inactivo'];

    protected $hidden = ['password'];

    protected $appends = ['foto_url'];

    protected function casts(): array
    {
        return ['fecha_inicio' => 'date:Y-m-d', 'fecha_fin' => 'date:Y-m-d'];
    }

    /** Credencial vigente (clase 03): activa y dentro de fecha_inicio..fecha_fin. */
    public function vigente(): bool
    {
        $hoy = now()->toDateString();

        return $this->estado === 'activo' && $this->fecha_inicio->toDateString() <= $hoy && $this->fecha_fin->toDateString() >= $hoy;
    }

    public function getFotoUrlAttribute(): ?string
    {
        return $this->foto ? url('/api/fotos/'.rawurlencode($this->foto)) : null;
    }

    public function tokens(): HasMany
    {
        return $this->hasMany(ApiToken::class, 'usuario_correo', 'correo');
    }

    public function programasACargo(): HasMany
    {
        return $this->hasMany(ProgramaResponsable::class, 'coordinador_correo', 'correo');
    }
}
