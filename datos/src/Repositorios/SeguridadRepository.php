<?php

namespace Datos\Repositorios;

use Illuminate\Contracts\Pagination\LengthAwarePaginator;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Collection;

/** Consultas y escrituras de la matriz de acceso y la bitácora. */
class SeguridadRepository
{
    public function matriz(): array
    {
        return [
            'roles' => DB::table('roles')->orderByRaw("nombre = 'administrador' desc")->orderBy('nombre')->get(['nombre', 'descripcion']),
            'recursos' => DB::table('recursos')->where('publico', false)->orderBy('orden')->get(['codigo', 'nombre', 'ruta', 'caso_uso']),
            'permisos' => DB::table('permisos')->get(['rol', 'recurso_codigo', 'acceso']),
        ];
    }

    public function guardarPermiso(array $clave, ?string $acceso): void
    {
        if ($acceso !== null) {
            DB::table('permisos')->updateOrInsert($clave, [
                'acceso' => $acceso,
                'updated_at' => now(),
                'created_at' => now(),
            ]);

            return;
        }

        DB::table('permisos')->where($clave)->delete();
    }

    public function bitacora(array $filtros): LengthAwarePaginator
    {
        return DB::table('bitacora as b')
            ->leftJoin('usuarios as u', 'u.correo', '=', 'b.usuario_correo')
            ->leftJoin('recursos as r', 'r.codigo', '=', 'b.recurso_codigo')
            ->when($filtros['evento'] ?? null, fn ($query, $evento) => $query->where('b.evento', $evento))
            ->when($filtros['usuario'] ?? null, fn ($query, $usuario) => $query->where(fn ($subquery) => $subquery
                ->where('b.usuario_correo', 'ilike', "%{$usuario}%")
                ->orWhere('b.correo_intentado', 'ilike', "%{$usuario}%")))
            ->when($filtros['ip'] ?? null, fn ($query, $ip) => $query->where('b.ip', 'like', "{$ip}%"))
            ->when($filtros['desde'] ?? null, fn ($query, $desde) => $query->where('b.fecha', '>=', $desde))
            ->when($filtros['hasta'] ?? null, fn ($query, $hasta) => $query->where('b.fecha', '<=', $hasta))
            ->orderByDesc('b.nro_registro')
            ->select('b.*', DB::raw("u.nombre || ' ' || u.apellido as usuario"), 'r.nombre as recurso')
            ->paginate(50);
    }

    public function resumen(Carbon $desde): array
    {
        return [
            'eventos' => DB::table('bitacora')->where('fecha', '>=', $desde)->groupBy('evento')
                ->selectRaw('evento, count(*) as total')->pluck('total', 'evento'),
            'recursos_mas_accedidos' => DB::table('recursos')->orderByDesc('visitas')->limit(10)
                ->get(['codigo', 'nombre', 'ruta', 'visitas']),
            'ips_con_fallos' => DB::table('bitacora')->where('evento', 'login_fallido')->where('fecha', '>=', $desde)
                ->groupBy('ip')->orderByDesc('total')->limit(8)
                ->selectRaw('ip, count(*) as total, max(fecha) as ultimo')->get(),
            'usuarios_mas_activos' => DB::table('bitacora as b')->join('usuarios as u', 'u.correo', '=', 'b.usuario_correo')
                ->where('b.evento', 'visita')->where('b.fecha', '>=', $desde)->groupBy('u.correo', 'u.nombre', 'u.apellido')
                ->orderByDesc('total')->limit(8)
                ->selectRaw("u.nombre || ' ' || u.apellido as usuario, count(*) as total")->get(),
        ];
    }
}
