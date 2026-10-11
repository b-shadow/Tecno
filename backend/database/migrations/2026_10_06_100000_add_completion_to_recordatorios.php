<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('recordatorios', function (Blueprint $table) {
            if (! Schema::hasColumn('recordatorios', 'fecha_realizada')) {
                $table->timestamp('fecha_realizada')->nullable()->after('fecha_programada');
            }
        });
    }

    public function down(): void
    {
        Schema::table('recordatorios', function (Blueprint $table) {
            if (Schema::hasColumn('recordatorios', 'fecha_realizada')) {
                $table->dropColumn('fecha_realizada');
            }
        });
    }
};
