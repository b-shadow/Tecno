<?php

namespace App\Services;

use App\Models\CatalogoCache;
use App\Models\Programa;
use App\Repositories\CatalogoRepository;
use Illuminate\Support\Collection;

/** Reglas y composición de la oferta académica consumida por el CRM. */
class CatalogoService
{
    public function __construct(
        private readonly CatalogoRepository $catalogo,
        private readonly CatalogoExternoDemo $externo,
    ) {
    }

    public function programas(string $buscar = ''): Collection
    {
        $ofertas = $this->externo->ofertas();
        $media = $ofertas->keyBy('external_modulo_id');
        $programasExternos = $ofertas->pluck('programa', 'programa.id');
        $termino = mb_strtolower($buscar);

        return $this->catalogo->programasAbiertos()
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
    }

    public function sincronizar(): int
    {
        $ofertas = $this->externo->ofertas();
        $this->catalogo->sincronizar($ofertas);

        return $ofertas->count();
    }
}
