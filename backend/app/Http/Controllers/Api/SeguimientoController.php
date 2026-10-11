<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Comision;
use App\Models\InscripcionComercial;
use App\Models\Interes;
use App\Models\Interaccion;
use App\Models\Prospecto;
use App\Models\Recordatorio;
use App\Models\SolicitudCompra;
use App\Models\Usuario;
use Carbon\CarbonImmutable;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class SeguimientoController extends Controller
{
    private const BUSINESS_TIMEZONE = 'America/La_Paz';

    public function interacciones(Request $request, Prospecto $prospecto): JsonResponse
    {
        $this->authorizeProspecto($request, $prospecto);

        return response()->json([
            'interacciones' => $prospecto->interacciones()->with('usuario')->latest('fecha')->get(),
        ]);
    }

    public function registrarInteraccion(Request $request): JsonResponse
    {
        $data = $request->validate([
            'prospecto_id' => ['nullable', 'exists:prospectos,id', 'required_without:interes_id'],
            'interes_id' => ['nullable', 'exists:intereses,id'],
            'tipo' => ['required', Rule::in(Interaccion::TIPOS)],
            'descripcion' => ['required', 'string'],
            'resultado' => ['nullable', 'string'],
            'fecha' => ['nullable', 'date'],
            'proximo_contacto' => ['nullable', 'date'],
        ]);

        $interes = isset($data['interes_id']) ? Interes::query()->with('prospecto')->findOrFail($data['interes_id']) : null;
        $prospecto = $interes?->prospecto ?? Prospecto::query()->findOrFail($data['prospecto_id']);
        $this->authorizeProspecto($request, $prospecto);
        $proximoContacto = $data['proximo_contacto'] ?? null;
        unset($data['proximo_contacto']);

        $interaccion = Interaccion::query()->create([
            ...$data,
            'prospecto_id' => $prospecto->id,
            'interes_id' => $interes?->id,
            'usuario_id' => $request->attributes->get('auth_usuario')->id,
            'fecha' => $data['fecha'] ?? now(),
        ]);

        if ($interes) {
            $interes->update([
                'estado' => $interes->estado === 'Nuevo' ? 'Contactado' : $interes->estado,
                'ultima_actividad_en' => now(),
                'proximo_contacto' => $proximoContacto ?? $interes->proximo_contacto,
            ]);
        }

        return response()->json(['interaccion' => $interaccion->load('usuario')], 201);
    }

    public function recordatorios(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $this->actualizarRecordatoriosAtrasados();

        $recordatorios = Recordatorio::query()
            ->with('prospecto', 'interes.vendedor', 'usuario')
            ->when($usuario->rol === 'vendedor', fn ($query) => $query->where('usuario_id', $usuario->id))
            ->when($request->query('estado'), fn ($query, string $estado) => $query->where('estado', $estado))
            ->when($request->query('fecha'), fn ($query, string $fecha) => $query->whereDate('fecha_programada', $fecha))
            ->orderBy('fecha_programada')
            ->get();

        return response()->json(['recordatorios' => $recordatorios]);
    }

    public function crearRecordatorio(Request $request): JsonResponse
    {
        $data = $request->validate([
            'prospecto_id' => ['nullable', 'exists:prospectos,id', 'required_without:interes_id'],
            'interes_id' => ['nullable', 'exists:intereses,id'],
            'fecha_programada' => ['required', 'date'],
            'descripcion' => ['required', 'string'],
        ]);

        $interes = isset($data['interes_id']) ? Interes::query()->with('prospecto')->findOrFail($data['interes_id']) : null;
        $prospecto = $interes?->prospecto ?? Prospecto::query()->findOrFail($data['prospecto_id']);
        $this->authorizeProspecto($request, $prospecto);
        $fechaProgramada = $this->parseBusinessDateTime($data['fecha_programada']);

        $recordatorio = Recordatorio::query()->create([
            ...$data,
            'fecha_programada' => $fechaProgramada,
            'prospecto_id' => $prospecto->id,
            'interes_id' => $interes?->id,
            'usuario_id' => $request->attributes->get('auth_usuario')->id,
            'estado' => 'Pendiente',
        ]);

        $interes?->update(['proximo_contacto' => $fechaProgramada]);

        return response()->json(['recordatorio' => $recordatorio->load('prospecto', 'interes', 'usuario')], 201);
    }

    public function completarRecordatorio(Request $request, Recordatorio $recordatorio): JsonResponse
    {
        $this->authorizeProspecto($request, $recordatorio->prospecto);

        $recordatorio->update([
            'estado' => 'Realizada',
            'fecha_realizada' => now(),
        ]);

        return response()->json(['recordatorio' => $recordatorio->fresh()->load('prospecto', 'interes', 'usuario')]);
    }

    public function cancelarRecordatorio(Request $request, Recordatorio $recordatorio): JsonResponse
    {
        $this->authorizeProspecto($request, $recordatorio->prospecto);

        $recordatorio->update(['estado' => 'Cancelado']);

        return response()->json(['recordatorio' => $recordatorio->fresh()->load('prospecto', 'interes', 'usuario')]);
    }

    public function confirmarInscripcion(Request $request): JsonResponse
    {
        $this->authorizeCoordinacion($request);

        $data = $request->validate([
            'solicitud_compra_id' => ['required', 'exists:solicitudes_compra,id'],
        ]);

        $solicitud = SolicitudCompra::query()->with('prospecto', 'pago')->findOrFail($data['solicitud_compra_id']);

        if (! $solicitud->pago || $solicitud->pago->estado !== 'Pago aprobado') {
            return response()->json(['mensaje' => 'Solo pagos aprobados permiten confirmar inscripcion.'], 422);
        }

        $inscripcion = InscripcionComercial::query()->firstOrCreate([
            'solicitud_compra_id' => $solicitud->id,
        ], [
            'prospecto_id' => $solicitud->prospecto_id,
            'fecha_confirmacion' => now(),
            'estado' => 'Confirmada',
        ]);

        $solicitud->prospecto->update(['estado' => 'Convertido']);

        $comision = null;
        if ($solicitud->prospecto->vendedor_id) {
            $comision = Comision::query()->firstOrCreate([
                'venta_id' => $solicitud->id,
            ], [
                'vendedor_id' => $solicitud->prospecto->vendedor_id,
                'porcentaje' => 2,
                'monto' => round(((float) $solicitud->precio_acordado) * 0.02, 2),
                'estado' => 'Pendiente',
            ]);
        }

        return response()->json([
            'inscripcion' => $inscripcion->load('prospecto', 'solicitudCompra'),
            'comision' => $comision?->load('vendedor', 'venta'),
        ]);
    }

    public function comisiones(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $comisiones = Comision::query()
            ->with('vendedor', 'venta.prospecto')
            ->when($usuario->rol === 'vendedor', fn ($query) => $query->where('vendedor_id', $usuario->id))
            ->orderByDesc('created_at')
            ->get();

        return response()->json(['comisiones' => $comisiones]);
    }

    public function resumenComisiones(Request $request): JsonResponse
    {
        $this->authorizeCoordinacion($request);

        $vendedores = Usuario::query()
            ->where('rol', 'vendedor')
            ->withSum('comisiones as comision_total', 'monto')
            ->withSum(['comisiones as comision_pendiente' => fn ($query) => $query->where('estado', 'Pendiente')], 'monto')
            ->withCount('comisiones')
            ->orderBy('nombre')
            ->get();

        return response()->json([
            'vendedores' => $vendedores,
            'ranking_ventas' => Comision::query()
                ->selectRaw('vendedor_id, count(*) as cursos_vendidos, sum(monto) as comision_total')
                ->with('vendedor')
                ->groupBy('vendedor_id')
                ->orderByDesc('cursos_vendidos')
                ->get(),
        ]);
    }

    public function pagarComisiones(Request $request, Usuario $vendedor): JsonResponse
    {
        $this->authorizeCoordinacion($request);
        abort_if($vendedor->rol !== 'vendedor', 422, 'El usuario seleccionado no es vendedor.');

        Comision::query()
            ->where('vendedor_id', $vendedor->id)
            ->where('estado', 'Pendiente')
            ->update([
                'estado' => 'Pagada',
                'fecha_pago' => now(),
            ]);

        return response()->json(['mensaje' => 'Comisiones marcadas como recibidas.']);
    }

    public function inscripciones(Request $request): JsonResponse
    {
        $this->authorizeCoordinacion($request);

        return response()->json([
            'inscripciones' => InscripcionComercial::query()
                ->with('prospecto', 'solicitudCompra.pago', 'solicitudCompra.ordenItem.ordenPago.pago')
                ->latest()
                ->get(),
        ]);
    }

    private function authorizeProspecto(Request $request, Prospecto $prospecto): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        $tieneInteresAsignado = $prospecto->intereses()->where('vendedor_id', $usuario?->id)->exists();

        abort_if(
            $usuario?->rol === 'vendedor' && $prospecto->vendedor_id !== $usuario->id && ! $tieneInteresAsignado,
            403,
            'Prospecto no asignado.'
        );
    }

    private function authorizeCoordinacion(Request $request): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if(! in_array($usuario?->rol, ['administrador', 'coordinador'], true), 403, 'No tiene permisos de coordinacion.');
    }

    private function actualizarRecordatoriosAtrasados(): void
    {
        Recordatorio::query()
            ->where('estado', 'Pendiente')
            ->where('fecha_programada', '<', now()->subHours(24))
            ->update(['estado' => 'Atrasada']);
    }

    private function parseBusinessDateTime(string $value): CarbonImmutable
    {
        return CarbonImmutable::parse($value, self::BUSINESS_TIMEZONE)->utc();
    }
}
