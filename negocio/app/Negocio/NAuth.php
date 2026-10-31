<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use App\Http\Requests\Auth\ActualizarPerfilRequest;
use App\Http\Requests\Auth\CambiarPasswordRequest;
use App\Http\Requests\Auth\LoginRequest;
use App\Http\Requests\ConsultaRequest;
use Datos\DAuth;
use Datos\DBitacora;
use Datos\Modelos\ApiToken;
use Datos\Modelos\Usuario;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;

/** Capa de negocio — CU1: sesión por token, vigencia de la credencial (clase 03), perfil propio y bitácora (enunciado 4). */
class NAuth
{
    public function __construct(private readonly DAuth $auth, private readonly DBitacora $bitacora)
    {
    }

    /** Devuelve token + sesión (usuario, menú y permisos). Todo intento queda en la bitácora con su IP. */
    public function login(LoginRequest $r): JsonResponse
    {
        $correo = mb_strtolower(trim($r->validated('correo')));
        $ip = (string) $r->ip();
        $navegador = $r->navegador();
        $usuario = $this->auth->usuarioPorCorreo($correo);

        if (! $usuario || ! Hash::check($r->validated('password'), $usuario->password)) {
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

        return response()->json(['mensaje' => 'Acceso correcto.', 'token' => $token] + $this->sesion($usuario));
    }

    public function me(ConsultaRequest $r): JsonResponse
    {
        return response()->json($this->sesion($r->usuario()));
    }

    public function logout(ConsultaRequest $r): JsonResponse
    {
        $this->bitacora->registrar('logout', (string) $r->ip(), $r->navegador(), $r->usuario()->correo);
        $this->auth->eliminarToken($r->attributes->get('auth_token'));

        return response()->json(['mensaje' => 'Sesión cerrada correctamente.']);
    }

    public function actualizarPerfil(ActualizarPerfilRequest $r): JsonResponse
    {
        $usuario = $r->usuario();
        $datos = $r->validated();
        if (! empty($datos['foto'])) {
            $datos['foto'] = NFoto::guardar($datos['foto'], $datos['apellido'], $datos['nombre'], $usuario->foto);
        } else {
            unset($datos['foto']);
        }

        return response()->json(['mensaje' => 'Perfil actualizado correctamente.', 'usuario' => $this->auth->actualizarUsuario($usuario, $datos)]);
    }

    /** Cambia la contraseña y cierra las demás sesiones del usuario. */
    public function cambiarPassword(CambiarPasswordRequest $r): JsonResponse
    {
        $usuario = $r->usuario();
        if (! Hash::check($r->validated('password_actual'), $usuario->password)) {
            throw ValidationException::withMessages(['password_actual' => 'La contraseña actual no es correcta.']);
        }

        $this->auth->actualizarUsuario($usuario, ['password' => Hash::make($r->validated('password'))]);
        $this->auth->revocarOtrosTokens($usuario, $r->attributes->get('auth_token')->token_hash);

        return response()->json(['mensaje' => 'Contraseña actualizada correctamente.']);
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

    private function sesion(Usuario $usuario): array
    {
        $menu = NAcceso::menu($usuario);

        return [
            'usuario' => $usuario,
            'menu' => $menu,
            'permisos' => $menu->pluck('acceso', 'codigo'),
        ];
    }
}
