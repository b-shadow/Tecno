<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Exportacion;
use App\Models\InscripcionComercial;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

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

        $usuario = $request->attributes->get('auth_usuario');
        $inscripciones = $this->inscripcionesExportables()->get();
        $filas = [];

        $exportaciones = $inscripciones->map(function (InscripcionComercial $inscripcion) use ($usuario, &$filas) {
            $filas[] = $this->filaCSV($inscripcion);

            $payload = [
                'prospecto' => $inscripcion->prospecto,
                'modulo' => [
                    'external_modulo_id' => $inscripcion->solicitudCompra->external_modulo_id,
                    'programa_nombre' => $inscripcion->solicitudCompra->programa_nombre,
                    'nombre' => $inscripcion->solicitudCompra->modulo_nombre,
                    'descripcion' => $inscripcion->solicitudCompra->modulo_descripcion,
                ],
                'pago' => $inscripcion->solicitudCompra->pago
                    ?? $inscripcion->solicitudCompra->ordenItem?->ordenPago?->pago,
                'inscripcion' => $inscripcion,
            ];

            return Exportacion::query()->create([
                'usuario_id' => $usuario->id,
                'prospecto_id' => $inscripcion->prospecto_id,
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
            ->with('prospecto', 'solicitudCompra.pago', 'solicitudCompra.ordenItem.ordenPago.pago')
            ->where('estado', 'Confirmada')
            ->whereHas('prospecto', fn ($query) => $query->where('estado', 'Convertido'))
            ->where(function ($query): void {
                $query
                    ->whereHas('solicitudCompra.pago', fn ($subquery) => $subquery->where('estado', 'Pago aprobado'))
                    ->orWhereHas('solicitudCompra.ordenItem.ordenPago.pago', fn ($subquery) => $subquery->where('estado', 'Pago aprobado'));
            });
    }

    private function filaCSV(InscripcionComercial $inscripcion): array
    {
        $prospecto = $inscripcion->prospecto;
        $solicitud = $inscripcion->solicitudCompra;
        $pago = $solicitud->pago ?? $solicitud->ordenItem?->ordenPago?->pago;

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
