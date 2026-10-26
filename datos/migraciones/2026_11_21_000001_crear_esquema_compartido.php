<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/*
 * Esquema compartido P1 (correo) + P2 (web) en db_grupo05sa.public, igual a p1/sql/esquema.sql.
 * Clase 46 del docente: cada tabla con la clave del diseño (natural, correlativa con nombre o compuesta),
 * sin campo `id`, y ninguna tabla sin relación. La tabla de control de migraciones vive en el esquema `laravel`.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('roles', function (Blueprint $t) {
            $t->string('nombre', 40)->primary();
            $t->string('descripcion');
            $t->timestamps(0);
        });

        Schema::create('usuarios', function (Blueprint $t) {
            $t->string('nombre');
            $t->string('apellido');
            $t->string('correo')->primary();
            $t->string('telefono')->nullable();
            $t->string('password');
            $t->string('rol', 40);
            $t->string('estado')->default('activo');
            $t->timestamps(0);
            $t->date('fecha_inicio')->default(DB::raw('CURRENT_DATE'));
            $t->date('fecha_fin');
            $t->foreign('rol', 'usuarios_rol_fk')->references('nombre')->on('roles')->cascadeOnUpdate()->restrictOnDelete();
            $t->index(['rol', 'estado']);
        });

        Schema::create('api_tokens', function (Blueprint $t) {
            $t->string('token_hash', 64)->primary();
            $t->timestamp('ultimo_uso_en', 0)->nullable();
            $t->timestamp('expira_en', 0)->nullable();
            $t->timestamps(0);
            $t->string('usuario_correo');
            $t->foreign('usuario_correo', 'api_tokens_usuario_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->cascadeOnDelete();
        });

        Schema::create('programas', function (Blueprint $t) {
            $t->string('codigo')->primary();
            $t->string('nombre');
        });

        Schema::create('catalogo_cache', function (Blueprint $t) {
            $t->string('codigo')->primary();
            $t->string('anuncio_codigo')->nullable();
            $t->string('programa_codigo');
            $t->string('nombre');
            $t->text('descripcion')->nullable();
            $t->decimal('precio', 12, 2);
            $t->string('estado');
            $t->timestamp('sincronizado_en', 0);
            $t->foreign('programa_codigo', 'catalogo_cache_programa_codigo_fk')->references('codigo')->on('programas')->cascadeOnUpdate()->restrictOnDelete();
        });

        Schema::create('programas_responsables', function (Blueprint $t) {
            $t->string('programa_codigo')->primary();
            $t->timestamps(0);
            $t->string('coordinador_correo');
            $t->foreign('coordinador_correo', 'programas_responsables_coordinador_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->restrictOnDelete();
            $t->foreign('programa_codigo', 'programas_responsables_programa_codigo_fk')->references('codigo')->on('programas')->cascadeOnUpdate()->restrictOnDelete();
        });

        Schema::create('motivos_perdida', function (Blueprint $t) {
            $t->string('nombre', 80)->primary();
            $t->string('categoria', 20);
        });

        Schema::create('prospectos', function (Blueprint $t) {
            $t->string('nombre');
            $t->string('apellido');
            $t->string('documento')->primary();
            $t->string('correo')->unique();
            $t->string('telefono');
            $t->string('estado')->default('Nuevo');
            $t->timestamp('fecha_registro', 0)->useCurrent();
            $t->timestamps(0);
            $t->string('profesion')->nullable();
            $t->string('ubicacion')->nullable();
            $t->string('origen', 20)->default('Web');
        });

        Schema::create('intereses', function (Blueprint $t) {
            $t->bigIncrements('nro_tarjeta');
            $t->timestamp('fecha', 0)->useCurrent();
            $t->timestamps(0);
            $t->string('modulo_codigo');
            $t->string('programa_nombre');
            $t->string('modulo_nombre');
            $t->decimal('precio', 12, 2)->nullable();
            $t->string('anuncio_codigo')->nullable();
            $t->text('modulo_descripcion')->nullable();
            $t->string('estado')->default('Nuevo');
            $t->timestamp('fecha_asignacion', 0)->nullable();
            $t->timestamp('ultima_actividad_en', 0)->nullable();
            $t->timestamp('proximo_contacto', 0)->nullable();
            $t->text('observacion')->nullable();
            $t->string('vendedor_correo')->nullable();
            $t->string('documento');
            $t->string('motivo_perdida', 80)->nullable();
            $t->unique(['documento', 'modulo_codigo']);
            $t->foreign('documento', 'intereses_documento_fk')->references('documento')->on('prospectos')->cascadeOnUpdate()->restrictOnDelete();
            $t->foreign('modulo_codigo', 'intereses_modulo_codigo_fk')->references('codigo')->on('catalogo_cache')->cascadeOnUpdate()->restrictOnDelete();
            $t->foreign('motivo_perdida', 'intereses_motivo_perdida_fk')->references('nombre')->on('motivos_perdida')->cascadeOnUpdate()->restrictOnDelete();
            $t->foreign('vendedor_correo', 'intereses_vendedor_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->nullOnDelete();
        });

        Schema::create('movimientos_interes', function (Blueprint $t) {
            $t->bigIncrements('nro_movimiento');
            $t->unsignedBigInteger('nro_tarjeta');
            $t->string('estado_anterior')->nullable();
            $t->string('estado_nuevo');
            $t->text('detalle')->nullable();
            $t->timestamp('fecha', 0)->useCurrent();
            $t->string('usuario_correo')->nullable();
            $t->index(['nro_tarjeta', 'fecha'], 'movimientos_interes_nro_tarjeta_fecha_idx');
            $t->foreign('nro_tarjeta', 'movimientos_interes_nro_tarjeta_fk')->references('nro_tarjeta')->on('intereses')->restrictOnDelete();
            $t->foreign('usuario_correo', 'movimientos_interes_usuario_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->restrictOnDelete();
        });

        Schema::create('interacciones', function (Blueprint $t) {
            $t->bigIncrements('nro_interaccion');
            $t->string('tipo');
            $t->text('descripcion');
            $t->text('resultado')->nullable();
            $t->timestamp('fecha', 0)->useCurrent();
            $t->timestamps(0);
            $t->unsignedBigInteger('nro_tarjeta');
            $t->string('usuario_correo');
            $t->index(['usuario_correo', 'fecha'], 'interacciones_usuario_fecha_idx');
            $t->foreign('nro_tarjeta', 'interacciones_nro_tarjeta_fk')->references('nro_tarjeta')->on('intereses')->restrictOnDelete();
            $t->foreign('usuario_correo', 'interacciones_usuario_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->restrictOnDelete();
        });

        Schema::create('recordatorios', function (Blueprint $t) {
            $t->bigIncrements('nro_recordatorio');
            $t->timestamp('fecha_programada', 0);
            $t->text('descripcion');
            $t->string('estado')->default('Pendiente');
            $t->timestamps(0);
            $t->unsignedBigInteger('nro_tarjeta');
            $t->timestamp('fecha_realizada', 0)->nullable();
            $t->boolean('notificado')->default(false);
            $t->string('usuario_correo');
            $t->index(['usuario_correo', 'estado', 'fecha_programada'], 'recordatorios_usuario_estado_fecha_idx');
            $t->foreign('nro_tarjeta', 'recordatorios_nro_tarjeta_fk')->references('nro_tarjeta')->on('intereses')->restrictOnDelete();
            $t->foreign('usuario_correo', 'recordatorios_usuario_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->restrictOnDelete();
        });

        Schema::create('descuentos', function (Blueprint $t) {
            $t->string('nombre');
            $t->string('codigo')->primary();
            $t->decimal('porcentaje', 5, 2);
            $t->string('estado')->default('activo');
            $t->timestamps(0);
        });

        Schema::create('ordenes_pago', function (Blueprint $t) {
            $t->bigIncrements('nro_orden');
            $t->unsignedBigInteger('nro_tarjeta');
            $t->decimal('subtotal', 12, 2);
            $t->decimal('descuento_total', 12, 2)->default(0);
            $t->decimal('total', 12, 2);
            $t->timestamp('fecha_generacion', 0)->useCurrent();
            $t->timestamps(0);
            $t->string('vendedor_correo');
            $t->foreign('nro_tarjeta', 'ordenes_pago_nro_tarjeta_fk')->references('nro_tarjeta')->on('intereses')->restrictOnDelete();
            $t->foreign('vendedor_correo', 'ordenes_pago_vendedor_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->restrictOnDelete();
        });

        Schema::create('orden_pago_descuentos', function (Blueprint $t) {
            $t->unsignedBigInteger('nro_orden');
            $t->decimal('porcentaje', 5, 2);
            $t->decimal('monto', 12, 2);
            $t->timestamps(0);
            $t->string('descuento_codigo');
            $t->primary(['nro_orden', 'descuento_codigo']);
            $t->foreign('descuento_codigo', 'orden_pago_descuentos_descuento_codigo_fk')->references('codigo')->on('descuentos')->cascadeOnUpdate()->restrictOnDelete();
            $t->foreign('nro_orden', 'orden_pago_descuentos_nro_orden_fk')->references('nro_orden')->on('ordenes_pago')->cascadeOnDelete();
        });

        Schema::create('solicitudes_compra', function (Blueprint $t) {
            $t->bigIncrements('nro_solicitud');
            $t->decimal('precio_acordado', 12, 2)->nullable();
            $t->timestamp('fecha', 0)->useCurrent();
            $t->timestamps(0);
            $t->string('anuncio_codigo')->nullable();
            $t->string('modulo_codigo');
            $t->string('programa_nombre');
            $t->string('modulo_nombre');
            $t->text('modulo_descripcion')->nullable();
            $t->string('anuncio_titulo')->nullable();
            $t->unsignedBigInteger('nro_orden');
            $t->index(['modulo_codigo', 'fecha'], 'solicitudes_modulo_fecha_idx');
            $t->foreign('modulo_codigo', 'solicitudes_compra_modulo_codigo_fk')->references('codigo')->on('catalogo_cache')->cascadeOnUpdate()->restrictOnDelete();
            $t->foreign('nro_orden', 'solicitudes_compra_nro_orden_fk')->references('nro_orden')->on('ordenes_pago')->cascadeOnDelete();
        });

        Schema::create('pagos', function (Blueprint $t) {
            $t->string('codigo_qr')->unique();
            $t->string('estado')->default('Pendiente de pago');
            $t->timestamp('fecha_validacion', 0)->nullable();
            $t->text('observacion_validacion')->nullable();
            $t->timestamps(0);
            $t->unsignedBigInteger('nro_orden')->primary();
            $t->index('estado', 'pagos_estado_idx');
            $t->foreign('nro_orden', 'pagos_nro_orden_fk')->references('nro_orden')->on('ordenes_pago')->restrictOnDelete();
        });

        Schema::create('comprobantes_pago', function (Blueprint $t) {
            $t->bigIncrements('nro_comprobante');
            $t->text('archivo');
            $t->string('nombre_archivo')->nullable();
            $t->string('mime')->nullable();
            $t->timestamp('fecha_envio', 0)->useCurrent();
            $t->text('observacion')->nullable();
            $t->string('estado_revision')->default('En revision');
            $t->timestamps(0);
            $t->string('remitente')->nullable();
            $t->timestamp('hora_pago', 0)->nullable();
            $t->unsignedBigInteger('nro_orden');
            $t->foreign('nro_orden', 'comprobantes_pago_nro_orden_fk')->references('nro_orden')->on('pagos')->cascadeOnDelete();
        });

        Schema::create('inscripciones_comerciales', function (Blueprint $t) {
            $t->unsignedBigInteger('nro_solicitud')->primary();
            $t->timestamp('fecha_confirmacion', 0)->useCurrent();
            $t->timestamps(0);
            $t->foreign('nro_solicitud', 'inscripciones_comerciales_nro_solicitud_fk')->references('nro_solicitud')->on('solicitudes_compra')->restrictOnDelete();
        });

        Schema::create('comisiones', function (Blueprint $t) {
            $t->unsignedBigInteger('nro_solicitud')->primary();
            $t->decimal('porcentaje', 5, 2)->default(2);
            $t->decimal('monto', 12, 2);
            $t->string('estado')->default('Pendiente');
            $t->timestamps(0);
            $t->timestamp('fecha_pago', 0)->nullable();
            $t->string('vendedor_correo');
            $t->foreign('nro_solicitud', 'comisiones_nro_solicitud_fk')->references('nro_solicitud')->on('solicitudes_compra')->restrictOnDelete();
            $t->foreign('vendedor_correo', 'comisiones_vendedor_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->restrictOnDelete();
        });

        Schema::create('exportaciones', function (Blueprint $t) {
            $t->bigIncrements('nro_exportacion');
            $t->timestamp('fecha_exportacion', 0)->useCurrent();
            $t->string('estado')->default('preparada');
            $t->text('respuesta')->nullable();
            $t->timestamps(0);
            $t->string('usuario_correo')->nullable();
            $t->unsignedBigInteger('nro_solicitud');
            $t->index(['estado', 'fecha_exportacion'], 'exportaciones_estado_fecha_idx');
            $t->foreign('nro_solicitud', 'exportaciones_nro_solicitud_fk')->references('nro_solicitud')->on('inscripciones_comerciales')->restrictOnDelete();
            $t->foreign('usuario_correo', 'exportaciones_usuario_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->nullOnDelete();
        });

        Schema::create('notificaciones', function (Blueprint $t) {
            $t->bigIncrements('nro_notificacion');
            $t->string('destinatario')->nullable();
            $t->string('tipo');
            $t->text('mensaje');
            $t->string('estado')->default('enviada');
            $t->timestamp('fecha_envio', 0)->useCurrent();
            $t->timestamps(0);
            $t->string('usuario_correo')->nullable();
            $t->index(['usuario_correo', 'estado', 'fecha_envio'], 'notificaciones_usuario_estado_fecha_idx');
            $t->foreign('usuario_correo', 'notificaciones_usuario_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->nullOnDelete();
        });

        Schema::create('configuraciones', function (Blueprint $t) {
            $t->string('clave')->primary();
            $t->string('valor');
            $t->timestamps(0);
            $t->string('actualizado_por')->nullable();
            $t->foreign('actualizado_por', 'configuraciones_actualizado_por_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->nullOnDelete();
        });

        // Bitácora de comandos del P1 (correo).
        Schema::create('log_comandos', function (Blueprint $t) {
            $t->bigIncrements('nro_registro');
            $t->string('remitente', 160);
            $t->string('asunto', 300);
            $t->string('resultado', 20);
            $t->text('detalle')->nullable();
            $t->timestamp('fecha', 0)->useCurrent();
            $t->string('rol_registrado', 40)->nullable();
            $t->string('usuario_correo')->nullable();
            $t->foreign('usuario_correo', 'log_comandos_usuario_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->restrictOnDelete();
        });

        $checks = [
            'usuarios' => [self::enLista('usuarios_estado_check', 'estado', ['activo','inactivo']), 'usuarios_vigencia_check CHECK (fecha_fin >= fecha_inicio)'],
            'motivos_perdida' => [self::enLista('motivos_categoria_check', 'categoria', ['Económico','Horario','Incompatibilidad','Contacto','Otro'])],
            'prospectos' => [self::enLista('prospectos_estado_check', 'estado', ['Nuevo','Contactado','Interesado','En proceso','Convertido','Perdido'])],
            'intereses' => [self::enLista('intereses_estado_check', 'estado', ['Nuevo','Contactado','Interesado','Pago enviado','En revision','Convertido','Perdido'])],
            'interacciones' => [self::enLista('interacciones_tipo_check', 'tipo', ['WhatsApp','Llamada','Correo electronico','Reunion','Nota comercial','Orden de pago enviada','Pago informado','Compra validada','Orden finalizada'])],
            'recordatorios' => [self::enLista('recordatorios_estado_check', 'estado', ['Pendiente','Realizada','Atrasada','Cancelado'])],
            'descuentos' => [self::enLista('descuentos_estado_check', 'estado', ['activo','inactivo'])],
            'pagos' => [self::enLista('pagos_estado_check', 'estado', ['Pendiente de pago','En revision','Pago aprobado','Pago rechazado'])],
            'comprobantes_pago' => [self::enLista('comprobantes_pago_estado_revision_check', 'estado_revision', ['En revision','Pago aprobado','Pago rechazado'])],
            'comisiones' => [self::enLista('comisiones_estado_check', 'estado', ['Pendiente','Pagada'])],
            'exportaciones' => [self::enLista('exportaciones_estado_check', 'estado', ['preparada','exportada','recibida','error'])],
            'notificaciones' => [self::enLista('notificaciones_estado_check', 'estado', ['enviada','fallida','leida'])],
        ];
        foreach ($checks as $tabla => $lista) {
            foreach ($lista as $check) {
                DB::statement("ALTER TABLE {$tabla} ADD CONSTRAINT {$check}");
            }
        }

        // Correo único sin distinguir mayúsculas.
        DB::statement('CREATE UNIQUE INDEX usuarios_correo_lower_unique ON usuarios (lower(correo))');
        DB::statement('CREATE UNIQUE INDEX prospectos_correo_lower_unique ON prospectos (lower(correo))');

        // Triggers del embudo: motivo de pérdida y historial de movimientos de cada tarjeta.
        DB::unprepared(<<<'SQL'
CREATE FUNCTION clasificar_perdida() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.estado <> 'Perdido' THEN NEW.motivo_perdida := NULL;
    ELSIF NEW.motivo_perdida IS NULL THEN NEW.motivo_perdida := 'Sin clasificar (web)';
    END IF;
    RETURN NEW;
END $$;

CREATE FUNCTION registrar_movimiento_web() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE anterior text; vendedor_anterior text;
BEGIN
    IF current_setting('crm.canal',true) IS DISTINCT FROM 'correo' THEN
        IF TG_OP='UPDATE' THEN
            anterior := OLD.estado;
            vendedor_anterior := OLD.vendedor_correo;
        END IF;
        IF TG_OP='INSERT' OR NEW.estado IS DISTINCT FROM anterior OR NEW.vendedor_correo IS DISTINCT FROM vendedor_anterior THEN
            INSERT INTO movimientos_interes(nro_tarjeta,usuario_correo,estado_anterior,estado_nuevo,detalle)
            VALUES(NEW.nro_tarjeta, NULLIF(current_setting('crm.usuario_correo',true),''),anterior,NEW.estado,
                'Cambio desde web. Vendedor: ' || COALESCE(vendedor_anterior,'sin asignar') || ' -> ' || COALESCE(NEW.vendedor_correo,'sin asignar'));
        END IF;
    END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER intereses_clasificar BEFORE INSERT OR UPDATE ON intereses FOR EACH ROW EXECUTE FUNCTION clasificar_perdida();
CREATE TRIGGER intereses_historial AFTER INSERT OR UPDATE ON intereses FOR EACH ROW EXECUTE FUNCTION registrar_movimiento_web();
SQL);
    }

    /** CHECK con la misma forma que guarda PostgreSQL para una columna varchar (igual a p1/sql/esquema.sql). */
    public static function enLista(string $nombre, string $columna, array $valores): string
    {
        $lista = implode(', ', array_map(fn ($v) => "('".str_replace("'", "''", $v)."'::character varying)::text", $valores));

        return "{$nombre} CHECK ((({$columna})::text = ANY (ARRAY[{$lista}])))";
    }

    public function down(): void
    {
        DB::unprepared('DROP TRIGGER IF EXISTS intereses_historial ON intereses; DROP TRIGGER IF EXISTS intereses_clasificar ON intereses;'
            .' DROP FUNCTION IF EXISTS registrar_movimiento_web(); DROP FUNCTION IF EXISTS clasificar_perdida();');
        foreach (['log_comandos', 'configuraciones', 'notificaciones', 'exportaciones', 'comisiones', 'inscripciones_comerciales',
            'comprobantes_pago', 'pagos', 'solicitudes_compra', 'orden_pago_descuentos', 'ordenes_pago', 'descuentos',
            'recordatorios', 'interacciones', 'movimientos_interes', 'intereses', 'prospectos', 'motivos_perdida',
            'programas_responsables', 'catalogo_cache', 'programas', 'api_tokens', 'usuarios', 'roles'] as $tabla) {
            Schema::dropIfExists($tabla);
        }
    }
};
