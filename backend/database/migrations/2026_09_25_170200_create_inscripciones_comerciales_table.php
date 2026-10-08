<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('inscripciones_comerciales', function (Blueprint $table) {
            $table->id();
            $table->foreignId('prospecto_id')->constrained('prospectos')->cascadeOnDelete();
            $table->foreignId('solicitud_compra_id')->unique()->constrained('solicitudes_compra')->cascadeOnDelete();
            $table->timestamp('fecha_confirmacion')->useCurrent();
            $table->string('estado')->default('Confirmada');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('inscripciones_comerciales');
    }
};
