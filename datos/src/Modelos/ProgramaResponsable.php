<?php

namespace Datos\Modelos;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ProgramaResponsable extends Model
{
    protected $table = 'programas_responsables';

    protected $primaryKey = 'programa_codigo';

    protected $keyType = 'string';

    public $incrementing = false;

    protected $guarded = [];

    public function programa(): BelongsTo
    {
        return $this->belongsTo(Programa::class, 'programa_codigo', 'codigo');
    }

    public function coordinador(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'coordinador_correo', 'correo');
    }
}
