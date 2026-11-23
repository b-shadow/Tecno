<?php

namespace App\Services;

use App\Models\Interes;
use App\Models\Recordatorio;
use App\Models\Usuario;
use App\Repositories\SeguimientoRepository;
use App\Services\Alcance;
use Carbon\CarbonImmutable;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

/** CU7: interacciones (RF4.1, RF4.2) y recordatorios (RF4.3). CU8: ventas, comisiones e inscripciones. */
class SeguimientoService
{
    private const ZONA_NEGOCIO = 'America/La_Paz';

    public function __construct(private readonly SeguimientoRepository $seguimiento)
    {
    }

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

        $interaccion = $this->seguimiento->transaccion(function () use ($interes, $usuario, $data) {
            $interaccion = $this->seguimiento->registrarInteraccion($interes, $data + ['usuario_correo' => $usuario->correo, 'fecha' => now()]);
            $this->seguimiento->actualizarInteres($interes, ['estado' => $interes->estado === 'Nuevo' ? 'En Contacto' : $interes->estado, 'ultima_actividad_en' => now()]);

            return $interaccion;
        });

        return response()->json(['mensaje' => 'Interacción registrada.', 'interaccion' => $this->seguimiento->cargarInteraccion($interaccion)], 201);
    }

    public function recordatorios(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $desde = $request->query('desde') ? $this->fechaNegocio($request->query('desde')) : null;
        $hasta = $request->query('hasta') ? $this->fechaNegocio($request->query('hasta'))->addDay() : null;
        $recordatorios = $this->seguimiento->listarRecordatorios($usuario, $request->query('estado'), $desde, $hasta);

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
        $recordatorio = $this->seguimiento->transaccion(function () use ($interes, $usuario, $data, $fecha) {
            $recordatorio = $this->seguimiento->crearRecordatorio($interes, [
                'fecha_programada' => $fecha, 'descripcion' => $data['descripcion'], 'estado' => 'Pendiente',
                'usuario_correo' => $interes->vendedor_correo ?? $usuario->correo,
            ]);
            $this->seguimiento->actualizarInteres($interes, ['proximo_contacto' => $fecha]);

            return $recordatorio;
        });

        return response()->json(['mensaje' => 'Actividad agendada.', 'recordatorio' => $recordatorio], 201);
    }

    /** Marcar como realizada exige el resultado; queda como interacción en el historial. */
    public function completarRecordatorio(Request $request, Recordatorio $recordatorio): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $this->seguimiento->cargarInteresRecordatorio($recordatorio);
        Alcance::autorizarTarjeta($usuario, $recordatorio->interes);
        $data = $request->validate(['resultado' => ['required', 'string', 'min:3', 'max:1000']], [], ['resultado' => 'resultado de la actividad']);

        $this->seguimiento->transaccion(function () use ($recordatorio, $usuario, $data) {
            $recordatorio = $this->seguimiento->buscarRecordatorioBloqueado($recordatorio->nro_recordatorio);
            abort_unless(in_array($recordatorio->estado, ['Pendiente', 'Atrasada'], true), 422, 'La actividad ya fue realizada o cancelada.');
            $this->seguimiento->recordatorio($recordatorio, ['estado' => 'Realizada', 'fecha_realizada' => now()]);

            $programada = $recordatorio->fecha_programada->timezone(self::ZONA_NEGOCIO)->format('d/m/Y H:i');
            $this->seguimiento->insertarInteraccion([
                'nro_tarjeta' => $recordatorio->nro_tarjeta, 'usuario_correo' => $usuario->correo, 'tipo' => 'Nota comercial',
                'descripcion' => "Actividad agendada para {$programada}: {$recordatorio->descripcion}", 'resultado' => $data['resultado'], 'fecha' => now(),
            ]);
            $this->seguimiento->actualizarInteres($recordatorio->interes, ['ultima_actividad_en' => now()]);
        });

        return response()->json(['mensaje' => 'Actividad marcada como realizada.']);
    }

    public function cancelarRecordatorio(Request $request, Recordatorio $recordatorio): JsonResponse
    {
        $this->seguimiento->cargarInteresRecordatorio($recordatorio);
        Alcance::autorizarTarjeta($request->attributes->get('auth_usuario'), $recordatorio->interes);
        abort_unless(in_array($recordatorio->estado, ['Pendiente', 'Atrasada'], true), 422, 'La actividad ya fue realizada o cancelada.');
        $this->seguimiento->recordatorio($recordatorio, ['estado' => 'Cancelado']);

        return response()->json(['mensaje' => 'Actividad cancelada.']);
    }

    public function comisiones(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $comisiones = $this->seguimiento->comisiones($usuario);

        return response()->json(['comisiones' => $comisiones, 'porcentaje' => Comision::porcentajeVigente()]);
    }

    public function resumenComisiones(Request $request): JsonResponse
    {
        $resumen = $this->seguimiento->resumenComisiones();

        return response()->json(['vendedores' => $resumen]);
    }

    public function pagarComisiones(Usuario $vendedor): JsonResponse
    {
        abort_if($vendedor->rol !== 'vendedor', 422, 'El usuario seleccionado no es vendedor.');
        $total = $this->seguimiento->pagarComisiones($vendedor->correo);

        return response()->json(['mensaje' => $total ? "{$total} comisión(es) marcadas como pagadas." : 'No había comisiones pendientes.']);
    }

    public function configuracionComision(): JsonResponse
    {
        return response()->json(['porcentaje' => $this->seguimiento->porcentajeComision()]);
    }

    public function actualizarConfiguracionComision(Request $request): JsonResponse
    {
        $data = $request->validate(['porcentaje' => ['required', 'numeric', 'min:0', 'max:50']], [], ['porcentaje' => 'porcentaje de comisión']);
        $this->seguimiento->actualizarPorcentajeComision((string) $data['porcentaje'], $request->attributes->get('auth_usuario')->correo);

        return response()->json(['mensaje' => 'Porcentaje de comisión actualizado.', 'porcentaje' => $this->seguimiento->porcentajeComision()]);
    }

    public function inscripciones(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        return response()->json(['inscripciones' => $this->seguimiento->inscripciones($usuario)]);
    }

    private function fechaNegocio(string $valor): CarbonImmutable
    {
        // El navegador envía la hora de Bolivia; la BD guarda la hora de la aplicación.
        return CarbonImmutable::parse($valor, self::ZONA_NEGOCIO)->setTimezone(config('app.timezone'));
    }
}
