<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/*
 * Refactorización definitiva de pagos: configuración de envío automático por orden,
 * enlace público seguro por cuota (token_pago) y control idempotente de recordatorios en PostgreSQL.
 * Las órdenes históricas quedan con envio_automatico = false para no enviar correos antiguos.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::table('ordenes_pago', function (Blueprint $t) {
            $t->boolean('envio_automatico')->default(false);
        });

        Schema::table('cuotas', function (Blueprint $t) {
            $t->string('token_pago', 80)->nullable()->unique('cuotas_token_pago_unique');
            $t->timestamp('primer_envio_en', 0)->nullable();
            $t->timestamp('recordatorio_previo_en', 0)->nullable();
            $t->timestamp('recordatorio_vencimiento_en', 0)->nullable();
            $t->timestamp('recordatorio_mora_en', 0)->nullable();
        });
    }

    public function down(): void
    {
        Schema::table('cuotas', function (Blueprint $t) {
            $t->dropUnique('cuotas_token_pago_unique');
            $t->dropColumn([
                'token_pago',
                'primer_envio_en',
                'recordatorio_previo_en',
                'recordatorio_vencimiento_en',
                'recordatorio_mora_en',
            ]);
        });

        Schema::table('ordenes_pago', function (Blueprint $t) {
            $t->dropColumn('envio_automatico');
        });
    }
};
