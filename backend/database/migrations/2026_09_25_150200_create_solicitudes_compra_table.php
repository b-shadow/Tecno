<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('solicitudes_compra', function (Blueprint $table) {
            $table->id();
            $table->foreignId('prospecto_id')->constrained('prospectos')->cascadeOnDelete();
            $table->foreignId('modulo_id')->constrained('modulos')->cascadeOnDelete();
            $table->foreignId('anuncio_id')->nullable()->constrained('anuncios')->nullOnDelete();
            $table->decimal('precio_acordado', 12, 2)->nullable();
            $table->string('estado')->default('pendiente');
            $table->timestamp('fecha')->useCurrent();
            $table->timestamps();

            $table->index(['modulo_id', 'fecha'], 'solicitudes_modulo_fecha_idx');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('solicitudes_compra');
    }
};
