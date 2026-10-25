<?php

namespace App\Services;

use App\Models\Interes;
use App\Models\Usuario;
use App\Repositories\ConversionRepository;

/**
 * CU6 / RF3.4: antes de pasar una tarjeta a Convertido se validan los datos que la matrícula necesita.
 * Si están completos se dispara la matrícula: inscripción comercial y comisión por cada módulo de la orden aprobada.
 * Se llama al aprobar la 1.ª cuota y al mover la tarjeta a Convertido en el Kanban.
 */
class Conversion
{
    /** @return string[] lo que falta para convertir (vacío = se puede) */
    public static function faltantes(Interes $interes): array
    {
        [$prospecto, $orden] = app(ConversionRepository::class)->datosConversion($interes);
        $faltan = [];

        foreach (['documento' => 'carnet de identidad', 'nombre' => 'nombre', 'apellido' => 'apellido', 'correo' => 'correo',
            'telefono' => 'teléfono', 'profesion' => 'profesión', 'ubicacion' => 'ciudad'] as $campo => $etiqueta) {
            if (trim((string) $prospecto?->{$campo}) === '') {
                $faltan[] = "Falta el dato del prospecto: {$etiqueta}.";
            }
        }

        if (! filter_var($prospecto?->correo, FILTER_VALIDATE_EMAIL)) {
            $faltan[] = 'El correo del prospecto no es válido.';
        }
        if (! $orden) {
            $faltan[] = 'La primera cuota de una orden de pago todavía no está aprobada.';
        }
        if (! $interes->vendedor_correo) {
            $faltan[] = 'La tarjeta no tiene vendedor asignado.';
        }

        return $faltan;
    }

    /** Matricula y deja la tarjeta en Convertido. Llamar dentro de una transacción. */
    public static function procesar(Interes $interes, Usuario $usuario): void
    {
        $conversiones = app(ConversionRepository::class);
        [$prospecto, $orden] = $conversiones->datosConversion($interes);
        abort_unless($orden, 422, 'No se encontró una orden de pago aprobada.');
        $conversiones->registrarInscripcionesYComisiones($orden);
        $conversiones->actualizarConversion($interes, ['estado' => 'Convertido', 'ultima_actividad_en' => now()], 'Convertido');
        $conversiones->registrarInteraccion($interes, [
            'usuario_correo' => $usuario->correo,
            'tipo' => 'Compra validada',
            'descripcion' => 'Datos completos validados. Matrícula comercial confirmada para '.$orden->items->count().' módulo(s).',
            'resultado' => 'Convertido',
            'fecha' => now(),
        ]);
    }

}
