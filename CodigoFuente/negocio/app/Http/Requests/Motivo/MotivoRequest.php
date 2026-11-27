<?php

namespace App\Http\Requests\Motivo;

use App\Http\Requests\ApiRequest;
use Datos\Modelos\MotivoPerdida;
use Illuminate\Validation\Rule;

/** CU5: alta o edición de un motivo de pérdida con su categoría. */
class MotivoRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'nombre' => ['required', 'string', 'max:80'],
            'categoria' => ['required', Rule::in(MotivoPerdida::CATEGORIAS)],
        ];
    }

    public function attributes(): array
    {
        return [
            'nombre' => 'motivo',
        ];
    }
}
