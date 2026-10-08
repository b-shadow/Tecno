<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\ApiToken;
use App\Models\Usuario;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

class AuthController extends Controller
{
    public function login(Request $request): JsonResponse
    {
        $data = $request->validate([
            'correo' => ['required', 'email'],
            'password' => ['required', 'string'],
        ]);

        $usuario = Usuario::query()->where('correo', $data['correo'])->first();

        if (! $usuario || ! Hash::check($data['password'], $usuario->password)) {
            return response()->json(['mensaje' => 'Credenciales incorrectas.'], 422);
        }

        if ($usuario->estado !== 'activo') {
            return response()->json(['mensaje' => 'El usuario se encuentra inactivo.'], 403);
        }

        $plainToken = Str::random(80);

        ApiToken::query()->create([
            'usuario_id' => $usuario->id,
            'token_hash' => hash('sha256', $plainToken),
            'expira_en' => now()->addHours(12),
        ]);

        return response()->json([
            'mensaje' => 'Acceso correcto',
            'token' => $plainToken,
            'usuario' => $usuario,
        ]);
    }

    public function me(Request $request): JsonResponse
    {
        return response()->json([
            'usuario' => $request->attributes->get('auth_usuario'),
        ]);
    }

    public function logout(Request $request): JsonResponse
    {
        $request->attributes->get('auth_token')?->delete();

        return response()->json(['mensaje' => 'Sesion cerrada correctamente.']);
    }

    public function actualizarPerfil(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $data = $request->validate([
            'nombre' => ['required', 'string', 'max:120'],
            'apellido' => ['required', 'string', 'max:120'],
            'telefono' => ['nullable', 'string', 'max:40'],
        ]);

        $usuario->update($data);

        return response()->json([
            'mensaje' => 'Perfil actualizado correctamente.',
            'usuario' => $usuario->fresh(),
        ]);
    }

    public function cambiarPassword(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $data = $request->validate([
            'password_actual' => ['required', 'string'],
            'password' => ['required', 'string', 'min:8', 'confirmed'],
        ]);

        if (! Hash::check($data['password_actual'], $usuario->password)) {
            return response()->json(['mensaje' => 'La contrasena actual no es correcta.'], 422);
        }

        $usuario->update(['password' => Hash::make($data['password'])]);

        return response()->json(['mensaje' => 'Contrasena actualizada correctamente.']);
    }
}
