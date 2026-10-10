<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('prospectos', function (Blueprint $table) {
            $table->string('profesion')->nullable()->after('telefono');
            $table->string('ubicacion')->nullable()->after('profesion');
        });
    }

    public function down(): void
    {
        Schema::table('prospectos', function (Blueprint $table) {
            $table->dropColumn(['profesion', 'ubicacion']);
        });
    }
};
