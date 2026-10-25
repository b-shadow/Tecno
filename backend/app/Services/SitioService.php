<?php

namespace App\Services;

use App\Models\Bitacora;
use App\Models\Usuario;
use App\Repositories\SitioRepository;
use Illuminate\Http\Request;
use Illuminate\Support\Collection;

/** Reglas de negocio compartidas del catálogo público, búsqueda y contador de visitas. */
class SitioService
{
    public function __construct(private readonly SitioRepository $sitio)
    {
    }

    public function visita(Request $request, string $ruta): int
    {
        $recurso = $this->sitio->recursoPorRuta($ruta);
        abort_unless($recurso, 404, 'La página no existe.');
        $usuario = $this->usuarioOpcional($request);

        if ($recurso->publico || Acceso::permite($usuario, $recurso->codigo)) {
            Bitacora::registrar('visita', $request, $usuario?->correo, $recurso->codigo);
        }

        return $this->sitio->visitas($recurso->codigo);
    }

    public function buscar(Request $request, string $termino): Collection
    {
        $termino = trim($termino);
        if (mb_strlen($termino) < 2) {
            return collect();
        }

        $like = '%'.str_replace(['%', '_'], ['\\%', '\\_'], $termino).'%';
        $usuario = $this->usuarioOpcional($request);
        $resultados = $this->sitio->buscarCatalogo($like)->map(fn ($modulo) => [
            'tipo' => 'Módulo',
            'titulo' => $modulo->nombre,
            'detalle' => $modulo->programa.' · '.number_format((float) $modulo->precio, 0, ',', '.').' Bs',
            'ruta' => '/anuncios?modulo='.$modulo->codigo,
        ]);

        if ($usuario && (Acceso::permite($usuario, 'embudo') || Acceso::permite($usuario, 'prospectos'))) {
            $resultados = $resultados->merge($this->sitio->buscarIntereses($like, $usuario)->map(fn ($interes) => [
                'tipo' => 'Prospecto',
                'titulo' => "{$interes->nombre} {$interes->apellido}",
                'detalle' => "CI {$interes->documento} · {$interes->modulo_nombre} · {$interes->estado}",
                'ruta' => '/agenda?interes='.$interes->nro_tarjeta,
            ]));
        }

        if ($usuario && Acceso::permite($usuario, 'usuarios')) {
            $resultados = $resultados->merge($this->sitio->buscarUsuarios($like)->map(fn ($persona) => [
                'tipo' => 'Usuario',
                'titulo' => "{$persona->nombre} {$persona->apellido}",
                'detalle' => "{$persona->rol} · {$persona->correo}",
                'ruta' => '/usuarios?buscar='.urlencode($persona->correo),
            ]));
        }

        if ($usuario) {
            $resultados = $resultados->merge($this->sitio->buscarPaginas($like, $usuario->rol)->map(fn ($pagina) => [
                'tipo' => 'Página',
                'titulo' => $pagina->nombre,
                'detalle' => 'Ir a la página',
                'ruta' => $pagina->ruta,
            ]));
        }

        return $resultados->values();
    }

    public function rutaFoto(string $archivo): string
    {
        $ruta = Fotos::ruta($archivo);
        abort_unless($ruta, 404, 'La foto no existe.');

        return $ruta;
    }

    public function salud(): array
    {
        try {
            $this->sitio->conexionDisponible();
            $base = 'conectada';
        } catch (\Throwable) {
            $base = 'sin conexión';
        }

        return [
            'sistema' => 'CRM Comercial Educativo',
            'arquitectura' => '3 capas: React (cliente) · Laravel API REST · PostgreSQL',
            'base_de_datos' => $base,
        ];
    }

    private function usuarioOpcional(Request $request): ?Usuario
    {
        $token = $request->bearerToken();
        $fila = $token ? $this->sitio->usuarioDeToken($token) : null;

        return $fila && (! $fila->expira_en || $fila->expira_en->isFuture()) && $fila->usuario?->vigente()
            ? $fila->usuario
            : null;
    }
}
