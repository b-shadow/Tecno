<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

/*
 * RF3.2: estados obligatorios del embudo (CU4) en la BD compartida con el P1:
 * Nuevo, En Contacto, Seguimiento, Promesa de Pago, Convertido, Perdido.
 * La revisión de un comprobante ya vive en pagos.estado, por eso "Pago enviado" y "En revision" se unen en Promesa de Pago.
 */
return new class extends Migration
{
    private const INTERESES = ['Contactado' => 'En Contacto', 'Interesado' => 'Seguimiento', 'Pago enviado' => 'Promesa de Pago', 'En revision' => 'Promesa de Pago'];

    private const PROSPECTOS = ['Contactado' => 'En Contacto', 'Interesado' => 'Seguimiento', 'En proceso' => 'Promesa de Pago'];

    public const ESTADOS = ['Nuevo', 'En Contacto', 'Seguimiento', 'Promesa de Pago', 'Convertido', 'Perdido'];

    public function up(): void
    {
        $this->cambiar(self::INTERESES, self::PROSPECTOS, self::ESTADOS, self::ESTADOS);
    }

    public function down(): void
    {
        $this->cambiar(
            ['En Contacto' => 'Contactado', 'Seguimiento' => 'Interesado', 'Promesa de Pago' => 'Pago enviado'],
            ['En Contacto' => 'Contactado', 'Seguimiento' => 'Interesado', 'Promesa de Pago' => 'En proceso'],
            ['Nuevo', 'Contactado', 'Interesado', 'Pago enviado', 'En revision', 'Convertido', 'Perdido'],
            ['Nuevo', 'Contactado', 'Interesado', 'En proceso', 'Convertido', 'Perdido'],
        );
    }

    private function cambiar(array $intereses, array $prospectos, array $checkIntereses, array $checkProspectos): void
    {
        // Renombrar un estado no es un movimiento comercial: el trigger de historial solo omite el canal 'correo'.
        DB::statement("SELECT set_config('crm.canal', 'correo', true)");
        foreach (['intereses' => [$intereses, $checkIntereses], 'prospectos' => [$prospectos, $checkProspectos]] as $tabla => [$mapa, $permitidos]) {
            DB::statement("ALTER TABLE {$tabla} DROP CONSTRAINT {$tabla}_estado_check");
            foreach ($mapa as $antes => $despues) {
                DB::table($tabla)->where('estado', $antes)->update(['estado' => $despues]);
            }
            $lista = implode(', ', array_map(fn ($v) => "('{$v}'::character varying)::text", $permitidos));
            DB::statement("ALTER TABLE {$tabla} ADD CONSTRAINT {$tabla}_estado_check CHECK (((estado)::text = ANY (ARRAY[{$lista}])))");
        }
        DB::statement("SELECT set_config('crm.canal', '', true)");
    }
};
