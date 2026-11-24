<?php

namespace App\Http\Requests;

/** Petición sin cuerpo que validar (consultas y acciones de un clic): solo aporta el usuario autenticado. */
class ConsultaRequest extends ApiRequest
{
    public function rules(): array
    {
        return [];
    }
}
