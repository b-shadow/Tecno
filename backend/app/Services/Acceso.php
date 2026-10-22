<?php

namespace App\Services;

use App\Models\Permiso;
use App\Models\Usuario;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Lee la matriz rol × recurso de la BD; el menú dinámico sale de la misma consulta. */
class Acceso
{
    /** @var array<string, array<string, string>> permisos por rol, leídos una vez por petición */
    private static array $cache = [];

    public static function permite(?Usuario $usuario, string $recurso, string $nivel = 'lectura'): bool
    {
        if (! $usuario) {
            return false;
        }

        $acceso = self::permisos($usuario->rol)[$recurso] ?? null;

        return $acceso !== null && Permiso::NIVELES[$acceso] >= Permiso::NIVELES[$nivel];
    }

    /** Menú del rol: páginas a las que tiene acceso, en orden, con su nivel. */
    public static function menu(Usuario $usuario): Collection
    {
        return DB::table('recursos as r')
            ->join('permisos as p', 'p.recurso_codigo', '=', 'r.codigo')
            ->where('p.rol', $usuario->rol)
            ->where('r.publico', false)
            ->orderBy('r.orden')
            ->get(['r.codigo', 'r.nombre', 'r.ruta', 'r.icono', 'r.caso_uso', 'p.acceso']);
    }

    public static function olvidar(): void
    {
        self::$cache = [];
    }

    private static function permisos(string $rol): array
    {
        return self::$cache[$rol] ??= DB::table('permisos')->where('rol', $rol)->pluck('acceso', 'recurso_codigo')->all();
    }
}
