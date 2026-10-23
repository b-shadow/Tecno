<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CatalogoCache;
use App\Models\Programa;
use App\Services\CatalogoExternoDemo;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

/**
 * CU2 (consumir oferta) y RNF2 (cliente API del catálogo del Grupo 06).
 * La oferta vigente es la réplica local `catalogo_cache` + `programas`; `CatalogoExternoDemo` simula la API externa
 * (imágenes, duración, área) hasta que el Grupo 06 publique la real, y `sincronizar` la vuelve a copiar.
 */
class CatalogoController extends Controller
{
    public function __construct(private readonly CatalogoExternoDemo $externo)
    {
    }

    /** Programas con sus módulos abiertos (RF2.2: programa completo o módulo independiente). */
    public function programas(Request $request): JsonResponse
    {
        $buscar = trim((string) $request->query('buscar', ''));
        $media = $this->externo->ofertas()->keyBy('external_modulo_id');
        $programasExternos = $this->externo->ofertas()->pluck('programa', 'programa.id');

        $programas = Programa::query()
            ->with(['modulos' => fn ($q) => $q->where('estado', 'abierto')->orderByRaw('length(codigo), codigo')])
            ->orderBy('nombre')
            ->get()
            ->map(function (Programa $programa) use ($media, $programasExternos, $buscar) {
                $modulos = $programa->modulos
                    ->filter(fn ($m) => $buscar === '' || str_contains(mb_strtolower($programa->nombre.' '.$m->nombre.' '.$m->descripcion), mb_strtolower($buscar)))
                    ->map(fn (CatalogoCache $m) => [
                        'codigo' => $m->codigo,
                        'anuncio_codigo' => $m->anuncio_codigo,
                        'nombre' => $m->nombre,
                        'descripcion' => $m->descripcion,
                        'precio' => (float) $m->precio,
                        'duracion' => $media[$m->codigo]['modulo']['duracion'] ?? null,
                        'imagen' => $media[$m->codigo]['imagen'] ?? null,
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
            ->filter(fn ($p) => $p['modulos']->isNotEmpty())
            ->values();

        return response()->json(['programas' => $programas]);
    }

    /** Copia la oferta de la API externa a la réplica local (solo quien gestiona la oferta). */
    public function sincronizar(): JsonResponse
    {
        $ofertas = $this->externo->ofertas();

        DB::transaction(function () use ($ofertas) {
            foreach ($ofertas->pluck('programa')->unique('id') as $p) {
                Programa::query()->updateOrCreate(['codigo' => $p['id']], ['nombre' => $p['nombre']]);
            }
            foreach ($ofertas as $o) {
                CatalogoCache::query()->updateOrCreate(['codigo' => $o['external_modulo_id']], [
                    'anuncio_codigo' => $o['external_anuncio_id'],
                    'programa_codigo' => $o['programa']['id'],
                    'nombre' => $o['modulo']['nombre'],
                    'descripcion' => $o['descripcion'],
                    'precio' => $o['precio'],
                    'estado' => 'abierto',
                    'sincronizado_en' => now(),
                ]);
            }
        });

        return response()->json(['mensaje' => 'Catálogo sincronizado: '.$ofertas->count().' módulos.']);
    }
}
