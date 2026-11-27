<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/*
 * Fase B: soporte aditivo para Stripe Checkout Sandbox (BOB), gestión de métodos de pago mediante Stripe Setup,
 * anulación controlada de órdenes pendientes y registro idempotente de transacciones y webhooks.
 * Conserva intactos los registros históricos (manuales/SIM-...), las 29 tablas anteriores y los 5 triggers.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::table('prospectos', function (Blueprint $t) {
            $t->string('stripe_cliente', 120)->nullable();
        });
        DB::statement('CREATE UNIQUE INDEX prospectos_stripe_cliente_unique ON prospectos (stripe_cliente) WHERE stripe_cliente IS NOT NULL');

        Schema::table('metodos_pago', function (Blueprint $t) {
            $t->string('proveedor', 20)->default('manual');
            $t->string('stripe_cliente', 120)->nullable();
            $t->string('stripe_metodo', 120)->nullable();
            $t->string('registrado_por')->nullable();
            $t->foreign('registrado_por', 'metodos_pago_registrado_por_fk')
                ->references('correo')->on('usuarios')->cascadeOnUpdate()->nullOnDelete();
        });
        DB::statement("ALTER TABLE metodos_pago ADD CONSTRAINT metodos_pago_proveedor_check CHECK (((proveedor)::text = ANY (ARRAY[('manual'::character varying)::text, ('stripe'::character varying)::text])))");
        DB::statement('CREATE UNIQUE INDEX metodos_pago_stripe_metodo_unique ON metodos_pago (stripe_metodo) WHERE stripe_metodo IS NOT NULL');

        Schema::table('ordenes_pago', function (Blueprint $t) {
            $t->string('estado', 20)->default('Activa');
            $t->text('motivo_anulacion')->nullable();
            $t->timestamp('fecha_anulacion', 0)->nullable();
            $t->string('anulada_por')->nullable();
            $t->foreign('anulada_por', 'ordenes_pago_anulada_por_fk')
                ->references('correo')->on('usuarios')->cascadeOnUpdate()->nullOnDelete();
        });
        DB::statement("ALTER TABLE ordenes_pago ADD CONSTRAINT ordenes_pago_estado_check CHECK (((estado)::text = ANY (ARRAY[('Activa'::character varying)::text, ('Anulada'::character varying)::text])))");

        Schema::table('cuotas', function (Blueprint $t) {
            $t->string('proveedor', 20)->default('manual');
            $t->string('moneda', 10)->default('BOB');
            $t->string('stripe_sesion', 160)->nullable();
            $t->string('stripe_pago_intent', 160)->nullable();
            $t->string('stripe_metodo', 160)->nullable();
            $t->text('stripe_recibo_url')->nullable();
        });
        DB::statement("ALTER TABLE cuotas ADD CONSTRAINT cuotas_proveedor_check CHECK (((proveedor)::text = ANY (ARRAY[('manual'::character varying)::text, ('stripe'::character varying)::text])))");

        Schema::create('transacciones_stripe', function (Blueprint $t) {
            $t->bigIncrements('nro_transaccion');
            $t->string('tipo', 20);
            $t->unsignedBigInteger('nro_orden')->nullable();
            $t->smallInteger('nro_cuota')->nullable();
            $t->string('documento')->nullable();
            $t->string('usuario_correo')->nullable();
            $t->string('stripe_sesion', 160)->unique('transacciones_stripe_sesion_unique');
            $t->string('stripe_pago_intent', 160)->nullable();
            $t->string('stripe_setup_intent', 160)->nullable();
            $t->string('stripe_cliente', 120)->nullable();
            $t->string('stripe_metodo', 120)->nullable();
            $t->string('moneda', 10)->default('bob');
            $t->decimal('monto_esperado', 12, 2)->nullable();
            $t->integer('monto_centavos')->nullable();
            $t->decimal('monto_confirmado', 12, 2)->nullable();
            $t->string('estado_sesion', 40)->default('open');
            $t->string('estado_pago', 40)->default('unpaid');
            $t->string('estado_interno', 35)->default('pendiente');
            $t->boolean('livemode')->default(false);
            $t->string('marca_tarjeta', 30)->nullable();
            $t->string('ultimos_digitos', 4)->nullable();
            $t->text('receipt_url')->nullable();
            $t->text('url_checkout')->nullable();
            $t->string('clave_idempotencia', 120)->nullable();
            $t->text('detalle_error')->nullable();
            $t->timestamp('confirmado_en', 0)->nullable();
            $t->timestamps(0);

            $t->index(['nro_orden', 'nro_cuota', 'estado_interno'], 'transacciones_stripe_cuota_estado_idx');
            $t->foreign('nro_orden', 'transacciones_stripe_orden_fk')
                ->references('nro_orden')->on('ordenes_pago')->restrictOnDelete();
            $t->foreign(['nro_orden', 'nro_cuota'], 'transacciones_stripe_cuota_fk')
                ->references(['nro_orden', 'nro_cuota'])->on('cuotas')->restrictOnDelete();
            $t->foreign('documento', 'transacciones_stripe_documento_fk')
                ->references('documento')->on('prospectos')->cascadeOnUpdate()->restrictOnDelete();
            $t->foreign('usuario_correo', 'transacciones_stripe_usuario_fk')
                ->references('correo')->on('usuarios')->cascadeOnUpdate()->nullOnDelete();
        });
        DB::statement("ALTER TABLE transacciones_stripe ADD CONSTRAINT transacciones_stripe_tipo_check CHECK (((tipo)::text = ANY (ARRAY[('payment'::character varying)::text, ('setup'::character varying)::text])))");
        DB::statement("ALTER TABLE transacciones_stripe ADD CONSTRAINT transacciones_stripe_estado_interno_check CHECK (((estado_interno)::text = ANY (ARRAY[('pendiente'::character varying)::text, ('confirmado'::character varying)::text, ('rechazado'::character varying)::text, ('cancelado'::character varying)::text, ('expirado'::character varying)::text, ('reconciliacion_duplicada'::character varying)::text])))");
        DB::statement('CREATE UNIQUE INDEX transacciones_stripe_pi_unique ON transacciones_stripe (stripe_pago_intent) WHERE stripe_pago_intent IS NOT NULL');
        DB::statement('CREATE UNIQUE INDEX transacciones_stripe_si_unique ON transacciones_stripe (stripe_setup_intent) WHERE stripe_setup_intent IS NOT NULL');

        Schema::create('webhook_eventos_stripe', function (Blueprint $t) {
            $t->string('stripe_evento', 160)->primary();
            $t->string('tipo', 100);
            $t->unsignedBigInteger('nro_transaccion')->nullable();
            $t->string('stripe_sesion', 160)->nullable();
            $t->string('stripe_pago_intent', 160)->nullable();
            $t->boolean('livemode')->default(false);
            $t->string('estado', 30)->default('procesado');
            $t->text('resumen')->nullable();
            $t->timestamp('procesado_en', 0)->useCurrent();
            $t->timestamps(0);

            $t->foreign('nro_transaccion', 'webhook_eventos_stripe_tx_fk')
                ->references('nro_transaccion')->on('transacciones_stripe')->nullOnDelete();
        });
        DB::statement("ALTER TABLE webhook_eventos_stripe ADD CONSTRAINT webhook_eventos_stripe_estado_check CHECK (((estado)::text = ANY (ARRAY[('procesado'::character varying)::text, ('ignorado'::character varying)::text, ('duplicado'::character varying)::text, ('error'::character varying)::text])))");
    }

    public function down(): void
    {
        Schema::dropIfExists('webhook_eventos_stripe');
        Schema::dropIfExists('transacciones_stripe');

        DB::statement('ALTER TABLE cuotas DROP CONSTRAINT IF EXISTS cuotas_proveedor_check');
        Schema::table('cuotas', function (Blueprint $t) {
            $t->dropColumn(['proveedor', 'moneda', 'stripe_sesion', 'stripe_pago_intent', 'stripe_metodo', 'stripe_recibo_url']);
        });

        DB::statement('ALTER TABLE ordenes_pago DROP CONSTRAINT IF EXISTS ordenes_pago_estado_check');
        Schema::table('ordenes_pago', function (Blueprint $t) {
            $t->dropForeign('ordenes_pago_anulada_por_fk');
            $t->dropColumn(['estado', 'motivo_anulacion', 'fecha_anulacion', 'anulada_por']);
        });

        DB::statement('DROP INDEX IF EXISTS metodos_pago_stripe_metodo_unique');
        DB::statement('ALTER TABLE metodos_pago DROP CONSTRAINT IF EXISTS metodos_pago_proveedor_check');
        Schema::table('metodos_pago', function (Blueprint $t) {
            $t->dropForeign('metodos_pago_registrado_por_fk');
            $t->dropColumn(['proveedor', 'stripe_cliente', 'stripe_metodo', 'registrado_por']);
        });

        DB::statement('DROP INDEX IF EXISTS prospectos_stripe_cliente_unique');
        Schema::table('prospectos', function (Blueprint $t) {
            $t->dropColumn('stripe_cliente');
        });
    }
};
