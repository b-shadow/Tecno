<?php

namespace App\Services;

use App\Exceptions\ReglaNegocioException;
use Datos\Modelos\Usuario;
use Datos\Repositorios\BitacoraRepository;
use Datos\Repositorios\SitioRepository;
use Illuminate\Support\Collection;

/** Reglas de negocio compartidas del catálogo público, búsqueda y contador de visitas. */
class SitioService
{
    public function __construct(
        private readonly SitioRepository $sitio,
        private readonly BitacoraRepository $bitacora,
        private readonly AuthService $auth,
    ) {
    }

    /** Contador de visitas de la página (enunciado 7): la bitácora la cuenta y el trigger contar_visita la suma. */
    public function visita(?string $token, string $ruta, string $ip, ?string $navegador): int
    {
        $recurso = $this->sitio->recursoPorRuta($ruta);
        ReglaNegocioException::si(! $recurso, 'La página no existe.', 404);
        $usuario = $this->auth->usuarioOpcional($token);

        if ($recurso->publico || AccesoService::permite($usuario, $recurso->codigo)) {
            $this->bitacora->registrar('visita', $ip, $navegador, $usuario?->correo, $recurso->codigo);
        }

        return $this->sitio->visitas($recurso->codigo);
    }

    /** Búsqueda global (enunciado 9): sin sesión, la oferta; con sesión, también lo que el rol puede ver. */
    public function buscar(?string $token, string $termino): Collection
    {
        $termino = trim($termino);
        if (mb_strlen($termino) < 2) {
            return collect();
        }

        $like = '%'.str_replace(['%', '_'], ['\\%', '\\_'], $termino).'%';
        $usuario = $this->auth->usuarioOpcional($token);
        $resultados = $this->sitio->buscarCatalogo($like)->map(fn ($modulo) => [
            'tipo' => 'Módulo',
            'titulo' => $modulo->nombre,
            'detalle' => $modulo->programa.' · '.number_format((float) $modulo->precio, 0, ',', '.').' Bs',
            'ruta' => '/anuncios?modulo='.$modulo->codigo,
        ]);

        if ($usuario && (AccesoService::permite($usuario, 'embudo') || AccesoService::permite($usuario, 'prospectos'))) {
            $resultados = $resultados->merge($this->sitio->buscarIntereses($like, $usuario)->map(fn ($interes) => [
                'tipo' => 'Prospecto',
                'titulo' => "{$interes->nombre} {$interes->apellido}",
                'detalle' => "CI {$interes->documento} · {$interes->modulo_nombre} · {$interes->estado}",
                'ruta' => '/agenda?interes='.$interes->nro_tarjeta,
            ]));
        }

        if ($usuario && AccesoService::permite($usuario, 'usuarios')) {
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
        $ruta = FotoService::ruta($archivo);
        ReglaNegocioException::si(! $ruta, 'La foto no existe.', 404);

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
}
