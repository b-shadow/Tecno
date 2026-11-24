<?php

namespace App\Services;

use Datos\Modelos\Permiso;
use Datos\Modelos\Usuario;
use Datos\Repositorios\AccesoRepository;
use Datos\Repositorios\BitacoraRepository;
use Illuminate\Support\Collection;

/** Lee la matriz rol × recurso de la BD; el menú dinámico sale de la misma consulta. */
class AccesoService
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

    /** Intento sin permiso: queda en la bitácora como acceso_denegado (enunciado 4). */
    public static function registrarDenegado(?Usuario $usuario, string $recurso, string $ip, ?string $navegador): void
    {
        app(BitacoraRepository::class)->registrar('acceso_denegado', $ip, $navegador, $usuario?->correo, $recurso);
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
