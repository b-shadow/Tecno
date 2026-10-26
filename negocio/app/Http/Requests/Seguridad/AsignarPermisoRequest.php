<?php

namespace App\Http\Requests\Seguridad;

use App\Http\Requests\ApiRequest;
use Datos\Modelos\Permiso;
use Illuminate\Validation\Rule;

/** CU1 (enunciado 2): permiso de un rol sobre un recurso de la matriz de acceso. */
class AsignarPermisoRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'rol' => ['required', 'exists:roles,nombre'],
            'recurso_codigo' => ['required', Rule::exists('recursos', 'codigo')->where('publico', false)],
            'acceso' => ['nullable', Rule::in(array_keys(Permiso::NIVELES))],
        ];
    }

    public function attributes(): array
    {
        return [
            'recurso_codigo' => 'recurso',
        ];
    }
}
