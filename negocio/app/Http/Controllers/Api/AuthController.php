<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Auth\ActualizarPerfilRequest;
use App\Http\Requests\Auth\CambiarPasswordRequest;
use App\Http\Requests\Auth\LoginRequest;
use App\Http\Requests\ConsultaRequest;
use App\Services\AuthService;
use Illuminate\Http\JsonResponse;

/** CU1: inicio y cierre de sesión, sesión actual (menú del rol) y perfil propio. */
class AuthController extends Controller
{
    public function __construct(private readonly AuthService $auth)
    {
    }

    public function login(LoginRequest $r): JsonResponse
    {
        $sesion = $this->auth->iniciarSesion($r->validated('correo'), $r->validated('password'), (string) $r->ip(), $r->navegador());

        return response()->json(['mensaje' => 'Acceso correcto.'] + $sesion);
    }

    public function me(ConsultaRequest $r): JsonResponse
    {
        return response()->json($this->auth->sesion($r->usuario()));
    }

    public function logout(ConsultaRequest $r): JsonResponse
    {
        $this->auth->cerrarSesion($r->usuario(), $r->attributes->get('auth_token'), (string) $r->ip(), $r->navegador());

        return response()->json(['mensaje' => 'Sesión cerrada correctamente.']);
    }

    public function actualizarPerfil(ActualizarPerfilRequest $r): JsonResponse
    {
        $usuario = $this->auth->actualizarPerfil($r->usuario(), $r->validated());

        return response()->json(['mensaje' => 'Perfil actualizado correctamente.', 'usuario' => $usuario]);
    }

    public function cambiarPassword(CambiarPasswordRequest $r): JsonResponse
    {
        $this->auth->cambiarPassword($r->usuario(), $r->attributes->get('auth_token'), $r->validated('password_actual'), $r->validated('password'));

        return response()->json(['mensaje' => 'Contraseña actualizada correctamente.']);
    }
}
