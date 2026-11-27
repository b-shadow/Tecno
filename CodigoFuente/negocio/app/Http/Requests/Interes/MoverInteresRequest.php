<?php

namespace App\Http\Requests\Interes;

use App\Http\Requests\ApiRequest;
use Datos\DMotivo;
use Datos\Modelos\Interes;
use Illuminate\Validation\Rule;

/** CU4/CU5: mover la tarjeta en el Kanban; Perdido exige motivo (RF3.3). */
class MoverInteresRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'estado' => ['required', Rule::in(Interes::ESTADOS)],
            'motivo_perdida' => ['nullable', 'required_if:estado,Perdido', $this->segun(fn ($v) => app(DMotivo::class)->existeNombre($v)), Rule::notIn(['Sin clasificar (web)'])],
            'observacion' => ['nullable', 'string', 'max:2000'],
        ];
    }

    public function messages(): array
    {
        return [
            'motivo_perdida.required_if' => 'Para marcar la tarjeta como Perdido debe elegir el motivo.',
        ];
    }

    public function attributes(): array
    {
        return [
            'motivo_perdida' => 'motivo de pérdida',
            'observacion' => 'observación',
        ];
    }
}
