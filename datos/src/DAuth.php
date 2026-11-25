<?php

namespace Datos;

use Datos\Modelos\ApiToken;
use Datos\Modelos\Usuario;
use Illuminate\Support\Facades\DB;

/** Persistencia de usuarios y tokens de autenticación. */
class DAuth
{
    public function usuarioPorCorreo(string $correo): ?Usuario
    {
        return Usuario::query()->whereRaw('lower(correo) = ?', [mb_strtolower($correo)])->first();
    }

    public function tokenPorPlano(string $tokenPlano): ?ApiToken
    {
        return ApiToken::query()->with('usuario')->find(hash('sha256', $tokenPlano));
    }

    public function marcarUso(ApiToken $token): void
    {
        $token->forceFill(['ultimo_uso_en' => now()])->save();
    }

    /** El trigger del historial del embudo (movimientos_interes) lee de aquí quién movió cada tarjeta. */
    public function fijarAutorDeCambios(string $correo): void
    {
        DB::select("select set_config('crm.usuario_correo', ?, false)", [$correo]);
    }

    public function crearToken(string $correo, string $tokenPlano): void
    {
        ApiToken::query()->create([
            'token_hash' => hash('sha256', $tokenPlano),
            'usuario_correo' => $correo,
            'expira_en' => now()->addHours(12),
        ]);
    }

    public function actualizarUsuario(Usuario $usuario, array $datos): Usuario
    {
        $usuario->update($datos);

        return $usuario->fresh() ?? $usuario;
    }

    public function revocarOtrosTokens(Usuario $usuario, string $tokenActual): void
    {
        $usuario->tokens()->whereKeyNot($tokenActual)->delete();
    }

    public function eliminarToken(?ApiToken $token): void
    {
        $token?->delete();
    }
}
