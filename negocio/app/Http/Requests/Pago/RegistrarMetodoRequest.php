<?php

namespace App\Http\Requests\Pago;

use App\Http\Requests\ApiRequest;
use Datos\Modelos\MetodoPago;
use Illuminate\Validation\Rule;

/** CU6: tarjeta (marca, últimos 4, vencimiento), QR o transferencia del prospecto. */
class RegistrarMetodoRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'tipo' => ['required', Rule::in(MetodoPago::TIPOS)],
            'titular' => ['required', 'string', 'max:120', "regex:/^[\\pL\\s'.-]+$/u"],
            'numero' => ['nullable', 'required_if:tipo,Tarjeta', 'string', 'regex:/^[0-9 ]{13,23}$/'],
            'vencimiento' => ['nullable', 'required_if:tipo,Tarjeta', 'regex:/^(0[1-9]|1[0-2])\/[0-9]{2}$/'],
        ];
    }

    public function messages(): array
    {
        return [
            'numero.regex' => 'El número de tarjeta debe tener entre 13 y 19 dígitos.',
            'vencimiento.regex' => 'El vencimiento debe tener el formato MM/AA.',
        ];
    }

    public function attributes(): array
    {
        return [
            'numero' => 'número de tarjeta',
            'vencimiento' => 'vencimiento',
        ];
    }
}
