<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;

/** CU6: inicio de Stripe Checkout para una cuota. El monto definitivo proviene exclusivamente de PostgreSQL. */
class CrearCheckoutRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'monto' => ['prohibited'],
            'amount' => ['prohibited'],
            'total' => ['prohibited'],
            'moneda' => ['prohibited'],
            'currency' => ['prohibited'],
        ];
    }

    public function messages(): array
    {
        return [
            'monto.prohibited' => 'El monto es determinado exclusivamente por el servidor y no puede modificarse.',
            'amount.prohibited' => 'El monto es determinado exclusivamente por el servidor y no puede modificarse.',
            'total.prohibited' => 'El monto es determinado exclusivamente por el servidor y no puede modificarse.',
            'moneda.prohibited' => 'La moneda oficial del sistema es BOB y no puede alterarse.',
            'currency.prohibited' => 'La moneda oficial del sistema es BOB y no puede alterarse.',
        ];
    }
}
