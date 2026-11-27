<?php

namespace App\Http\Requests\Usuario;

use App\Http\Requests\ApiRequest;
use Datos\Modelos\Usuario;
use Illuminate\Validation\Rule;

/** CU1: activar o desactivar una credencial. */
class CambiarEstadoUsuarioRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'estado' => ['required', Rule::in(Usuario::ESTADOS)],
        ];
    }
}
