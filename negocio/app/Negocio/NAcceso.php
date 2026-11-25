<?php

namespace App\Negocio;

use Datos\Modelos\Permiso;
use Datos\Modelos\Usuario;
use Datos\DAcceso;
use Datos\DBitacora;
use Illuminate\Support\Collection;

/** Lee la matriz rol × recurso de la BD; el menú dinámico sale de la misma consulta. */
class NAcceso
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
        return DAcceso::menuPorRol($usuario->rol);
    }

    /** Intento sin permiso: queda en la bitácora como acceso_denegado (enunciado 4). */
    public static function registrarDenegado(?Usuario $usuario, string $recurso, string $ip, ?string $navegador): void
    {
        app(DBitacora::class)->registrar('acceso_denegado', $ip, $navegador, $usuario?->correo, $recurso);
    }

    public static function olvidar(): void
    {
        self::$cache = [];
    }

    private static function permisos(string $rol): array
    {
        return self::$cache[$rol] ??= DAcceso::permisosPorRol($rol);
    }
}
