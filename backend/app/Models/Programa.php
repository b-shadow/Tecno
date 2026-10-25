<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;

class Programa extends Model
{
    protected $table = 'programas';

    protected $primaryKey = 'codigo';

    protected $keyType = 'string';

    public $incrementing = false;

    public $timestamps = false;

    protected $guarded = [];

    public function modulos(): HasMany
    {
        return $this->hasMany(CatalogoCache::class, 'programa_codigo', 'codigo');
    }

    public function responsable(): HasOne
    {
        return $this->hasOne(ProgramaResponsable::class, 'programa_codigo', 'codigo');
    }
}
