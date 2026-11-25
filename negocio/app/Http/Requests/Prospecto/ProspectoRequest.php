<?php

namespace App\Http\Requests\Prospecto;

use App\Http\Requests\ApiRequest;
use App\Negocio\NProspecto;

/** Base de los formularios con datos personales del prospecto: correo normalizado y atributos en español. */
abstract class ProspectoRequest extends ApiRequest
{
    protected function prepareForValidation(): void
    {
        if ($this->has('correo')) {
            $this->merge(['correo' => mb_strtolower(trim((string) $this->input('correo')))]);
        }
    }

    public function attributes(): array
    {
        return NProspecto::ATRIBUTOS;
    }
}
