<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/*
 * Menú dinámico y matriz de acceso (enunciado 1, 2 y 4; clase 40 del docente).
 * recursos = cada página del sitio, ligada al caso de uso que implementa (el menú sale del diagrama de CU).
 * permisos = rol × recurso con su tipo de acceso: lectura < modificacion < eliminacion (cada nivel incluye al anterior).
 * Un recurso público (catálogo, login) no necesita permiso; igual lleva su contador de visitas.
 */
return new class extends Migration
{
    public const RECURSOS = [
        // codigo, nombre, ruta, icono, orden, caso de uso, público
        ['catalogo', 'Catálogo de programas', '/anuncios', 'GraduationCap', 1, 'CU2', true],
        ['login', 'Iniciar sesión', '/login', 'LogIn', 2, 'CU1', true],
        ['dashboard', 'Dashboard', '/dashboard', 'LayoutDashboard', 10, 'CU8', false],
        ['inicio-vendedor', 'Mi día', '/inicio-vendedor', 'CalendarDays', 11, 'CU7', false],
        ['embudo', 'Embudo de ventas', '/embudo', 'KanbanSquare', 20, 'CU4', false],
        ['prospectos', 'Prospectos', '/prospectos', 'UserRound', 21, 'CU3', false],
        ['interesados', 'Asignación de prospectos', '/interesados', 'Shuffle', 22, 'CU3', false],
        ['agenda', 'Seguimiento y agenda', '/agenda', 'NotebookTabs', 23, 'CU7', false],
        ['motivos', 'Motivos de pérdida', '/motivos-perdida', 'CircleSlash', 24, 'CU5', false],
        ['validacion-pagos', 'Validación de pagos', '/validacion-pagos', 'CreditCard', 30, 'CU6', false],
        ['alumnos', 'Matrículas y SIS', '/alumnos', 'School', 31, 'CU6', false],
        ['gestion-anuncios', 'Oferta académica', '/gestion-anuncios', 'Megaphone', 32, 'CU2', false],
        ['seguimiento', 'Ventas y comisiones', '/seguimiento', 'BadgeDollarSign', 40, 'CU8', false],
        ['reportes', 'Reportes y estadísticas', '/reportes', 'BarChart3', 41, 'CU8', false],
        ['notificaciones', 'Notificaciones', '/notificaciones', 'Mail', 42, 'CU7', false],
        ['usuarios', 'Usuarios', '/usuarios', 'Users', 50, 'CU1', false],
        ['matriz', 'Matriz de acceso', '/matriz-acceso', 'ShieldCheck', 51, 'CU1', false],
        ['bitacora', 'Bitácora de accesos', '/bitacora', 'ScrollText', 52, 'CU1', false],
    ];

    /** Acceso de cada rol de negocio; el administrador tiene eliminación sobre todo salvo "Mi día" del vendedor. */
    public const PERMISOS = [
        'coordinador' => [
            'dashboard' => 'lectura', 'embudo' => 'modificacion', 'prospectos' => 'modificacion', 'interesados' => 'modificacion',
            'agenda' => 'modificacion', 'motivos' => 'modificacion', 'validacion-pagos' => 'modificacion', 'alumnos' => 'modificacion',
            'gestion-anuncios' => 'lectura', 'seguimiento' => 'modificacion', 'reportes' => 'lectura', 'notificaciones' => 'modificacion',
        ],
        'vendedor' => [
            'inicio-vendedor' => 'lectura', 'embudo' => 'modificacion', 'prospectos' => 'modificacion', 'agenda' => 'modificacion',
            'seguimiento' => 'lectura', 'reportes' => 'lectura', 'notificaciones' => 'lectura',
        ],
    ];

    public function up(): void
    {
        Schema::create('recursos', function (Blueprint $t) {
            $t->string('codigo', 40)->primary();
            $t->string('nombre', 80);
            $t->string('ruta', 80)->unique();
            $t->string('icono', 40);
            $t->smallInteger('orden');
            $t->string('caso_uso', 4);
            $t->boolean('publico')->default(false);
            $t->bigInteger('visitas')->default(0);
        });

        Schema::create('permisos', function (Blueprint $t) {
            $t->string('rol', 40);
            $t->string('recurso_codigo', 40);
            $t->string('acceso', 20);
            $t->timestamps(0);
            $t->primary(['rol', 'recurso_codigo']);
            $t->foreign('rol', 'permisos_rol_fk')->references('nombre')->on('roles')->cascadeOnUpdate()->cascadeOnDelete();
            $t->foreign('recurso_codigo', 'permisos_recurso_codigo_fk')->references('codigo')->on('recursos')->cascadeOnUpdate()->cascadeOnDelete();
        });

        DB::statement("ALTER TABLE recursos ADD CONSTRAINT recursos_caso_uso_check CHECK (caso_uso ~ '^CU[1-8]$')");
        DB::statement("ALTER TABLE permisos ADD CONSTRAINT permisos_acceso_check CHECK (((acceso)::text = ANY (ARRAY[('lectura'::character varying)::text, ('modificacion'::character varying)::text, ('eliminacion'::character varying)::text])))");

        foreach (self::RECURSOS as [$codigo, $nombre, $ruta, $icono, $orden, $cu, $publico]) {
            DB::table('recursos')->insert(compact('codigo', 'nombre', 'ruta', 'icono', 'orden', 'publico') + ['caso_uso' => $cu]);
        }

        $ahora = now();
        // Los tres roles de RF1.1 (iguales a p1/sql/referencias.sql); en una base existente ya están.
        DB::table('roles')->insertOrIgnore([
            ['nombre' => 'administrador', 'descripcion' => 'Gestiona usuarios y toda la operacion comercial', 'created_at' => $ahora, 'updated_at' => $ahora],
            ['nombre' => 'coordinador', 'descripcion' => 'Asigna interesados, valida pagos y supervisa vendedores', 'created_at' => $ahora, 'updated_at' => $ahora],
            ['nombre' => 'vendedor', 'descripcion' => 'Da seguimiento a los interesados asignados', 'created_at' => $ahora, 'updated_at' => $ahora],
        ]);
        $permisos = self::PERMISOS;
        foreach (self::RECURSOS as [$codigo, , , , , , $publico]) {
            if (! $publico && $codigo !== 'inicio-vendedor') {
                $permisos['administrador'][$codigo] = 'eliminacion';
            }
        }
        foreach ($permisos as $rol => $lista) {
            foreach ($lista as $recurso => $acceso) {
                DB::table('permisos')->insert(['rol' => $rol, 'recurso_codigo' => $recurso, 'acceso' => $acceso, 'created_at' => $ahora, 'updated_at' => $ahora]);
            }
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('permisos');
        Schema::dropIfExists('recursos');
    }
};
