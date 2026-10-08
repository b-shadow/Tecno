<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Comision;
use App\Models\InscripcionComercial;
use App\Models\Interes;
use App\Models\OrdenPago;
use App\Models\Pago;
use App\Models\Prospecto;
use App\Models\SolicitudCompra;
use App\Models\Usuario;
use App\Services\CatalogoExternoDemo;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ReporteController extends Controller
{
    public function __construct(private readonly CatalogoExternoDemo $catalogo)
    {
    }

    public function dashboard(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $desde = now()->subDays(6)->startOfDay();

        $inscripciones = InscripcionComercial::query()
            ->with('prospecto', 'solicitudCompra.comision.vendedor', 'solicitudCompra.ordenItem.ordenPago.vendedor')
            ->when($usuario?->rol === 'vendedor', fn ($query) => $query->whereHas('solicitudCompra.comision', fn ($relation) => $relation->where('vendedor_id', $usuario->id)))
            ->get();

        $pagos = Pago::query()
            ->with('ordenPago.vendedor')
            ->when($usuario?->rol === 'vendedor', fn ($query) => $query->whereHas('ordenPago', fn ($relation) => $relation->where('vendedor_id', $usuario->id)))
            ->get();

        $intereses = Interes::query()
            ->when($usuario?->rol === 'vendedor', fn ($query) => $query->where('vendedor_id', $usuario->id))
            ->get();

        $comisiones = Comision::query()
            ->with('vendedor')
            ->when($usuario?->rol === 'vendedor', fn ($query) => $query->where('vendedor_id', $usuario->id))
            ->get();

        $inscripcionesSemana = $inscripciones->filter(fn (InscripcionComercial $inscripcion) => $inscripcion->fecha_confirmacion && $inscripcion->fecha_confirmacion->gte($desde));
        $pagosAprobadosSemana = $pagos->filter(fn (Pago $pago) => $pago->estado === 'Pago aprobado' && $pago->fecha_validacion && $pago->fecha_validacion->gte($desde));

        return response()->json([
            'kpis' => [
                'cursos_semana' => $inscripcionesSemana->count(),
                'ingresos_semana' => (float) $pagosAprobadosSemana->sum('monto'),
                'pagos_revision' => $pagos->where('estado', 'En revision')->count(),
                'chats_abiertos' => $intereses->whereIn('estado', ['Nuevo', 'Contactado', 'Interesado', 'Pago enviado', 'En revision'])->count(),
                'comisiones_pendientes' => (float) $comisiones->where('estado', 'Pendiente')->sum('monto'),
                'alumnos_total' => $inscripciones->count(),
            ],
            'series' => [
                'cursos_por_dia' => $this->serieUltimosDias($inscripciones, 'fecha_confirmacion'),
                'ingresos_por_dia' => $this->serieUltimosDias($pagos->where('estado', 'Pago aprobado'), 'fecha_validacion', 'monto'),
                'pagos_por_estado' => $this->conteoEstados($pagos, Pago::ESTADOS),
                'prospectos_por_estado' => $this->prospectosPorEstado($usuario),
                'modulos_mas_vendidos' => $this->rankingModulos($inscripciones),
                'vendedores_por_cursos' => $this->rankingVendedores($comisiones),
                'comisiones_por_vendedor' => $this->rankingComisionesPorVendedor($comisiones),
                'pagos_pendientes_por_vendedor' => $this->rankingPagosPendientesPorVendedor($pagos),
            ],
        ]);
    }

    public function administrativo(Request $request): JsonResponse
    {
        $this->authorizeRoles($request, ['administrador']);

        $filters = $request->validate([
            'fecha_desde' => ['nullable', 'date'],
            'fecha_hasta' => ['nullable', 'date', 'after_or_equal:fecha_desde'],
            'programa_id' => ['nullable', 'string'],
            'modulo_id' => ['nullable', 'string'],
            'estado' => ['nullable', 'string', 'max:80'],
        ]);

        $catalogo = $this->catalogo->ofertas();
        $ventas = $this->applyPagoFilters(Pago::query()->where('estado', 'Pago aprobado'), $filters);
        $prospectos = $this->applyProspectoFilters(Prospecto::query(), $filters);
        $convertidos = (clone $prospectos)->where('estado', 'Convertido')->count();
        $totalProspectos = (clone $prospectos)->count();
        $pagosPendientes = $this->applyPagoFilters(Pago::query()->whereIn('estado', ['Pendiente de pago', 'En revision']), $filters);
        $inscripciones = $this->applyInscripcionFilters(InscripcionComercial::query(), $filters);
        $ordenesAprobadas = $this->applyOrdenFilters(OrdenPago::query()->whereHas('pago', fn ($query) => $query->where('estado', 'Pago aprobado')), $filters);

        return response()->json([
            'indicadores' => [
                'programas_publicados' => $catalogo->pluck('programa.nombre')->unique()->count(),
                'modulos_publicados' => $catalogo->pluck('external_modulo_id')->unique()->count(),
                'prospectos_registrados' => $totalProspectos,
                'cursos_vendidos' => (clone $inscripciones)->count(),
                'ventas_realizadas' => (clone $ordenesAprobadas)->count() ?: (clone $ventas)->count(),
                'pagos_aprobados' => (clone $ventas)->count(),
                'ingresos_generados' => (float) (clone $ventas)->sum('monto'),
                'conversion_comercial' => $totalProspectos > 0 ? round(($convertidos / $totalProspectos) * 100, 2) : 0,
                'comisiones_generadas' => (float) $this->applyComisionFilters(Comision::query(), $filters)->sum('monto'),
                'pagos_pendientes' => (clone $pagosPendientes)->count(),
                'chats_asignados' => $this->applyInteresFilters(Interes::query()->whereNotNull('vendedor_id'), $filters)->count(),
            ],
            'modulos_mas_vendidos' => $this->modulosMasVendidos($filters),
            'rendimiento_vendedores' => Usuario::query()
                ->where('rol', 'vendedor')
                ->withCount(['interesesAsignados', 'comisiones'])
                ->withSum('comisiones as comision_total', 'monto')
                ->get(),
        ]);
    }

    public function comercial(Request $request): JsonResponse
    {
        $this->authorizeRoles($request, ['administrador', 'coordinador']);

        $filters = $request->validate([
            'fecha_desde' => ['nullable', 'date'],
            'fecha_hasta' => ['nullable', 'date', 'after_or_equal:fecha_desde'],
            'programa_id' => ['nullable', 'string'],
            'modulo_id' => ['nullable', 'string'],
            'estado' => ['nullable', 'string', 'max:80'],
        ]);

        $prospectos = $this->applyProspectoFilters(Prospecto::query(), $filters);
        $totalProspectos = (clone $prospectos)->count();
        $convertidos = (clone $prospectos)->where('estado', 'Convertido')->count();
        $intereses = $this->applyInteresFilters(Interes::query(), $filters);
        $interesesAsignados = (clone $intereses)->whereNotNull('vendedor_id')->count();

        return response()->json([
            'indicadores' => [
                'prospectos_nuevos' => (clone $prospectos)->where('estado', 'Nuevo')->count(),
                'prospectos_contactados' => (clone $prospectos)->where('estado', 'Contactado')->count(),
                'prospectos_convertidos' => $convertidos,
                'prospectos_perdidos' => (clone $prospectos)->where('estado', 'Perdido')->count(),
                'tasa_conversion' => $totalProspectos > 0 ? round(($convertidos / $totalProspectos) * 100, 2) : 0,
                'conversaciones_abiertas' => (clone $intereses)->whereIn('estado', ['Nuevo', 'Contactado', 'Interesado', 'Pago enviado', 'En revision'])->count(),
                'conversaciones_asignadas' => $interesesAsignados,
                'intereses_registrados' => (clone $intereses)->count(),
            ],
            'estados' => (clone $prospectos)
                ->select('estado', DB::raw('count(*) as total'))
                ->groupBy('estado')
                ->orderBy('estado')
                ->get(),
            'seguimientos' => [
                'interacciones' => DB::table('interacciones')->count(),
                'recordatorios_pendientes' => DB::table('recordatorios')->where('estado', 'Pendiente')->count(),
                'ventas_confirmadas' => InscripcionComercial::query()->count(),
                'ordenes_pago' => OrdenPago::query()->count(),
            ],
            'vendedores' => Usuario::query()
                ->where('rol', 'vendedor')
                ->withCount(['interesesAsignados', 'interaccionesRegistradas', 'recordatorios', 'comisiones'])
                ->withSum('comisiones as comision_total', 'monto')
                ->get(),
        ]);
    }

    public function estadisticasVendedor(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $vendedorId = $usuario->rol === 'vendedor' ? $usuario->id : $request->query('vendedor_id', $usuario->id);

        return response()->json([
            'estadisticas' => [
                'conversaciones_asignadas' => Interes::query()->where('vendedor_id', $vendedorId)->count(),
                'prospectos_atendidos' => Interes::query()->where('vendedor_id', $vendedorId)->distinct('prospecto_id')->count('prospecto_id'),
                'interacciones_realizadas' => DB::table('interacciones')->where('usuario_id', $vendedorId)->count(),
                'ventas_logradas' => Comision::query()->where('vendedor_id', $vendedorId)->count(),
                'comisiones_generadas' => (float) Comision::query()->where('vendedor_id', $vendedorId)->sum('monto'),
                'comisiones_pendientes' => (float) Comision::query()->where('vendedor_id', $vendedorId)->where('estado', 'Pendiente')->sum('monto'),
                'pendientes_actuales' => DB::table('recordatorios')->where('usuario_id', $vendedorId)->where('estado', 'Pendiente')->count(),
            ],
        ]);
    }

    public function listado(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $filters = $request->validate([
            'tipo' => ['required', 'in:prospectos,intereses,pagos,alumnos,comisiones,vendedores'],
            'fecha_desde' => ['nullable', 'date'],
            'fecha_hasta' => ['nullable', 'date', 'after_or_equal:fecha_desde'],
            'programa_id' => ['nullable', 'string'],
            'modulo_id' => ['nullable', 'string'],
            'estado' => ['nullable', 'string', 'max:80'],
            'vendedor_id' => ['nullable', 'integer', 'exists:usuarios,id'],
            'buscar' => ['nullable', 'string', 'max:160'],
        ]);

        if ($usuario->rol === 'vendedor') {
            $filters['vendedor_id'] = $usuario->id;
        }

        return match ($filters['tipo']) {
            'prospectos' => $this->reporteProspectos($filters),
            'intereses' => $this->reporteIntereses($filters),
            'pagos' => $this->reportePagos($filters),
            'alumnos' => $this->reporteAlumnos($filters),
            'comisiones' => $this->reporteComisiones($filters),
            'vendedores' => $this->reporteVendedores($filters),
        };
    }

    private function authorizeRoles(Request $request, array $roles): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if(! in_array($usuario?->rol, $roles, true), 403, 'No tiene permisos para esta operacion.');
    }

    private function reporteProspectos(array $filters): JsonResponse
    {
        $query = $this->applyProspectoFilters(Prospecto::query()->withCount(['intereses']), $filters)
            ->when($filters['buscar'] ?? null, fn ($query, $buscar) => $this->buscarProspecto($query, $buscar))
            ->orderByDesc('fecha_registro');

        return $this->reportResponse('Prospectos', [
            ['key' => 'prospecto', 'label' => 'Prospecto'],
            ['key' => 'ci', 'label' => 'CI'],
            ['key' => 'contacto', 'label' => 'Contacto'],
            ['key' => 'perfil', 'label' => 'Perfil'],
            ['key' => 'estado', 'label' => 'Estado'],
            ['key' => 'intereses', 'label' => 'Intereses'],
            ['key' => 'fecha', 'label' => 'Registro'],
        ], $query->get()->map(fn (Prospecto $prospecto) => [
            'prospecto' => trim($prospecto->nombre.' '.$prospecto->apellido),
            'ci' => $prospecto->documento,
            'contacto' => $prospecto->correo.' / '.$prospecto->telefono,
            'perfil' => trim(($prospecto->profesion ?: 'Sin profesion').' - '.($prospecto->ubicacion ?: 'Sin ubicacion')),
            'estado' => $prospecto->estado,
            'intereses' => $prospecto->intereses_count,
            'fecha' => optional($prospecto->fecha_registro)->format('d/m/Y'),
        ])->values());
    }

    private function reporteIntereses(array $filters): JsonResponse
    {
        $query = $this->applyInteresFilters(Interes::query()->with('prospecto', 'vendedor'), $filters)
            ->when($filters['estado'] ?? null, fn ($query, $estado) => $query->where('estado', $estado))
            ->when($filters['vendedor_id'] ?? null, fn ($query, $vendedorId) => $query->where('vendedor_id', $vendedorId))
            ->when($filters['buscar'] ?? null, fn ($query, $buscar) => $query->where(function ($subquery) use ($buscar): void {
                $subquery->where('modulo_nombre', 'ilike', "%{$buscar}%")
                    ->orWhere('programa_nombre', 'ilike', "%{$buscar}%")
                    ->orWhereHas('prospecto', fn ($relation) => $this->buscarProspecto($relation, $buscar));
            }))
            ->latest();

        return $this->reportResponse('Intereses y agenda', [
            ['key' => 'prospecto', 'label' => 'Prospecto'],
            ['key' => 'modulo', 'label' => 'Modulo'],
            ['key' => 'programa', 'label' => 'Programa'],
            ['key' => 'vendedor', 'label' => 'Vendedor'],
            ['key' => 'estado', 'label' => 'Estado'],
            ['key' => 'fecha', 'label' => 'Fecha'],
        ], $query->get()->map(fn (Interes $interes) => [
            'prospecto' => $this->nombreProspecto($interes->prospecto),
            'modulo' => $interes->modulo_nombre,
            'programa' => $interes->programa_nombre,
            'vendedor' => $this->nombreUsuario($interes->vendedor) ?: 'Sin vendedor',
            'estado' => $interes->estado,
            'fecha' => optional($interes->created_at)->format('d/m/Y H:i'),
        ])->values());
    }

    private function reportePagos(array $filters): JsonResponse
    {
        $query = $this->applyPagoFilters(Pago::query()->with([
            'solicitudCompra.prospecto',
            'ordenPago.prospecto',
            'ordenPago.vendedor',
            'ordenPago.items',
        ]), $filters)
            ->when($filters['estado'] ?? null, fn ($query, $estado) => $query->where('estado', $estado))
            ->when($filters['vendedor_id'] ?? null, fn ($query, $vendedorId) => $query->whereHas('ordenPago', fn ($relation) => $relation->where('vendedor_id', $vendedorId)))
            ->latest('fecha_generacion');

        return $this->reportResponse('Pagos', [
            ['key' => 'prospecto', 'label' => 'Prospecto'],
            ['key' => 'vendedor', 'label' => 'Vendedor'],
            ['key' => 'modulos', 'label' => 'Modulo(s)'],
            ['key' => 'monto', 'label' => 'Monto'],
            ['key' => 'estado', 'label' => 'Estado'],
            ['key' => 'fecha', 'label' => 'Fecha'],
        ], $query->get()->map(fn (Pago $pago) => [
            'prospecto' => $this->nombreProspecto($pago->ordenPago?->prospecto ?: $pago->solicitudCompra?->prospecto),
            'vendedor' => $this->nombreUsuario($pago->ordenPago?->vendedor) ?: 'Sin vendedor',
            'modulos' => $pago->ordenPago ? $pago->ordenPago->items->pluck('modulo_nombre')->join(', ') : $pago->solicitudCompra?->modulo_nombre,
            'monto' => number_format((float) $pago->monto, 2).' Bs',
            'estado' => $pago->estado,
            'fecha' => optional($pago->fecha_generacion)->format('d/m/Y H:i'),
        ])->values());
    }

    private function reporteAlumnos(array $filters): JsonResponse
    {
        $query = $this->applyInscripcionFilters(InscripcionComercial::query()->with('prospecto', 'solicitudCompra.ordenItem.ordenPago.vendedor'), $filters)
            ->when($filters['estado'] ?? null, fn ($query, $estado) => $query->where('estado', $estado))
            ->when($filters['vendedor_id'] ?? null, fn ($query, $vendedorId) => $query->whereHas('solicitudCompra.ordenItem.ordenPago', fn ($relation) => $relation->where('vendedor_id', $vendedorId)))
            ->latest('fecha_confirmacion');

        return $this->reportResponse('Alumnos inscritos', [
            ['key' => 'alumno', 'label' => 'Alumno'],
            ['key' => 'ci', 'label' => 'CI'],
            ['key' => 'correo', 'label' => 'Correo'],
            ['key' => 'programa', 'label' => 'Programa'],
            ['key' => 'modulo', 'label' => 'Modulo'],
            ['key' => 'estado', 'label' => 'Estado'],
            ['key' => 'fecha', 'label' => 'Inscripcion'],
        ], $query->get()->map(fn (InscripcionComercial $inscripcion) => [
            'alumno' => $this->nombreProspecto($inscripcion->prospecto),
            'ci' => $inscripcion->prospecto?->documento,
            'correo' => $inscripcion->prospecto?->correo,
            'programa' => $inscripcion->solicitudCompra?->programa_nombre,
            'modulo' => $inscripcion->solicitudCompra?->modulo_nombre,
            'estado' => $inscripcion->estado,
            'fecha' => optional($inscripcion->fecha_confirmacion)->format('d/m/Y H:i'),
        ])->values());
    }

    private function reporteComisiones(array $filters): JsonResponse
    {
        $query = $this->applyComisionFilters(Comision::query()->with('vendedor', 'venta.prospecto'), $filters)
            ->when($filters['estado'] ?? null, fn ($query, $estado) => $query->where('estado', $estado))
            ->when($filters['vendedor_id'] ?? null, fn ($query, $vendedorId) => $query->where('vendedor_id', $vendedorId))
            ->latest();

        return $this->reportResponse('Comisiones', [
            ['key' => 'vendedor', 'label' => 'Vendedor'],
            ['key' => 'prospecto', 'label' => 'Prospecto'],
            ['key' => 'curso', 'label' => 'Curso'],
            ['key' => 'porcentaje', 'label' => 'Porcentaje'],
            ['key' => 'monto', 'label' => 'Monto'],
            ['key' => 'estado', 'label' => 'Estado'],
            ['key' => 'fecha_pago', 'label' => 'Fecha recibida'],
        ], $query->get()->map(fn (Comision $comision) => [
            'vendedor' => $this->nombreUsuario($comision->vendedor),
            'prospecto' => $this->nombreProspecto($comision->venta?->prospecto),
            'curso' => $comision->venta?->modulo_nombre,
            'porcentaje' => number_format((float) $comision->porcentaje, 0).'%',
            'monto' => number_format((float) $comision->monto, 2).' Bs',
            'estado' => $comision->estado,
            'fecha_pago' => $comision->fecha_pago ? $comision->fecha_pago->format('d/m/Y H:i') : 'Pendiente',
        ])->values());
    }

    private function reporteVendedores(array $filters): JsonResponse
    {
        $query = Usuario::query()
            ->where('rol', 'vendedor')
            ->when($filters['vendedor_id'] ?? null, fn ($query, $vendedorId) => $query->where('id', $vendedorId))
            ->withCount(['interesesAsignados', 'comisiones'])
            ->withSum('comisiones as comision_total', 'monto');

        return $this->reportResponse('Vendedores', [
            ['key' => 'vendedor', 'label' => 'Vendedor'],
            ['key' => 'correo', 'label' => 'Correo'],
            ['key' => 'intereses', 'label' => 'Intereses'],
            ['key' => 'cursos_vendidos', 'label' => 'Cursos vendidos'],
            ['key' => 'comision_total', 'label' => 'Comision total'],
            ['key' => 'estado', 'label' => 'Estado'],
        ], $query->get()->map(fn (Usuario $vendedor) => [
            'vendedor' => $this->nombreUsuario($vendedor),
            'correo' => $vendedor->correo,
            'intereses' => $vendedor->intereses_asignados_count,
            'cursos_vendidos' => $vendedor->comisiones_count,
            'comision_total' => number_format((float) ($vendedor->comision_total ?? 0), 2).' Bs',
            'estado' => $vendedor->estado,
        ])->values());
    }

    private function reportResponse(string $titulo, array $columns, $rows): JsonResponse
    {
        return response()->json([
            'titulo' => $titulo,
            'columns' => $columns,
            'rows' => $rows,
            'total' => $rows->count(),
        ]);
    }

    private function buscarProspecto($query, string $buscar)
    {
        return $query->where(function ($subquery) use ($buscar): void {
            $subquery->where('nombre', 'ilike', "%{$buscar}%")
                ->orWhere('apellido', 'ilike', "%{$buscar}%")
                ->orWhere('correo', 'ilike', "%{$buscar}%")
                ->orWhere('documento', 'ilike', "%{$buscar}%")
                ->orWhere('telefono', 'ilike', "%{$buscar}%");
        });
    }

    private function nombreProspecto(?Prospecto $prospecto): string
    {
        return $prospecto ? trim($prospecto->nombre.' '.$prospecto->apellido) : 'Sin prospecto';
    }

    private function nombreUsuario(?Usuario $usuario): string
    {
        return $usuario ? trim($usuario->nombre.' '.$usuario->apellido) : '';
    }

    private function applyProspectoFilters($query, array $filters)
    {
        return $query
            ->when($filters['fecha_desde'] ?? null, fn ($query, $date) => $query->whereDate('fecha_registro', '>=', $date))
            ->when($filters['fecha_hasta'] ?? null, fn ($query, $date) => $query->whereDate('fecha_registro', '<=', $date))
            ->when($filters['estado'] ?? null, fn ($query, $estado) => $query->where('estado', $estado))
            ->when($filters['modulo_id'] ?? null, fn ($query, $moduloId) => $query->where(function ($subquery) use ($moduloId): void {
                $subquery
                    ->whereHas('intereses', fn ($relation) => $relation->where('external_modulo_id', $moduloId))
                    ->orWhereHas('solicitudesCompra', fn ($relation) => $relation->where('external_modulo_id', $moduloId));
            }))
            ->when($filters['programa_id'] ?? null, fn ($query, $programaId) => $query->where(function ($subquery) use ($programaId): void {
                $subquery
                    ->whereHas('intereses', fn ($relation) => $relation->where('programa_nombre', $programaId))
                    ->orWhereHas('solicitudesCompra', fn ($relation) => $relation->where('programa_nombre', $programaId));
            }));
    }

    private function applyPagoFilters($query, array $filters)
    {
        return $query
            ->when($filters['fecha_desde'] ?? null, fn ($query, $date) => $query->whereDate('fecha_generacion', '>=', $date))
            ->when($filters['fecha_hasta'] ?? null, fn ($query, $date) => $query->whereDate('fecha_generacion', '<=', $date))
            ->when($filters['modulo_id'] ?? null, fn ($query, $moduloId) => $query->where(function ($subquery) use ($moduloId): void {
                $subquery
                    ->whereHas('solicitudCompra', fn ($relation) => $relation->where('external_modulo_id', $moduloId))
                    ->orWhereHas('ordenPago.items', fn ($relation) => $relation->where('external_modulo_id', $moduloId));
            }))
            ->when($filters['programa_id'] ?? null, fn ($query, $programaId) => $query->where(function ($subquery) use ($programaId): void {
                $subquery
                    ->whereHas('solicitudCompra', fn ($relation) => $relation->where('programa_nombre', $programaId))
                    ->orWhereHas('ordenPago.items', fn ($relation) => $relation->where('programa_nombre', $programaId));
            }));
    }

    private function applySolicitudFilters($query, array $filters)
    {
        return $query
            ->when($filters['fecha_desde'] ?? null, fn ($query, $date) => $query->whereDate('fecha', '>=', $date))
            ->when($filters['fecha_hasta'] ?? null, fn ($query, $date) => $query->whereDate('fecha', '<=', $date))
            ->when($filters['modulo_id'] ?? null, fn ($query, $moduloId) => $query->where('external_modulo_id', $moduloId))
            ->when($filters['programa_id'] ?? null, fn ($query, $programaId) => $query->where('programa_nombre', $programaId));
    }

    private function applyInscripcionFilters($query, array $filters)
    {
        return $query
            ->when($filters['fecha_desde'] ?? null, fn ($query, $date) => $query->whereDate('fecha_confirmacion', '>=', $date))
            ->when($filters['fecha_hasta'] ?? null, fn ($query, $date) => $query->whereDate('fecha_confirmacion', '<=', $date))
            ->when($filters['modulo_id'] ?? null, fn ($query, $moduloId) => $query->whereHas('solicitudCompra', fn ($relation) => $relation->where('external_modulo_id', $moduloId)))
            ->when($filters['programa_id'] ?? null, fn ($query, $programaId) => $query->whereHas('solicitudCompra', fn ($relation) => $relation->where('programa_nombre', $programaId)));
    }

    private function applyOrdenFilters($query, array $filters)
    {
        return $query
            ->when($filters['fecha_desde'] ?? null, fn ($query, $date) => $query->whereDate('fecha_generacion', '>=', $date))
            ->when($filters['fecha_hasta'] ?? null, fn ($query, $date) => $query->whereDate('fecha_generacion', '<=', $date))
            ->when($filters['modulo_id'] ?? null, fn ($query, $moduloId) => $query->whereHas('items', fn ($relation) => $relation->where('external_modulo_id', $moduloId)))
            ->when($filters['programa_id'] ?? null, fn ($query, $programaId) => $query->whereHas('items', fn ($relation) => $relation->where('programa_nombre', $programaId)));
    }

    private function applyInteresFilters($query, array $filters)
    {
        return $query
            ->when($filters['fecha_desde'] ?? null, fn ($query, $date) => $query->whereDate('fecha', '>=', $date))
            ->when($filters['fecha_hasta'] ?? null, fn ($query, $date) => $query->whereDate('fecha', '<=', $date))
            ->when($filters['modulo_id'] ?? null, fn ($query, $moduloId) => $query->where('external_modulo_id', $moduloId))
            ->when($filters['programa_id'] ?? null, fn ($query, $programaId) => $query->where('programa_nombre', $programaId));
    }

    private function applyComisionFilters($query, array $filters)
    {
        return $query
            ->when($filters['fecha_desde'] ?? null, fn ($query, $date) => $query->whereDate('created_at', '>=', $date))
            ->when($filters['fecha_hasta'] ?? null, fn ($query, $date) => $query->whereDate('created_at', '<=', $date))
            ->when($filters['modulo_id'] ?? null, fn ($query, $moduloId) => $query->whereHas('venta', fn ($relation) => $relation->where('external_modulo_id', $moduloId)))
            ->when($filters['programa_id'] ?? null, fn ($query, $programaId) => $query->whereHas('venta', fn ($relation) => $relation->where('programa_nombre', $programaId)));
    }

    private function modulosMasVendidos(array $filters)
    {
        return $this->applyInscripcionFilters(InscripcionComercial::query(), $filters)
            ->join('solicitudes_compra', 'inscripciones_comerciales.solicitud_compra_id', '=', 'solicitudes_compra.id')
            ->select('solicitudes_compra.external_modulo_id', 'solicitudes_compra.programa_nombre', 'solicitudes_compra.modulo_nombre', DB::raw('count(*) as total'))
            ->groupBy('solicitudes_compra.external_modulo_id', 'solicitudes_compra.programa_nombre', 'solicitudes_compra.modulo_nombre')
            ->orderByDesc('total')
            ->limit(5)
            ->get();
    }

    private function serieUltimosDias($items, string $dateField, ?string $sumField = null): array
    {
        return collect(range(6, 0))->map(function (int $offset) use ($items, $dateField, $sumField): array {
            $date = now()->subDays($offset);
            $dayItems = $items->filter(fn ($item) => $item->{$dateField} && $item->{$dateField}->isSameDay($date));

            return [
                'label' => $date->format('d/m'),
                'total' => $sumField ? round((float) $dayItems->sum($sumField), 2) : $dayItems->count(),
            ];
        })->values()->all();
    }

    private function conteoEstados($items, array $states): array
    {
        return collect($states)->map(fn (string $state): array => [
            'label' => $state,
            'total' => $items->where('estado', $state)->count(),
        ])->values()->all();
    }

    private function prospectosPorEstado(?Usuario $usuario): array
    {
        $query = Prospecto::query()
            ->when($usuario?->rol === 'vendedor', fn ($query) => $query->whereHas('intereses', fn ($relation) => $relation->where('vendedor_id', $usuario->id)));

        $prospectos = $query->get();

        return collect(Prospecto::ESTADOS)->map(fn (string $state): array => [
            'label' => $state,
            'total' => $prospectos->where('estado', $state)->count(),
        ])->values()->all();
    }

    private function rankingModulos($inscripciones): array
    {
        return $inscripciones
            ->groupBy(fn (InscripcionComercial $inscripcion) => $inscripcion->solicitudCompra?->modulo_nombre ?: 'Sin modulo')
            ->map(fn ($items, string $module): array => [
                'label' => $module,
                'total' => $items->count(),
            ])
            ->sortByDesc('total')
            ->take(6)
            ->values()
            ->all();
    }

    private function rankingVendedores($comisiones): array
    {
        return $comisiones
            ->groupBy(fn (Comision $comision) => $this->nombreUsuario($comision->vendedor) ?: 'Sin vendedor')
            ->map(fn ($items, string $seller): array => [
                'label' => $seller,
                'total' => $items->count(),
                'monto' => round((float) $items->sum('monto'), 2),
            ])
            ->sortByDesc('total')
            ->take(6)
            ->values()
            ->all();
    }

    private function rankingComisionesPorVendedor($comisiones): array
    {
        return $comisiones
            ->groupBy(fn (Comision $comision) => $this->nombreUsuario($comision->vendedor) ?: 'Sin vendedor')
            ->map(fn ($items, string $seller): array => [
                'label' => $seller,
                'total' => round((float) $items->sum('monto'), 2),
            ])
            ->sortByDesc('total')
            ->take(6)
            ->values()
            ->all();
    }

    private function rankingPagosPendientesPorVendedor($pagos): array
    {
        return $pagos
            ->whereIn('estado', ['Pendiente de pago', 'En revision', 'Pago rechazado'])
            ->groupBy(fn (Pago $pago) => $this->nombreUsuario($pago->ordenPago?->vendedor) ?: 'Sin vendedor')
            ->map(fn ($items, string $seller): array => [
                'label' => $seller,
                'total' => $items->count(),
            ])
            ->sortByDesc('total')
            ->take(6)
            ->values()
            ->all();
    }
}
