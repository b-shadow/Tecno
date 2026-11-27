<?php

namespace App\Http\Requests\Reporte;

use App\Http\Requests\ApiRequest;

/** CU8: filtros de los reportes (listados). */
class ListadoRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'tipo' => ['required', 'in:tarjetas,pagos,matriculas,comisiones,perdidas,vendedores'],
            'desde' => ['nullable', 'date'],
            'hasta' => ['nullable', 'date', 'after_or_equal:desde'],
            'vendedor' => ['nullable', 'email'],
            'programa' => ['nullable', 'string', 'max:255'],
            'estado' => ['nullable', 'string', 'max:40'],
            'buscar' => ['nullable', 'string', 'max:120'],
        ];
    }

    public function attributes(): array
    {
        return [
            'desde' => 'fecha inicial',
            'hasta' => 'fecha final',
        ];
    }
}
