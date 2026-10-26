<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\AuthService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/** Adaptador HTTP de inicio/cierre de sesión y perfil propio. */
class AuthController extends Controller
{
    public function login(Request $request, AuthService $service): JsonResponse
    {
        $datos = $request->validate([
            'correo' => ['required', 'email', 'max:160'],
            'password' => ['required', 'string', 'max:120'],
        ]);
        [$estado, $respuesta] = $service->iniciarSesion($request, $datos['correo'], $datos['password']);

        return response()->json($respuesta, $estado);
    }

    public function me(Request $request, AuthService $service): JsonResponse
    {
        return response()->json($service->sesion($request->attributes->get('auth_usuario')));
    }

    public function logout(Request $request, AuthService $service): JsonResponse
    {
        $service->cerrarSesion(
            $request,
            $request->attributes->get('auth_usuario'),
            $request->attributes->get('auth_token'),
        );

        return response()->json(['mensaje' => 'Sesión cerrada correctamente.']);
    }

    public function actualizarPerfil(Request $request, AuthService $service): JsonResponse
    {
        $datos = $request->validate([
            'nombre' => ['required', 'string', 'max:120'],
            'apellido' => ['required', 'string', 'max:120'],
            'telefono' => ['nullable', 'string', 'regex:/^[0-9+ ]{7,20}$/'],
            'foto' => ['nullable', 'string'],
        ]);
        $usuario = $service->actualizarPerfil($request->attributes->get('auth_usuario'), $datos);

        return response()->json(['mensaje' => 'Perfil actualizado correctamente.', 'usuario' => $usuario]);
    }

    public function cambiarPassword(Request $request, AuthService $service): JsonResponse
    {
        $datos = $request->validate([
            'password_actual' => ['required', 'string'],
            'password' => ['required', 'string', 'min:8', 'max:120', 'regex:/(?=.*[A-Za-z])(?=.*\d)/', 'confirmed'],
        ]);

        if (! $service->cambiarPassword(
            $request->attributes->get('auth_usuario'),
            $request->attributes->get('auth_token'),
            $datos,
        )) {
            return response()->json([
                'mensaje' => 'La contraseña actual no es correcta.',
                'errores' => ['password_actual' => ['La contraseña actual no es correcta.']],
            ], 422);
        }

        return response()->json(['mensaje' => 'Contraseña actualizada correctamente.']);
    }
}
