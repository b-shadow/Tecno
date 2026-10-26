<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Sitio\VisitaRequest;
use App\Services\SitioService;
use Illuminate\Http\JsonResponse;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

/** Contador de visitas (enunciado 7), búsqueda global (enunciado 9), fotos de usuario y salud del sistema. */
class SitioController extends Controller
{
    public function __construct(private readonly SitioService $sitio)
    {
    }

    public function visita(VisitaRequest $r): JsonResponse
    {
        $visitas = $this->sitio->visita($r->bearerToken(), $r->validated('ruta'), (string) $r->ip(), $r->navegador());

        return response()->json(['visitas' => $visitas]);
    }

    public function buscar(ConsultaRequest $r): JsonResponse
    {
        return response()->json(['resultados' => $this->sitio->buscar($r->bearerToken(), (string) $r->query('q', ''))]);
    }

    public function foto(string $archivo): BinaryFileResponse
    {
        return response()->file($this->sitio->rutaFoto($archivo), ['Cache-Control' => 'public, max-age=86400']);
    }

    public function salud(): JsonResponse
    {
        return response()->json($this->sitio->salud());
    }
}
