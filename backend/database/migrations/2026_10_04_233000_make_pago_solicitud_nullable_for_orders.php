<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::statement('ALTER TABLE pagos ALTER COLUMN solicitud_compra_id DROP NOT NULL');
    }

    public function down(): void
    {
        DB::statement('DELETE FROM pagos WHERE solicitud_compra_id IS NULL');
        DB::statement('ALTER TABLE pagos ALTER COLUMN solicitud_compra_id SET NOT NULL');
    }
};
