<?php

namespace App\Http\Requests\Seguridad;

use App\Http\Requests\ApiRequest;
use Datos\DSeguridad;
use Datos\Modelos\Permiso;
use Illuminate\Validation\Rule;

/** CU1 (enunciado 2): permiso de un rol sobre un recurso de la matriz de acceso. */
class AsignarPermisoRequest extends ApiRequest
{
    public function rules(): array
    {
        return [
            'rol' => ['required', $this->segun(fn ($v) => app(DSeguridad::class)->existeRol($v))],
            'recurso_codigo' => ['required', $this->segun(fn ($v) => app(DSeguridad::class)->esRecursoPrivado($v))],
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
