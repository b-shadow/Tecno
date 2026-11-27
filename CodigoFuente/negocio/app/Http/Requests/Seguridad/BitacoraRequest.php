<?php

namespace App\Http\Requests\Seguridad;

use App\Http\Requests\ApiRequest;
use Datos\Modelos\Bitacora;
use Illuminate\Validation\Rule;

/** Enunciado 4: filtros de la bitácora de auditoría. */
class BitacoraRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'evento' => ['nullable', Rule::in(Bitacora::EVENTOS)],
            'desde' => ['nullable', 'date'],
            'hasta' => ['nullable', 'date', 'after_or_equal:desde'],
            'usuario' => ['nullable', 'string', 'max:160'],
            'ip' => ['nullable', 'string', 'max:45'],
        ];
    }

    public function attributes(): array
    {
        return [
            'desde' => 'fecha inicial',
            'hasta' => 'fecha final',
        ];
    }
}
