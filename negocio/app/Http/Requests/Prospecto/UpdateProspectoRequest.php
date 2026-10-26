<?php

namespace App\Http\Requests\Prospecto;

use App\Services\ProspectoService;
use Illuminate\Validation\Rule;

/** CU3: corrección de los datos del prospecto (el carnet, que es su clave, no se cambia). */
class UpdateProspectoRequest extends ProspectoRequest
{
    public function rules(): array
    {
        return [
            'correo' => ['required', 'email', 'max:160', Rule::unique('prospectos', 'correo')->ignore($this->route('prospecto')?->documento, 'documento')],
            'origen' => ['required', Rule::in(ProspectoService::ORIGENES)],
        ] + collect(ProspectoService::reglasPersona())->except(['documento', 'correo'])->all();
    }
}
