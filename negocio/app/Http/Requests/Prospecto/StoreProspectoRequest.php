<?php

namespace App\Http\Requests\Prospecto;

use App\Services\ProspectoService;
use Illuminate\Validation\Rule;

/** CU3 (RF2.1): alta manual de un prospecto con su primer interés opcional. */
class StoreProspectoRequest extends ProspectoRequest
{
    public function rules(): array
    {
        return [
            'documento' => ['required', 'string', 'max:20', 'regex:/^[0-9A-Za-z-]+$/', 'unique:prospectos,documento'],
            'correo' => ['required', 'email', 'max:160', Rule::unique('prospectos', 'correo')],
            'origen' => ['required', Rule::in(ProspectoService::ORIGENES)],
            'modulo_codigo' => ['nullable', 'string'],
            'programa_codigo' => ['nullable', 'string'],
        ] + ProspectoService::reglasPersona();
    }
}
