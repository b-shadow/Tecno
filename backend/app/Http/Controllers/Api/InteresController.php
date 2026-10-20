<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Interes;
use App\Models\Usuario;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\Rule;

class InteresController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');

        $intereses = Interes::query()
            ->with('prospecto', 'vendedor', 'interacciones.usuario', 'recordatorios.usuario', 'ordenesPago.items', 'ordenesPago.descuentos.descuento', 'ordenesPago.pago.comprobantes')
            ->when($usuario->rol === 'vendedor', fn ($query) => $query->where('vendedor_id', $usuario->id))
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
            ->orderByRaw('case when vendedor_id is null then 0 else 1 end')
            ->latest('ultima_actividad_en')
            ->latest('created_at')
            ->get();

        return response()->json(['intereses' => $intereses]);
    }

    public function show(Request $request, Interes $interes): JsonResponse
    {
        $this->authorizeInteres($request, $interes);

        return response()->json([
            'interes' => $interes->load('prospecto', 'vendedor', 'interacciones.usuario', 'recordatorios.usuario', 'ordenesPago.items', 'ordenesPago.descuentos.descuento', 'ordenesPago.pago.comprobantes'),
        ]);
    }

    /**
     * Asigna o reasigna un interes. El historial (interacciones con su usuario_id) no se toca;
     * se deja constancia de la reasignacion y las actividades pendientes pasan al nuevo vendedor.
     */
    public function asignar(Request $request, Interes $interes): JsonResponse
    {
        $this->authorizeCoordinacion($request);

        $data = $request->validate([
            'vendedor_id' => ['required', Rule::exists('usuarios', 'id')->where('rol', 'vendedor')->where('estado', 'activo')],
        ]);

        $this->asignarA($interes, Usuario::query()->findOrFail($data['vendedor_id']), $request->attributes->get('auth_usuario'));

        return response()->json(['interes' => $interes->fresh()->load('prospecto', 'vendedor')]);
    }

    /**
     * Distribucion equitativa (RF2.3): cada prospecto sin vendedor va al vendedor activo con menos
     * intereses abiertos; todos los intereses de un mismo prospecto quedan con el mismo vendedor.
     */
    public function distribuir(Request $request): JsonResponse
    {
        $this->authorizeCoordinacion($request);
        $coordinador = $request->attributes->get('auth_usuario');

        $vendedores = Usuario::query()
            ->where('rol', 'vendedor')
            ->where('estado', 'activo')
            ->withCount(['interesesAsignados as abiertos' => fn ($query) => $query->whereNotIn('estado', ['Convertido', 'Perdido'])])
            ->get();

        abort_if($vendedores->isEmpty(), 422, 'No hay vendedores activos para distribuir.');

        $carga = $vendedores->pluck('abiertos', 'id')->all();
        $pendientes = Interes::query()->whereNull('vendedor_id')->orderBy('created_at')->get()->groupBy('prospecto_id');

        DB::transaction(function () use ($pendientes, $vendedores, $coordinador, &$carga): void {
            foreach ($pendientes as $prospectoId => $intereses) {
                $yaAsignado = Interes::query()->where('prospecto_id', $prospectoId)->whereNotNull('vendedor_id')
                    ->whereIn('vendedor_id', array_keys($carga))->value('vendedor_id');
                $vendedorId = $yaAsignado ?? array_keys($carga, min($carga))[0];
                $vendedor = $vendedores->firstWhere('id', $vendedorId);

                foreach ($intereses as $interes) {
                    $this->asignarA($interes, $vendedor, $coordinador);
                    $carga[$vendedorId]++;
                }
            }
        });

        return response()->json([
            'mensaje' => 'Interesados distribuidos equitativamente.',
            'asignados' => $pendientes->flatten()->count(),
        ]);
    }

    private function asignarA(Interes $interes, Usuario $vendedor, Usuario $coordinador): void
    {
        $anterior = $interes->vendedor;

        if ($anterior?->id === $vendedor->id) {
            return;
        }

        $interes->update([
            'vendedor_id' => $vendedor->id,
            'fecha_asignacion' => $interes->fecha_asignacion ?? now(),
        ]);

        $interes->recordatorios()->whereIn('estado', ['Pendiente', 'Atrasada'])->update(['usuario_id' => $vendedor->id]);

        if (! $anterior) {
            return;
        }

        $interes->interacciones()->create([
            'usuario_id' => $coordinador->id,
            'tipo' => 'Nota comercial',
            'descripcion' => "Reasignado de {$anterior->nombre} {$anterior->apellido} a {$vendedor->nombre} {$vendedor->apellido} por {$coordinador->nombre} {$coordinador->apellido}.",
            'resultado' => 'Reasignacion con historial completo',
            'fecha' => now(),
        ]);
    }

    private function authorizeCoordinacion(Request $request): void
    {
        $usuario = $request->attributes->get('auth_usuario');
        abort_if(! in_array($usuario?->rol, ['administrador', 'coordinador'], true), 403, 'Solo coordinacion puede asignar interesados.');
    }

    public function cambiarEstado(Request $request, Interes $interes): JsonResponse
    {
        $this->authorizeInteres($request, $interes);

        $data = $request->validate([
            'estado' => ['required', Rule::in(Interes::ESTADOS)],
            'observacion' => ['required_if:estado,Perdido', 'nullable', 'string', 'max:2000'],
        ]);

        abort_if($data['estado'] === 'Convertido' && $interes->estado !== 'Convertido', 422, 'La conversion se realiza al aprobar el pago y confirmar la inscripcion.');

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

    private function authorizeInteres(Request $request, Interes $interes): void
    {
        $usuario = $request->attributes->get('auth_usuario');

        if (in_array($usuario?->rol, ['administrador', 'coordinador'], true)) {
            return;
        }

        abort_if($usuario?->rol !== 'vendedor', 403, 'No tiene permisos comerciales.');
        abort_if($interes->vendedor_id !== $usuario->id, 403, 'Interes asignado a otro vendedor.');
    }
}
