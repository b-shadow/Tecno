<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\ProspectoService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Datos\Modelos\Prospecto;

class ProspectoController extends Controller
{
    public function registrarInteres(Request $request, ProspectoService $service): JsonResponse
    {
        return $service->registrarInteres($request);
    }

    public function index(Request $request, ProspectoService $service): JsonResponse
    {
        return $service->index($request);
    }

    public function store(Request $request, ProspectoService $service): JsonResponse
    {
        return $service->store($request);
    }

    public function update(Request $request, Prospecto $prospecto, ProspectoService $service): JsonResponse
    {
        return $service->update($request, $prospecto);
    }

    public function crearInteres(Request $request, Prospecto $prospecto, ProspectoService $service): JsonResponse
    {
        return $service->crearInteres($request, $prospecto);
    }

    public function importarCSV(Request $request, ProspectoService $service): JsonResponse
    {
        return $service->importarCSV($request);
    }
}
