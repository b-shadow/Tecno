<?php

namespace App\Http\Requests\Prospecto;

/** CU3 (RF2.2): nuevo interés de un prospecto existente. */
class CrearInteresRequest extends ProspectoRequest
{
    public function rules(): array
    {
        return [
            'modulo_codigo' => ['nullable', 'string', 'required_without:programa_codigo'],
            'programa_codigo' => ['nullable', 'string'],
        ];
    }

    public function attributes(): array
    {
        return [
            'modulo_codigo' => 'módulo',
            'programa_codigo' => 'programa',
        ];
    }
}
