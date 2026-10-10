<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('prospectos', function (Blueprint $table) {
            $table->id();
            $table->string('nombre');
            $table->string('apellido');
            $table->string('documento')->unique();
            $table->string('correo')->unique();
            $table->string('telefono');
            $table->string('estado')->default('Nuevo');
            $table->foreignId('vendedor_id')->nullable()->constrained('usuarios')->nullOnDelete();
            $table->timestamp('fecha_registro')->useCurrent();
            $table->timestamps();

            $table->index(['estado', 'vendedor_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('prospectos');
    }
};
