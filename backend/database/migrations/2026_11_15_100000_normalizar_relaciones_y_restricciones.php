<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/**
 * Revision del modelo de datos:
 * - quita las tablas del chat retirado y la columna usuarios.prospecto_id (rol "prospecto" eliminado);
 * - el vendedor se asigna por interes: se quita prospectos.vendedor_id (dos fuentes de verdad);
 * - tabla roles referenciada por usuarios.rol y configuraciones.actualizado_por (quien cambio el parametro);
 * - el historial comercial y financiero no se borra en cascada (ON DELETE RESTRICT);
 * - restricciones CHECK para los estados y tipos que hoy eran texto libre.
 */
return new class extends Migration
{
    private const CHECKS = [
        'usuarios' => ['estado' => ['activo', 'inactivo']],
        'prospectos' => ['estado' => ['Nuevo', 'Contactado', 'Interesado', 'En proceso', 'Convertido', 'Perdido']],
        'intereses' => ['estado' => ['Nuevo', 'Contactado', 'Interesado', 'Pago enviado', 'En revision', 'Convertido', 'Perdido']],
        'interacciones' => ['tipo' => ['WhatsApp', 'Llamada', 'Correo electronico', 'Reunion', 'Nota comercial', 'Orden de pago enviada', 'Pago informado', 'Compra validada', 'Orden finalizada']],
        'recordatorios' => ['estado' => ['Pendiente', 'Realizada', 'Atrasada', 'Cancelado']],
        'solicitudes_compra' => ['estado' => ['pendiente', 'confirmada']],
        'ordenes_pago' => ['estado' => ['Pendiente de pago', 'En revision', 'Pago aprobado', 'Pago rechazado']],
        'pagos' => ['estado' => ['Pendiente de pago', 'En revision', 'Pago aprobado', 'Pago rechazado']],
        'comprobantes_pago' => ['estado_revision' => ['En revision', 'Pago aprobado', 'Pago rechazado']],
        'inscripciones_comerciales' => ['estado' => ['Confirmada']],
        'comisiones' => ['estado' => ['Pendiente', 'Pagada']],
        'descuentos' => ['estado' => ['activo', 'inactivo']],
        'notificaciones' => ['estado' => ['enviada', 'fallida', 'leida']],
        'exportaciones' => ['estado' => ['preparada', 'exportada', 'recibida', 'error']],
    ];

    /** [tabla, columna, tabla referida] que pasan de CASCADE a RESTRICT. */
    private const RESTRICT = [
        ['comisiones', 'vendedor_id', 'usuarios'],
        ['interacciones', 'usuario_id', 'usuarios'],
        ['ordenes_pago', 'vendedor_id', 'usuarios'],
        ['recordatorios', 'usuario_id', 'usuarios'],
        ['intereses', 'prospecto_id', 'prospectos'],
        ['interacciones', 'prospecto_id', 'prospectos'],
        ['recordatorios', 'prospecto_id', 'prospectos'],
        ['ordenes_pago', 'prospecto_id', 'prospectos'],
        ['solicitudes_compra', 'prospecto_id', 'prospectos'],
        ['inscripciones_comerciales', 'prospecto_id', 'prospectos'],
        ['comisiones', 'venta_id', 'solicitudes_compra'],
        ['inscripciones_comerciales', 'solicitud_compra_id', 'solicitudes_compra'],
        ['pagos', 'solicitud_compra_id', 'solicitudes_compra'],
        ['pagos', 'orden_pago_id', 'ordenes_pago'],
        ['orden_pago_descuentos', 'descuento_id', 'descuentos'],
    ];

    public function up(): void
    {
        // Chat comercial retirado del sistema.
        Schema::table('ordenes_pago', function (Blueprint $table) {
            $table->dropForeign(['chat_conversacion_id']);
            $table->dropColumn('chat_conversacion_id');
        });
        Schema::dropIfExists('chat_mensajes');
        Schema::dropIfExists('chat_conversaciones');

        // Resto del rol "prospecto" (relacion circular usuarios <-> prospectos).
        Schema::table('usuarios', function (Blueprint $table) {
            $table->dropForeign(['prospecto_id']);
            $table->dropUnique(['prospecto_id']);
            $table->dropColumn('prospecto_id');
        });

        // La asignacion vive en intereses.vendedor_id.
        Schema::table('prospectos', function (Blueprint $table) {
            $table->dropForeign(['vendedor_id']);
            $table->dropColumn('vendedor_id');
        });

        // Roles como entidad: usuarios.rol referencia roles.nombre.
        Schema::create('roles', function (Blueprint $table) {
            $table->string('nombre', 40)->primary();
            $table->string('descripcion');
            $table->timestamps();
        });
        DB::table('roles')->insert([
            ['nombre' => 'administrador', 'descripcion' => 'Gestiona usuarios y toda la operacion comercial', 'created_at' => now(), 'updated_at' => now()],
            ['nombre' => 'coordinador', 'descripcion' => 'Asigna interesados, valida pagos y supervisa vendedores', 'created_at' => now(), 'updated_at' => now()],
            ['nombre' => 'vendedor', 'descripcion' => 'Da seguimiento a los interesados asignados', 'created_at' => now(), 'updated_at' => now()],
        ]);
        Schema::table('usuarios', function (Blueprint $table) {
            $table->string('rol', 40)->change();
            $table->foreign('rol')->references('nombre')->on('roles')->cascadeOnUpdate()->restrictOnDelete();
        });

        Schema::table('configuraciones', function (Blueprint $table) {
            $table->foreignId('actualizado_por')->nullable()->after('valor')->constrained('usuarios')->nullOnDelete();
        });

        foreach (self::RESTRICT as [$tabla, $columna, $referida]) {
            Schema::table($tabla, function (Blueprint $table) use ($columna, $referida) {
                $table->dropForeign([$columna]);
                $table->foreign($columna)->references('id')->on($referida)->restrictOnDelete();
            });
        }

        Schema::table('comisiones', function (Blueprint $table) {
            $table->string('estado')->default('Pendiente')->change();
        });

        foreach (self::CHECKS as $tabla => $columnas) {
            foreach ($columnas as $columna => $valores) {
                $lista = implode(', ', array_map(fn (string $valor) => DB::getPdo()->quote($valor), $valores));
                DB::statement("alter table {$tabla} add constraint {$tabla}_{$columna}_check check ({$columna} in ({$lista}))");
            }
        }
    }

    public function down(): void
    {
        foreach (self::CHECKS as $tabla => $columnas) {
            foreach (array_keys($columnas) as $columna) {
                DB::statement("alter table {$tabla} drop constraint if exists {$tabla}_{$columna}_check");
            }
        }

        Schema::table('comisiones', function (Blueprint $table) {
            $table->string('estado')->default('Generada')->change();
        });

        foreach (self::RESTRICT as [$tabla, $columna, $referida]) {
            Schema::table($tabla, function (Blueprint $table) use ($columna, $referida) {
                $table->dropForeign([$columna]);
                $table->foreign($columna)->references('id')->on($referida)->cascadeOnDelete();
            });
        }

        Schema::table('configuraciones', function (Blueprint $table) {
            $table->dropConstrainedForeignId('actualizado_por');
        });

        Schema::table('usuarios', function (Blueprint $table) {
            $table->dropForeign(['rol']);
        });
        Schema::dropIfExists('roles');

        Schema::table('prospectos', function (Blueprint $table) {
            $table->foreignId('vendedor_id')->nullable()->constrained('usuarios')->nullOnDelete();
        });

        Schema::table('usuarios', function (Blueprint $table) {
            $table->foreignId('prospecto_id')->nullable()->unique()->constrained('prospectos')->nullOnDelete();
        });

        Schema::create('chat_conversaciones', function (Blueprint $table) {
            $table->id();
            $table->foreignId('prospecto_id')->constrained('prospectos')->cascadeOnDelete();
            $table->foreignId('vendedor_id')->nullable()->constrained('usuarios')->nullOnDelete();
            $table->string('external_modulo_id');
            $table->string('external_anuncio_id')->nullable();
            $table->string('estado')->default('abierta');
            $table->timestamps();
        });
        Schema::create('chat_mensajes', function (Blueprint $table) {
            $table->id();
            $table->foreignId('chat_conversacion_id')->constrained('chat_conversaciones')->cascadeOnDelete();
            $table->foreignId('usuario_id')->nullable()->constrained('usuarios')->nullOnDelete();
            $table->text('mensaje');
            $table->timestamps();
        });
        Schema::table('ordenes_pago', function (Blueprint $table) {
            $table->foreignId('chat_conversacion_id')->nullable()->constrained('chat_conversaciones')->nullOnDelete();
        });
    }
};
