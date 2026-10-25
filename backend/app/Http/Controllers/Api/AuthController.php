<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\ApiToken;
use App\Models\Bitacora;
use App\Models\Usuario;
use App\Services\Acceso;
use App\Services\Fotos;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

/** CU1: inicio y cierre de sesión, perfil propio. Cada intento queda en la bitácora con la IP (enunciado 4). */
class AuthController extends Controller
{
    public function login(Request $request): JsonResponse
    {
        $data = $request->validate([
            'correo' => ['required', 'email', 'max:160'],
            'password' => ['required', 'string', 'max:120'],
        ]);
        $correo = mb_strtolower(trim($data['correo']));
        $usuario = Usuario::query()->whereRaw('lower(correo) = ?', [$correo])->first();

        if (! $usuario || ! Hash::check($data['password'], $usuario->password)) {
            Bitacora::registrar('login_fallido', $request, $usuario?->correo, 'login', $correo);

            return response()->json(['mensaje' => 'Correo o contraseña incorrectos.'], 422);
        }

        if (! $usuario->vigente()) {
            Bitacora::registrar('login_fallido', $request, $usuario->correo, 'login', $correo);

            return response()->json(['mensaje' => 'Su cuenta está inactiva o fuera de su periodo de vigencia.'], 403);
        }

        $plainToken = Str::random(80);
        ApiToken::query()->create([
            'token_hash' => hash('sha256', $plainToken),
            'usuario_correo' => $usuario->correo,
            'expira_en' => now()->addHours(12),
        ]);
        Bitacora::registrar('login_exitoso', $request, $usuario->correo, 'login');

        return response()->json(['mensaje' => 'Acceso correcto.', 'token' => $plainToken] + $this->sesion($usuario));
    }

    public function me(Request $request): JsonResponse
    {
        return response()->json($this->sesion($request->attributes->get('auth_usuario')));
    }

    public function logout(Request $request): JsonResponse
    {
        Bitacora::registrar('logout', $request, $request->attributes->get('auth_usuario')->correo);
        $request->attributes->get('auth_token')?->delete();

        return response()->json(['mensaje' => 'Sesión cerrada correctamente.']);
    }

    public function actualizarPerfil(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $data = $request->validate([
            'nombre' => ['required', 'string', 'max:120'],
            'apellido' => ['required', 'string', 'max:120'],
            'telefono' => ['nullable', 'string', 'regex:/^[0-9+ ]{7,20}$/'],
            'foto' => ['nullable', 'string'],
        ]);

        if (! empty($data['foto'])) {
            $data['foto'] = Fotos::guardar($data['foto'], $data['apellido'], $data['nombre'], $usuario->foto);
        } else {
            unset($data['foto']);
        }

        $usuario->update($data);

        return response()->json(['mensaje' => 'Perfil actualizado correctamente.', 'usuario' => $usuario->fresh()]);
    }

    public function cambiarPassword(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $data = $request->validate([
            'password_actual' => ['required', 'string'],
            'password' => ['required', 'string', 'min:8', 'max:120', 'regex:/(?=.*[A-Za-z])(?=.*\d)/', 'confirmed'],
        ]);

        if (! Hash::check($data['password_actual'], $usuario->password)) {
            return response()->json([
                'mensaje' => 'La contraseña actual no es correcta.',
                'errores' => ['password_actual' => ['La contraseña actual no es correcta.']],
            ], 422);
        }

        $usuario->update(['password' => Hash::make($data['password'])]);
        $usuario->tokens()->whereKeyNot($request->attributes->get('auth_token')->token_hash)->delete();

        return response()->json(['mensaje' => 'Contraseña actualizada correctamente.']);
    }

    /** Usuario, menú dinámico y permisos (recurso => nivel) del rol activo. */
    private function sesion(Usuario $usuario): array
    {
        $menu = Acceso::menu($usuario);

        return [
            'usuario' => $usuario,
            'menu' => $menu,
            'permisos' => $menu->pluck('acceso', 'codigo'),
        ];
    }
}
