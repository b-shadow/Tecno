<?php

namespace App\Http\Requests\Seguimiento;

use App\Http\Requests\ApiRequest;
use Illuminate\Validation\Rule;

/** CU7 (RF4.2): nota o contacto ya ocurrido con el prospecto. */
class RegistrarInteraccionRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'tipo' => ['required', Rule::in(['WhatsApp', 'Llamada', 'Correo electronico', 'Reunion', 'Nota comercial'])],
            'descripcion' => ['required', 'string', 'min:3', 'max:2000'],
            'resultado' => ['nullable', 'string', 'max:500'],
        ];
    }

    public function attributes(): array
    {
        return [
            'descripcion' => 'descripción',
        ];
    }
}
