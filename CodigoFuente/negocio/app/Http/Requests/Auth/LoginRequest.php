<?php

namespace App\Http\Requests\Auth;

use App\Http\Requests\ApiRequest;

/** CU1: inicio de sesión con correo y contraseña. */
class LoginRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'correo' => ['required', 'email', 'max:160'],
            'password' => ['required', 'string', 'max:120'],
        ];
    }
}
