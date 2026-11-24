<?php

namespace App\Http\Requests\Usuario;

use App\Http\Requests\ApiRequest;
use Datos\Modelos\Usuario;
use Illuminate\Validation\Rule;

/**
 * CU1: alta (POST /usuarios) o edición (PUT /usuarios/{usuario}) de una credencial con rol, estado,
 * vigencia (fecha_inicio/fecha_fin, clase 03) y foto. En la edición el correo, que es la clave, no cambia.
 */
class UsuarioRequest extends ApiRequest
{
    protected function prepareForValidation(): void
    {
        $this->merge(['correo' => mb_strtolower(trim((string) $this->input('correo')))]);
    }

    public function rules(): array
    {
        $actual = $this->route('usuario');

        return [
            'nombre' => ['required', 'string', 'max:120', "regex:/^[\\pL\\s'.-]+$/u"],
            'apellido' => ['required', 'string', 'max:120', "regex:/^[\\pL\\s'.-]+$/u"],
            'correo' => $actual !== null
                ? ['required', Rule::in([$actual])]
                : ['required', 'email', 'max:160', 'unique:usuarios,correo'],
            'telefono' => ['nullable', 'string', 'regex:/^\\+?[0-9 ]{7,20}$/'],
            'password' => [$actual === null ? 'required' : 'nullable', 'string', 'min:8', 'max:120', 'regex:/(?=.*[A-Za-z])(?=.*\\d)/'],
            'rol' => ['required', Rule::exists('roles', 'nombre')],
            'estado' => ['required', Rule::in(Usuario::ESTADOS)],
            'fecha_inicio' => ['required', 'date'],
            'fecha_fin' => ['required', 'date', 'after_or_equal:fecha_inicio'],
            'foto' => ['nullable', 'string'],
            'programas' => ['nullable', 'array'],
            'programas.*' => ['string', 'exists:programas,codigo'],
        ];
    }

    public function messages(): array
    {
        return [
            'correo.in' => 'El correo identifica al usuario y no se puede cambiar.',
            'password.regex' => 'La contraseña debe combinar letras y números.',
        ];
    }

    public function attributes(): array
    {
        return ['fecha_inicio' => 'inicio de vigencia', 'fecha_fin' => 'fin de vigencia', 'programas' => 'programas a cargo', 'telefono' => 'teléfono'];
    }
}
