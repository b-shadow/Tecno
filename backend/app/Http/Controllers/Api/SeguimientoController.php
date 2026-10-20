<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Comision;
use App\Models\InscripcionComercial;
use App\Models\Interaccion;
use App\Models\Interes;
use App\Models\Prospecto;
use App\Models\Recordatorio;
use App\Models\Usuario;
use Carbon\CarbonImmutable;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\Rule;

class SeguimientoController extends Controller
{
    private const BUSINESS_TIMEZONE = 'America/La_Paz';

    public function interacciones(Request $request, Prospecto $prospecto): JsonResponse
    {
        $this->authorizeProspecto($request, $prospecto);

        return response()->json([
            'interacciones' => $prospecto->interacciones()
                ->when($request->attributes->get('auth_usuario')->rol === 'vendedor', fn ($query) => $query->whereHas('interes', fn ($query) => $query->where('vendedor_id', $request->attributes->get('auth_usuario')->id)))
                ->with('usuario')->latest('interacciones.fecha')->get(),
        ]);
    }

    public function registrarInteraccion(Request $request): JsonResponse
    {
        $data = $request->validate([
            'interes_id' => ['required', 'exists:intereses,id'],
            'tipo' => ['required', Rule::in(Interaccion::TIPOS)],
            'descripcion' => ['required', 'string'],
            'resultado' => ['nullable', 'string'],
            'proximo_contacto' => ['nullable', 'date'],
        ]);

        $interes = Interes::query()->with('prospecto')->findOrFail($data['interes_id']);
        $this->authorizeInteres($request, $interes);
        $proximoContacto = $data['proximo_contacto'] ?? null;
        unset($data['proximo_contacto']);

        $interaccion = Interaccion::query()->create([
            ...$data,
            'usuario_id' => $request->attributes->get('auth_usuario')->id,
            'fecha' => now(),
        ]);

        $interes->update([
            'estado' => $interes->estado === 'Nuevo' ? 'Contactado' : $interes->estado,
            'ultima_actividad_en' => now(),
            'proximo_contacto' => $proximoContacto ?? $interes->proximo_contacto,
        ]);

        return response()->json(['interaccion' => $interaccion->load('usuario')], 201);
    }

    public function recordatorios(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $this->actualizarRecordatoriosAtrasados();

        $recordatorios = Recordatorio::query()
            ->with('prospecto', 'interes.vendedor', 'usuario')
            ->when($usuario->rol === 'vendedor', fn ($query) => $query->whereHas('interes', fn ($query) => $query->where('vendedor_id', $usuario->id)))
            ->when($request->query('estado'), fn ($query, string $estado) => $query->where('estado', $estado))
            ->when($request->query('fecha'), fn ($query, string $fecha) => $query->whereDate('fecha_programada', $fecha))
            ->orderBy('fecha_programada')
            ->get();

        return response()->json(['recordatorios' => $recordatorios]);
    }

    public function crearRecordatorio(Request $request): JsonResponse
    {
        $data = $request->validate([
            'interes_id' => ['required', 'exists:intereses,id'],
            'fecha_programada' => ['required', 'date'],
            'descripcion' => ['required', 'string'],
        ]);

        $interes = Interes::query()->with('prospecto')->findOrFail($data['interes_id']);
        $this->authorizeInteres($request, $interes);
        $fechaProgramada = $this->parseBusinessDateTime($data['fecha_programada']);

        $recordatorio = Recordatorio::query()->create([
            ...$data,
            'fecha_programada' => $fechaProgramada,
            'usuario_id' => $interes->vendedor_id ?? $request->attributes->get('auth_usuario')->id,
            'estado' => 'Pendiente',
        ]);

        $interes->update(['proximo_contacto' => $fechaProgramada]);

        return response()->json(['recordatorio' => $recordatorio->load('prospecto', 'interes', 'usuario')], 201);
    }

    public function completarRecordatorio(Request $request, Recordatorio $recordatorio): JsonResponse
    {
        return DB::transaction(function () use ($request, $recordatorio): JsonResponse {
            $recordatorio = Recordatorio::query()->lockForUpdate()->findOrFail($recordatorio->id);
            $this->authorizeInteres($request, $recordatorio->interes);
            abort_if(! in_array($recordatorio->estado, ['Pendiente', 'Atrasada'], true), 422, 'La actividad ya fue realizada o cancelada.');

            $data = $request->validate(['resultado' => ['required', 'string']]);

            $recordatorio->update([
                'estado' => 'Realizada',
                'fecha_realizada' => now(),
            ]);

            $programada = $recordatorio->fecha_programada->timezone(self::BUSINESS_TIMEZONE)->format('d/m/Y H:i');
            Interaccion::query()->create([
                'interes_id' => $recordatorio->interes_id,
                'usuario_id' => $request->attributes->get('auth_usuario')->id,
                'tipo' => 'Nota comercial',
                'descripcion' => "Actividad agendada para {$programada}: {$recordatorio->descripcion}",
                'resultado' => $data['resultado'],
                'fecha' => now(),
            ]);
            $recordatorio->interes?->update(['ultima_actividad_en' => now()]);

            return response()->json(['recordatorio' => $recordatorio->fresh()->load('prospecto', 'interes', 'usuario')]);
        });
    }

    public function cancelarRecordatorio(Request $request, Recordatorio $recordatorio): JsonResponse
    {
        return DB::transaction(function () use ($request, $recordatorio): JsonResponse {
            $recordatorio = Recordatorio::query()->lockForUpdate()->findOrFail($recordatorio->id);
            $this->authorizeInteres($request, $recordatorio->interes);
            abort_if(! in_array($recordatorio->estado, ['Pendiente', 'Atrasada'], true), 422, 'La actividad ya fue realizada o cancelada.');

            $recordatorio->update(['estado' => 'Cancelado']);

            return response()->json(['recordatorio' => $recordatorio->fresh()->load('prospecto', 'interes', 'usuario')]);
        });
    }

    public function comisiones(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $comisiones = Comision::query()
            ->with('vendedor', 'venta.ordenPago.prospecto')
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

    public function configuracionComision(): JsonResponse
    {
        return response()->json(['porcentaje' => Comision::porcentajeVigente()]);
    }

    public function actualizarConfiguracionComision(Request $request): JsonResponse
    {
        $this->authorizeCoordinacion($request);

        $data = $request->validate(['porcentaje' => ['required', 'numeric', 'min:0', 'max:100']]);

        DB::table('configuraciones')->updateOrInsert(
            ['clave' => 'comision_porcentaje'],
            [
                'valor' => (string) $data['porcentaje'],
                'actualizado_por' => $request->attributes->get('auth_usuario')->id,
                'updated_at' => now(),
            ],
        );

        return response()->json(['porcentaje' => Comision::porcentajeVigente()]);
    }

    public function inscripciones(Request $request): JsonResponse
    {
        $this->authorizeCoordinacion($request);

        return response()->json([
            'inscripciones' => InscripcionComercial::query()
                ->with('solicitudCompra.ordenPago.prospecto', 'solicitudCompra.ordenPago.pago')
                ->latest()
                ->get(),
        ]);
    }

    private function authorizeProspecto(Request $request, Prospecto $prospecto): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        $tieneInteresAsignado = $prospecto->intereses()->where('vendedor_id', $usuario?->id)->exists();

        abort_if(
            $usuario?->rol === 'vendedor' && ! $tieneInteresAsignado,
            403,
            'Prospecto no asignado.'
        );
    }

    private function authorizeCoordinacion(Request $request): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if(! in_array($usuario?->rol, ['administrador', 'coordinador'], true), 403, 'No tiene permisos de coordinacion.');
    }

    private function authorizeInteres(Request $request, Interes $interes): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if($usuario->rol === 'vendedor' && $interes->vendedor_id !== $usuario->id, 403, 'Interes asignado a otro vendedor.');
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
        // Las columnas timestamp se guardan en la zona de la aplicacion; Eloquent serializa a UTC.
        return CarbonImmutable::parse($value, self::BUSINESS_TIMEZONE)->setTimezone(config('app.timezone'));
    }
}
