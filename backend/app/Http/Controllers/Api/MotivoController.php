<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Interes;
use App\Models\MotivoPerdida;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

/** CU5: gestión de los motivos de pérdida y su clasificación por categoría (RF3.3). */
class MotivoController extends Controller
{
    public function index(): JsonResponse
    {
        $usos = Interes::query()->whereNotNull('motivo_perdida')->groupBy('motivo_perdida')->selectRaw('motivo_perdida, count(*) as total')->pluck('total', 'motivo_perdida');

        return response()->json([
            'motivos' => MotivoPerdida::query()->orderBy('categoria')->orderBy('nombre')->get()
                ->map(fn ($m) => $m->toArray() + ['usos' => (int) ($usos[$m->nombre] ?? 0)]),
            'categorias' => MotivoPerdida::CATEGORIAS,
        ]);
    }

    public function store(Request $request): JsonResponse
    {
        $data = $request->validate([
            'nombre' => ['required', 'string', 'max:80', 'unique:motivos_perdida,nombre'],
            'categoria' => ['required', Rule::in(MotivoPerdida::CATEGORIAS)],
        ], [], ['nombre' => 'motivo']);

        return response()->json(['mensaje' => 'Motivo registrado.', 'motivo' => MotivoPerdida::query()->create($data)], 201);
    }

    /** Renombrar se propaga a las tarjetas (FK ON UPDATE CASCADE). */
    public function update(Request $request, MotivoPerdida $motivo): JsonResponse
    {
        abort_if($motivo->nombre === 'Sin clasificar (web)', 422, 'Este motivo lo usa el sistema y no se puede cambiar.');
        $data = $request->validate([
            'nombre' => ['required', 'string', 'max:80', Rule::unique('motivos_perdida', 'nombre')->ignore($motivo->nombre, 'nombre')],
            'categoria' => ['required', Rule::in(MotivoPerdida::CATEGORIAS)],
        ], [], ['nombre' => 'motivo']);

        MotivoPerdida::query()->whereKey($motivo->nombre)->update($data);

        return response()->json(['mensaje' => 'Motivo actualizado.']);
    }

    public function destroy(MotivoPerdida $motivo): JsonResponse
    {
        abort_if(Interes::query()->where('motivo_perdida', $motivo->nombre)->exists(), 422, 'No se puede eliminar: hay prospectos perdidos con este motivo.');
        abort_if($motivo->nombre === 'Sin clasificar (web)', 422, 'Este motivo lo usa el sistema y no se puede eliminar.');
        $motivo->delete();

        return response()->json(['mensaje' => 'Motivo eliminado.']);
    }
}
