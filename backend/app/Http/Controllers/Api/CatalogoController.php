<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\CatalogoExternoDemo;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class CatalogoController extends Controller
{
    public function __construct(private readonly CatalogoExternoDemo $catalogo)
    {
    }

    public function anuncios(Request $request): JsonResponse
    {
        $this->authorizeCatalogo($request);

        return response()->json([
            'anuncios' => $this->filtrarOfertas($request)->values(),
        ]);
    }

    public function ofertas(Request $request): JsonResponse
    {
        return response()->json([
            'ofertas' => $this->filtrarOfertas($request)
                ->where('estado', 'publicado')
                ->values(),
        ]);
    }

    public function oferta(string $anuncioId): JsonResponse
    {
        $oferta = $this->catalogo->buscarOferta(anuncioId: $anuncioId);

        abort_if(! $oferta || $oferta['estado'] !== 'publicado', 404);

        return response()->json(['oferta' => $oferta]);
    }

    private function filtrarOfertas(Request $request)
    {
        $buscar = mb_strtolower(trim((string) $request->query('buscar', '')));
        $programaId = (string) $request->query('programa_id', '');
        $moduloId = (string) $request->query('modulo_id', '');
        $estado = (string) $request->query('estado', '');

        return $this->catalogo->ofertas()
            ->filter(function (array $oferta) use ($buscar, $programaId, $moduloId, $estado): bool {
                if ($programaId !== '' && $oferta['programa']['id'] !== $programaId) {
                    return false;
                }

                if ($moduloId !== '' && $oferta['external_modulo_id'] !== $moduloId) {
                    return false;
                }

                if ($estado !== '' && $oferta['estado'] !== $estado) {
                    return false;
                }

                if ($buscar === '') {
                    return true;
                }

                $texto = mb_strtolower(implode(' ', [
                    $oferta['titulo'],
                    $oferta['descripcion'],
                    $oferta['programa']['nombre'],
                    $oferta['modulo']['nombre'],
                ]));

                return str_contains($texto, $buscar);
            })
            ->sortByDesc('created_at')
            ->values();
    }

    private function authorizeCatalogo(Request $request): void
    {
        $usuario = $request->attributes->get('auth_usuario');

        abort_if(! in_array($usuario?->rol, ['administrador', 'coordinador'], true), 403, 'No tiene permisos para consultar anuncios.');
    }
}
