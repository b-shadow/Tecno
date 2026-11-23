<?php

namespace App\Repositories;

use App\Models\Interes;
use App\Models\Usuario;
use Illuminate\Database\Query\Builder;
use Illuminate\Support\Carbon;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Consultas de lectura y agregación para los informes del negocio. */
class ReporteRepository
{
    public function dashboard(Usuario $usuario, Collection $dias, bool $incluirAccesos): array
    {
        $tarjetas = $this->tarjetas($usuario);
        $ventas = (clone $tarjetas)->join('ordenes_pago as o', 'o.nro_tarjeta', '=', 'i.nro_tarjeta')
            ->join('cuotas as c', 'c.nro_orden', '=', 'o.nro_orden')->where('c.estado', 'Pago aprobado');
        $embudo = (clone $tarjetas)->groupBy('i.estado')->selectRaw('i.estado as etiqueta, count(*) as total')->pluck('total', 'etiqueta');
        $ingresos = (clone $ventas)->where('c.fecha_pago', '>=', $dias->first())
            ->groupByRaw('c.fecha_pago::date')->selectRaw('c.fecha_pago::date as dia, sum(c.monto) as total')->pluck('total', 'dia');
        $programas = (clone $tarjetas)->where('i.estado', 'Convertido')->groupBy('i.programa_nombre')
            ->selectRaw('i.programa_nombre as etiqueta, count(*) as total')->pluck('total', 'etiqueta');

        $resultado = [
            'indicadores' => [
                'tarjetas_abiertas' => (clone $tarjetas)->whereNotIn('i.estado', ['Convertido', 'Perdido'])->count(),
                'sin_asignar' => (clone $tarjetas)->whereNull('i.vendedor_correo')->count(),
                'convertidos' => (clone $tarjetas)->where('i.estado', 'Convertido')->count(),
                'perdidos' => (clone $tarjetas)->where('i.estado', 'Perdido')->count(),
                'ingresos_mes' => (float) (clone $ventas)->where('c.fecha_pago', '>=', now()->startOfMonth())->sum('c.monto'),
                'cuotas_en_revision' => (clone $tarjetas)->join('ordenes_pago as o', 'o.nro_tarjeta', '=', 'i.nro_tarjeta')
                    ->join('cuotas as c', 'c.nro_orden', '=', 'o.nro_orden')->where('c.estado', 'En revision')->count(),
                'cuotas_vencidas' => (clone $tarjetas)->join('ordenes_pago as o', 'o.nro_tarjeta', '=', 'i.nro_tarjeta')
                    ->join('cuotas as c', 'c.nro_orden', '=', 'o.nro_orden')->whereIn('c.estado', ['Pendiente de pago', 'Pago rechazado'])
                    ->where('c.fecha_vencimiento', '<', now()->toDateString())->count(),
                'actividades_hoy' => DB::table('recordatorios as r')->joinSub((clone $tarjetas)->select('i.nro_tarjeta'), 't', 't.nro_tarjeta', '=', 'r.nro_tarjeta')
                    ->whereIn('r.estado', ['Pendiente', 'Atrasada'])->whereDate('r.fecha_programada', now()->toDateString())->count(),
            ],
            'embudo' => $embudo,
            'ingresos_por_dia' => $ingresos,
            'ventas_por_programa' => $programas,
            'visitas_por_pagina' => DB::table('recursos')->orderByDesc('visitas')->limit(8)->get(['nombre', 'visitas']),
        ];

        if ($incluirAccesos) {
            $logins = DB::table('bitacora')->whereIn('evento', ['login_exitoso', 'login_fallido'])->where('fecha', '>=', $dias->first())
                ->groupByRaw('fecha::date, evento')->selectRaw('fecha::date as dia, evento, count(*) as total')->get();
            $resultado['accesos'] = [
                'exitosos' => $logins->where('evento', 'login_exitoso')->pluck('total', 'dia'),
                'fallidos' => $logins->where('evento', 'login_fallido')->pluck('total', 'dia'),
                'denegados_semana' => DB::table('bitacora')->where('evento', 'acceso_denegado')->where('fecha', '>=', now()->subDays(7))->count(),
            ];
        }

        return $resultado;
    }

    public function estadisticas(Usuario $usuario, array $filtros): array
    {
        $tarjetas = $this->filtrar($this->tarjetas($usuario), $filtros);
        $porVendedor = (clone $tarjetas)->join('usuarios as v', 'v.correo', '=', 'i.vendedor_correo')
            ->groupBy('v.correo', 'v.nombre', 'v.apellido')
            ->selectRaw("v.nombre || ' ' || v.apellido as vendedor, count(*) as total, count(*) filter (where i.estado = 'Convertido') as convertidos, count(*) filter (where i.estado = 'Perdido') as perdidos")
            ->get();

        return [
            'embudo' => (clone $tarjetas)->groupBy('i.estado')->selectRaw('i.estado as etiqueta, count(*) as total')->pluck('total', 'etiqueta'),
            'perdidas_por_categoria' => (clone $tarjetas)->join('motivos_perdida as m', 'm.nombre', '=', 'i.motivo_perdida')
                ->groupBy('m.categoria')->selectRaw('m.categoria as etiqueta, count(*) as total')->pluck('total', 'etiqueta'),
            'perdidas_por_motivo' => (clone $tarjetas)->whereNotNull('i.motivo_perdida')
                ->groupBy('i.motivo_perdida')->selectRaw('i.motivo_perdida as etiqueta, count(*) as total')->pluck('total', 'etiqueta'),
            'origen_de_leads' => (clone $tarjetas)->join('prospectos as p', 'p.documento', '=', 'i.documento')
                ->groupBy('p.origen')->selectRaw('p.origen as etiqueta, count(distinct p.documento) as total')->pluck('total', 'etiqueta'),
            'conversion_por_vendedor' => $porVendedor,
        ];
    }

    public function listado(Usuario $usuario, array $filtros): array
    {
        $base = $this->filtrar($this->tarjetas($usuario), $filtros)->join('prospectos as p', 'p.documento', '=', 'i.documento')
            ->leftJoin('usuarios as v', 'v.correo', '=', 'i.vendedor_correo');
        $prospecto = DB::raw("p.nombre || ' ' || p.apellido as prospecto");
        $vendedor = DB::raw("coalesce(v.nombre || ' ' || v.apellido, 'Sin asignar') as vendedor");

        [$titulo, $columnas, $filas] = match ($filtros['tipo']) {
            'tarjetas' => ['Embudo de ventas', ['prospecto' => 'Prospecto', 'documento' => 'CI', 'modulo' => 'Módulo', 'programa' => 'Programa', 'vendedor' => 'Vendedor', 'estado' => 'Estado', 'fecha' => 'Registro'],
                $base->orderByDesc('i.fecha')->get([$prospecto, 'p.documento', 'i.modulo_nombre as modulo', 'i.programa_nombre as programa', $vendedor, 'i.estado', DB::raw("to_char(i.fecha, 'DD/MM/YYYY') as fecha")])],
            'perdidas' => ['Prospectos perdidos y motivo', ['prospecto' => 'Prospecto', 'modulo' => 'Módulo', 'vendedor' => 'Vendedor', 'motivo' => 'Motivo', 'categoria' => 'Categoría'],
                $base->where('i.estado', 'Perdido')->leftJoin('motivos_perdida as m', 'm.nombre', '=', 'i.motivo_perdida')->orderBy('m.categoria')
                    ->get([$prospecto, 'i.modulo_nombre as modulo', $vendedor, 'i.motivo_perdida as motivo', 'm.categoria'])],
            'pagos' => ['Cuotas y pagos', ['prospecto' => 'Prospecto', 'orden' => 'Orden', 'cuota' => 'Cuota', 'monto' => 'Monto (Bs)', 'vence' => 'Vence', 'estado' => 'Estado', 'vendedor' => 'Vendedor'],
                $base->join('ordenes_pago as o', 'o.nro_tarjeta', '=', 'i.nro_tarjeta')->join('cuotas as c', 'c.nro_orden', '=', 'o.nro_orden')
                    ->when(in_array($filtros['estado'] ?? null, ['Pendiente de pago', 'En revision', 'Pago aprobado', 'Pago rechazado'], true), fn ($query) => $query->where('c.estado', $filtros['estado']))
                    ->orderBy('c.fecha_vencimiento')->get([$prospecto, 'o.nro_orden as orden', 'c.nro_cuota as cuota', 'c.monto', DB::raw("to_char(c.fecha_vencimiento, 'DD/MM/YYYY') as vence"), 'c.estado', $vendedor])],
            'matriculas' => ['Matrículas confirmadas', ['prospecto' => 'Alumno', 'documento' => 'CI', 'modulo' => 'Módulo', 'precio' => 'Precio (Bs)', 'vendedor' => 'Vendedor', 'fecha' => 'Confirmación'],
                $base->join('ordenes_pago as o', 'o.nro_tarjeta', '=', 'i.nro_tarjeta')->join('solicitudes_compra as s', 's.nro_orden', '=', 'o.nro_orden')
                    ->join('inscripciones_comerciales as ic', 'ic.nro_solicitud', '=', 's.nro_solicitud')->orderByDesc('ic.fecha_confirmacion')
                    ->get([$prospecto, 'p.documento', 's.modulo_nombre as modulo', 's.precio_acordado as precio', $vendedor, DB::raw("to_char(ic.fecha_confirmacion, 'DD/MM/YYYY') as fecha")])],
            'comisiones' => ['Comisiones', ['vendedor' => 'Vendedor', 'prospecto' => 'Alumno', 'modulo' => 'Módulo', 'porcentaje' => '%', 'monto' => 'Monto (Bs)', 'estado' => 'Estado'],
                $base->join('ordenes_pago as o', 'o.nro_tarjeta', '=', 'i.nro_tarjeta')->join('solicitudes_compra as s', 's.nro_orden', '=', 'o.nro_orden')
                    ->join('comisiones as k', 'k.nro_solicitud', '=', 's.nro_solicitud')->orderBy('vendedor')
                    ->get([$vendedor, $prospecto, 's.modulo_nombre as modulo', 'k.porcentaje', 'k.monto', 'k.estado'])],
            'vendedores' => ['Cartera por vendedor', ['vendedor' => 'Vendedor', 'total' => 'Tarjetas', 'abiertas' => 'Abiertas', 'convertidos' => 'Concretadas', 'perdidos' => 'Perdidas'],
                $base->whereNotNull('i.vendedor_correo')->groupBy('v.correo', 'v.nombre', 'v.apellido')
                    ->get([DB::raw("v.nombre || ' ' || v.apellido as vendedor"), DB::raw('count(*) as total'),
                        DB::raw("count(*) filter (where i.estado not in ('Convertido','Perdido')) as abiertas"),
                        DB::raw("count(*) filter (where i.estado = 'Convertido') as convertidos"), DB::raw("count(*) filter (where i.estado = 'Perdido') as perdidos")])],
        };

        return ['titulo' => $titulo, 'columnas' => $columnas, 'filas' => $filas];
    }

    public function estadisticasVendedor(string $correo): array
    {
        $tarjetas = DB::table('intereses')->where('vendedor_correo', $correo);

        return [
            'tarjetas' => (clone $tarjetas)->count(),
            'abiertas' => (clone $tarjetas)->whereNotIn('estado', ['Convertido', 'Perdido'])->count(),
            'convertidos' => (clone $tarjetas)->where('estado', 'Convertido')->count(),
            'interacciones_mes' => DB::table('interacciones')->where('usuario_correo', $correo)->where('fecha', '>=', now()->startOfMonth())->count(),
            'comision_pendiente' => (float) DB::table('comisiones')->where('vendedor_correo', $correo)->where('estado', 'Pendiente')->sum('monto'),
            'actividades_pendientes' => DB::table('recordatorios')->where('usuario_correo', $correo)->whereIn('estado', ['Pendiente', 'Atrasada'])->count(),
        ];
    }

    public function vendedores(): Collection
    {
        return Usuario::query()->where('rol', 'vendedor')->orderBy('nombre')->get(['correo', 'nombre', 'apellido']);
    }

    private function tarjetas(Usuario $usuario): Builder
    {
        $query = DB::table('intereses as i');

        return match ($usuario->rol) {
            'vendedor' => $query->where('i.vendedor_correo', $usuario->correo),
            'coordinador' => $query->whereIn('i.modulo_codigo', AlcanceRepository::codigosModuloCoordinador($usuario->correo)),
            default => $query,
        };
    }

    private function filtrar(Builder $query, array $filtros): Builder
    {
        return $query
            ->when($filtros['desde'] ?? null, fn ($builder, $desde) => $builder->where('i.fecha', '>=', Carbon::parse($desde, 'America/La_Paz')->startOfDay()->utc()))
            ->when($filtros['hasta'] ?? null, fn ($builder, $hasta) => $builder->where('i.fecha', '<=', Carbon::parse($hasta, 'America/La_Paz')->endOfDay()->utc()))
            ->when($filtros['vendedor'] ?? null, fn ($builder, $vendedor) => $builder->where('i.vendedor_correo', $vendedor))
            ->when($filtros['programa'] ?? null, fn ($builder, $programa) => $builder->where('i.programa_nombre', $programa))
            ->when(($filtros['estado'] ?? null) && in_array($filtros['estado'], Interes::ESTADOS, true), fn ($builder) => $builder->where('i.estado', $filtros['estado']))
            ->when($filtros['buscar'] ?? null, fn ($builder, $buscar) => $builder->where(fn ($subquery) => $subquery
                ->where('i.modulo_nombre', 'ilike', "%{$buscar}%")->orWhere('i.programa_nombre', 'ilike', "%{$buscar}%")
                ->orWhereExists(fn ($existe) => $existe->from('prospectos as px')->whereColumn('px.documento', 'i.documento')
                    ->where(fn ($persona) => $persona->where('px.nombre', 'ilike', "%{$buscar}%")
                        ->orWhere('px.apellido', 'ilike', "%{$buscar}%")->orWhere('px.documento', 'ilike', "%{$buscar}%")))));
    }
}
