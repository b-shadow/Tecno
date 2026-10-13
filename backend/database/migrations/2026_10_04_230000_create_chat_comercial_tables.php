<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('usuarios', function (Blueprint $table) {
            $table->foreignId('prospecto_id')->nullable()->after('id')->constrained('prospectos')->nullOnDelete();
            $table->unique('prospecto_id');
        });

        Schema::create('chat_conversaciones', function (Blueprint $table) {
            $table->id();
            $table->foreignId('prospecto_id')->constrained('prospectos')->cascadeOnDelete();
            $table->foreignId('vendedor_id')->nullable()->constrained('usuarios')->nullOnDelete();
            $table->string('external_anuncio_id')->nullable();
            $table->string('external_modulo_id');
            $table->string('programa_nombre');
            $table->string('modulo_nombre');
            $table->text('modulo_descripcion')->nullable();
            $table->string('estado')->default('nuevo');
            $table->timestamp('asignado_en')->nullable();
            $table->timestamps();

            $table->index(['estado', 'vendedor_id']);
            $table->index(['prospecto_id', 'external_modulo_id']);
        });

        Schema::create('chat_mensajes', function (Blueprint $table) {
            $table->id();
            $table->foreignId('chat_conversacion_id')->constrained('chat_conversaciones')->cascadeOnDelete();
            $table->foreignId('usuario_id')->nullable()->constrained('usuarios')->nullOnDelete();
            $table->string('remitente_tipo');
            $table->text('mensaje');
            $table->timestamp('leido_en')->nullable();
            $table->timestamps();

            $table->index(['chat_conversacion_id', 'created_at']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('chat_mensajes');
        Schema::dropIfExists('chat_conversaciones');

        Schema::table('usuarios', function (Blueprint $table) {
            $table->dropUnique(['prospecto_id']);
            $table->dropForeign(['prospecto_id']);
            $table->dropColumn('prospecto_id');
        });
    }
};
