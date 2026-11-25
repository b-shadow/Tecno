<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;

/** CU6: registro de método de pago con tarjeta en Stripe Checkout (mode=setup). */
class CrearSetupTarjetaRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'nro_tarjeta' => ['nullable', 'integer', 'min:1'],
        ];
    }
}
