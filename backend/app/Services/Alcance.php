<?php

namespace App\Services;

use App\Models\Usuario;
use App\Repositories\AlcanceRepository;
use Illuminate\Contracts\Database\Eloquent\Builder;

/**
 * Qué tarjetas (intereses) ve cada rol:
 * RF1.2 el vendedor, solo su cartera; RF1.3 el coordinador, los programas a su cargo (programas_responsables);
 * el administrador, todo.
 */
class Alcance
{
    /** Filtra una consulta sobre `intereses` (o una relación que llegue a ella). */
    public static function intereses(Builder $query, Usuario $usuario, string $tabla = 'intereses'): Builder
    {
        return AlcanceRepository::intereses($query, $usuario, $tabla);
    }

    /** Filtra prospectos: los que tienen al menos una tarjeta dentro del alcance. */
    public static function prospectos(Builder $query, Usuario $usuario): Builder
    {
        return AlcanceRepository::prospectos($query, $usuario);
    }

    public static function veTarjeta(Usuario $usuario, object $interes): bool
    {
        return AlcanceRepository::veTarjeta($usuario, $interes);
    }

    public static function autorizarTarjeta(Usuario $usuario, object $interes): void
    {
        abort_unless(self::veTarjeta($usuario, $interes), 403, 'Este prospecto no está dentro de su cartera.');
    }

    /** Códigos de módulo de los programas que coordina el usuario. */
    public static function modulosACargo(Usuario $usuario)
    {
        return AlcanceRepository::codigosModuloCoordinador($usuario->correo);
    }
}
