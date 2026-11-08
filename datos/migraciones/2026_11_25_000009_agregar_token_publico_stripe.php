<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/*
 * Fase B.2: referencia pública impredecible (token_publico) y vigencia (expira_en) por transacción Stripe
 * para permitir el retorno seguro del cliente a confirmación/cancelación sin autenticación de vendedor.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::table('transacciones_stripe', function (Blueprint $t) {
            $t->string('token_publico', 80)->nullable()->unique('transacciones_stripe_token_publico_unique');
            $t->timestamp('expira_en', 0)->nullable();
        });
    }

    public function down(): void
    {
        Schema::table('transacciones_stripe', function (Blueprint $t) {
            $t->dropUnique('transacciones_stripe_token_publico_unique');
            $t->dropColumn(['token_publico', 'expira_en']);
        });
    }
};
