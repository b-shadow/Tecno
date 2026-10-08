<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[Fillable(['usuario_id', 'token_hash', 'ultimo_uso_en', 'expira_en'])]
class ApiToken extends Model
{
    protected $table = 'api_tokens';

    protected function casts(): array
    {
        return [
            'ultimo_uso_en' => 'datetime',
            'expira_en' => 'datetime',
        ];
    }

    public function usuario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class);
    }
}
