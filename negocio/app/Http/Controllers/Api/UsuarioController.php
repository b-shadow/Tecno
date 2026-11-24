<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Datos\Modelos\Usuario;
use App\Services\UsuarioService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

/** Adaptador HTTP del CU1: valida entradas y devuelve respuestas JSON. */
class UsuarioController extends Controller
{
    public function index(Request $request, UsuarioService $service): JsonResponse
    {
        $filtros = $request->only(['buscar', 'rol', 'estado']);

        return response()->json($service->listar($filtros));
    }

    public function vendedores(UsuarioService $service): JsonResponse
    {
        return response()->json(['vendedores' => $service->vendedores()]);
    }

    public function store(Request $request, UsuarioService $service): JsonResponse
    {
        $datos = $this->validar($request);

        return response()->json([
            'mensaje' => 'Usuario creado correctamente.',
            'usuario' => $service->crear($datos),
        ], 201);
    }

    public function update(Request $request, string $usuario, UsuarioService $service): JsonResponse
    {
        $datos = $this->validar($request, $usuario);
        $actor = $request->attributes->get('auth_usuario');

        return response()->json([
            'mensaje' => 'Usuario actualizado correctamente.',
            'usuario' => $service->actualizar($usuario, $datos, $actor->correo),
        ]);
    }

    public function cambiarEstado(Request $request, string $usuario, UsuarioService $service): JsonResponse
    {
        $datos = $request->validate(['estado' => ['required', Rule::in(Usuario::ESTADOS)]]);
        $actualizado = $service->cambiarEstado($usuario, $datos['estado']);

        return response()->json([
            'mensaje' => $datos['estado'] === 'activo' ? 'Usuario activado.' : 'Usuario desactivado.',
            'usuario' => $actualizado,
        ]);
    }

    public function foto(string $usuario, UsuarioService $service): JsonResponse
    {
        $service->eliminarFoto($usuario);

        return response()->json(['mensaje' => 'Foto eliminada.']);
    }

    private function validar(Request $request, ?string $correoActual = null): array
    {
        $request->merge(['correo' => mb_strtolower(trim((string) $request->input('correo')))]);

        return $request->validate([
            'nombre' => ['required', 'string', 'max:120', "regex:/^[\\pL\\s'.-]+$/u"],
            'apellido' => ['required', 'string', 'max:120', "regex:/^[\\pL\\s'.-]+$/u"],
            'correo' => $correoActual !== null
                ? ['required', Rule::in([$correoActual])]
                : ['required', 'email', 'max:160', 'unique:usuarios,correo'],
            'telefono' => ['nullable', 'string', 'regex:/^\\+?[0-9 ]{7,20}$/'],
            'password' => [$correoActual === null ? 'required' : 'nullable', 'string', 'min:8', 'max:120', 'regex:/(?=.*[A-Za-z])(?=.*\\d)/'],
            'rol' => ['required', Rule::exists('roles', 'nombre')],
            'estado' => ['required', Rule::in(Usuario::ESTADOS)],
            'fecha_inicio' => ['required', 'date'],
            'fecha_fin' => ['required', 'date', 'after_or_equal:fecha_inicio'],
            'foto' => ['nullable', 'string'],
            'programas' => ['nullable', 'array'],
            'programas.*' => ['string', 'exists:programas,codigo'],
        ], [
            'correo.in' => 'El correo identifica al usuario y no se puede cambiar.',
            'password.regex' => 'La contraseña debe combinar letras y números.',
        ], ['fecha_inicio' => 'inicio de vigencia', 'fecha_fin' => 'fin de vigencia', 'programas' => 'programas a cargo']);
    }
}
