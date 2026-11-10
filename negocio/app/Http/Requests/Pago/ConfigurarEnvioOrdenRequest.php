<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;

/** CU6 / CU7: activa o desactiva el envío automático de recordatorios en una orden. */
class ConfigurarEnvioOrdenRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'envio_automatico' => ['required', 'boolean'],
        ];
    }
}
