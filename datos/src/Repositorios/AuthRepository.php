<?php

namespace Datos\Repositorios;

use Datos\Modelos\ApiToken;
use Datos\Modelos\Usuario;

/** Persistencia de usuarios y tokens de autenticación. */
class AuthRepository
{
    public function usuarioPorCorreo(string $correo): ?Usuario
    {
        return Usuario::query()->whereRaw('lower(correo) = ?', [mb_strtolower($correo)])->first();
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
