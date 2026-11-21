<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Bitacora;
use App\Models\Permiso;
use App\Services\Acceso;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\Rule;

/** Enunciado 2 y 4: matriz de acceso editable (rol × recurso) y bitácora de auditoría. */
class SeguridadController extends Controller
{
    public function matriz(): JsonResponse
    {
        return response()->json([
            'roles' => DB::table('roles')->orderByRaw("nombre = 'administrador' desc")->orderBy('nombre')->get(['nombre', 'descripcion']),
            'recursos' => DB::table('recursos')->where('publico', false)->orderBy('orden')->get(['codigo', 'nombre', 'ruta', 'caso_uso']),
            'permisos' => DB::table('permisos')->get(['rol', 'recurso_codigo', 'acceso']),
            'niveles' => array_keys(Permiso::NIVELES),
        ]);
    }

    /** Fija (o quita, con acceso = null) el permiso de un rol sobre un recurso. El menú cambia en el próximo ingreso. */
    public function asignar(Request $request): JsonResponse
    {
        $data = $request->validate([
            'rol' => ['required', 'exists:roles,nombre'],
            'recurso_codigo' => ['required', Rule::exists('recursos', 'codigo')->where('publico', false)],
            'acceso' => ['nullable', Rule::in(array_keys(Permiso::NIVELES))],
        ], [], ['recurso_codigo' => 'recurso']);

        // Candado: el administrador no puede quitarse la gestión de la propia matriz.
        abort_if($data['rol'] === 'administrador' && in_array($data['recurso_codigo'], ['matriz', 'usuarios'], true) && $data['acceso'] !== 'eliminacion',
            422, 'El administrador debe conservar acceso total a Usuarios y Matriz de acceso.');

        $clave = ['rol' => $data['rol'], 'recurso_codigo' => $data['recurso_codigo']];
        if ($data['acceso']) {
            DB::table('permisos')->updateOrInsert($clave, ['acceso' => $data['acceso'], 'updated_at' => now(), 'created_at' => now()]);
        } else {
            DB::table('permisos')->where($clave)->delete();
        }
        Acceso::olvidar();

        return response()->json(['mensaje' => 'Permiso actualizado.']);
    }

    public function bitacora(Request $request): JsonResponse
    {
        $request->validate([
            'evento' => ['nullable', Rule::in(Bitacora::EVENTOS)],
            'desde' => ['nullable', 'date'],
            'hasta' => ['nullable', 'date', 'after_or_equal:desde'],
        ], [], ['desde' => 'fecha inicial', 'hasta' => 'fecha final']);

        $registros = DB::table('bitacora as b')
            ->leftJoin('usuarios as u', 'u.correo', '=', 'b.usuario_correo')
            ->leftJoin('recursos as r', 'r.codigo', '=', 'b.recurso_codigo')
            ->when($request->query('evento'), fn ($q, $e) => $q->where('b.evento', $e))
            ->when($request->query('usuario'), fn ($q, $u) => $q->where(fn ($s) => $s->where('b.usuario_correo', 'ilike', "%{$u}%")->orWhere('b.correo_intentado', 'ilike', "%{$u}%")))
            ->when($request->query('ip'), fn ($q, $ip) => $q->where('b.ip', 'like', "{$ip}%"))
            ->when($request->query('desde'), fn ($q, $d) => $q->where('b.fecha', '>=', Carbon::parse($d, 'America/La_Paz')->startOfDay()->utc()))
            ->when($request->query('hasta'), fn ($q, $h) => $q->where('b.fecha', '<=', Carbon::parse($h, 'America/La_Paz')->endOfDay()->utc()))
            ->orderByDesc('b.nro_registro')
            ->select('b.*', DB::raw("u.nombre || ' ' || u.apellido as usuario"), 'r.nombre as recurso')
            ->paginate(50);

        return response()->json(['registros' => $registros]);
    }

    /** Recursos más accedidos, IPs con más intentos fallidos y resumen de eventos (últimos 30 días). */
    public function resumen(): JsonResponse
    {
        $desde = now()->subDays(30);

        return response()->json([
            'eventos' => DB::table('bitacora')->where('fecha', '>=', $desde)->groupBy('evento')->selectRaw('evento, count(*) as total')->pluck('total', 'evento'),
            'recursos_mas_accedidos' => DB::table('recursos')->orderByDesc('visitas')->limit(10)->get(['codigo', 'nombre', 'ruta', 'visitas']),
            'ips_con_fallos' => DB::table('bitacora')->where('evento', 'login_fallido')->where('fecha', '>=', $desde)
                ->groupBy('ip')->orderByDesc('total')->limit(8)->selectRaw('ip, count(*) as total, max(fecha) as ultimo')->get(),
            'usuarios_mas_activos' => DB::table('bitacora as b')->join('usuarios as u', 'u.correo', '=', 'b.usuario_correo')
                ->where('b.evento', 'visita')->where('b.fecha', '>=', $desde)->groupBy('u.correo', 'u.nombre', 'u.apellido')
                ->orderByDesc('total')->limit(8)->selectRaw("u.nombre || ' ' || u.apellido as usuario, count(*) as total")->get(),
        ]);
    }
}
