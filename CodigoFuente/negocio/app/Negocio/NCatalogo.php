<?php

namespace App\Negocio;

use App\Http\Requests\ConsultaRequest;
use Datos\DCatalogo;
use Datos\Modelos\CatalogoCache;
use Datos\Modelos\Programa;
use Illuminate\Http\JsonResponse;

/** Capa de negocio — CU2 y RNF2: oferta académica (cliente de la API del catálogo del Grupo 06). */
class NCatalogo
{
    public function __construct(
        private readonly DCatalogo $catalogo,
        private readonly NCatalogoExterno $externo,
    ) {
    }

    public function programas(ConsultaRequest $r): JsonResponse
    {
        $ofertas = $this->externo->ofertas();
        $media = $ofertas->keyBy('external_modulo_id');
        $programasExternos = $ofertas->pluck('programa', 'programa.id');
        $termino = mb_strtolower(trim((string) $r->query('buscar', '')));

        $programas = $this->catalogo->programasAbiertos()
            ->map(function (Programa $programa) use ($media, $programasExternos, $termino) {
                $modulos = $programa->modulos
                    ->filter(fn (CatalogoCache $modulo) => $termino === '' || str_contains(
                        mb_strtolower($programa->nombre.' '.$modulo->nombre.' '.$modulo->descripcion),
                        $termino,
                    ))
                    ->map(fn (CatalogoCache $modulo) => [
                        'codigo' => $modulo->codigo,
                        'anuncio_codigo' => $modulo->anuncio_codigo,
                        'nombre' => $modulo->nombre,
                        'descripcion' => $modulo->descripcion,
                        'precio' => (float) $modulo->precio,
                        'duracion' => $media[$modulo->codigo]['modulo']['duracion'] ?? null,
                        'imagen' => $media[$modulo->codigo]['imagen'] ?? null,
                    ])->values();

                return [
                    'codigo' => $programa->codigo,
                    'nombre' => $programa->nombre,
                    'descripcion' => $programasExternos[$programa->codigo]['descripcion'] ?? null,
                    'area' => $programasExternos[$programa->codigo]['area'] ?? 'Otros programas',
                    'imagen' => $programasExternos[$programa->codigo]['imagen'] ?? null,
                    'precio_total' => round($modulos->sum('precio'), 2),
                    'modulos' => $modulos,
                ];
            })
            ->filter(fn ($programa) => $programa['modulos']->isNotEmpty())
            ->values();

        return response()->json(['programas' => $programas]);
    }

    public function sincronizar(): JsonResponse
    {
        $ofertas = $this->externo->ofertas();
        $this->catalogo->sincronizar($ofertas);

        return response()->json(['mensaje' => "Catálogo sincronizado: {$ofertas->count()} módulos."]);
    }
}
