<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;

/** CU6: coordinación aprueba una cuota en revisión. */
class AprobarCuotaRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'observacion' => ['nullable', 'string', 'max:1000'],
        ];
    }
}
