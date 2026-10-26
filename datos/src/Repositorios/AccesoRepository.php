<?php

namespace Datos\Repositorios;

use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Lectura del catálogo de recursos y permisos almacenado en PostgreSQL. */
class AccesoRepository
{
    public static function permisosPorRol(string $rol): array
    {
        return DB::table('permisos')->where('rol', $rol)->pluck('acceso', 'recurso_codigo')->all();
    }

    public static function menuPorRol(string $rol): Collection
    {
        return DB::table('recursos as r')
            ->join('permisos as p', 'p.recurso_codigo', '=', 'r.codigo')
            ->where('p.rol', $rol)
            ->where('r.publico', false)
            ->orderBy('r.orden')
            ->get(['r.codigo', 'r.nombre', 'r.ruta', 'r.icono', 'r.caso_uso', 'p.acceso']);
    }
}
