<?php

namespace App\Http\Requests\Prospecto;

use App\Negocio\NProspecto;
use Illuminate\Validation\Rule;

/** CU3: corrección de los datos del prospecto (el carnet, que es su clave, no se cambia). */
class UpdateProspectoRequest extends ProspectoRequest
{
    public function rules(): array
    {
        return [
            'correo' => ['required', 'email', 'max:160', Rule::unique('prospectos', 'correo')->ignore($this->route('prospecto'), 'documento')],
            'origen' => ['required', Rule::in(NProspecto::ORIGENES)],
        ] + collect(NProspecto::reglasPersona())->except(['documento', 'correo'])->all();
    }
}
