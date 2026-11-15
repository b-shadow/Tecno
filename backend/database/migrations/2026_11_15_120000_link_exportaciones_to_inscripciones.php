<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('exportaciones', function (Blueprint $table) {
            $table->foreignId('inscripcion_comercial_id')->nullable()
                ->constrained('inscripciones_comerciales')->restrictOnDelete();
        });
        // Recupera el enlace del payload historico sin borrar intentos anteriores.
        foreach (DB::table('exportaciones')->orderBy('id')->cursor() as $exportacion) {
            $payload = json_decode($exportacion->respuesta ?? '', true);
            $id = is_array($payload) ? ($payload['inscripcion']['id'] ?? null) : null;
            if ($id && DB::table('inscripciones_comerciales')->where('id', $id)->exists()) {
                DB::table('exportaciones')->where('id', $exportacion->id)
                    ->update(['inscripcion_comercial_id' => $id]);
            }
        }
    }

    public function down(): void
    {
        Schema::table('exportaciones', fn (Blueprint $table) => $table->dropConstrainedForeignId('inscripcion_comercial_id'));
    }
};
