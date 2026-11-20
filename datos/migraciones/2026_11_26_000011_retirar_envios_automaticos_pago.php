<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('ordenes_pago', function (Blueprint $t) {
            $t->dropColumn('envio_automatico');
        });

        Schema::table('cuotas', function (Blueprint $t) {
            $t->dropColumn([
                'primer_envio_en',
                'recordatorio_previo_en',
                'recordatorio_vencimiento_en',
                'recordatorio_mora_en',
            ]);
        });
    }

    public function down(): void
    {
        Schema::table('ordenes_pago', function (Blueprint $t) {
            $t->boolean('envio_automatico')->default(false);
        });

        // El respaldo previo es necesario para recuperar los valores retirados.
        Schema::table('cuotas', function (Blueprint $t) {
            $t->timestamp('primer_envio_en', 0)->nullable();
            $t->timestamp('recordatorio_previo_en', 0)->nullable();
            $t->timestamp('recordatorio_vencimiento_en', 0)->nullable();
            $t->timestamp('recordatorio_mora_en', 0)->nullable();
        });
    }
};
