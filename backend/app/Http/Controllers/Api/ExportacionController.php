<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Exportacion;
use App\Models\InscripcionComercial;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ExportacionController extends Controller
{
    public function prepararDatosExportacion(Request $request): JsonResponse
    {
        $this->authorizeRoles($request, ['administrador', 'coordinador']);

        $inscripciones = $this->inscripcionesExportables()->get();

        return response()->json([
            'total' => $inscripciones->count(),
            'inscripciones' => $inscripciones,
        ]);
    }

    public function exportarInscripciones(Request $request): JsonResponse
    {
        $this->authorizeRoles($request, ['administrador', 'coordinador']);

        return DB::transaction(function () use ($request): JsonResponse {
            $usuario = $request->attributes->get('auth_usuario');
            // Serializa exportaciones concurrentes y vuelve a consultar los pendientes.
            DB::table('inscripciones_comerciales')->orderBy('id')->lockForUpdate()->get();
            $inscripciones = $this->inscripcionesExportables()->get();
            $filas = [];

            $exportaciones = $inscripciones->map(function (InscripcionComercial $inscripcion) use ($usuario, &$filas) {
                $filas[] = $this->filaCSV($inscripcion);

                $payload = [
                    'prospecto' => $inscripcion->alumno(),
                    'modulo' => [
                        'external_modulo_id' => $inscripcion->solicitudCompra->external_modulo_id,
                        'programa_nombre' => $inscripcion->solicitudCompra->programa_nombre,
                        'nombre' => $inscripcion->solicitudCompra->modulo_nombre,
                        'descripcion' => $inscripcion->solicitudCompra->modulo_descripcion,
                    ],
                    'pago' => $inscripcion->solicitudCompra->ordenPago->pago,
                    'inscripcion' => $inscripcion,
                ];

                return Exportacion::query()->create([
                    'inscripcion_comercial_id' => $inscripcion->id,
                    'usuario_id' => $usuario->id,
                    'prospecto_id' => $inscripcion->alumno()?->id,
                    'fecha_exportacion' => now(),
                    'estado' => 'exportada',
                    'respuesta' => json_encode($payload, JSON_UNESCAPED_UNICODE),
                ]);
            });

            return response()->json([
                'archivo' => 'alumnos_inscritos_'.now()->format('Ymd_His').'.csv',
                'filas' => $filas,
                'exportaciones' => $exportaciones,
            ]);
        });
    }

    public function registrarResultadoExportacion(Request $request, Exportacion $exportacion): JsonResponse
    {
        $this->authorizeRoles($request, ['administrador', 'coordinador']);

        $data = $request->validate([
            'estado' => ['required', 'in:preparada,exportada,recibida,error'],
            'respuesta' => ['nullable', 'string'],
        ]);

        $exportacion->update($data);

        return response()->json(['exportacion' => $exportacion->load('usuario', 'prospecto')]);
    }

    public function exportaciones(Request $request): JsonResponse
    {
        $this->authorizeRoles($request, ['administrador', 'coordinador']);

        return response()->json([
            'exportaciones' => Exportacion::query()->with('usuario', 'prospecto')->latest('fecha_exportacion')->get(),
        ]);
    }

    private function inscripcionesExportables()
    {
        return InscripcionComercial::query()
            ->with('solicitudCompra.ordenPago.prospecto', 'solicitudCompra.ordenPago.pago')
            ->where('estado', 'Confirmada')
            ->whereDoesntHave('exportaciones', fn ($query) => $query->whereIn('estado', ['preparada', 'exportada', 'recibida']))
            ->whereHas('solicitudCompra.ordenPago.prospecto', fn ($query) => $query->where('prospectos.estado', 'Convertido'))
            ->whereHas('solicitudCompra.ordenPago.pago', fn ($query) => $query->where('estado', 'Pago aprobado'));
    }

    private function filaCSV(InscripcionComercial $inscripcion): array
    {
        $prospecto = $inscripcion->alumno();
        $solicitud = $inscripcion->solicitudCompra;
        $pago = $solicitud->ordenPago->pago;

        return [
            'nombres' => $prospecto?->nombre,
            'apellidos' => $prospecto?->apellido,
            'ci' => $prospecto?->documento,
            'telefono' => $prospecto?->telefono,
            'profesion' => $prospecto?->profesion,
            'ubicacion' => $prospecto?->ubicacion,
            'correo' => $prospecto?->correo,
            'programa' => $solicitud?->programa_nombre,
            'modulo' => $solicitud?->modulo_nombre,
            'external_modulo_id' => $solicitud?->external_modulo_id,
            'precio_acordado' => $solicitud?->precio_acordado,
            'estado_pago' => $pago?->estado ?? 'Pago aprobado',
            'fecha_inscripcion' => optional($inscripcion->fecha_confirmacion)->toDateTimeString(),
        ];
    }

    private function authorizeRoles(Request $request, array $roles): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if(! in_array($usuario?->rol, $roles, true), 403, 'No tiene permisos para esta operacion.');
    }
}
