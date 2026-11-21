<?php

namespace App\Services;

use App\Models\Usuario;
use Illuminate\Contracts\Database\Eloquent\Builder;
use Illuminate\Support\Facades\DB;

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
        return match ($usuario->rol) {
            'vendedor' => $query->where("{$tabla}.vendedor_correo", $usuario->correo),
            'coordinador' => $query->whereIn("{$tabla}.modulo_codigo", self::modulosACargo($usuario)),
            default => $query,
        };
    }

    /** Filtra prospectos: los que tienen al menos una tarjeta dentro del alcance. */
    public static function prospectos(Builder $query, Usuario $usuario): Builder
    {
        if ($usuario->rol === 'administrador') {
            return $query;
        }

        return $query->whereHas('intereses', fn ($q) => self::intereses($q, $usuario));
    }

    public static function veTarjeta(Usuario $usuario, object $interes): bool
    {
        return match ($usuario->rol) {
            'vendedor' => $interes->vendedor_correo === $usuario->correo,
            'coordinador' => in_array($interes->modulo_codigo, self::modulosACargo($usuario)->all(), true),
            default => true,
        };
    }

    public static function autorizarTarjeta(Usuario $usuario, object $interes): void
    {
        abort_unless(self::veTarjeta($usuario, $interes), 403, 'Este prospecto no está dentro de su cartera.');
    }

    /** Códigos de módulo de los programas que coordina el usuario. */
    public static function modulosACargo(Usuario $usuario)
    {
        return DB::table('catalogo_cache as c')
            ->join('programas_responsables as r', 'r.programa_codigo', '=', 'c.programa_codigo')
            ->where('r.coordinador_correo', $usuario->correo)
            ->pluck('c.codigo');
    }
}
