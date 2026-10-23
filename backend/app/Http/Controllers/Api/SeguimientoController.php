<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Comision;
use App\Models\InscripcionComercial;
use App\Models\Interaccion;
use App\Models\Interes;
use App\Models\Recordatorio;
use App\Models\Usuario;
use App\Services\Alcance;
use Carbon\CarbonImmutable;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\Rule;

/** CU7: interacciones (RF4.1, RF4.2) y recordatorios (RF4.3). CU8: ventas, comisiones e inscripciones. */
class SeguimientoController extends Controller
{
    private const ZONA_NEGOCIO = 'America/La_Paz';

    /** RF4.2: nota o contacto ya ocurrido. La primera interacción de una tarjeta nueva la pasa a En Contacto. */
    public function registrarInteraccion(Request $request, Interes $interes): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        Alcance::autorizarTarjeta($usuario, $interes);
        $data = $request->validate([
            'tipo' => ['required', Rule::in(['WhatsApp', 'Llamada', 'Correo electronico', 'Reunion', 'Nota comercial'])],
            'descripcion' => ['required', 'string', 'min:3', 'max:2000'],
            'resultado' => ['nullable', 'string', 'max:500'],
        ], [], ['descripcion' => 'descripción']);

        $interaccion = DB::transaction(function () use ($interes, $usuario, $data) {
            $interaccion = $interes->interacciones()->create($data + ['usuario_correo' => $usuario->correo, 'fecha' => now()]);
            $interes->update(['estado' => $interes->estado === 'Nuevo' ? 'En Contacto' : $interes->estado, 'ultima_actividad_en' => now()]);

            return $interaccion;
        });

        return response()->json(['mensaje' => 'Interacción registrada.', 'interaccion' => $interaccion->load('usuario:correo,nombre,apellido')], 201);
    }

    public function recordatorios(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        Recordatorio::query()->where('estado', 'Pendiente')->where('fecha_programada', '<', now()->subHours(24))->update(['estado' => 'Atrasada']);

        $recordatorios = Recordatorio::query()
            ->whereHas('interes', fn ($q) => Alcance::intereses($q, $usuario))
            ->with('interes.prospecto:documento,nombre,apellido,telefono', 'usuario:correo,nombre,apellido')
            ->when($request->query('estado'), fn ($q, $estado) => $q->where('estado', $estado))
            ->when($request->query('desde'), fn ($q, $desde) => $q->where('fecha_programada', '>=', $this->fechaNegocio($desde)))
            ->when($request->query('hasta'), fn ($q, $hasta) => $q->where('fecha_programada', '<', $this->fechaNegocio($hasta)->addDay()))
            ->orderBy('fecha_programada')
            ->get();

        return response()->json(['recordatorios' => $recordatorios]);
    }

    /** RF4.3: actividad a futuro ("Llamar mañana a las 10:00"). Queda a cargo del vendedor de la tarjeta. */
    public function crearRecordatorio(Request $request, Interes $interes): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        Alcance::autorizarTarjeta($usuario, $interes);
        $data = $request->validate([
            'fecha_programada' => ['required', 'date'],
            'descripcion' => ['required', 'string', 'min:3', 'max:1000'],
        ], [], ['fecha_programada' => 'fecha y hora', 'descripcion' => 'descripción']);

        $fecha = $this->fechaNegocio($data['fecha_programada']);
        if ($fecha->isPast()) {
            throw \Illuminate\Validation\ValidationException::withMessages(['fecha_programada' => 'La actividad debe programarse para una fecha y hora futura.']);
        }
        $recordatorio = DB::transaction(function () use ($interes, $usuario, $data, $fecha) {
            $recordatorio = $interes->recordatorios()->create([
                'fecha_programada' => $fecha, 'descripcion' => $data['descripcion'], 'estado' => 'Pendiente',
                'usuario_correo' => $interes->vendedor_correo ?? $usuario->correo,
            ]);
            $interes->update(['proximo_contacto' => $fecha]);

            return $recordatorio;
        });

        return response()->json(['mensaje' => 'Actividad agendada.', 'recordatorio' => $recordatorio], 201);
    }

    /** Marcar como realizada exige el resultado; queda como interacción en el historial. */
    public function completarRecordatorio(Request $request, Recordatorio $recordatorio): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        Alcance::autorizarTarjeta($usuario, $recordatorio->interes);
        $data = $request->validate(['resultado' => ['required', 'string', 'min:3', 'max:1000']], [], ['resultado' => 'resultado de la actividad']);

        DB::transaction(function () use ($recordatorio, $usuario, $data) {
            $recordatorio = Recordatorio::query()->lockForUpdate()->findOrFail($recordatorio->nro_recordatorio);
            abort_unless(in_array($recordatorio->estado, ['Pendiente', 'Atrasada'], true), 422, 'La actividad ya fue realizada o cancelada.');
            $recordatorio->update(['estado' => 'Realizada', 'fecha_realizada' => now()]);

            $programada = $recordatorio->fecha_programada->timezone(self::ZONA_NEGOCIO)->format('d/m/Y H:i');
            Interaccion::query()->create([
                'nro_tarjeta' => $recordatorio->nro_tarjeta, 'usuario_correo' => $usuario->correo, 'tipo' => 'Nota comercial',
                'descripcion' => "Actividad agendada para {$programada}: {$recordatorio->descripcion}", 'resultado' => $data['resultado'], 'fecha' => now(),
            ]);
            $recordatorio->interes->update(['ultima_actividad_en' => now()]);
        });

        return response()->json(['mensaje' => 'Actividad marcada como realizada.']);
    }

    public function cancelarRecordatorio(Request $request, Recordatorio $recordatorio): JsonResponse
    {
        Alcance::autorizarTarjeta($request->attributes->get('auth_usuario'), $recordatorio->interes);
        abort_unless(in_array($recordatorio->estado, ['Pendiente', 'Atrasada'], true), 422, 'La actividad ya fue realizada o cancelada.');
        $recordatorio->update(['estado' => 'Cancelado']);

        return response()->json(['mensaje' => 'Actividad cancelada.']);
    }

    public function comisiones(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $comisiones = Comision::query()
            ->whereHas('venta.ordenPago.interes', fn ($q) => Alcance::intereses($q, $usuario))
            ->with('vendedor:correo,nombre,apellido', 'venta.ordenPago.interes.prospecto:documento,nombre,apellido')
            ->orderByDesc('created_at')
            ->get();

        return response()->json(['comisiones' => $comisiones, 'porcentaje' => Comision::porcentajeVigente()]);
    }

    public function resumenComisiones(Request $request): JsonResponse
    {
        $resumen = DB::table('usuarios as u')
            ->leftJoin('comisiones as c', 'c.vendedor_correo', '=', 'u.correo')
            ->where('u.rol', 'vendedor')
            ->groupBy('u.correo', 'u.nombre', 'u.apellido')
            ->orderBy('u.nombre')
            ->selectRaw("u.correo, u.nombre, u.apellido, count(c.nro_solicitud) as cursos_vendidos, coalesce(sum(c.monto),0) as comision_total,
                coalesce(sum(c.monto) filter (where c.estado = 'Pendiente'),0) as comision_pendiente")
            ->get();

        return response()->json(['vendedores' => $resumen]);
    }

    public function pagarComisiones(Usuario $vendedor): JsonResponse
    {
        abort_if($vendedor->rol !== 'vendedor', 422, 'El usuario seleccionado no es vendedor.');
        $total = Comision::query()->where('vendedor_correo', $vendedor->correo)->where('estado', 'Pendiente')->update(['estado' => 'Pagada', 'fecha_pago' => now()]);

        return response()->json(['mensaje' => $total ? "{$total} comisión(es) marcadas como pagadas." : 'No había comisiones pendientes.']);
    }

    public function configuracionComision(): JsonResponse
    {
        return response()->json(['porcentaje' => Comision::porcentajeVigente()]);
    }

    public function actualizarConfiguracionComision(Request $request): JsonResponse
    {
        $data = $request->validate(['porcentaje' => ['required', 'numeric', 'min:0', 'max:50']], [], ['porcentaje' => 'porcentaje de comisión']);
        DB::table('configuraciones')->updateOrInsert(['clave' => 'comision_porcentaje'], [
            'valor' => (string) $data['porcentaje'], 'actualizado_por' => $request->attributes->get('auth_usuario')->correo, 'updated_at' => now(),
        ]);

        return response()->json(['mensaje' => 'Porcentaje de comisión actualizado.', 'porcentaje' => Comision::porcentajeVigente()]);
    }

    public function inscripciones(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        return response()->json(['inscripciones' => InscripcionComercial::query()
            ->whereHas('solicitudCompra.ordenPago.interes', fn ($q) => Alcance::intereses($q, $usuario))
            ->with('solicitudCompra.ordenPago.interes.prospecto', 'solicitudCompra.ordenPago.vendedor:correo,nombre,apellido', 'exportaciones')
            ->orderByDesc('fecha_confirmacion')
            ->get()]);
    }

    private function fechaNegocio(string $valor): CarbonImmutable
    {
        // El navegador envía la hora de Bolivia; la BD guarda la hora de la aplicación.
        return CarbonImmutable::parse($valor, self::ZONA_NEGOCIO)->setTimezone(config('app.timezone'));
    }
}
