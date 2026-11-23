<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\SitioService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

/** Adaptador HTTP de búsqueda global, contador de visitas, fotos y salud. */
class SitioController extends Controller
{
    public function visita(Request $request, SitioService $service): JsonResponse
    {
        $datos = $request->validate(['ruta' => ['required', 'string', 'max:80']]);

        return response()->json(['visitas' => $service->visita($request, $datos['ruta'])]);
    }

    public function buscar(Request $request, SitioService $service): JsonResponse
    {
        return response()->json(['resultados' => $service->buscar($request, (string) $request->query('q', ''))]);
    }

    public function foto(string $archivo, SitioService $service): BinaryFileResponse
    {
        return response()->file($service->rutaFoto($archivo), ['Cache-Control' => 'public, max-age=86400']);
    }

    public function salud(SitioService $service): JsonResponse
    {
        return response()->json($service->salud());
    }
}
