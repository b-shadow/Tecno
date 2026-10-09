<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('usuarios', function (Blueprint $table) {
            $table->id();
            $table->string('nombre');
            $table->string('apellido');
            $table->string('correo')->unique();
            $table->string('telefono')->nullable();
            $table->string('password');
            $table->string('rol');
            $table->string('estado')->default('activo');
            $table->timestamps();

            $table->index(['rol', 'estado']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('usuarios');
    }
};
