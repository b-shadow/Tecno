<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;
use Illuminate\Validation\Rule;

/** CU6: orden de pago con pago único o plan de 2 a 12 cuotas. */
class CrearOrdenRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'modulos' => ['required', 'array', 'min:1'],
            'modulos.*' => ['required', 'string', 'distinct', Rule::exists('catalogo_cache', 'codigo')->where('estado', 'abierto')],
            'descuentos' => ['nullable', 'array'],
            'descuentos.*' => ['string', Rule::exists('descuentos', 'codigo')->where('estado', 'activo')],
            'cuotas' => ['required', 'integer', 'between:1,12'],
            'primer_vencimiento' => ['required', 'date', 'after_or_equal:today'],
            'envio_automatico' => ['nullable', 'boolean'],
        ];
    }

    public function attributes(): array
    {
        return [
            'modulos' => 'módulos',
            'cuotas' => 'número de cuotas',
            'primer_vencimiento' => 'primer vencimiento',
        ];
    }
}
