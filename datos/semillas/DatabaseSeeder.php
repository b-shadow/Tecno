<?php

namespace Database\Seeders;

use Datos\Modelos\CatalogoCache;
use Datos\Modelos\Interes;
use Datos\Modelos\Usuario;
use App\Services\Conversion;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

/**
 * Solo para una base de desarrollo o de prueba vacía: catálogo de referencia y datos de demostración ficticios.
 * Nunca correr sobre db_grupo05sa del servidor (allí ya están las referencias y los datos reales del P1).
 */
class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        if (app()->isProduction()) {
            throw new \RuntimeException('El seeder de demostración no se corre en producción (db_grupo05sa del servidor).');
        }

        if (! CatalogoCache::query()->exists()) {
            DB::unprepared(file_get_contents(__DIR__.'/referencias.sql'));
        }

        $fin = now()->addYear()->toDateString();
        $usuarios = [
            ['admin@crm-educativo.local', 'Andrea', 'Rojas Salvatierra', 'administrador', 'Admin12345'],
            ['coord@test.local', 'Marcelo', 'Antelo Vaca', 'coordinador', 'Clave12345'],
            ['vendedor.demo@crm-educativo.local', 'Lucía', 'Suárez Peña', 'vendedor', 'Vendedor12345'],
            ['vendedor2@crm-educativo.local', 'Diego', 'Justiniano Roca', 'vendedor', 'Vendedor12345'],
        ];
        foreach ($usuarios as [$correo, $nombre, $apellido, $rol, $clave]) {
            Usuario::query()->updateOrCreate(['correo' => $correo], [
                'nombre' => $nombre, 'apellido' => $apellido, 'telefono' => '7'.random_int(1000000, 9999999),
                'password' => Hash::make($clave), 'rol' => $rol, 'estado' => 'activo', 'fecha_inicio' => now()->subMonths(3)->toDateString(), 'fecha_fin' => $fin,
            ]);
        }
        // RF1.3: el coordinador demo supervisa tres programas.
        foreach (['desarrollo-web', 'ia-aplicada', 'datos-bi'] as $programa) {
            DB::table('programas_responsables')->updateOrInsert(['programa_codigo' => $programa], ['coordinador_correo' => 'coord@test.local', 'created_at' => now(), 'updated_at' => now()]);
        }

        if (Interes::query()->exists()) {
            return;
        }

        $personas = [
            ['Camila', 'Vargas Méndez', 'Facebook', 'Ingeniera comercial'], ['Jorge', 'Quiroga Arce', 'Instagram', 'Contador'],
            ['Valeria', 'Gutiérrez Ribera', 'WhatsApp', 'Diseñadora'], ['Mateo', 'Céspedes Rocha', 'Web', 'Estudiante'],
            ['Sofía', 'Moreno Aguilera', 'Referido', 'Abogada'], ['Rodrigo', 'Paz Terceros', 'TikTok', 'Técnico en redes'],
            ['Daniela', 'Chávez Landívar', 'Feria', 'Administradora'], ['Gabriel', 'Mercado Soliz', 'Facebook', 'Ingeniero civil'],
            ['Fernanda', 'Ortiz Callaú', 'Web', 'Analista de datos'], ['Andrés', 'Montaño Ibáñez', 'Correo', 'Docente'],
            ['Paola', 'Saucedo Durán', 'Instagram', 'Economista'], ['Luis', 'Fernández Melgar', 'WhatsApp', 'Programador'],
            ['Natalia', 'Rivero Antezana', 'Referido', 'Psicóloga'], ['Sebastián', 'Añez Coimbra', 'Web', 'Estudiante'],
            ['Mariana', 'Lijerón Parada', 'Facebook', 'Auditora'], ['Ricardo', 'Hurtado Velasco', 'Otro', 'Bioquímico'],
        ];
        $modulos = CatalogoCache::query()->with('programa')->orderBy('codigo')->get()->values();
        $vendedores = ['vendedor.demo@crm-educativo.local', 'vendedor2@crm-educativo.local'];
        $estados = ['Nuevo', 'Nuevo', 'En Contacto', 'En Contacto', 'Seguimiento', 'Seguimiento', 'Promesa de Pago', 'Promesa de Pago', 'Convertido', 'Convertido', 'Perdido', 'Perdido', 'Nuevo', 'Seguimiento', 'En Contacto', 'Nuevo'];
        $motivos = ['Precio fuera de su presupuesto', 'Horario incompatible con su trabajo'];
        $admin = Usuario::query()->find('admin@crm-educativo.local');

        foreach ($personas as $i => [$nombre, $apellido, $origen, $profesion]) {
            $documento = (string) (6100000 + $i * 7919);
            DB::table('prospectos')->insert([
                'documento' => $documento, 'nombre' => $nombre, 'apellido' => $apellido,
                'correo' => Str::slug($nombre.'.'.explode(' ', $apellido)[0], '.').'@correo-demo.bo', 'telefono' => '7'.(1000000 + $i * 37171),
                'profesion' => $profesion, 'ubicacion' => 'Santa Cruz de la Sierra', 'origen' => $origen, 'estado' => 'Nuevo',
                'fecha_registro' => now()->subDays(20 - $i), 'created_at' => now(), 'updated_at' => now(),
            ]);
            $m = $modulos[($i * 3) % $modulos->count()];
            $vendedor = $i >= 13 ? null : $vendedores[$i % 2];
            $interes = Interes::query()->create([
                'documento' => $documento, 'modulo_codigo' => $m->codigo, 'anuncio_codigo' => $m->anuncio_codigo, 'programa_nombre' => $m->programa->nombre,
                'modulo_nombre' => $m->nombre, 'modulo_descripcion' => $m->descripcion, 'precio' => $m->precio, 'estado' => 'Nuevo',
                'vendedor_correo' => $vendedor, 'fecha_asignacion' => $vendedor ? now()->subDays(15 - $i % 10) : null,
                'fecha' => now()->subDays(20 - $i), 'ultima_actividad_en' => now()->subDays(10 - $i % 9),
            ]);
            $estado = $estados[$i];
            if ($estado === 'Nuevo' || ! $vendedor) {
                continue;
            }

            $interes->interacciones()->create(['usuario_correo' => $vendedor, 'tipo' => 'WhatsApp', 'fecha' => now()->subDays(9 - $i % 8),
                'descripcion' => 'Se envió el PDF del programa por WhatsApp.', 'resultado' => 'Pidió detalles de horarios']);
            $interes->recordatorios()->create(['usuario_correo' => $vendedor, 'estado' => 'Pendiente', 'descripcion' => 'Llamar para confirmar interés',
                'fecha_programada' => now()->addDays($i % 4)->setTime(10 + $i % 6, 0)]);

            if (in_array($estado, ['Promesa de Pago', 'Convertido'], true)) {
                $orden = DB::table('ordenes_pago')->insertGetId(['nro_tarjeta' => $interes->nro_tarjeta, 'vendedor_correo' => $vendedor,
                    'subtotal' => $m->precio, 'descuento_total' => 0, 'total' => $m->precio, 'fecha_generacion' => now()->subDays(5), 'created_at' => now(), 'updated_at' => now()], 'nro_orden');
                DB::table('solicitudes_compra')->insert(['nro_orden' => $orden, 'modulo_codigo' => $m->codigo, 'anuncio_codigo' => $m->anuncio_codigo,
                    'programa_nombre' => $m->programa->nombre, 'modulo_nombre' => $m->nombre, 'modulo_descripcion' => $m->descripcion, 'precio_acordado' => $m->precio,
                    'fecha' => now()->subDays(5), 'created_at' => now(), 'updated_at' => now()]);
                $cuotas = $i % 2 ? 3 : 1;
                $base = floor($m->precio / $cuotas * 100) / 100;
                for ($c = 1; $c <= $cuotas; $c++) {
                    DB::table('cuotas')->insert(['nro_orden' => $orden, 'nro_cuota' => $c, 'monto' => $c === $cuotas ? round($m->precio - $base * ($cuotas - 1), 2) : $base,
                        'fecha_vencimiento' => now()->addMonths($c - 1)->toDateString(), 'estado' => 'Pendiente de pago', 'created_at' => now(), 'updated_at' => now()]);
                }
                DB::table('pagos')->insert(['nro_orden' => $orden, 'codigo_qr' => 'CRM-QR-ORD-'.$orden.'-DEMO', 'estado' => 'Pendiente de pago', 'created_at' => now(), 'updated_at' => now()]);
                $interes->update(['estado' => 'Promesa de Pago']);

                if ($estado === 'Convertido') {
                    DB::table('pagos')->where('nro_orden', $orden)->update(['estado' => 'Pago aprobado', 'fecha_validacion' => now()->subDays(2)]);
                    Conversion::procesar($interes->fresh(), $admin);
                }
                continue;
            }

            $interes->update(['estado' => $estado, 'motivo_perdida' => $estado === 'Perdido' ? $motivos[$i % 2] : null]);
        }

        // Unas visitas e intentos de acceso para que la bitácora y el dashboard tengan datos.
        foreach (['catalogo' => 42, 'login' => 18, 'dashboard' => 25, 'embudo' => 31, 'agenda' => 22, 'reportes' => 9] as $recurso => $veces) {
            for ($n = 0; $n < $veces; $n++) {
                DB::table('bitacora')->insert(['evento' => 'visita', 'recurso_codigo' => $recurso, 'ip' => '192.168.1.'.(10 + $n % 30), 'fecha' => now()->subDays($n % 14)]);
            }
        }
        for ($n = 0; $n < 14; $n++) {
            DB::table('bitacora')->insert(['evento' => 'login_exitoso', 'usuario_correo' => $vendedores[$n % 2], 'recurso_codigo' => 'login', 'ip' => '192.168.1.20', 'fecha' => now()->subDays($n)]);
            if ($n % 3 === 0) {
                DB::table('bitacora')->insert(['evento' => 'login_fallido', 'correo_intentado' => 'desconocido@correo.bo', 'recurso_codigo' => 'login', 'ip' => '181.115.20.'.$n, 'fecha' => now()->subDays($n)]);
            }
        }
    }
}
