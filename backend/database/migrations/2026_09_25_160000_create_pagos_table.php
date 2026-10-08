<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('pagos', function (Blueprint $table) {
            $table->id();
            $table->foreignId('solicitud_compra_id')->unique()->constrained('solicitudes_compra')->cascadeOnDelete();
            $table->decimal('monto', 12, 2);
            $table->string('codigo_qr')->unique();
            $table->string('estado')->default('Pendiente de pago');
            $table->timestamp('fecha_generacion')->useCurrent();
            $table->timestamp('fecha_validacion')->nullable();
            $table->text('observacion_validacion')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('pagos');
    }
};
