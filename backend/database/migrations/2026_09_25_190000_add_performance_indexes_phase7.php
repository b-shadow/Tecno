<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('pagos', function (Blueprint $table) {
            $table->index(['estado', 'fecha_generacion'], 'pagos_estado_fecha_idx');
        });

        Schema::table('solicitudes_compra', function (Blueprint $table) {
            $table->index(['prospecto_id', 'estado'], 'solicitudes_prospecto_estado_idx');
        });

        Schema::table('interacciones', function (Blueprint $table) {
            $table->index(['prospecto_id', 'fecha'], 'interacciones_prospecto_fecha_idx');
            $table->index(['usuario_id', 'fecha'], 'interacciones_usuario_fecha_idx');
        });

        Schema::table('recordatorios', function (Blueprint $table) {
            $table->index(['usuario_id', 'estado', 'fecha_programada'], 'recordatorios_usuario_estado_fecha_idx');
        });

        Schema::table('notificaciones', function (Blueprint $table) {
            $table->index(['usuario_id', 'estado', 'fecha_envio'], 'notificaciones_usuario_estado_fecha_idx');
        });

        Schema::table('exportaciones', function (Blueprint $table) {
            $table->index(['estado', 'fecha_exportacion'], 'exportaciones_estado_fecha_idx');
        });
    }

    public function down(): void
    {
        Schema::table('exportaciones', function (Blueprint $table) {
            $table->dropIndex('exportaciones_estado_fecha_idx');
        });

        Schema::table('notificaciones', function (Blueprint $table) {
            $table->dropIndex('notificaciones_usuario_estado_fecha_idx');
        });

        Schema::table('recordatorios', function (Blueprint $table) {
            $table->dropIndex('recordatorios_usuario_estado_fecha_idx');
        });

        Schema::table('interacciones', function (Blueprint $table) {
            $table->dropIndex('interacciones_prospecto_fecha_idx');
            $table->dropIndex('interacciones_usuario_fecha_idx');
        });

        Schema::table('solicitudes_compra', function (Blueprint $table) {
            $table->dropIndex('solicitudes_prospecto_estado_idx');
        });

        Schema::table('pagos', function (Blueprint $table) {
            $table->dropIndex('pagos_estado_fecha_idx');
        });
    }
};
