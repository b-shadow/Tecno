<?php

namespace App\Http\Requests\Seguimiento;

use App\Http\Requests\ApiRequest;

/** CU6: porcentaje global de comisión de las ventas. */
class ActualizarComisionRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'porcentaje' => ['required', 'numeric', 'min:0', 'max:50'],
        ];
    }

    public function attributes(): array
    {
        return [
            'porcentaje' => 'porcentaje de comisión',
        ];
    }
}
