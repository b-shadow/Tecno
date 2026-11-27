<?php

namespace App\Http\Requests\Interes;

use App\Http\Requests\ApiRequest;
use Datos\DUsuario;

/** CU3 (RF2.3): asignación manual de la tarjeta a un vendedor activo. */
class AsignarInteresRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'vendedor_correo' => ['required', $this->segun(fn ($v) => app(DUsuario::class)->esVendedorActivo($v))],
        ];
    }

    public function attributes(): array
    {
        return [
            'vendedor_correo' => 'vendedor',
        ];
    }
}
