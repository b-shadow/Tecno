<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use Datos\Modelos\Usuario;
use Datos\DAlcance;

/**
 * Qué tarjetas (intereses) ve cada rol:
 * RF1.2 el vendedor, solo su cartera; RF1.3 el coordinador, los programas a su cargo (programas_responsables);
 * el administrador, todo.
 */
class NAlcance
{
    public static function veTarjeta(Usuario $usuario, object $interes): bool
    {
        return match ($usuario->rol) {
            'vendedor' => $interes->vendedor_correo === $usuario->correo,
            'coordinador' => DAlcance::codigosModuloCoordinador($usuario->correo)->contains($interes->modulo_codigo),
            default => true,
        };
    }

    public static function autorizarTarjeta(Usuario $usuario, object $interes): void
    {
        ReglaNegocioException::si(! self::veTarjeta($usuario, $interes), 'Este prospecto no está dentro de su cartera.', 403);
    }

    /** Códigos de módulo de los programas que coordina el usuario. */
    public static function modulosACargo(Usuario $usuario)
    {
        return DAlcance::codigosModuloCoordinador($usuario->correo);
    }
}
