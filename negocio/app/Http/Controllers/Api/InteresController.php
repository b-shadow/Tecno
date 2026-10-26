<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Interes\AsignarInteresRequest;
use App\Http\Requests\Interes\MoverInteresRequest;
use App\Services\InteresService;
use Illuminate\Http\JsonResponse;

/** CU3 (asignación y Round-Robin), CU4 (embudo Kanban) y CU5 (pérdida con motivo): delega en InteresService. */
class InteresController extends Controller
{
    public function __construct(private readonly InteresService $intereses)
    {
    }

    public function index(ConsultaRequest $r): JsonResponse
    {
        return response()->json($this->intereses->listar($r->usuario(), $r->only(['buscar', 'estado', 'vendedor', 'sin_asignar'])));
    }

    public function show(ConsultaRequest $r, int $interes): JsonResponse
    {
        return response()->json($this->intereses->detalle($r->usuario(), $interes));
    }

    public function mover(MoverInteresRequest $r, int $interes): JsonResponse
    {
        $actualizado = $this->intereses->mover($r->usuario(), $interes, $r->validated());

        return response()->json(['mensaje' => "Tarjeta movida a {$r->validated('estado')}.", 'interes' => $actualizado]);
    }

    public function asignar(AsignarInteresRequest $r, int $interes): JsonResponse
    {
        $actualizado = $this->intereses->asignar($r->usuario(), $interes, $r->validated('vendedor_correo'));

        return response()->json(['mensaje' => 'Prospecto asignado.', 'interes' => $actualizado]);
    }

    public function distribuir(ConsultaRequest $r): JsonResponse
    {
        return response()->json($this->intereses->distribuir($r->usuario()));
    }
}
