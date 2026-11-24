<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Datos\Modelos\MotivoPerdida;
use App\Services\MotivoPerdidaService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

/** CU5: gestión de los motivos de pérdida y su clasificación por categoría (RF3.3). */
class MotivoController extends Controller
{
    public function index(MotivoPerdidaService $service): JsonResponse
    {
        return response()->json([
            'motivos' => $service->listar(),
            'categorias' => MotivoPerdida::CATEGORIAS,
        ]);
    }

    public function store(Request $request, MotivoPerdidaService $service): JsonResponse
    {
        $data = $request->validate([
            'nombre' => ['required', 'string', 'max:80'],
            'categoria' => ['required', Rule::in(MotivoPerdida::CATEGORIAS)],
        ], [], ['nombre' => 'motivo']);

        return response()->json(['mensaje' => 'Motivo registrado.', 'motivo' => $service->crear($data)], 201);
    }

    /** Renombrar se propaga a las tarjetas (FK ON UPDATE CASCADE). */
    public function update(Request $request, string $motivo, MotivoPerdidaService $service): JsonResponse
    {
        $data = $request->validate([
            'nombre' => ['required', 'string', 'max:80'],
            'categoria' => ['required', Rule::in(MotivoPerdida::CATEGORIAS)],
        ], [], ['nombre' => 'motivo']);

        $service->actualizar($motivo, $data);

        return response()->json(['mensaje' => 'Motivo actualizado.']);
    }

    public function destroy(string $motivo, MotivoPerdidaService $service): JsonResponse
    {
        $service->eliminar($motivo);

        return response()->json(['mensaje' => 'Motivo eliminado.']);
    }
}
