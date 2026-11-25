<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Seguimiento\ActualizarComisionRequest;
use App\Http\Requests\Seguimiento\CompletarRecordatorioRequest;
use App\Http\Requests\Seguimiento\CrearRecordatorioRequest;
use App\Http\Requests\Seguimiento\RegistrarInteraccionRequest;
use Carbon\CarbonImmutable;
use Datos\DSeguimiento;
use Datos\Modelos\Recordatorio;
use Illuminate\Http\JsonResponse;
use Illuminate\Validation\ValidationException;

/** Capa de negocio — CU7: interacciones (RF4.1, RF4.2) y recordatorios (RF4.3). CU6/CU8: inscripciones y comisiones. */
class NSeguimiento
{
    private const ZONA_NEGOCIO = 'America/La_Paz';

    public function __construct(private readonly DSeguimiento $seguimiento)
    {
    }

    /** RF4.2: nota o contacto ya ocurrido. La primera interacción de una tarjeta nueva la pasa a En Contacto. */
    public function registrarInteraccion(RegistrarInteraccionRequest $r, int $interes): JsonResponse
    {
        $usuario = $r->usuario();
        $datos = $r->validated();
        $tarjeta = $this->seguimiento->interes($interes);
        NAlcance::autorizarTarjeta($usuario, $tarjeta);

        $interaccion = $this->seguimiento->transaccion(function () use ($tarjeta, $usuario, $datos) {
            $interaccion = $this->seguimiento->registrarInteraccion($tarjeta, $datos + ['usuario_correo' => $usuario->correo, 'fecha' => now()]);
            $this->seguimiento->actualizarInteres($tarjeta, ['estado' => $tarjeta->estado === 'Nuevo' ? 'En Contacto' : $tarjeta->estado, 'ultima_actividad_en' => now()]);

            return $interaccion;
        });

        return response()->json(['mensaje' => 'Interacción registrada.', 'interaccion' => $this->seguimiento->cargarInteraccion($interaccion)], 201);
    }

    /** Recordatorios dentro del alcance; desde/hasta llegan como fechas de Bolivia (YYYY-MM-DD). */
    public function recordatorios(ConsultaRequest $r): JsonResponse
    {
        $desde = $r->query('desde');
        $hasta = $r->query('hasta');
        $recordatorios = $this->seguimiento->listarRecordatorios(
            $r->usuario(), $r->query('estado'),
            $desde ? $this->fechaNegocio($desde) : null,
            $hasta ? $this->fechaNegocio($hasta)->addDay() : null,
        );

        return response()->json(['recordatorios' => $recordatorios]);
    }

    /** RF4.3: actividad a futuro ("Llamar mañana a las 10:00"). Queda a cargo del vendedor de la tarjeta. */
    public function crearRecordatorio(CrearRecordatorioRequest $r, int $interes): JsonResponse
    {
        $usuario = $r->usuario();
        $datos = $r->validated();
        $tarjeta = $this->seguimiento->interes($interes);
        NAlcance::autorizarTarjeta($usuario, $tarjeta);
        $fecha = $this->fechaNegocio($datos['fecha_programada']);
        if ($fecha->isPast()) {
            throw ValidationException::withMessages(['fecha_programada' => 'La actividad debe programarse para una fecha y hora futura.']);
        }

        $recordatorio = $this->seguimiento->transaccion(function () use ($tarjeta, $usuario, $datos, $fecha) {
            $recordatorio = $this->seguimiento->crearRecordatorio($tarjeta, [
                'fecha_programada' => $fecha, 'descripcion' => $datos['descripcion'], 'estado' => 'Pendiente',
                'usuario_correo' => $tarjeta->vendedor_correo ?? $usuario->correo,
            ]);
            $this->seguimiento->actualizarInteres($tarjeta, ['proximo_contacto' => $fecha]);

            return $recordatorio;
        });

        return response()->json(['mensaje' => 'Actividad agendada.', 'recordatorio' => $recordatorio], 201);
    }

    /** Marcar como realizada exige el resultado; queda como interacción en el historial. */
    public function completarRecordatorio(CompletarRecordatorioRequest $r, int $recordatorio): JsonResponse
    {
        $usuario = $r->usuario();
        $resultado = $r->validated('resultado');
        $registro = $this->seguimiento->obtenerRecordatorio($recordatorio);
        $this->seguimiento->cargarInteresRecordatorio($registro);
        NAlcance::autorizarTarjeta($usuario, $registro->interes);

        $this->seguimiento->transaccion(function () use ($registro, $usuario, $resultado) {
            $bloqueado = $this->seguimiento->buscarRecordatorioBloqueado($registro->nro_recordatorio);
            $this->exigirAbierto($bloqueado);
            $this->seguimiento->recordatorio($bloqueado, ['estado' => 'Realizada', 'fecha_realizada' => now()]);

            $programada = $bloqueado->fecha_programada->timezone(self::ZONA_NEGOCIO)->format('d/m/Y H:i');
            $this->seguimiento->insertarInteraccion([
                'nro_tarjeta' => $bloqueado->nro_tarjeta, 'usuario_correo' => $usuario->correo, 'tipo' => 'Nota comercial',
                'descripcion' => "Actividad agendada para {$programada}: {$bloqueado->descripcion}", 'resultado' => $resultado, 'fecha' => now(),
            ]);
            $this->seguimiento->actualizarInteres($bloqueado->interes, ['ultima_actividad_en' => now()]);
        });

        return response()->json(['mensaje' => 'Actividad marcada como realizada.']);
    }

    public function cancelarRecordatorio(ConsultaRequest $r, int $recordatorio): JsonResponse
    {
        $registro = $this->seguimiento->obtenerRecordatorio($recordatorio);
        $this->seguimiento->cargarInteresRecordatorio($registro);
        NAlcance::autorizarTarjeta($r->usuario(), $registro->interes);
        $this->exigirAbierto($registro);
        $this->seguimiento->recordatorio($registro, ['estado' => 'Cancelado']);

        return response()->json(['mensaje' => 'Actividad cancelada.']);
    }

    /** RF1.2/RF1.3: el vendedor ve las suyas; el coordinador, las de sus programas; el administrador, todas. */
    public function comisiones(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['comisiones' => $this->seguimiento->comisiones($r->usuario()), 'porcentaje' => $this->seguimiento->porcentajeComision()]);
    }

    public function resumenComisiones(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['vendedores' => $this->seguimiento->resumenComisiones($r->usuario())]);
    }

    /** Registra el pago de las comisiones pendientes del vendedor dentro del alcance de quien paga. */
    public function pagarComisiones(ConsultaRequest $r, string $vendedor): JsonResponse
    {
        $registro = $this->seguimiento->usuario($vendedor);
        ReglaNegocioException::si($registro->rol !== 'vendedor', 'El usuario seleccionado no es vendedor.');
        $total = $this->seguimiento->pagarComisiones($registro->correo, $r->usuario());

        return response()->json(['mensaje' => $total ? "{$total} comisión(es) marcadas como pagadas." : 'No había comisiones pendientes.']);
    }

    public function configuracionComision(): JsonResponse
    {
        return response()->json(['porcentaje' => $this->seguimiento->porcentajeComision()]);
    }

    /** El porcentaje es global (todas las ventas): solo el administrador lo cambia. */
    public function actualizarConfiguracionComision(ActualizarComisionRequest $r): JsonResponse
    {
        $usuario = $r->usuario();
        ReglaNegocioException::si($usuario->rol !== 'administrador', 'Solo el administrador cambia el porcentaje de comisión.', 403);
        $this->seguimiento->actualizarPorcentajeComision((string) (float) $r->validated('porcentaje'), $usuario->correo);

        return response()->json(['mensaje' => 'Porcentaje de comisión actualizado.', 'porcentaje' => $this->seguimiento->porcentajeComision()]);
    }

    public function inscripciones(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['inscripciones' => $this->seguimiento->inscripciones($r->usuario())]);
    }

    private function exigirAbierto(Recordatorio $recordatorio): void
    {
        ReglaNegocioException::si(! in_array($recordatorio->estado, ['Pendiente', 'Atrasada'], true), 'La actividad ya fue realizada o cancelada.');
    }

    private function fechaNegocio(string $valor): CarbonImmutable
    {
        // El navegador envía la hora de Bolivia; la BD guarda la hora de la aplicación.
        return CarbonImmutable::parse($valor, self::ZONA_NEGOCIO)->setTimezone(config('app.timezone'));
    }
}
