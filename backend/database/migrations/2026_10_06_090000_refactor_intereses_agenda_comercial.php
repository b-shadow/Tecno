<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('intereses', function (Blueprint $table) {
            if (! Schema::hasColumn('intereses', 'external_anuncio_id')) {
                $table->string('external_anuncio_id')->nullable()->after('external_modulo_id');
            }
            if (! Schema::hasColumn('intereses', 'modulo_descripcion')) {
                $table->text('modulo_descripcion')->nullable()->after('modulo_nombre');
            }
            if (! Schema::hasColumn('intereses', 'vendedor_id')) {
                $table->foreignId('vendedor_id')->nullable()->after('prospecto_id')->constrained('usuarios')->nullOnDelete();
            }
            if (! Schema::hasColumn('intereses', 'estado')) {
                $table->string('estado')->default('Nuevo')->after('precio');
            }
            if (! Schema::hasColumn('intereses', 'fecha_asignacion')) {
                $table->timestamp('fecha_asignacion')->nullable()->after('estado');
            }
            if (! Schema::hasColumn('intereses', 'ultima_actividad_en')) {
                $table->timestamp('ultima_actividad_en')->nullable()->after('fecha_asignacion');
            }
            if (! Schema::hasColumn('intereses', 'proximo_contacto')) {
                $table->timestamp('proximo_contacto')->nullable()->after('ultima_actividad_en');
            }
            if (! Schema::hasColumn('intereses', 'observacion')) {
                $table->text('observacion')->nullable()->after('proximo_contacto');
            }
        });

        Schema::table('interacciones', function (Blueprint $table) {
            if (! Schema::hasColumn('interacciones', 'interes_id')) {
                $table->foreignId('interes_id')->nullable()->after('prospecto_id')->constrained('intereses')->nullOnDelete();
            }
        });

        Schema::table('recordatorios', function (Blueprint $table) {
            if (! Schema::hasColumn('recordatorios', 'interes_id')) {
                $table->foreignId('interes_id')->nullable()->after('prospecto_id')->constrained('intereses')->nullOnDelete();
            }
        });

        Schema::table('ordenes_pago', function (Blueprint $table) {
            if (! Schema::hasColumn('ordenes_pago', 'interes_id')) {
                $table->foreignId('interes_id')->nullable()->after('chat_conversacion_id')->constrained('intereses')->nullOnDelete();
            }
        });

        if (Schema::hasColumn('ordenes_pago', 'chat_conversacion_id')) {
            $driver = DB::connection()->getDriverName();

            if ($driver === 'pgsql') {
                DB::statement('alter table ordenes_pago alter column chat_conversacion_id drop not null');
            } elseif ($driver === 'mysql') {
                DB::statement('alter table ordenes_pago modify chat_conversacion_id bigint unsigned null');
            }

            try {
                Schema::table('ordenes_pago', function (Blueprint $table) {
                    $table->dropForeign(['chat_conversacion_id']);
                });
            } catch (Throwable) {
            }

            try {
                Schema::table('ordenes_pago', function (Blueprint $table) {
                    $table->foreignId('chat_conversacion_id')->nullable()->change();
                });
            } catch (Throwable) {
            }

            try {
                Schema::table('ordenes_pago', function (Blueprint $table) {
                    $table->foreign('chat_conversacion_id')->references('id')->on('chat_conversaciones')->nullOnDelete();
                });
            } catch (Throwable) {
            }
        }

        if (Schema::hasColumn('usuarios', 'prospecto_id')) {
            DB::table('usuarios')->where('rol', 'prospecto')->delete();
        }
    }

    public function down(): void
    {
        Schema::table('recordatorios', function (Blueprint $table) {
            if (Schema::hasColumn('recordatorios', 'interes_id')) {
                $table->dropForeign(['interes_id']);
                $table->dropColumn('interes_id');
            }
        });

        Schema::table('interacciones', function (Blueprint $table) {
            if (Schema::hasColumn('interacciones', 'interes_id')) {
                $table->dropForeign(['interes_id']);
                $table->dropColumn('interes_id');
            }
        });

        Schema::table('intereses', function (Blueprint $table) {
            foreach (['external_anuncio_id', 'modulo_descripcion', 'estado', 'fecha_asignacion', 'ultima_actividad_en', 'proximo_contacto', 'observacion'] as $column) {
                if (Schema::hasColumn('intereses', $column)) {
                    $table->dropColumn($column);
                }
            }

            if (Schema::hasColumn('intereses', 'vendedor_id')) {
                $table->dropForeign(['vendedor_id']);
                $table->dropColumn('vendedor_id');
            }
        });
    }
};
