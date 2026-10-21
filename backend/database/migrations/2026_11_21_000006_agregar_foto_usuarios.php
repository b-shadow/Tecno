<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/*
 * CU1: foto del usuario. Clase 40 del docente: el archivo se guarda con un nombre legible y ligado al dato
 * (apellido_nombre.jpg) y ese nombre queda en la BD.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::table('usuarios', fn (Blueprint $t) => $t->string('foto')->nullable());
    }

    public function down(): void
    {
        Schema::table('usuarios', fn (Blueprint $t) => $t->dropColumn('foto'));
    }
};
