<?php

namespace App\Http\Requests\Seguimiento;

use App\Http\Requests\ApiRequest;

/** CU7 (RF4.3): actividad agendada a futuro. */
class CrearRecordatorioRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'fecha_programada' => ['required', 'date'],
            'descripcion' => ['required', 'string', 'min:3', 'max:1000'],
        ];
    }

    public function attributes(): array
    {
        return [
            'fecha_programada' => 'fecha y hora',
            'descripcion' => 'descripción',
        ];
    }
}
