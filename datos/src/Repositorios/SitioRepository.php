<?php

namespace Datos\Repositorios;

use Datos\Modelos\ApiToken;
use Datos\Modelos\Interes;
use Datos\Modelos\Usuario;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Lecturas de persistencia públicas y globales del sitio. */
class SitioRepository
{
    public function recursoPorRuta(string $ruta): ?object
    {
        return DB::table('recursos')->where('ruta', $ruta)->first(['codigo', 'publico']);
    }

    public function visitas(string $codigo): int
    {
        return (int) DB::table('recursos')->where('codigo', $codigo)->value('visitas');
    }

    public function buscarCatalogo(string $like): Collection
    {
        return DB::table('catalogo_cache as c')->join('programas as p', 'p.codigo', '=', 'c.programa_codigo')
            ->where('c.estado', 'abierto')
            ->where(fn ($query) => $query->where('c.nombre', 'ilike', $like)
                ->orWhere('p.nombre', 'ilike', $like)->orWhere('c.descripcion', 'ilike', $like))
            ->limit(5)->get(['c.codigo', 'c.nombre', 'p.nombre as programa', 'c.precio']);
    }

    public function buscarIntereses(string $like, Usuario $usuario): Collection
    {
        return Interes::query()
            ->when($usuario->rol === 'vendedor', fn ($query) => $query->where('intereses.vendedor_correo', $usuario->correo))
            ->when($usuario->rol === 'coordinador', fn ($query) => $query->whereIn('intereses.modulo_codigo', AlcanceRepository::codigosModuloCoordinador($usuario->correo)))
            ->join('prospectos as p', 'p.documento', '=', 'intereses.documento')
            ->where(fn ($query) => $query->where('p.nombre', 'ilike', $like)->orWhere('p.apellido', 'ilike', $like)
                ->orWhere('p.documento', 'ilike', $like)->orWhere('p.telefono', 'ilike', $like)->orWhere('p.correo', 'ilike', $like))
            ->orderByDesc('intereses.nro_tarjeta')->limit(6)
            ->get(['intereses.nro_tarjeta', 'intereses.modulo_nombre', 'intereses.estado', 'p.nombre', 'p.apellido', 'p.documento']);
    }

    public function buscarUsuarios(string $like): Collection
    {
        return Usuario::query()
            ->where(fn ($query) => $query->where('nombre', 'ilike', $like)
                ->orWhere('apellido', 'ilike', $like)->orWhere('correo', 'ilike', $like))
            ->limit(4)->get();
    }

    public function buscarPaginas(string $like, string $rol): Collection
    {
        return DB::table('recursos as r')->join('permisos as p', 'p.recurso_codigo', '=', 'r.codigo')
            ->where('p.rol', $rol)->where('r.nombre', 'ilike', $like)->limit(3)
            ->get(['r.nombre', 'r.ruta']);
    }

    public function conexionDisponible(): bool
    {
        DB::select('select 1');

        return true;
    }
}
