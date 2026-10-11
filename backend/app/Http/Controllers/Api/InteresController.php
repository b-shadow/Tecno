<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Interes;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class InteresController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $intereses = Interes::query()
            ->with('prospecto', 'vendedor', 'interacciones.usuario', 'recordatorios.usuario', 'ordenesPago.items', 'ordenesPago.descuentos.descuento', 'ordenesPago.pago.comprobantes')
            ->when($usuario->rol === 'vendedor', function ($query) use ($usuario, $request) {
                if ($request->query('bandeja') === 'nuevos') {
                    $query->whereNull('vendedor_id');
                    return;
                }

                $query->where(function ($subquery) use ($usuario) {
                    $subquery->where('vendedor_id', $usuario->id)->orWhereNull('vendedor_id');
                });
            })
            ->when($request->query('estado'), fn ($query, string $estado) => $query->where('estado', $estado))
            ->when($request->query('buscar'), function ($query, string $buscar) {
                $query->where(function ($subquery) use ($buscar) {
                    $subquery->where('programa_nombre', 'ilike', "%{$buscar}%")
                        ->orWhere('modulo_nombre', 'ilike', "%{$buscar}%")
                        ->orWhereHas('prospecto', function ($relation) use ($buscar) {
                            $relation->where('nombre', 'ilike', "%{$buscar}%")
                                ->orWhere('apellido', 'ilike', "%{$buscar}%")
                                ->orWhere('correo', 'ilike', "%{$buscar}%")
                                ->orWhere('telefono', 'ilike', "%{$buscar}%");
                        });
                });
            })
            ->orderByRaw("case when vendedor_id is null then 0 else 1 end")
            ->latest('ultima_actividad_en')
            ->latest('created_at')
            ->get();

        return response()->json(['intereses' => $intereses]);
    }

    public function show(Request $request, Interes $interes): JsonResponse
    {
        $this->authorizeInteres($request, $interes, allowUnassigned: true);

        return response()->json([
            'interes' => $interes->load('prospecto', 'vendedor', 'interacciones.usuario', 'recordatorios.usuario', 'ordenesPago.items', 'ordenesPago.descuentos.descuento', 'ordenesPago.pago.comprobantes'),
        ]);
    }

    public function tomar(Request $request, Interes $interes): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        abort_if($usuario->rol !== 'vendedor', 403, 'Solo un vendedor puede tomar seguimiento.');
        abort_if($interes->vendedor_id && $interes->vendedor_id !== $usuario->id, 403, 'Este interes ya fue tomado por otro vendedor.');

        $interes->update([
            'vendedor_id' => $usuario->id,
            'estado' => $interes->estado === 'Nuevo' ? 'Contactado' : $interes->estado,
            'fecha_asignacion' => $interes->fecha_asignacion ?? now(),
            'ultima_actividad_en' => now(),
        ]);

        $interes->prospecto->update(['estado' => 'Contactado']);

        return response()->json(['interes' => $interes->fresh()->load('prospecto', 'vendedor', 'interacciones.usuario', 'recordatorios.usuario', 'ordenesPago.pago')]);
    }

    public function cambiarEstado(Request $request, Interes $interes): JsonResponse
    {
        $this->authorizeInteres($request, $interes);

        $data = $request->validate([
            'estado' => ['required', Rule::in(Interes::ESTADOS)],
            'observacion' => ['nullable', 'string'],
        ]);

        $interes->update([
            'estado' => $data['estado'],
            'observacion' => $data['observacion'] ?? $interes->observacion,
            'ultima_actividad_en' => now(),
        ]);

        if ($data['estado'] === 'Convertido') {
            $interes->prospecto->update(['estado' => 'Convertido']);
        }

        return response()->json(['interes' => $interes->fresh()->load('prospecto', 'vendedor')]);
    }

    private function authorizeInteres(Request $request, Interes $interes, bool $allowUnassigned = false): void
    {
        $usuario = $request->attributes->get('auth_usuario');

        if (in_array($usuario?->rol, ['administrador', 'coordinador'], true)) {
            return;
        }

        abort_if($usuario?->rol !== 'vendedor', 403, 'No tiene permisos comerciales.');
        abort_if($interes->vendedor_id !== $usuario->id && ! ($allowUnassigned && ! $interes->vendedor_id), 403, 'Interes asignado a otro vendedor.');
    }
}
