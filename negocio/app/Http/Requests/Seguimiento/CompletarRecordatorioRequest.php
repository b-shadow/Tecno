<?php

namespace App\Http\Requests\Seguimiento;

use App\Http\Requests\ApiRequest;

/** CU7: marcar una actividad como realizada con su resultado. */
class CompletarRecordatorioRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'resultado' => ['required', 'string', 'min:3', 'max:1000'],
        ];
    }

    public function attributes(): array
    {
        return [
            'resultado' => 'resultado de la actividad',
        ];
    }
}
