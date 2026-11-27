<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;
use Datos\Modelos\MetodoPago;
use Illuminate\Validation\Rule;

/** CU6: registro manual de QR o transferencia del prospecto. Las tarjetas se registran mediante Stripe Checkout (mode=setup). */
class RegistrarMetodoRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'tipo' => ['required', Rule::in(MetodoPago::TIPOS_MANUALES)],
            'titular' => ['required', 'string', 'max:120', "regex:/^[\\pL\\s'.-]+$/u"],
        ];
    }

    public function messages(): array
    {
        return [
            'tipo.in' => 'Para registrar una tarjeta debe utilizar la pasarela oficial de Stripe.',
        ];
    }

    public function attributes(): array
    {
        return [
            'tipo' => 'tipo de método',
            'titular' => 'titular',
        ];
    }
}
