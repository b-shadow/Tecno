<?php

namespace App\Services;

use App\Models\ApiToken;
use App\Models\Usuario;
use App\Repositories\AuthRepository;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

/** Casos de negocio de autenticación, vigencia y perfil. */
class AuthService
{
    public function __construct(private readonly AuthRepository $auth)
    {
    }

    public function iniciarSesion(Request $request, string $correo, string $password): array
    {
        $correo = mb_strtolower(trim($correo));
        $usuario = $this->auth->usuarioPorCorreo($correo);

        if (! $usuario || ! Hash::check($password, $usuario->password)) {
            Bitacora::registrar('login_fallido', $request, $usuario?->correo, 'login', $correo);

            return [422, ['mensaje' => 'Correo o contraseña incorrectos.']];
        }

        if (! $usuario->vigente()) {
            Bitacora::registrar('login_fallido', $request, $usuario->correo, 'login', $correo);

            return [403, ['mensaje' => 'Su cuenta está inactiva o fuera de su periodo de vigencia.']];
        }

        $token = Str::random(80);
        $this->auth->crearToken($usuario->correo, $token);
        Bitacora::registrar('login_exitoso', $request, $usuario->correo, 'login');

        return [200, ['mensaje' => 'Acceso correcto.', 'token' => $token] + $this->sesion($usuario)];
    }

    public function sesion(Usuario $usuario): array
    {
        $menu = Acceso::menu($usuario);

        return [
            'usuario' => $usuario,
            'menu' => $menu,
            'permisos' => $menu->pluck('acceso', 'codigo'),
        ];
    }

    public function cerrarSesion(Request $request, Usuario $usuario, ?ApiToken $token): void
    {
        Bitacora::registrar('logout', $request, $usuario->correo);
        $this->auth->eliminarToken($token);
    }

    public function actualizarPerfil(Usuario $usuario, array $datos): Usuario
    {
        if (! empty($datos['foto'])) {
            $datos['foto'] = Fotos::guardar($datos['foto'], $datos['apellido'], $datos['nombre'], $usuario->foto);
        } else {
            unset($datos['foto']);
        }

        return $this->auth->actualizarUsuario($usuario, $datos);
    }

    public function cambiarPassword(Usuario $usuario, ApiToken $token, array $datos): bool
    {
        if (! Hash::check($datos['password_actual'], $usuario->password)) {
            return false;
        }

        $this->auth->actualizarUsuario($usuario, ['password' => Hash::make($datos['password'])]);
        $this->auth->revocarOtrosTokens($usuario, $token->token_hash);

        return true;
    }
}
