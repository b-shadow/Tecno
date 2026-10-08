<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Usuario;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rule;

class UsuarioController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $this->authorizeAdministrador($request);

        $usuarios = Usuario::query()
            ->when($request->query('buscar'), function ($query, string $buscar) {
                $query->where(function ($subquery) use ($buscar) {
                    $subquery->where('nombre', 'ilike', "%{$buscar}%")
                        ->orWhere('apellido', 'ilike', "%{$buscar}%")
                        ->orWhere('correo', 'ilike', "%{$buscar}%");
                });
            })
            ->when($request->query('rol'), fn ($query, string $rol) => $query->where('rol', $rol))
            ->when($request->query('estado'), fn ($query, string $estado) => $query->where('estado', $estado))
            ->orderBy('nombre')
            ->get();

        return response()->json(['usuarios' => $usuarios]);
    }

    public function store(Request $request): JsonResponse
    {
        $this->authorizeAdministrador($request);

        $data = $this->validatedData($request);
        $data['password'] = Hash::make($data['password']);

        $usuario = Usuario::query()->create($data);

        return response()->json([
            'mensaje' => 'Usuario creado correctamente.',
            'usuario' => $usuario,
        ], 201);
    }

    public function update(Request $request, Usuario $usuario): JsonResponse
    {
        $this->authorizeAdministrador($request);

        $data = $this->validatedData($request, $usuario);

        if (! empty($data['password'])) {
            $data['password'] = Hash::make($data['password']);
        } else {
            unset($data['password']);
        }

        $usuario->update($data);

        return response()->json([
            'mensaje' => 'Usuario actualizado correctamente.',
            'usuario' => $usuario->fresh(),
        ]);
    }

    public function cambiarEstado(Request $request, Usuario $usuario): JsonResponse
    {
        $this->authorizeAdministrador($request);

        $data = $request->validate([
            'estado' => ['required', Rule::in(Usuario::ESTADOS)],
        ]);

        $usuario->update(['estado' => $data['estado']]);

        if ($data['estado'] === 'inactivo') {
            $usuario->tokens()->delete();
        }

        return response()->json([
            'mensaje' => 'Estado actualizado correctamente.',
            'usuario' => $usuario->fresh(),
        ]);
    }

    private function validatedData(Request $request, ?Usuario $usuario = null): array
    {
        return $request->validate([
            'nombre' => ['required', 'string', 'max:120'],
            'apellido' => ['required', 'string', 'max:120'],
            'correo' => [
                'required',
                'email',
                'max:160',
                Rule::unique('usuarios', 'correo')->ignore($usuario?->id),
            ],
            'telefono' => ['nullable', 'string', 'max:40'],
            'password' => [$usuario ? 'nullable' : 'required', 'string', 'min:8'],
            'rol' => ['required', Rule::in(Usuario::ROLES)],
            'estado' => ['required', Rule::in(Usuario::ESTADOS)],
        ]);
    }

    private function authorizeAdministrador(Request $request): void
    {
        $usuario = $request->attributes->get('auth_usuario');

        abort_if($usuario?->rol !== 'administrador', 403, 'Solo el administrador puede gestionar usuarios.');
    }
}
