<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\DB;

class SystemController extends Controller
{
    public function health(): JsonResponse
    {
        $database = 'disconnected';

        try {
            DB::connection()->select('select 1');
            $database = 'connected';
        } catch (\Throwable) {
            $database = 'disconnected';
        }

        return response()->json([
            'system' => 'CRM Comercial Educativo',
            'status' => 'ok',
            'database' => $database,
            'architecture' => 'MVC API + frontend Vue',
            'domains' => [
                'Seguridad y acceso',
                'Gestion academica comercial',
                'Captacion, compras y pagos',
                'Ventas, pagos y comisiones',
                'Reportes, comunicacion e integracion',
            ],
        ]);
    }
}
