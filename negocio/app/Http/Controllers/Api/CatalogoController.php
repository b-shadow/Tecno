<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\CatalogoService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/** Adaptador HTTP del CU2 y RNF2 para el catálogo de ofertas. */
class CatalogoController extends Controller
{
    public function programas(Request $request, CatalogoService $service): JsonResponse
    {
        $buscar = trim((string) $request->query('buscar', ''));

        return response()->json(['programas' => $service->programas($buscar)]);
    }

    public function sincronizar(CatalogoService $service): JsonResponse
    {
        $cantidad = $service->sincronizar();

        return response()->json(['mensaje' => "Catálogo sincronizado: {$cantidad} módulos."]);
    }
}
