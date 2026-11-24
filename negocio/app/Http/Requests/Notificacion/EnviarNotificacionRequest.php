<?php

namespace App\Http\Requests\Notificacion;

use App\Http\Requests\ApiRequest;

/** CU7: correo al prospecto o a un usuario. */
class EnviarNotificacionRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'destinatario' => ['required', 'email', 'max:160'],
            'tipo' => ['required', 'string', 'max:120'],
            'mensaje' => ['required', 'string', 'min:3', 'max:5000'],
        ];
    }

    public function attributes(): array
    {
        return [
            'tipo' => 'asunto',
        ];
    }
}
