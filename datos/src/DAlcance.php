<?php

namespace Datos;

use Datos\Modelos\Prospecto;
use Datos\Modelos\Usuario;
use Illuminate\Contracts\Database\Eloquent\Builder;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Consultas de persistencia usadas para determinar los programas asignados. */
class DAlcance
{
    public static function intereses(Builder $query, Usuario $usuario, string $tabla = 'intereses'): Builder
    {
        return match ($usuario->rol) {
            'vendedor' => $query->where("{$tabla}.vendedor_correo", $usuario->correo),
            'coordinador' => $query->whereIn("{$tabla}.modulo_codigo", self::codigosModuloCoordinador($usuario->correo)),
            default => $query,
        };
    }

    public static function prospectos(Builder $query, Usuario $usuario): Builder
    {
        if ($usuario->rol === 'administrador') {
            return $query;
        }

        return $query->whereHas('intereses', fn ($intereses) => self::intereses($intereses, $usuario));
    }

    public static function prospectoEnCartera(Prospecto $prospecto, Usuario $usuario): bool
    {
        return self::prospectos(Prospecto::query()->whereKey($prospecto->documento), $usuario)->exists();
    }

    public static function codigosModuloCoordinador(string $correo): Collection
    {
        return DB::table('catalogo_cache as c')
            ->join('programas_responsables as r', 'r.programa_codigo', '=', 'c.programa_codigo')
            ->where('r.coordinador_correo', $correo)
            ->pluck('c.codigo');
    }

    /** Escapa comodines LIKE/ILIKE de PostgreSQL (\, %, _) para tratar la búsqueda como texto literal. */
    public static function escaparLike(string $texto): string
    {
        return '%'.str_replace(['\\', '%', '_'], ['\\\\', '\\%', '\\_'], trim($texto)).'%';
    }
}
