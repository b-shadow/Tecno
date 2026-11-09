<?php

namespace App\Console\Commands;

use App\Negocio\NPago;
use Illuminate\Console\Command;
use Illuminate\Support\Carbon;

/**
 * Ejecuta la programación automática de solicitudes y recordatorios de pago (CU6 / CU7).
 * Toda la lógica de negocio reside en NPago::procesarEnviosAutomaticos().
 */
class RecordatoriosPagosComando extends Command
{
    protected $signature = 'unexo:recordatorios-pago {--fecha= : Fecha de evaluación YYYY-MM-DD (opcional)}';

    protected $description = 'Envía automáticamente por SMTP las solicitudes y recordatorios de cuotas pendientes según vencimiento.';

    public function handle(NPago $pagos): int
    {
        $fechaOpt = $this->option('fecha');
        $tz = (string) config('pagos_recordatorios.zona_horaria', 'America/La_Paz');
        $fecha = $fechaOpt ? Carbon::parse((string) $fechaOpt, $tz) : null;

        $resumen = $pagos->procesarEnviosAutomaticos($fecha);
        $this->info(sprintf(
            'Recordatorios [%s]: evaluadas=%d, enviados=%d, fallidos=%d, omitidos=%d',
            $resumen['fecha'],
            $resumen['evaluadas'],
            $resumen['enviados'],
            $resumen['fallidos'],
            $resumen['omitidos']
        ));

        return self::SUCCESS;
    }
}
