<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('descuentos', function (Blueprint $table) {
            $table->id();
            $table->string('nombre');
            $table->string('codigo')->unique();
            $table->decimal('porcentaje', 5, 2);
            $table->string('estado')->default('activo');
            $table->timestamps();
        });

        Schema::create('ordenes_pago', function (Blueprint $table) {
            $table->id();
            $table->foreignId('chat_conversacion_id')->nullable()->constrained('chat_conversaciones')->nullOnDelete();
            $table->foreignId('interes_id')->nullable()->constrained('intereses')->nullOnDelete();
            $table->foreignId('prospecto_id')->constrained('prospectos')->cascadeOnDelete();
            $table->foreignId('vendedor_id')->constrained('usuarios')->cascadeOnDelete();
            $table->decimal('subtotal', 12, 2);
            $table->decimal('descuento_total', 12, 2)->default(0);
            $table->decimal('total', 12, 2);
            $table->string('estado')->default('Pendiente de pago');
            $table->timestamp('fecha_generacion')->useCurrent();
            $table->timestamps();
        });

        Schema::create('orden_pago_items', function (Blueprint $table) {
            $table->id();
            $table->foreignId('orden_pago_id')->constrained('ordenes_pago')->cascadeOnDelete();
            $table->foreignId('solicitud_compra_id')->nullable()->constrained('solicitudes_compra')->nullOnDelete();
            $table->string('external_modulo_id');
            $table->string('programa_nombre');
            $table->string('modulo_nombre');
            $table->text('modulo_descripcion')->nullable();
            $table->decimal('precio', 12, 2);
            $table->timestamps();
        });

        Schema::create('orden_pago_descuentos', function (Blueprint $table) {
            $table->id();
            $table->foreignId('orden_pago_id')->constrained('ordenes_pago')->cascadeOnDelete();
            $table->foreignId('descuento_id')->constrained('descuentos')->cascadeOnDelete();
            $table->decimal('porcentaje', 5, 2);
            $table->decimal('monto', 12, 2);
            $table->timestamps();
        });

        Schema::table('pagos', function (Blueprint $table) {
            $table->dropUnique(['solicitud_compra_id']);
            $table->foreignId('orden_pago_id')->nullable()->after('solicitud_compra_id')->constrained('ordenes_pago')->cascadeOnDelete();
            $table->unique('orden_pago_id');
            $table->unique('solicitud_compra_id');
        });

        Schema::table('comisiones', function (Blueprint $table) {
            $table->decimal('porcentaje', 5, 2)->default(2)->change();
            $table->timestamp('fecha_pago')->nullable()->after('estado');
        });

        DB::table('descuentos')->insert([
            ['nombre' => '3 o mas modulos', 'codigo' => '3_MAS_MODULOS', 'porcentaje' => 10, 'estado' => 'activo', 'created_at' => now(), 'updated_at' => now()],
            ['nombre' => 'Programa completo', 'codigo' => 'PROGRAMA_COMPLETO', 'porcentaje' => 15, 'estado' => 'activo', 'created_at' => now(), 'updated_at' => now()],
            ['nombre' => 'Cliente recurrente', 'codigo' => 'CLIENTE_RECURRENTE', 'porcentaje' => 10, 'estado' => 'activo', 'created_at' => now(), 'updated_at' => now()],
        ]);
    }

    public function down(): void
    {
        Schema::table('comisiones', function (Blueprint $table) {
            $table->dropColumn('fecha_pago');
        });

        Schema::table('pagos', function (Blueprint $table) {
            $table->dropUnique(['orden_pago_id']);
            $table->dropForeign(['orden_pago_id']);
            $table->dropColumn('orden_pago_id');
        });

        Schema::dropIfExists('orden_pago_descuentos');
        Schema::dropIfExists('orden_pago_items');
        Schema::dropIfExists('ordenes_pago');
        Schema::dropIfExists('descuentos');
    }
};
