<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/*
 * Módulo de pagos (enunciado 10): métodos de pago registrados por prospecto (tarjeta simulada, QR, transferencia),
 * pago único y plan de pagos en cuotas. Pago único = plan de una cuota.
 * pagos.estado sigue siendo el estado de la cuota 1, la que habilita la matrícula (CU6): así el P1 sigue funcionando
 * igual. Dos triggers lo mantienen: toda orden con pago tiene su cuota 1, y el estado del pago se copia a esa cuota.
 * De una tarjeta solo se guarda marca, últimos 4 dígitos y vencimiento: nunca el número completo ni el CVV.
 */
return new class extends Migration
{
    public const ESTADOS = ['Pendiente de pago', 'En revision', 'Pago aprobado', 'Pago rechazado'];

    public function up(): void
    {
        Schema::create('metodos_pago', function (Blueprint $t) {
            $t->bigIncrements('nro_metodo');
            $t->string('documento');
            $t->string('tipo', 20);
            $t->string('titular');
            $t->string('marca', 20)->nullable();
            $t->string('ultimos_digitos', 4)->nullable();
            $t->string('vencimiento', 5)->nullable();
            $t->string('estado', 10)->default('activo');
            $t->timestamps(0);
            $t->foreign('documento', 'metodos_pago_documento_fk')->references('documento')->on('prospectos')->cascadeOnUpdate()->restrictOnDelete();
        });

        Schema::create('cuotas', function (Blueprint $t) {
            $t->unsignedBigInteger('nro_orden');
            $t->smallInteger('nro_cuota');
            $t->decimal('monto', 12, 2);
            $t->date('fecha_vencimiento');
            $t->string('estado')->default('Pendiente de pago');
            $t->timestamp('fecha_pago', 0)->nullable();
            $t->unsignedBigInteger('nro_metodo')->nullable();
            $t->text('observacion')->nullable();
            $t->timestamps(0);
            $t->primary(['nro_orden', 'nro_cuota']);
            $t->foreign('nro_orden', 'cuotas_nro_orden_fk')->references('nro_orden')->on('ordenes_pago')->cascadeOnDelete();
            $t->foreign('nro_metodo', 'cuotas_nro_metodo_fk')->references('nro_metodo')->on('metodos_pago')->restrictOnDelete();
        });

        Schema::table('comprobantes_pago', function (Blueprint $t) {
            $t->smallInteger('nro_cuota')->nullable();
            $t->foreign(['nro_orden', 'nro_cuota'], 'comprobantes_pago_cuota_fk')->references(['nro_orden', 'nro_cuota'])->on('cuotas')->cascadeOnDelete();
        });

        $estados = implode(', ', array_map(fn ($v) => "('{$v}'::character varying)::text", self::ESTADOS));
        DB::statement("ALTER TABLE metodos_pago ADD CONSTRAINT metodos_pago_tipo_check CHECK (((tipo)::text = ANY (ARRAY[('Tarjeta'::character varying)::text, ('QR'::character varying)::text, ('Transferencia'::character varying)::text])))");
        DB::statement("ALTER TABLE metodos_pago ADD CONSTRAINT metodos_pago_estado_check CHECK (((estado)::text = ANY (ARRAY[('activo'::character varying)::text, ('inactivo'::character varying)::text])))");
        DB::statement("ALTER TABLE metodos_pago ADD CONSTRAINT metodos_pago_tarjeta_check CHECK (tipo <> 'Tarjeta' OR (marca IS NOT NULL AND ultimos_digitos ~ '^[0-9]{4}$' AND vencimiento ~ '^(0[1-9]|1[0-2])/[0-9]{2}$'))");
        DB::statement("ALTER TABLE cuotas ADD CONSTRAINT cuotas_estado_check CHECK (((estado)::text = ANY (ARRAY[{$estados}])))");
        DB::statement('ALTER TABLE cuotas ADD CONSTRAINT cuotas_nro_cuota_check CHECK (nro_cuota BETWEEN 1 AND 24)');
        DB::statement('ALTER TABLE cuotas ADD CONSTRAINT cuotas_monto_check CHECK (monto > 0)');

        // Órdenes que ya existían: una sola cuota por el total, con el estado de su pago.
        DB::statement(<<<'SQL'
INSERT INTO cuotas(nro_orden, nro_cuota, monto, fecha_vencimiento, estado, fecha_pago, created_at, updated_at)
SELECT o.nro_orden, 1, o.total, o.fecha_generacion::date, p.estado, p.fecha_validacion, now(), now()
FROM ordenes_pago o JOIN pagos p ON p.nro_orden = o.nro_orden
WHERE o.total > 0
SQL);
        DB::statement('UPDATE comprobantes_pago SET nro_cuota = 1 WHERE EXISTS (SELECT 1 FROM cuotas c WHERE c.nro_orden = comprobantes_pago.nro_orden AND c.nro_cuota = 1)');

        DB::unprepared(<<<'SQL'
CREATE FUNCTION crear_cuota_unica() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO cuotas(nro_orden, nro_cuota, monto, fecha_vencimiento, estado, created_at, updated_at)
    SELECT o.nro_orden, 1, o.total, CURRENT_DATE, NEW.estado, now(), now()
    FROM ordenes_pago o WHERE o.nro_orden = NEW.nro_orden AND o.total > 0
    ON CONFLICT (nro_orden, nro_cuota) DO NOTHING;
    RETURN NEW;
END $$;

CREATE FUNCTION copiar_estado_cuota_inicial() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    UPDATE cuotas SET estado = NEW.estado,
        fecha_pago = CASE WHEN NEW.estado = 'Pago aprobado' THEN COALESCE(NEW.fecha_validacion, now()) ELSE fecha_pago END,
        updated_at = now()
    WHERE nro_orden = NEW.nro_orden AND nro_cuota = 1 AND estado IS DISTINCT FROM NEW.estado;
    RETURN NEW;
END $$;

CREATE TRIGGER pagos_crear_cuota AFTER INSERT ON pagos FOR EACH ROW EXECUTE FUNCTION crear_cuota_unica();
CREATE TRIGGER pagos_copiar_estado AFTER UPDATE OF estado ON pagos FOR EACH ROW EXECUTE FUNCTION copiar_estado_cuota_inicial();
SQL);
    }

    public function down(): void
    {
        DB::unprepared('DROP TRIGGER IF EXISTS pagos_copiar_estado ON pagos; DROP TRIGGER IF EXISTS pagos_crear_cuota ON pagos;'
            .' DROP FUNCTION IF EXISTS copiar_estado_cuota_inicial(); DROP FUNCTION IF EXISTS crear_cuota_unica();');
        Schema::table('comprobantes_pago', function (Blueprint $t) {
            $t->dropForeign('comprobantes_pago_cuota_fk');
            $t->dropColumn('nro_cuota');
        });
        Schema::dropIfExists('cuotas');
        Schema::dropIfExists('metodos_pago');
    }
};
