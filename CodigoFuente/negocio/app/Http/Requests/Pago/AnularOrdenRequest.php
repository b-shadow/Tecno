<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;

/** CU6: anulación controlada de una orden de pago sin cuotas aprobadas ni en revisión. */
class AnularOrdenRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'motivo' => ['required', 'string', 'min:5', 'max:500'],
        ];
    }

    public function attributes(): array
    {
        return [
            'motivo' => 'motivo de anulación',
        ];
    }
}
