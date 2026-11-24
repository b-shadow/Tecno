<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Prospecto\CrearInteresRequest;
use App\Http\Requests\Prospecto\ImportarCsvRequest;
use App\Http\Requests\Prospecto\RegistrarInteresRequest;
use App\Http\Requests\Prospecto\StoreProspectoRequest;
use App\Http\Requests\Prospecto\UpdateProspectoRequest;
use App\Services\ProspectoService;
use Datos\Modelos\Prospecto;
use Illuminate\Http\JsonResponse;

/** CU2 (registro público de interés) y CU3 (prospectos: alta, edición, CSV e intereses). */
class ProspectoController extends Controller
{
    public function __construct(private readonly ProspectoService $prospectos)
    {
    }

    public function registrarInteres(RegistrarInteresRequest $r): JsonResponse
    {
        $nuevo = $this->prospectos->registrarInteres($r->validated());

        return response()->json([
            'mensaje' => 'Interés registrado correctamente.',
            'detalle' => 'Un asesor se comunicará con usted por WhatsApp.',
            'nuevo_prospecto' => $nuevo,
        ], $nuevo ? 201 : 200);
    }

    public function index(ConsultaRequest $r): JsonResponse
    {
        $prospectos = $this->prospectos->listar($r->usuario(), (string) $r->query('buscar', ''), $r->query('origen'));

        return response()->json(['prospectos' => $prospectos, 'origenes' => ProspectoService::ORIGENES]);
    }

    public function store(StoreProspectoRequest $r): JsonResponse
    {
        $prospecto = $this->prospectos->registrar($r->usuario(), $r->validated());

        return response()->json(['mensaje' => 'Prospecto registrado correctamente.', 'prospecto' => $prospecto], 201);
    }

    public function update(UpdateProspectoRequest $r, Prospecto $prospecto): JsonResponse
    {
        $prospecto = $this->prospectos->actualizar($r->usuario(), $prospecto, $r->validated());

        return response()->json(['mensaje' => 'Datos del prospecto actualizados.', 'prospecto' => $prospecto]);
    }

    public function crearInteres(CrearInteresRequest $r, Prospecto $prospecto): JsonResponse
    {
        $intereses = $this->prospectos->crearInteres($r->usuario(), $prospecto, $r->validated());

        return response()->json(['mensaje' => 'Interés registrado.', 'intereses' => $intereses], 201);
    }

    public function importarCSV(ImportarCsvRequest $r): JsonResponse
    {
        $creados = $this->prospectos->importarCSV($r->usuario(), $r->validated('csv'));

        return response()->json(['mensaje' => "{$creados} prospecto(s) cargados.", 'creados' => $creados, 'errores' => []]);
    }
}
