<?php

namespace App\Services;

use App\Exceptions\ReglaNegocioException;
use Datos\Modelos\ApiToken;
use Datos\Modelos\Usuario;
use Datos\Repositorios\AuthRepository;
use Datos\Repositorios\BitacoraRepository;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;

/** Autenticación por token, vigencia de la credencial (clase 03), perfil propio y bitácora de accesos (enunciado 4). */
class AuthService
{
    public function __construct(private readonly AuthRepository $auth, private readonly BitacoraRepository $bitacora)
    {
    }

    /** Devuelve token + sesión (usuario, menú y permisos). Todo intento queda en la bitácora con su IP. */
    public function iniciarSesion(string $correo, string $password, string $ip, ?string $navegador): array
    {
        $correo = mb_strtolower(trim($correo));
        $usuario = $this->auth->usuarioPorCorreo($correo);

        if (! $usuario || ! Hash::check($password, $usuario->password)) {
            $this->bitacora->registrar('login_fallido', $ip, $navegador, $usuario?->correo, 'login', $correo);
            throw new ReglaNegocioException('Correo o contraseña incorrectos.');
        }

        if (! $usuario->vigente()) {
            $this->bitacora->registrar('login_fallido', $ip, $navegador, $usuario->correo, 'login', $correo);
            throw new ReglaNegocioException('Su cuenta está inactiva o fuera de su periodo de vigencia.', 403);
        }

        $token = Str::random(80);
        $this->auth->crearToken($usuario->correo, $token);
        $this->bitacora->registrar('login_exitoso', $ip, $navegador, $usuario->correo, 'login');

        return ['token' => $token] + $this->sesion($usuario);
    }

    /** Token vigente y credencial vigente; deja al usuario como autor de los cambios en la BD (trigger del embudo). */
    public function autenticarToken(string $tokenPlano): ApiToken
    {
        $token = $this->auth->tokenPorPlano($tokenPlano);
        ReglaNegocioException::si(! $token || ($token->expira_en && $token->expira_en->isPast()), 'Su sesión expiró. Vuelva a iniciar sesión.', 401);

        if (! $token->usuario || ! $token->usuario->vigente()) {
            $this->auth->eliminarToken($token);
            throw new ReglaNegocioException('Su cuenta está inactiva o fuera de vigencia.', 401);
        }

        $this->auth->marcarUso($token);
        $this->auth->fijarAutorDeCambios($token->usuario->correo);

        return $token;
    }

    /** Usuario de un token válido, o null (rutas públicas que se comportan distinto con sesión). */
    public function usuarioOpcional(?string $tokenPlano): ?Usuario
    {
        $token = $tokenPlano ? $this->auth->tokenPorPlano($tokenPlano) : null;

        return $token && (! $token->expira_en || $token->expira_en->isFuture()) && $token->usuario?->vigente()
            ? $token->usuario
            : null;
    }

    public function sesion(Usuario $usuario): array
    {
        $menu = AccesoService::menu($usuario);

        return [
            'usuario' => $usuario,
            'menu' => $menu,
            'permisos' => $menu->pluck('acceso', 'codigo'),
        ];
    }

    public function cerrarSesion(Usuario $usuario, ?ApiToken $token, string $ip, ?string $navegador): void
    {
        $this->bitacora->registrar('logout', $ip, $navegador, $usuario->correo);
        $this->auth->eliminarToken($token);
    }

    public function actualizarPerfil(Usuario $usuario, array $datos): Usuario
    {
        if (! empty($datos['foto'])) {
            $datos['foto'] = FotoService::guardar($datos['foto'], $datos['apellido'], $datos['nombre'], $usuario->foto);
        } else {
            unset($datos['foto']);
        }

        return $this->auth->actualizarUsuario($usuario, $datos);
    }

    /** Cambia la contraseña y cierra las demás sesiones del usuario. */
    public function cambiarPassword(Usuario $usuario, ApiToken $token, string $actual, string $nueva): void
    {
        if (! Hash::check($actual, $usuario->password)) {
            throw ValidationException::withMessages(['password_actual' => 'La contraseña actual no es correcta.']);
        }

        $this->auth->actualizarUsuario($usuario, ['password' => Hash::make($nueva)]);
        $this->auth->revocarOtrosTokens($usuario, $token->token_hash);
    }
}
