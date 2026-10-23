<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Exportacion;
use App\Models\InscripcionComercial;
use App\Services\Alcance;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

/** CU6: envío de los alumnos matriculados al SIS del Grupo 06 (por ahora CSV + constancia del resultado). */
class ExportacionController extends Controller
{
    public function pendientes(Request $request): JsonResponse
    {
        $inscripciones = $this->exportables($request)->get();

        return response()->json(['total' => $inscripciones->count(), 'inscripciones' => $inscripciones]);
    }

    public function exportar(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        return DB::transaction(function () use ($request, $usuario) {
            // Serializa exportaciones simultáneas y vuelve a leer los pendientes.
            DB::table('inscripciones_comerciales')->orderBy('nro_solicitud')->lockForUpdate()->get();
            $filas = [];

            foreach ($this->exportables($request)->get() as $inscripcion) {
                $s = $inscripcion->solicitudCompra;
                $p = $s->ordenPago->interes->prospecto;
                $fila = [
                    'nombres' => $p->nombre, 'apellidos' => $p->apellido, 'ci' => $p->documento, 'telefono' => $p->telefono,
                    'profesion' => $p->profesion, 'ubicacion' => $p->ubicacion, 'correo' => $p->correo,
                    'programa' => $s->programa_nombre, 'modulo' => $s->modulo_nombre, 'codigo_modulo' => $s->modulo_codigo,
                    'precio_acordado' => $s->precio_acordado, 'fecha_inscripcion' => optional($inscripcion->fecha_confirmacion)->toDateTimeString(),
                ];
                $filas[] = $fila;
                Exportacion::query()->create([
                    'nro_solicitud' => $inscripcion->nro_solicitud, 'usuario_correo' => $usuario->correo,
                    'fecha_exportacion' => now(), 'estado' => 'exportada', 'respuesta' => json_encode($fila, JSON_UNESCAPED_UNICODE),
                ]);
            }

            return response()->json([
                'mensaje' => count($filas) ? count($filas).' matrícula(s) exportadas.' : 'No hay matrículas pendientes de enviar.',
                'archivo' => 'alumnos_inscritos_'.now()->format('Ymd_His').'.csv',
                'filas' => $filas,
            ]);
        });
    }

    public function registrarResultado(Request $request, Exportacion $exportacion): JsonResponse
    {
        $data = $request->validate([
            'estado' => ['required', 'in:recibida,error'],
            'respuesta' => ['nullable', 'string', 'max:2000'],
        ]);
        $exportacion->update($data);

        return response()->json(['mensaje' => 'Resultado registrado.', 'exportacion' => $exportacion]);
    }

    public function historial(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        return response()->json(['exportaciones' => Exportacion::query()
            ->whereExists(fn ($q) => $q->from('solicitudes_compra as s')->join('ordenes_pago as o', 'o.nro_orden', '=', 's.nro_orden')
                ->join('intereses as i', 'i.nro_tarjeta', '=', 'o.nro_tarjeta')->whereColumn('s.nro_solicitud', 'exportaciones.nro_solicitud')
                ->tap(fn ($w) => $usuario->rol === 'coordinador' ? $w->whereIn('i.modulo_codigo', Alcance::modulosACargo($usuario)) : $w))
            ->with('usuario:correo,nombre,apellido')
            ->orderByDesc('fecha_exportacion')->get()]);
    }

    private function exportables(Request $request): Builder
    {
        $usuario = $request->attributes->get('auth_usuario');

        return InscripcionComercial::query()
            ->with('solicitudCompra.ordenPago.interes.prospecto')
            ->whereHas('solicitudCompra.ordenPago.interes', fn ($q) => Alcance::intereses($q, $usuario))
            ->whereDoesntHave('exportaciones', fn ($q) => $q->whereIn('estado', ['preparada', 'exportada', 'recibida']));
    }
}
