<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('intereses', function (Blueprint $table) {
            $table->dropUnique(['prospecto_id', 'modulo_id']);
            $table->dropForeign(['modulo_id']);
            $table->dropColumn('modulo_id');
            $table->string('external_modulo_id')->after('prospecto_id');
            $table->string('programa_nombre')->after('external_modulo_id');
            $table->string('modulo_nombre')->after('programa_nombre');
            $table->decimal('precio', 12, 2)->nullable()->after('modulo_nombre');
            $table->unique(['prospecto_id', 'external_modulo_id'], 'intereses_prospecto_external_modulo_unique');
        });

        Schema::table('solicitudes_compra', function (Blueprint $table) {
            $table->dropIndex('solicitudes_modulo_fecha_idx');
            $table->dropForeign(['modulo_id']);
            $table->dropForeign(['anuncio_id']);
            $table->dropColumn(['modulo_id', 'anuncio_id']);
            $table->string('external_anuncio_id')->nullable()->after('prospecto_id');
            $table->string('external_modulo_id')->after('external_anuncio_id');
            $table->string('programa_nombre')->after('external_modulo_id');
            $table->string('modulo_nombre')->after('programa_nombre');
            $table->text('modulo_descripcion')->nullable()->after('modulo_nombre');
            $table->string('anuncio_titulo')->nullable()->after('modulo_descripcion');
            $table->index(['external_modulo_id', 'fecha'], 'solicitudes_external_modulo_fecha_idx');
        });

        Schema::dropIfExists('anuncios');
        Schema::dropIfExists('modulos');
        Schema::dropIfExists('programas');
    }

    public function down(): void
    {
        Schema::create('programas', function (Blueprint $table) {
            $table->id();
            $table->string('nombre')->unique();
            $table->text('descripcion')->nullable();
            $table->text('imagen')->nullable();
            $table->string('estado')->default('activo');
            $table->timestamps();
        });

        Schema::create('modulos', function (Blueprint $table) {
            $table->id();
            $table->foreignId('programa_id')->constrained('programas')->cascadeOnDelete();
            $table->string('nombre');
            $table->text('descripcion')->nullable();
            $table->unsignedInteger('orden')->default(1);
            $table->string('duracion');
            $table->decimal('precio', 12, 2);
            $table->text('imagen')->nullable();
            $table->string('estado')->default('activo');
            $table->timestamps();
            $table->unique(['programa_id', 'nombre']);
        });

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

        Schema::table('solicitudes_compra', function (Blueprint $table) {
            $table->dropIndex('solicitudes_external_modulo_fecha_idx');
            $table->dropColumn(['external_anuncio_id', 'external_modulo_id', 'programa_nombre', 'modulo_nombre', 'modulo_descripcion', 'anuncio_titulo']);
            $table->foreignId('modulo_id')->nullable()->constrained('modulos')->nullOnDelete();
            $table->foreignId('anuncio_id')->nullable()->constrained('anuncios')->nullOnDelete();
            $table->index(['modulo_id', 'fecha'], 'solicitudes_modulo_fecha_idx');
        });

        Schema::table('intereses', function (Blueprint $table) {
            $table->dropUnique('intereses_prospecto_external_modulo_unique');
            $table->dropColumn(['external_modulo_id', 'programa_nombre', 'modulo_nombre', 'precio']);
            $table->foreignId('modulo_id')->nullable()->constrained('modulos')->nullOnDelete();
            $table->unique(['prospecto_id', 'modulo_id']);
        });
    }
};
