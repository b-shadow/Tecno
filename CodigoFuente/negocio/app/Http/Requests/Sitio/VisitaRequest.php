<?php

namespace App\Http\Requests\Sitio;

use App\Http\Requests\ApiRequest;

/** Enunciado 7: ruta de la página que se acaba de abrir. */
class VisitaRequest extends ApiRequest
{
    public function rules(): array
    {
        return ['ruta' => ['required', 'string', 'max:80']];
    }
}
