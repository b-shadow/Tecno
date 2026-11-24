<?php

namespace App\Http\Requests\Prospecto;

use App\Services\ProspectoService;

/** CU2: formulario público "Me interesa" del catálogo (módulos sueltos o programa completo). */
class RegistrarInteresRequest extends ProspectoRequest
{
    public function rules(): array
    {
        return [
            'modulo_codigo' => ['nullable', 'string', 'required_without_all:programa_codigo,modulo_codigos'],
            'programa_codigo' => ['nullable', 'string', 'required_without_all:modulo_codigo,modulo_codigos'],
            'modulo_codigos' => ['sometimes', 'array', 'min:1'],
            'modulo_codigos.*' => ['required', 'string', 'distinct'],
        ] + ProspectoService::reglasPersona();
    }
}
