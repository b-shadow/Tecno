<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('anuncios', function (Blueprint $table) {
            $table->id();
            $table->foreignId('modulo_id')->constrained('modulos')->cascadeOnDelete();
            $table->string('titulo');
            $table->text('descripcion');
            $table->text('imagen')->nullable();
            $table->decimal('precio', 12, 2);
            $table->date('fecha_limite_inscripcion')->nullable();
            $table->string('estado')->default('no_publicado');
            $table->timestamps();

            $table->index(['estado', 'fecha_limite_inscripcion'], 'anuncios_estado_fecha_limite_idx');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('anuncios');
    }
};
