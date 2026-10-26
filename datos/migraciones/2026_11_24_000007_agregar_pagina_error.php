<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

/*
 * Página de error (ruta inexistente) del diagrama de navegación. Es pública como el login y lleva su
 * contador de visitas en el pie (enunciado 7).
 */
return new class extends Migration
{
    public function up(): void
    {
        DB::table('recursos')->insert([
            'codigo' => 'error', 'nombre' => 'Página no encontrada', 'ruta' => '/error', 'icono' => 'CircleSlash',
            'orden' => 3, 'caso_uso' => 'CU1', 'publico' => true,
        ]);
    }

    public function down(): void
    {
        DB::table('recursos')->where('codigo', 'error')->delete();
    }
};
