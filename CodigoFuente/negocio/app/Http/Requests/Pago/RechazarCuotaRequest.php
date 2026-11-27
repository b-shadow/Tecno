<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;

/** CU6: coordinación rechaza una cuota en revisión con el motivo para el vendedor. */
class RechazarCuotaRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'observacion' => ['required', 'string', 'max:1000'],
        ];
    }

    public function messages(): array
    {
        return [
            'observacion.required' => 'Indique el motivo del rechazo para el vendedor.',
        ];
    }
}
