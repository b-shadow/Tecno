<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;
use Datos\DCatalogo;
use Datos\DPago;

/** CU6: orden de pago con pago único o plan de 2 a 12 cuotas. */
class CrearOrdenRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'modulos' => ['required', 'array', 'min:1'],
            'modulos.*' => ['required', 'string', 'distinct', $this->segun(fn ($v) => app(DCatalogo::class)->esModuloAbierto($v))],
            'descuentos' => ['nullable', 'array'],
            'descuentos.*' => ['string', $this->segun(fn ($v) => app(DPago::class)->esDescuentoActivo($v))],
            'cuotas' => ['required', 'integer', 'between:1,12'],
            'primer_vencimiento' => ['required', 'date', 'after_or_equal:today'],
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
