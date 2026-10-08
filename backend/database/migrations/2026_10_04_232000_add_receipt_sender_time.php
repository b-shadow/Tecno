<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('comprobantes_pago', function (Blueprint $table) {
            $table->string('remitente')->nullable()->after('mime');
            $table->timestamp('hora_pago')->nullable()->after('remitente');
        });
    }

    public function down(): void
    {
        Schema::table('comprobantes_pago', function (Blueprint $table) {
            $table->dropColumn(['remitente', 'hora_pago']);
        });
    }
};
