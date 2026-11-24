<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;
use Illuminate\Validation\Rule;

/** CU6: activar o desactivar un método de pago. */
class CambiarEstadoMetodoRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'estado' => ['required', Rule::in(['activo', 'inactivo'])],
        ];
    }
}
