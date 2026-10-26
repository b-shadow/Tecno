<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ConsultaRequest;
use App\Services\CatalogoService;
use Illuminate\Http\JsonResponse;

/** CU2 y RNF2: catálogo de programas y módulos (cliente de la API del catálogo del Grupo 06). */
class CatalogoController extends Controller
{
    public function __construct(private readonly CatalogoService $catalogo)
    {
    }

    public function programas(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['programas' => $this->catalogo->programas(trim((string) $r->query('buscar', '')))]);
    }

    public function sincronizar(): JsonResponse
    {
        return response()->json(['mensaje' => "Catálogo sincronizado: {$this->catalogo->sincronizar()} módulos."]);
    }
}
