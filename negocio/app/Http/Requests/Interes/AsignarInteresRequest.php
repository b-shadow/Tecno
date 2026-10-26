<?php

namespace App\Http\Requests\Interes;

use App\Http\Requests\ApiRequest;
use Illuminate\Validation\Rule;

/** CU3 (RF2.3): asignación manual de la tarjeta a un vendedor activo. */
class AsignarInteresRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'vendedor_correo' => ['required', Rule::exists('usuarios', 'correo')->where('rol', 'vendedor')->where('estado', 'activo')],
        ];
    }

    public function attributes(): array
    {
        return [
            'vendedor_correo' => 'vendedor',
        ];
    }
}
