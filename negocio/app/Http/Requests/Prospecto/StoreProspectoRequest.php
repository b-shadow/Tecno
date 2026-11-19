<?php

namespace App\Http\Requests\Prospecto;

use App\Negocio\NProspecto;
use Datos\DProspecto;
use Illuminate\Validation\Rule;

/** CU3 (RF2.1): alta manual de un prospecto con su primer interés opcional. */
class StoreProspectoRequest extends ProspectoRequest
{
    public function rules(): array
    {
        return [
            'documento' => ['required', 'string', 'max:20', 'regex:/^[0-9A-Za-z-]+$/', $this->segun(fn ($v) => ! app(DProspecto::class)->existeDocumento($v), 'validation.unique')],
            'correo' => ['required', 'email', 'max:160', $this->segun(fn ($v) => ! app(DProspecto::class)->correoEnUso($v), 'validation.unique')],
            'origen' => ['required', Rule::in(NProspecto::ORIGENES)],
            'modulo_codigo' => ['nullable', 'string'],
            'programa_codigo' => ['nullable', 'string'],
        ] + NProspecto::reglasPersona();
    }
}
