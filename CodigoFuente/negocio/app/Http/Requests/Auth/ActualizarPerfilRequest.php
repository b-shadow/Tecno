<?php

namespace App\Http\Requests\Auth;

use App\Http\Requests\ApiRequest;

/** CU1: datos del perfil propio y foto (data URL; se guarda con nombre legible). */
class ActualizarPerfilRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'nombre' => ['required', 'string', 'max:120'],
            'apellido' => ['required', 'string', 'max:120'],
            'telefono' => ['nullable', 'string', 'regex:/^[0-9+ ]{7,20}$/'],
            'foto' => ['nullable', 'string'],
        ];
    }

    public function attributes(): array
    {
        return [
            'telefono' => 'teléfono',
        ];
    }
}
