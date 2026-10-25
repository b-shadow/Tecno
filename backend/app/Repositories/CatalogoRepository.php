<?php

namespace App\Repositories;

use App\Models\CatalogoCache;
use App\Models\Programa;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Acceso de persistencia al catálogo PostgreSQL. */
class CatalogoRepository
{
    public function programasAbiertos(): Collection
    {
        return Programa::query()
            ->with(['modulos' => fn ($query) => $query->where('estado', 'abierto')->orderByRaw('length(codigo), codigo')])
            ->orderBy('nombre')
            ->get();
    }

    public function sincronizar(Collection $ofertas): void
    {
        DB::transaction(function () use ($ofertas): void {
            foreach ($ofertas->pluck('programa')->unique('id') as $programa) {
                Programa::query()->updateOrCreate(
                    ['codigo' => $programa['id']],
                    ['nombre' => $programa['nombre']],
                );
            }

            foreach ($ofertas as $oferta) {
                CatalogoCache::query()->updateOrCreate(
                    ['codigo' => $oferta['external_modulo_id']],
                    [
                        'anuncio_codigo' => $oferta['external_anuncio_id'],
                        'programa_codigo' => $oferta['programa']['id'],
                        'nombre' => $oferta['modulo']['nombre'],
                        'descripcion' => $oferta['descripcion'],
                        'precio' => $oferta['precio'],
                        'estado' => 'abierto',
                        'sincronizado_en' => now(),
                    ],
                );
            }
        });
    }
}
