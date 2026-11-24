<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;

/** CU6: comprobante de una cuota (imagen o PDF en base64, hasta 5 MB). */
class RegistrarComprobanteRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'archivo' => ['required', 'string', 'max:8388608'],
            'nro_metodo' => ['nullable', 'integer'],
            'remitente' => ['nullable', 'string', 'max:160'],
            'hora_pago' => ['nullable', 'date', 'before_or_equal:now'],
            'observacion' => ['nullable', 'string', 'max:1000'],
        ];
    }

    public function attributes(): array
    {
        return [
            'archivo' => 'comprobante',
            'nro_metodo' => 'método de pago',
            'hora_pago' => 'hora del pago',
        ];
    }
}
