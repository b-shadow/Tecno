<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/**
 * Normalizacion de ventas:
 * - solicitudes_compra pasa a ser la linea (un modulo) de una orden de pago; orden_pago_items duplicaba
 *   esos mismos datos 1 a 1 y se elimina;
 * - todo pago pertenece a una orden (se retira el flujo anterior de pago por solicitud suelta);
 * - comisiones.venta_id pasa a llamarse solicitud_compra_id (la tabla a la que apunta);
 * - se quitan las llaves derivables (3FN): el prospecto se obtiene por el interes
 *   (ordenes_pago, interacciones, recordatorios) o por la orden (solicitudes_compra, inscripciones_comerciales).
 */
return new class extends Migration
{
    public function up(): void
    {
        DB::transaction(function (): void {
            // Solo se autorizo retirar el pago de prueba antiguo: modulo 1, 400 Bs,
            // pendiente y sin comprobante. No ampliar ese permiso a otras ventas.
            $pagosSueltos = DB::table('pagos')->whereNull('orden_pago_id')->pluck('id');
            $solicitudesSueltas = DB::table('solicitudes_compra')
                ->whereNotIn('id', DB::table('orden_pago_items')->whereNotNull('solicitud_compra_id')->select('solicitud_compra_id'))
                ->pluck('id');
            $pagoPermitido = DB::table('pagos')->whereIn('id', $pagosSueltos)
                ->whereIn('solicitud_compra_id', $solicitudesSueltas)
                ->where('estado', 'Pendiente de pago')->where('monto', 400)->count();
            $solicitudPermitida = DB::table('solicitudes_compra')->whereIn('id', $solicitudesSueltas)
                ->where('external_modulo_id', '1')->where('precio_acordado', 400)
                ->where('estado', 'pendiente')->count();
            if ($pagosSueltos->count() > 1 || $solicitudesSueltas->count() > 1
                || $pagoPermitido !== $pagosSueltos->count()
                || $solicitudPermitida !== $solicitudesSueltas->count()
                || $pagosSueltos->count() !== $solicitudesSueltas->count()
                || DB::table('comprobantes_pago')->whereIn('pago_id', $pagosSueltos)->exists()
                || DB::table('comisiones')->whereIn('venta_id', $solicitudesSueltas)->exists()
                || DB::table('inscripciones_comerciales')->whereIn('solicitud_compra_id', $solicitudesSueltas)->exists()) {
                throw new RuntimeException('Hay ventas antiguas distintas del dato de prueba autorizado; deben migrarse sin borrarlas.');
            }
            DB::table('comprobantes_pago')->whereIn('pago_id', $pagosSueltos)->delete();
            DB::table('pagos')->whereIn('id', $pagosSueltos)->delete();

            DB::table('comisiones')->whereIn('venta_id', $solicitudesSueltas)->delete();
            DB::table('inscripciones_comerciales')->whereIn('solicitud_compra_id', $solicitudesSueltas)->delete();
            DB::table('solicitudes_compra')->whereIn('id', $solicitudesSueltas)->delete();

            // Toda orden nace de un interes: completar las que no lo tengan (mismo prospecto y modulo).
            DB::statement(<<<'SQL'
                update ordenes_pago o set interes_id = i.id
                from intereses i
                where o.interes_id is null and i.prospecto_id = o.prospecto_id
                  and i.external_modulo_id = (select external_modulo_id from orden_pago_items where orden_pago_id = o.id order by id limit 1)
            SQL);

            // Interacciones y recordatorios sin interes: al primer interes del mismo prospecto.
            foreach (['interacciones', 'recordatorios'] as $tabla) {
                DB::statement(<<<SQL
                    update {$tabla} t set interes_id = (select id from intereses where prospecto_id = t.prospecto_id order by id limit 1)
                    where t.interes_id is null
                SQL);
            }

            foreach (['ordenes_pago', 'interacciones', 'recordatorios'] as $tabla) {
                if (DB::table($tabla)->whereNull('interes_id')->exists()) {
                    throw new RuntimeException("Hay filas en {$tabla} sin interes asociable; revisarlas antes de migrar.");
                }
            }
        });

        // Las lineas de la orden son las solicitudes de compra.
        Schema::table('solicitudes_compra', function (Blueprint $table) {
            $table->foreignId('orden_pago_id')->nullable()->after('id');
        });
        DB::statement(<<<'SQL'
            update solicitudes_compra s set orden_pago_id = i.orden_pago_id
            from orden_pago_items i where i.solicitud_compra_id = s.id
        SQL);
        DB::statement(<<<'SQL'
            insert into solicitudes_compra (orden_pago_id, prospecto_id, external_modulo_id, programa_nombre, modulo_nombre,
                modulo_descripcion, precio_acordado, estado, fecha, created_at, updated_at)
            select i.orden_pago_id, o.prospecto_id, i.external_modulo_id, i.programa_nombre, i.modulo_nombre,
                i.modulo_descripcion, i.precio, 'pendiente', i.created_at, i.created_at, i.updated_at
            from orden_pago_items i join ordenes_pago o on o.id = i.orden_pago_id
            where i.solicitud_compra_id is null
        SQL);
        Schema::table('solicitudes_compra', function (Blueprint $table) {
            $table->unsignedBigInteger('orden_pago_id')->nullable(false)->change();
            $table->foreign('orden_pago_id')->references('id')->on('ordenes_pago')->cascadeOnDelete();
        });
        Schema::drop('orden_pago_items');

        Schema::table('pagos', function (Blueprint $table) {
            $table->dropForeign(['solicitud_compra_id']);
            $table->dropUnique(['solicitud_compra_id']);
            $table->dropColumn('solicitud_compra_id');
            $table->unsignedBigInteger('orden_pago_id')->nullable(false)->change();
        });

        Schema::table('comisiones', function (Blueprint $table) {
            $table->dropForeign(['venta_id']);
            $table->renameColumn('venta_id', 'solicitud_compra_id');
        });
        Schema::table('comisiones', function (Blueprint $table) {
            $table->renameIndex('comisiones_venta_id_unique', 'comisiones_solicitud_compra_id_unique');
            $table->foreign('solicitud_compra_id')->references('id')->on('solicitudes_compra')->restrictOnDelete();
        });

        // Llaves derivables.
        foreach (['ordenes_pago', 'interacciones', 'recordatorios'] as $tabla) {
            Schema::table($tabla, function (Blueprint $table) {
                $table->dropForeign(['interes_id']);
                $table->unsignedBigInteger('interes_id')->nullable(false)->change();
                $table->foreign('interes_id')->references('id')->on('intereses')->restrictOnDelete();
                $table->dropForeign(['prospecto_id']);
                $table->dropColumn('prospecto_id');
            });
        }
        foreach (['solicitudes_compra', 'inscripciones_comerciales'] as $tabla) {
            Schema::table($tabla, function (Blueprint $table) {
                $table->dropForeign(['prospecto_id']);
                $table->dropColumn('prospecto_id');
            });
        }
    }

    public function down(): void
    {
        foreach (['solicitudes_compra', 'inscripciones_comerciales', 'ordenes_pago', 'interacciones', 'recordatorios'] as $tabla) {
            Schema::table($tabla, function (Blueprint $table) {
                $table->foreignId('prospecto_id')->nullable();
            });
        }
        foreach (['ordenes_pago', 'interacciones', 'recordatorios'] as $tabla) {
            DB::statement("update {$tabla} t set prospecto_id = i.prospecto_id from intereses i where i.id = t.interes_id");
        }
        DB::statement('update solicitudes_compra s set prospecto_id = o.prospecto_id from ordenes_pago o where o.id = s.orden_pago_id');
        DB::statement('update inscripciones_comerciales c set prospecto_id = s.prospecto_id from solicitudes_compra s where s.id = c.solicitud_compra_id');
        foreach (['solicitudes_compra', 'inscripciones_comerciales', 'ordenes_pago', 'interacciones', 'recordatorios'] as $tabla) {
            Schema::table($tabla, function (Blueprint $table) {
                $table->unsignedBigInteger('prospecto_id')->nullable(false)->change();
                $table->foreign('prospecto_id')->references('id')->on('prospectos')->restrictOnDelete();
            });
        }
        foreach (['ordenes_pago', 'interacciones', 'recordatorios'] as $tabla) {
            Schema::table($tabla, function (Blueprint $table) {
                $table->dropForeign(['interes_id']);
                $table->unsignedBigInteger('interes_id')->nullable()->change();
                $table->foreign('interes_id')->references('id')->on('intereses')->nullOnDelete();
            });
        }

        Schema::table('comisiones', function (Blueprint $table) {
            $table->dropForeign(['solicitud_compra_id']);
            $table->renameIndex('comisiones_solicitud_compra_id_unique', 'comisiones_venta_id_unique');
            $table->renameColumn('solicitud_compra_id', 'venta_id');
        });
        Schema::table('comisiones', function (Blueprint $table) {
            $table->foreign('venta_id')->references('id')->on('solicitudes_compra')->restrictOnDelete();
        });

        Schema::table('pagos', function (Blueprint $table) {
            $table->unsignedBigInteger('orden_pago_id')->nullable()->change();
            $table->foreignId('solicitud_compra_id')->nullable()->unique()->constrained('solicitudes_compra')->restrictOnDelete();
        });

        Schema::create('orden_pago_items', function (Blueprint $table) {
            $table->id();
            $table->foreignId('orden_pago_id')->constrained('ordenes_pago')->cascadeOnDelete();
            $table->foreignId('solicitud_compra_id')->nullable()->constrained('solicitudes_compra')->nullOnDelete();
            $table->string('external_modulo_id');
            $table->string('programa_nombre');
            $table->string('modulo_nombre');
            $table->text('modulo_descripcion')->nullable();
            $table->decimal('precio', 12, 2);
            $table->timestamps();
        });
        DB::statement(<<<'SQL'
            insert into orden_pago_items (orden_pago_id, solicitud_compra_id, external_modulo_id, programa_nombre,
                modulo_nombre, modulo_descripcion, precio, created_at, updated_at)
            select orden_pago_id, id, external_modulo_id, programa_nombre, modulo_nombre, modulo_descripcion,
                precio_acordado, created_at, updated_at
            from solicitudes_compra
        SQL);
        Schema::table('solicitudes_compra', function (Blueprint $table) {
            $table->dropForeign(['orden_pago_id']);
            $table->dropColumn('orden_pago_id');
        });
    }
};
