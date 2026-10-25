<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Interes;
use App\Models\Usuario;
use App\Services\Acceso;
use App\Services\Alcance;
use Illuminate\Database\Query\Builder;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;

/**
 * CU8 y enunciado 8. Clase del docente: "reporte es un listado, estadística es la representación porcentual".
 * Todo se calcula dentro del alcance del rol (RF1.2 / RF1.3).
 */
class ReporteController extends Controller
{
    /** Panel analítico: indicadores y series del negocio, y flujo de accesos del sitio. */
    public function dashboard(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $dias = collect(range(13, 0))->map(fn ($n) => now()->subDays($n)->toDateString());
        $tarjetas = $this->tarjetas($usuario);

        $ventas = (clone $tarjetas)
            ->join('ordenes_pago as o', 'o.nro_tarjeta', '=', 'i.nro_tarjeta')
            ->join('cuotas as c', 'c.nro_orden', '=', 'o.nro_orden')
            ->where('c.estado', 'Pago aprobado');

        $respuesta = [
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
            'embudo' => $this->porcentajes((clone $tarjetas)->groupBy('i.estado')->selectRaw('i.estado as etiqueta, count(*) as total')->pluck('total', 'etiqueta'), Interes::ESTADOS),
            'ingresos_por_dia' => $this->serie($dias, (clone $ventas)->where('c.fecha_pago', '>=', $dias->first())
                ->groupByRaw('c.fecha_pago::date')->selectRaw('c.fecha_pago::date as dia, sum(c.monto) as total')->pluck('total', 'dia')),
            'ventas_por_programa' => $this->porcentajes((clone $tarjetas)->where('i.estado', 'Convertido')->groupBy('i.programa_nombre')
                ->selectRaw('i.programa_nombre as etiqueta, count(*) as total')->pluck('total', 'etiqueta')),
            'visitas_por_pagina' => DB::table('recursos')->orderByDesc('visitas')->limit(8)->get(['nombre', 'visitas']),
        ];

        // El flujo de inicios de sesión es información de auditoría: solo para quien ve la bitácora.
        if (Acceso::permite($usuario, 'bitacora')) {
            $logins = DB::table('bitacora')->whereIn('evento', ['login_exitoso', 'login_fallido'])->where('fecha', '>=', $dias->first())
                ->groupByRaw('fecha::date, evento')->selectRaw('fecha::date as dia, evento, count(*) as total')->get();
            $respuesta['accesos'] = [
                'exitosos' => $this->serie($dias, $logins->where('evento', 'login_exitoso')->pluck('total', 'dia')),
                'fallidos' => $this->serie($dias, $logins->where('evento', 'login_fallido')->pluck('total', 'dia')),
                'denegados_semana' => DB::table('bitacora')->where('evento', 'acceso_denegado')->where('fecha', '>=', now()->subDays(7))->count(),
            ];
        }

        return response()->json($respuesta);
    }

    /** Estadísticas porcentuales (CU8, CU5). */
    public function estadisticas(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $tarjetas = $this->filtrar($this->tarjetas($usuario), $request);

        $porVendedor = (clone $tarjetas)->join('usuarios as v', 'v.correo', '=', 'i.vendedor_correo')
            ->groupBy('v.correo', 'v.nombre', 'v.apellido')
            ->selectRaw("v.nombre || ' ' || v.apellido as vendedor, count(*) as total, count(*) filter (where i.estado = 'Convertido') as convertidos, count(*) filter (where i.estado = 'Perdido') as perdidos")
            ->get()
            ->map(fn ($f) => (array) $f + ['tasa_conversion' => $f->total ? round($f->convertidos * 100 / $f->total, 1) : 0]);

        return response()->json([
            'embudo' => $this->porcentajes((clone $tarjetas)->groupBy('i.estado')->selectRaw('i.estado as etiqueta, count(*) as total')->pluck('total', 'etiqueta'), Interes::ESTADOS),
            'perdidas_por_categoria' => $this->porcentajes((clone $tarjetas)->join('motivos_perdida as m', 'm.nombre', '=', 'i.motivo_perdida')
                ->groupBy('m.categoria')->selectRaw('m.categoria as etiqueta, count(*) as total')->pluck('total', 'etiqueta')),
            'perdidas_por_motivo' => $this->porcentajes((clone $tarjetas)->whereNotNull('i.motivo_perdida')
                ->groupBy('i.motivo_perdida')->selectRaw('i.motivo_perdida as etiqueta, count(*) as total')->pluck('total', 'etiqueta')),
            'origen_de_leads' => $this->porcentajes((clone $tarjetas)->join('prospectos as p', 'p.documento', '=', 'i.documento')
                ->groupBy('p.origen')->selectRaw('p.origen as etiqueta, count(distinct p.documento) as total')->pluck('total', 'etiqueta')),
            'conversion_por_vendedor' => $porVendedor,
        ]);
    }

    /** Reportes (listados) con filtros. El vendedor siempre ve solo lo suyo. */
    public function listado(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $request->validate([
            'tipo' => ['required', 'in:tarjetas,pagos,matriculas,comisiones,perdidas,vendedores'],
            'desde' => ['nullable', 'date'],
            'hasta' => ['nullable', 'date', 'after_or_equal:desde'],
            'vendedor' => ['nullable', 'email'],
            'programa' => ['nullable', 'string', 'max:255'],
            'estado' => ['nullable', 'string', 'max:40'],
            'buscar' => ['nullable', 'string', 'max:120'],
        ], [], ['desde' => 'fecha inicial', 'hasta' => 'fecha final']);

        $base = $this->filtrar($this->tarjetas($usuario), $request)->join('prospectos as p', 'p.documento', '=', 'i.documento')
            ->leftJoin('usuarios as v', 'v.correo', '=', 'i.vendedor_correo');
        $prospecto = DB::raw("p.nombre || ' ' || p.apellido as prospecto");
        $vendedor = DB::raw("coalesce(v.nombre || ' ' || v.apellido, 'Sin asignar') as vendedor");

        [$titulo, $columnas, $filas] = match ($request->query('tipo')) {
            'tarjetas' => ['Embudo de ventas', ['prospecto' => 'Prospecto', 'documento' => 'CI', 'modulo' => 'Módulo', 'programa' => 'Programa', 'vendedor' => 'Vendedor', 'estado' => 'Estado', 'fecha' => 'Registro'],
                $base->orderByDesc('i.fecha')->get([$prospecto, 'p.documento', 'i.modulo_nombre as modulo', 'i.programa_nombre as programa', $vendedor, 'i.estado', DB::raw("to_char(i.fecha, 'DD/MM/YYYY') as fecha")])],
            'perdidas' => ['Prospectos perdidos y motivo', ['prospecto' => 'Prospecto', 'modulo' => 'Módulo', 'vendedor' => 'Vendedor', 'motivo' => 'Motivo', 'categoria' => 'Categoría'],
                $base->where('i.estado', 'Perdido')->leftJoin('motivos_perdida as m', 'm.nombre', '=', 'i.motivo_perdida')
                    ->orderBy('m.categoria')->get([$prospecto, 'i.modulo_nombre as modulo', $vendedor, 'i.motivo_perdida as motivo', 'm.categoria'])],
            'pagos' => ['Cuotas y pagos', ['prospecto' => 'Prospecto', 'orden' => 'Orden', 'cuota' => 'Cuota', 'monto' => 'Monto (Bs)', 'vence' => 'Vence', 'estado' => 'Estado', 'vendedor' => 'Vendedor'],
                $base->join('ordenes_pago as o', 'o.nro_tarjeta', '=', 'i.nro_tarjeta')->join('cuotas as c', 'c.nro_orden', '=', 'o.nro_orden')
                    ->when($request->query('estado') && in_array($request->query('estado'), ['Pendiente de pago', 'En revision', 'Pago aprobado', 'Pago rechazado'], true), fn ($q) => $q->where('c.estado', $request->query('estado')))
                    ->orderBy('c.fecha_vencimiento')->get([$prospecto, 'o.nro_orden as orden', 'c.nro_cuota as cuota', 'c.monto', DB::raw("to_char(c.fecha_vencimiento, 'DD/MM/YYYY') as vence"), 'c.estado', $vendedor])],
            'matriculas' => ['Matrículas confirmadas', ['prospecto' => 'Alumno', 'documento' => 'CI', 'modulo' => 'Módulo', 'precio' => 'Precio (Bs)', 'vendedor' => 'Vendedor', 'fecha' => 'Confirmación'],
                $base->join('ordenes_pago as o', 'o.nro_tarjeta', '=', 'i.nro_tarjeta')->join('solicitudes_compra as s', 's.nro_orden', '=', 'o.nro_orden')
                    ->join('inscripciones_comerciales as ic', 'ic.nro_solicitud', '=', 's.nro_solicitud')
                    ->orderByDesc('ic.fecha_confirmacion')->get([$prospecto, 'p.documento', 's.modulo_nombre as modulo', 's.precio_acordado as precio', $vendedor, DB::raw("to_char(ic.fecha_confirmacion, 'DD/MM/YYYY') as fecha")])],
            'comisiones' => ['Comisiones', ['vendedor' => 'Vendedor', 'prospecto' => 'Alumno', 'modulo' => 'Módulo', 'porcentaje' => '%', 'monto' => 'Monto (Bs)', 'estado' => 'Estado'],
                $base->join('ordenes_pago as o', 'o.nro_tarjeta', '=', 'i.nro_tarjeta')->join('solicitudes_compra as s', 's.nro_orden', '=', 'o.nro_orden')
                    ->join('comisiones as k', 'k.nro_solicitud', '=', 's.nro_solicitud')
                    ->orderBy('vendedor')->get([$vendedor, $prospecto, 's.modulo_nombre as modulo', 'k.porcentaje', 'k.monto', 'k.estado'])],
            'vendedores' => ['Cartera por vendedor', ['vendedor' => 'Vendedor', 'total' => 'Tarjetas', 'abiertas' => 'Abiertas', 'convertidos' => 'Concretadas', 'perdidos' => 'Perdidas'],
                $base->whereNotNull('i.vendedor_correo')->groupBy('v.correo', 'v.nombre', 'v.apellido')
                    ->get([DB::raw("v.nombre || ' ' || v.apellido as vendedor"), DB::raw('count(*) as total'),
                        DB::raw("count(*) filter (where i.estado not in ('Convertido','Perdido')) as abiertas"),
                        DB::raw("count(*) filter (where i.estado = 'Convertido') as convertidos"), DB::raw("count(*) filter (where i.estado = 'Perdido') as perdidos")])],
        };

        return response()->json([
            'titulo' => $titulo,
            'columnas' => collect($columnas)->map(fn ($label, $key) => ['key' => $key, 'label' => $label])->values(),
            'filas' => $filas,
            'vendedores' => $usuario->rol === 'vendedor' ? [] : Usuario::query()->where('rol', 'vendedor')->orderBy('nombre')->get(['correo', 'nombre', 'apellido']),
        ]);
    }

    /** Resumen personal del vendedor ("Mi día"). */
    public function estadisticasVendedor(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $correo = $usuario->correo;
        $tarjetas = DB::table('intereses')->where('vendedor_correo', $correo);

        return response()->json(['estadisticas' => [
            'tarjetas' => (clone $tarjetas)->count(),
            'abiertas' => (clone $tarjetas)->whereNotIn('estado', ['Convertido', 'Perdido'])->count(),
            'convertidos' => (clone $tarjetas)->where('estado', 'Convertido')->count(),
            'interacciones_mes' => DB::table('interacciones')->where('usuario_correo', $correo)->where('fecha', '>=', now()->startOfMonth())->count(),
            'comision_pendiente' => (float) DB::table('comisiones')->where('vendedor_correo', $correo)->where('estado', 'Pendiente')->sum('monto'),
            'actividades_pendientes' => DB::table('recordatorios')->where('usuario_correo', $correo)->whereIn('estado', ['Pendiente', 'Atrasada'])->count(),
        ]]);
    }

    private function tarjetas(Usuario $usuario): Builder
    {
        $query = DB::table('intereses as i');

        return match ($usuario->rol) {
            'vendedor' => $query->where('i.vendedor_correo', $usuario->correo),
            'coordinador' => $query->whereIn('i.modulo_codigo', Alcance::modulosACargo($usuario)),
            default => $query,
        };
    }

    private function filtrar(Builder $query, Request $request): Builder
    {
        $tz = 'America/La_Paz';

        return $query
            ->when($request->query('desde'), fn ($q, $d) => $q->where('i.fecha', '>=', Carbon::parse($d, $tz)->startOfDay()->utc()))
            ->when($request->query('hasta'), fn ($q, $h) => $q->where('i.fecha', '<=', Carbon::parse($h, $tz)->endOfDay()->utc()))
            ->when($request->query('vendedor'), fn ($q, $v) => $q->where('i.vendedor_correo', $v))
            ->when($request->query('programa'), fn ($q, $p) => $q->where('i.programa_nombre', $p))
            ->when($request->query('estado') && in_array($request->query('estado'), Interes::ESTADOS, true), fn ($q) => $q->where('i.estado', $request->query('estado')))
            ->when($request->query('buscar'), fn ($q, $b) => $q->where(fn ($s) => $s->where('i.modulo_nombre', 'ilike', "%{$b}%")->orWhere('i.programa_nombre', 'ilike', "%{$b}%")
                ->orWhereExists(fn ($e) => $e->from('prospectos as px')->whereColumn('px.documento', 'i.documento')
                    ->where(fn ($n) => $n->where('px.nombre', 'ilike', "%{$b}%")->orWhere('px.apellido', 'ilike', "%{$b}%")->orWhere('px.documento', 'ilike', "%{$b}%")))));
    }

    /** [{etiqueta, total, porcentaje}] en el orden dado (si se da) y con ceros explícitos. */
    private function porcentajes($conteos, ?array $orden = null): array
    {
        $conteos = collect($conteos)->map(fn ($v) => (int) $v);
        $etiquetas = $orden ?? $conteos->sortDesc()->keys()->all();
        $suma = max($conteos->sum(), 1);

        return array_map(fn ($e) => ['etiqueta' => $e, 'total' => $conteos[$e] ?? 0, 'porcentaje' => round(($conteos[$e] ?? 0) * 100 / $suma, 1)], $etiquetas);
    }

    private function serie($dias, $valores): array
    {
        return $dias->map(fn ($d) => ['dia' => $d, 'total' => (float) ($valores[$d] ?? 0)])->all();
    }
}
