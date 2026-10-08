<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('intereses', function (Blueprint $table) {
            $table->id();
            $table->foreignId('prospecto_id')->constrained('prospectos')->cascadeOnDelete();
            $table->foreignId('modulo_id')->constrained('modulos')->cascadeOnDelete();
            $table->timestamp('fecha')->useCurrent();
            $table->timestamps();

            $table->unique(['prospecto_id', 'modulo_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('intereses');
    }
};
