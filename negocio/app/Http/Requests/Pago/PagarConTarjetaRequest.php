<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;

/** CU6: cobro de una cuota con una tarjeta registrada (pasarela simulada). */
class PagarConTarjetaRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'nro_metodo' => ['required', 'integer'],
        ];
    }

    public function attributes(): array
    {
        return [
            'nro_metodo' => 'tarjeta',
        ];
    }
}
