<?php

namespace App\Http\Requests\Notificacion;

use App\Http\Requests\ApiRequest;

/** CU7: correo al prospecto o a un usuario. */
class EnviarNotificacionRequest extends ApiRequest
{
    public function rules(): array
    {
        $frontend = preg_quote(rtrim((string) config('services.frontend.url', 'http://localhost:5173'), '/'), '#');

        return [
            'destinatario' => ['required', 'email', 'max:160'],
            'tipo' => ['required', 'string', 'max:120'],
            'mensaje' => ['required', 'string', 'min:3', 'max:5000'],
            'enlace' => ['nullable', 'url', 'max:2048', "regex:#^(https://checkout\\.stripe\\.com/|{$frontend}/)#"],
            'texto_boton' => ['nullable', 'string', 'min:2', 'max:60'],
        ];
    }

    public function messages(): array
    {
        return [
            'enlace.regex' => 'Solo se permiten enlaces oficiales de Stripe Checkout o del sistema UNEXO.',
        ];
    }

    public function attributes(): array
    {
        return [
            'tipo' => 'asunto',
        ];
    }
}
