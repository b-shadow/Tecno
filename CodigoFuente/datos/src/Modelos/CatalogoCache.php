<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class CatalogoCache extends Model
{
    protected $table = 'catalogo_cache';

    protected $primaryKey = 'codigo';

    protected $keyType = 'string';

    public $incrementing = false;

    public $timestamps = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return ['precio' => 'decimal:2', 'sincronizado_en' => 'datetime'];
    }

    public function programa(): BelongsTo
    {
        return $this->belongsTo(Programa::class, 'programa_codigo', 'codigo');
    }
}
