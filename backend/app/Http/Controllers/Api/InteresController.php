<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Interes;
use App\Services\InteresService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

/** Adaptador HTTP del embudo: valida las peticiones y presenta sus respuestas. */
class InteresController extends Controller
{
    public function index(Request $request, InteresService $service): JsonResponse
    {
        $filtros = $request->only(['buscar', 'estado', 'vendedor', 'sin_asignar']);

        return response()->json($service->listar($request->attributes->get('auth_usuario'), $filtros));
    }

    public function show(Request $request, int $interes, InteresService $service): JsonResponse
    {
        return response()->json($service->detalle($request->attributes->get('auth_usuario'), $interes));
    }

    public function mover(Request $request, int $interes, InteresService $service): JsonResponse
    {
        $datos = $request->validate([
            'estado' => ['required', Rule::in(Interes::ESTADOS)],
            'motivo_perdida' => ['nullable', 'required_if:estado,Perdido', 'exists:motivos_perdida,nombre', Rule::notIn(['Sin clasificar (web)'])],
            'observacion' => ['nullable', 'string', 'max:2000'],
        ], ['motivo_perdida.required_if' => 'Para marcar la tarjeta como Perdido debe elegir el motivo.'],
            ['motivo_perdida' => 'motivo de pérdida', 'observacion' => 'observación']);
        $actualizado = $service->mover($request->attributes->get('auth_usuario'), $interes, $datos);

        return response()->json([
            'mensaje' => "Tarjeta movida a {$datos['estado']}.",
            'interes' => $actualizado,
        ]);
    }

    public function asignar(Request $request, int $interes, InteresService $service): JsonResponse
    {
        $datos = $request->validate([
            'vendedor_correo' => ['required', Rule::exists('usuarios', 'correo')->where('rol', 'vendedor')->where('estado', 'activo')],
        ], [], ['vendedor_correo' => 'vendedor']);
        $actualizado = $service->asignar(
            $request->attributes->get('auth_usuario'),
            $interes,
            $datos['vendedor_correo'],
        );

        return response()->json(['mensaje' => 'Prospecto asignado.', 'interes' => $actualizado]);
    }

    public function distribuir(Request $request, InteresService $service): JsonResponse
    {
        return response()->json($service->distribuir($request->attributes->get('auth_usuario')));
    }
}
