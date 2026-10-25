<?php

namespace App\Services;

use App\Models\Permiso;
use App\Models\Usuario;
use App\Repositories\AccesoRepository;
use Illuminate\Support\Collection;

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
        return AccesoRepository::menuPorRol($usuario->rol);
    }

    public static function olvidar(): void
    {
        self::$cache = [];
    }

    private static function permisos(string $rol): array
    {
        return self::$cache[$rol] ??= AccesoRepository::permisosPorRol($rol);
    }
}
