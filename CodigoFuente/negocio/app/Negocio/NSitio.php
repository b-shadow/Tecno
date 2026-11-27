<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Sitio\VisitaRequest;
use Datos\DBitacora;
use Datos\DSitio;
use Illuminate\Http\JsonResponse;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

/** Capa de negocio — contador de visitas (enunciado 7), búsqueda global (enunciado 9), fotos de usuario y salud. */
class NSitio
{
    public function __construct(
        private readonly DSitio $sitio,
        private readonly DBitacora $bitacora,
        private readonly NAuth $auth,
    ) {
    }

    /** Contador de visitas de la página (enunciado 7): la bitácora la cuenta y el trigger contar_visita la suma. */
    public function visita(VisitaRequest $r): JsonResponse
    {
        $recurso = $this->sitio->recursoPorRuta($r->validated('ruta'));
        ReglaNegocioException::si(! $recurso, 'La página no existe.', 404);
        $usuario = $this->auth->usuarioOpcional($r->bearerToken());

        if ($recurso->publico || NAcceso::permite($usuario, $recurso->codigo)) {
            $this->bitacora->registrar('visita', (string) $r->ip(), $r->navegador(), $usuario?->correo, $recurso->codigo);
        }

        return response()->json(['visitas' => $this->sitio->visitas($recurso->codigo)]);
    }

    /** Búsqueda global (enunciado 9): sin sesión, la oferta; con sesión, también lo que el rol puede ver. */
    public function buscar(ConsultaRequest $r): JsonResponse
    {
        $termino = trim((string) $r->query('q', ''));
        if (mb_strlen($termino) < 2) {
            return response()->json(['resultados' => []]);
        }

        $like = '%'.str_replace(['\\', '%', '_'], ['\\\\', '\\%', '\\_'], $termino).'%';
        $usuario = $this->auth->usuarioOpcional($r->bearerToken());
        $resultados = $this->sitio->buscarCatalogo($like)->map(fn ($modulo) => [
            'tipo' => 'Módulo',
            'titulo' => $modulo->nombre,
            'detalle' => $modulo->programa.' · '.number_format((float) $modulo->precio, 0, ',', '.').' Bs',
            'ruta' => '/anuncios?modulo='.$modulo->codigo,
        ]);

        if ($usuario && (NAcceso::permite($usuario, 'embudo') || NAcceso::permite($usuario, 'prospectos'))) {
            $resultados = $resultados->merge($this->sitio->buscarIntereses($like, $usuario)->map(fn ($interes) => [
                'tipo' => 'Prospecto',
                'titulo' => "{$interes->nombre} {$interes->apellido}",
                'detalle' => "CI {$interes->documento} · {$interes->modulo_nombre} · {$interes->estado}",
                'ruta' => '/agenda?interes='.$interes->nro_tarjeta,
            ]));
        }

        if ($usuario && NAcceso::permite($usuario, 'usuarios')) {
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

        return response()->json(['resultados' => $resultados->values()]);
    }

    public function foto(string $archivo): BinaryFileResponse
    {
        $ruta = NFoto::ruta($archivo);
        ReglaNegocioException::si(! $ruta, 'La foto no existe.', 404);

        return response()->file($ruta, ['Cache-Control' => 'public, max-age=86400']);
    }

    public function salud(): JsonResponse
    {
        try {
            $this->sitio->conexionDisponible();
            $base = 'conectada';
        } catch (\Throwable) {
            $base = 'sin conexión';
        }

        return response()->json([
            'sistema' => 'CRM Comercial Educativo',
            'arquitectura' => '3 capas: React (cliente) · Laravel API REST · PostgreSQL',
            'base_de_datos' => $base,
        ]);
    }
}
