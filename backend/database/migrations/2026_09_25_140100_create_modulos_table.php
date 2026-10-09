<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('modulos', function (Blueprint $table) {
            $table->id();
            $table->foreignId('programa_id')->constrained('programas')->cascadeOnDelete();
            $table->string('nombre');
            $table->text('descripcion')->nullable();
            $table->integer('orden')->default(1);
            $table->string('duracion');
            $table->decimal('precio', 12, 2);
            $table->text('imagen')->nullable();
            $table->string('estado')->default('activo');
            $table->timestamps();

            $table->unique(['programa_id', 'nombre']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('modulos');
    }
};
