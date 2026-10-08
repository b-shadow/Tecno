<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('comisiones', function (Blueprint $table) {
            $table->id();
            $table->foreignId('vendedor_id')->constrained('usuarios')->cascadeOnDelete();
            $table->foreignId('venta_id')->unique()->constrained('solicitudes_compra')->cascadeOnDelete();
            $table->decimal('porcentaje', 5, 2)->default(1);
            $table->decimal('monto', 12, 2);
            $table->string('estado')->default('Generada');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('comisiones');
    }
};
