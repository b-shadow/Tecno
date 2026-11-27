<?php

namespace App\Http\Requests\Auth;

use App\Http\Requests\ApiRequest;

/** CU1: cambio de la contraseña propia (mínimo 8 caracteres con letras y números). */
class CambiarPasswordRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'password_actual' => ['required', 'string'],
            'password' => ['required', 'string', 'min:8', 'max:120', 'regex:/(?=.*[A-Za-z])(?=.*\\d)/', 'confirmed'],
        ];
    }

    public function messages(): array
    {
        return [
            'password.regex' => 'La nueva contraseña debe tener letras y números.',
        ];
    }

    public function attributes(): array
    {
        return [
            'password_actual' => 'contraseña actual',
            'password' => 'nueva contraseña',
        ];
    }
}
