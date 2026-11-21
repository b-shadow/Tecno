<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/*
 * Bitácora de auditoría del sitio web (enunciado 4 y 7): inicios de sesión exitosos y fallidos, cierres,
 * accesos denegados y visitas a cada página, con la IP. Un trigger suma la visita al contador persistente
 * de la página (recursos.visitas), que se muestra en el pie de cada vista.
 * La bitácora de comandos del P1 (correo) sigue en log_comandos.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('bitacora', function (Blueprint $t) {
            $t->bigIncrements('nro_registro');
            $t->string('evento', 20);
            $t->string('usuario_correo')->nullable();
            $t->string('correo_intentado')->nullable();
            $t->string('recurso_codigo', 40)->nullable();
            $t->string('ip', 45);
            $t->string('navegador')->nullable();
            $t->timestamp('fecha', 0)->useCurrent();
            $t->index(['evento', 'fecha'], 'bitacora_evento_fecha_idx');
            $t->index(['recurso_codigo', 'fecha'], 'bitacora_recurso_fecha_idx');
            $t->foreign('usuario_correo', 'bitacora_usuario_correo_fk')->references('correo')->on('usuarios')->cascadeOnUpdate()->nullOnDelete();
            $t->foreign('recurso_codigo', 'bitacora_recurso_codigo_fk')->references('codigo')->on('recursos')->cascadeOnUpdate()->restrictOnDelete();
        });

        DB::statement("ALTER TABLE bitacora ADD CONSTRAINT bitacora_evento_check CHECK (((evento)::text = ANY (ARRAY[('login_exitoso'::character varying)::text, ('login_fallido'::character varying)::text, ('logout'::character varying)::text, ('visita'::character varying)::text, ('acceso_denegado'::character varying)::text])))");

        DB::unprepared(<<<'SQL'
CREATE FUNCTION contar_visita() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    UPDATE recursos SET visitas = visitas + 1 WHERE codigo = NEW.recurso_codigo;
    RETURN NEW;
END $$;

CREATE TRIGGER bitacora_contar_visita AFTER INSERT ON bitacora
    FOR EACH ROW WHEN (NEW.evento = 'visita' AND NEW.recurso_codigo IS NOT NULL)
    EXECUTE FUNCTION contar_visita();
SQL);
    }

    public function down(): void
    {
        DB::unprepared('DROP TRIGGER IF EXISTS bitacora_contar_visita ON bitacora; DROP FUNCTION IF EXISTS contar_visita();');
        Schema::dropIfExists('bitacora');
    }
};
