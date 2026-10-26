<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Motivo\MotivoRequest;
use App\Services\MotivoPerdidaService;
use Datos\Modelos\MotivoPerdida;
use Illuminate\Http\JsonResponse;

/** CU5: gestión de los motivos de pérdida y su clasificación por categoría (RF3.3). */
class MotivoController extends Controller
{
    public function __construct(private readonly MotivoPerdidaService $motivos)
    {
    }

    public function index(): JsonResponse
    {
        return response()->json(['motivos' => $this->motivos->listar(), 'categorias' => MotivoPerdida::CATEGORIAS]);
    }

    public function store(MotivoRequest $r): JsonResponse
    {
        return response()->json(['mensaje' => 'Motivo registrado.', 'motivo' => $this->motivos->crear($r->validated())], 201);
    }

    /** Renombrar se propaga a las tarjetas (FK ON UPDATE CASCADE). */
    public function update(MotivoRequest $r, string $motivo): JsonResponse
    {
        $this->motivos->actualizar($motivo, $r->validated());

        return response()->json(['mensaje' => 'Motivo actualizado.']);
    }

    public function destroy(string $motivo): JsonResponse
    {
        $this->motivos->eliminar($motivo);

        return response()->json(['mensaje' => 'Motivo eliminado.']);
    }
}
