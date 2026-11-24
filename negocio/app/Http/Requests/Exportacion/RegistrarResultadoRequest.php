<?php

namespace App\Http\Requests\Exportacion;

use App\Http\Requests\ApiRequest;

/** CU6: respuesta del SIS a una exportación de matriculados. */
class RegistrarResultadoRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'estado' => ['required', 'in:recibida,error'],
            'respuesta' => ['nullable', 'string', 'max:2000'],
        ];
    }
}
