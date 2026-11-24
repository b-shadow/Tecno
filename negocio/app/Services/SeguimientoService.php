<?php

namespace App\Services;

use App\Exceptions\ReglaNegocioException;
use Carbon\CarbonImmutable;
use Datos\Modelos\Interaccion;
use Datos\Modelos\Interes;
use Datos\Modelos\Recordatorio;
use Datos\Modelos\Usuario;
use Datos\Repositorios\SeguimientoRepository;
use Illuminate\Support\Collection;
use Illuminate\Validation\ValidationException;

/** CU7: interacciones (RF4.1, RF4.2) y recordatorios (RF4.3). CU6: inscripciones y comisiones de las ventas. */
class SeguimientoService
{
    private const ZONA_NEGOCIO = 'America/La_Paz';

    public function __construct(private readonly SeguimientoRepository $seguimiento)
    {
    }

    /** RF4.2: nota o contacto ya ocurrido. La primera interacción de una tarjeta nueva la pasa a En Contacto. */
    public function registrarInteraccion(Usuario $usuario, Interes $interes, array $datos): Interaccion
    {
        AlcanceService::autorizarTarjeta($usuario, $interes);

        $interaccion = $this->seguimiento->transaccion(function () use ($interes, $usuario, $datos) {
            $interaccion = $this->seguimiento->registrarInteraccion($interes, $datos + ['usuario_correo' => $usuario->correo, 'fecha' => now()]);
            $this->seguimiento->actualizarInteres($interes, ['estado' => $interes->estado === 'Nuevo' ? 'En Contacto' : $interes->estado, 'ultima_actividad_en' => now()]);

            return $interaccion;
        });

        return $this->seguimiento->cargarInteraccion($interaccion);
    }

    /** Recordatorios dentro del alcance; desde/hasta llegan como fechas de Bolivia (YYYY-MM-DD). */
    public function recordatorios(Usuario $usuario, ?string $estado, ?string $desde, ?string $hasta): Collection
    {
        return $this->seguimiento->listarRecordatorios(
            $usuario, $estado,
            $desde ? $this->fechaNegocio($desde) : null,
            $hasta ? $this->fechaNegocio($hasta)->addDay() : null,
        );
    }

    /** RF4.3: actividad a futuro ("Llamar mañana a las 10:00"). Queda a cargo del vendedor de la tarjeta. */
    public function crearRecordatorio(Usuario $usuario, Interes $interes, array $datos): Recordatorio
    {
        AlcanceService::autorizarTarjeta($usuario, $interes);
        $fecha = $this->fechaNegocio($datos['fecha_programada']);
        if ($fecha->isPast()) {
            throw ValidationException::withMessages(['fecha_programada' => 'La actividad debe programarse para una fecha y hora futura.']);
        }

        return $this->seguimiento->transaccion(function () use ($interes, $usuario, $datos, $fecha) {
            $recordatorio = $this->seguimiento->crearRecordatorio($interes, [
                'fecha_programada' => $fecha, 'descripcion' => $datos['descripcion'], 'estado' => 'Pendiente',
                'usuario_correo' => $interes->vendedor_correo ?? $usuario->correo,
            ]);
            $this->seguimiento->actualizarInteres($interes, ['proximo_contacto' => $fecha]);

            return $recordatorio;
        });
    }

    /** Marcar como realizada exige el resultado; queda como interacción en el historial. */
    public function completarRecordatorio(Usuario $usuario, Recordatorio $recordatorio, string $resultado): void
    {
        $this->seguimiento->cargarInteresRecordatorio($recordatorio);
        AlcanceService::autorizarTarjeta($usuario, $recordatorio->interes);

        $this->seguimiento->transaccion(function () use ($recordatorio, $usuario, $resultado) {
            $recordatorio = $this->seguimiento->buscarRecordatorioBloqueado($recordatorio->nro_recordatorio);
            $this->exigirAbierto($recordatorio);
            $this->seguimiento->recordatorio($recordatorio, ['estado' => 'Realizada', 'fecha_realizada' => now()]);

            $programada = $recordatorio->fecha_programada->timezone(self::ZONA_NEGOCIO)->format('d/m/Y H:i');
            $this->seguimiento->insertarInteraccion([
                'nro_tarjeta' => $recordatorio->nro_tarjeta, 'usuario_correo' => $usuario->correo, 'tipo' => 'Nota comercial',
                'descripcion' => "Actividad agendada para {$programada}: {$recordatorio->descripcion}", 'resultado' => $resultado, 'fecha' => now(),
            ]);
            $this->seguimiento->actualizarInteres($recordatorio->interes, ['ultima_actividad_en' => now()]);
        });
    }

    public function cancelarRecordatorio(Usuario $usuario, Recordatorio $recordatorio): void
    {
        $this->seguimiento->cargarInteresRecordatorio($recordatorio);
        AlcanceService::autorizarTarjeta($usuario, $recordatorio->interes);
        $this->exigirAbierto($recordatorio);
        $this->seguimiento->recordatorio($recordatorio, ['estado' => 'Cancelado']);
    }

    /** RF1.2/RF1.3: el vendedor ve las suyas; el coordinador, las de sus programas; el administrador, todas. */
    public function comisiones(Usuario $usuario): Collection
    {
        return $this->seguimiento->comisiones($usuario);
    }

    public function resumenComisiones(Usuario $usuario): Collection
    {
        return $this->seguimiento->resumenComisiones($usuario);
    }

    /** Registra el pago de las comisiones pendientes del vendedor dentro del alcance de quien paga. */
    public function pagarComisiones(Usuario $usuario, Usuario $vendedor): int
    {
        ReglaNegocioException::si($vendedor->rol !== 'vendedor', 'El usuario seleccionado no es vendedor.');

        return $this->seguimiento->pagarComisiones($vendedor->correo, $usuario);
    }

    public function porcentajeComision(): float
    {
        return $this->seguimiento->porcentajeComision();
    }

    /** El porcentaje es global (todas las ventas): solo el administrador lo cambia. */
    public function actualizarPorcentajeComision(Usuario $usuario, float $porcentaje): float
    {
        ReglaNegocioException::si($usuario->rol !== 'administrador', 'Solo el administrador cambia el porcentaje de comisión.', 403);
        $this->seguimiento->actualizarPorcentajeComision((string) $porcentaje, $usuario->correo);

        return $this->seguimiento->porcentajeComision();
    }

    public function inscripciones(Usuario $usuario): Collection
    {
        return $this->seguimiento->inscripciones($usuario);
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
