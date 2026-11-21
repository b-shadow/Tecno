<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\ApiToken;
use App\Models\Bitacora;
use App\Models\Interes;
use App\Models\Usuario;
use App\Services\Acceso;
use App\Services\Alcance;
use App\Services\Fotos;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

/** Servicios de todo el sitio: contador de visitas (enunciado 7), búsqueda global (9), fotos y estado. */
class SitioController extends Controller
{
    /** Registra la visita a una página y devuelve su contador persistente (lo suma un trigger de la BD). */
    public function visita(Request $request): JsonResponse
    {
        $data = $request->validate(['ruta' => ['required', 'string', 'max:80']]);
        $recurso = DB::table('recursos')->where('ruta', $data['ruta'])->first(['codigo', 'publico']);
        abort_unless($recurso, 404, 'La página no existe.');

        $usuario = $this->usuarioOpcional($request);
        // Una página privada solo cuenta la visita de quien tiene permiso de verla.
        if ($recurso->publico || Acceso::permite($usuario, $recurso->codigo)) {
            Bitacora::registrar('visita', $request, $usuario?->correo, $recurso->codigo);
        }

        return response()->json(['visitas' => (int) DB::table('recursos')->where('codigo', $recurso->codigo)->value('visitas')]);
    }

    /** Búsqueda predictiva del encabezado. Sin sesión: la oferta académica. Con sesión: datos del negocio según la matriz. */
    public function buscar(Request $request): JsonResponse
    {
        $q = trim((string) $request->query('q', ''));
        if (mb_strlen($q) < 2) {
            return response()->json(['resultados' => []]);
        }
        $like = '%'.str_replace(['%', '_'], ['\\%', '\\_'], $q).'%';
        $usuario = $this->usuarioOpcional($request);
        $resultados = collect();

        $resultados = $resultados->merge(DB::table('catalogo_cache as c')->join('programas as p', 'p.codigo', '=', 'c.programa_codigo')
            ->where('c.estado', 'abierto')
            ->where(fn ($s) => $s->where('c.nombre', 'ilike', $like)->orWhere('p.nombre', 'ilike', $like)->orWhere('c.descripcion', 'ilike', $like))
            ->limit(5)->get(['c.codigo', 'c.nombre', 'p.nombre as programa', 'c.precio'])
            ->map(fn ($m) => ['tipo' => 'Módulo', 'titulo' => $m->nombre, 'detalle' => $m->programa.' · '.number_format((float) $m->precio, 0, ',', '.').' Bs', 'ruta' => '/anuncios?modulo='.$m->codigo]));

        if ($usuario && (Acceso::permite($usuario, 'embudo') || Acceso::permite($usuario, 'prospectos'))) {
            $resultados = $resultados->merge(Alcance::intereses(Interes::query(), $usuario)
                ->join('prospectos as p', 'p.documento', '=', 'intereses.documento')
                ->where(fn ($s) => $s->where('p.nombre', 'ilike', $like)->orWhere('p.apellido', 'ilike', $like)
                    ->orWhere('p.documento', 'ilike', $like)->orWhere('p.telefono', 'ilike', $like)->orWhere('p.correo', 'ilike', $like))
                ->orderByDesc('intereses.nro_tarjeta')->limit(6)
                ->get(['intereses.nro_tarjeta', 'intereses.modulo_nombre', 'intereses.estado', 'p.nombre', 'p.apellido', 'p.documento'])
                ->map(fn ($t) => ['tipo' => 'Prospecto', 'titulo' => "{$t->nombre} {$t->apellido}", 'detalle' => "CI {$t->documento} · {$t->modulo_nombre} · {$t->estado}", 'ruta' => '/agenda?interes='.$t->nro_tarjeta]));
        }

        if ($usuario && Acceso::permite($usuario, 'usuarios')) {
            $resultados = $resultados->merge(Usuario::query()
                ->where(fn ($s) => $s->where('nombre', 'ilike', $like)->orWhere('apellido', 'ilike', $like)->orWhere('correo', 'ilike', $like))
                ->limit(4)->get()
                ->map(fn ($u) => ['tipo' => 'Usuario', 'titulo' => "{$u->nombre} {$u->apellido}", 'detalle' => "{$u->rol} · {$u->correo}", 'ruta' => '/usuarios?buscar='.urlencode($u->correo)]));
        }

        if ($usuario) {
            $resultados = $resultados->merge(DB::table('recursos as r')->join('permisos as p', 'p.recurso_codigo', '=', 'r.codigo')
                ->where('p.rol', $usuario->rol)->where('r.nombre', 'ilike', $like)->limit(3)->get(['r.nombre', 'r.ruta'])
                ->map(fn ($r) => ['tipo' => 'Página', 'titulo' => $r->nombre, 'detalle' => 'Ir a la página', 'ruta' => $r->ruta]));
        }

        return response()->json(['resultados' => $resultados->values()]);
    }

    public function foto(string $archivo)
    {
        $ruta = Fotos::ruta($archivo);
        abort_unless($ruta, 404, 'La foto no existe.');

        return response()->file($ruta, ['Cache-Control' => 'public, max-age=86400']);
    }

    public function salud(): JsonResponse
    {
        try {
            DB::select('select 1');
            $bd = 'conectada';
        } catch (\Throwable) {
            $bd = 'sin conexión';
        }

        return response()->json(['sistema' => 'CRM Comercial Educativo', 'arquitectura' => '3 capas: React (cliente) · Laravel API REST · PostgreSQL', 'base_de_datos' => $bd]);
    }

    private function usuarioOpcional(Request $request): ?Usuario
    {
        $token = $request->bearerToken();
        $fila = $token ? ApiToken::query()->with('usuario')->find(hash('sha256', $token)) : null;

        return $fila && (! $fila->expira_en || $fila->expira_en->isFuture()) && $fila->usuario?->vigente() ? $fila->usuario : null;
    }
}
