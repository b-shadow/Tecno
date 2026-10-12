<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('comprobantes_pago', function (Blueprint $table) {
            $table->id();
            $table->foreignId('pago_id')->constrained('pagos')->cascadeOnDelete();
            $table->longText('archivo');
            $table->string('nombre_archivo')->nullable();
            $table->string('mime')->nullable();
            $table->timestamp('fecha_envio')->useCurrent();
            $table->text('observacion')->nullable();
            $table->string('estado_revision')->default('En revision');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('comprobantes_pago');
    }
};
