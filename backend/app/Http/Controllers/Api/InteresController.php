<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Interes;
use App\Models\MotivoPerdida;
use App\Models\Usuario;
use App\Services\Alcance;
use App\Services\Conversion;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\Rule;

/**
 * Tarjetas del embudo (intereses).
 * CU3: asignación manual y Round-Robin (RF2.3). CU4: tablero Kanban con los estados de RF3.2.
 * CU5: Perdido exige motivo (RF3.3). CU6: Convertido valida datos y matricula (RF3.4).
 */
class InteresController extends Controller
{
    private const CON_DETALLE = ['prospecto', 'vendedor:correo,nombre,apellido,telefono', 'ordenesPago.pago', 'ordenesPago.cuotas'];

    /** Tarjetas visibles para el rol, con filtros; el Kanban las agrupa por estado. */
    public function index(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $buscar = trim((string) $request->query('buscar', ''));

        $tarjetas = Alcance::intereses(Interes::query(), $usuario)
            ->with(self::CON_DETALLE)
            ->when($request->query('estado'), fn ($q, $estado) => $q->where('estado', $estado))
            ->when($request->query('vendedor'), fn ($q, $correo) => $q->where('vendedor_correo', $correo))
            ->when($request->query('sin_asignar'), fn ($q) => $q->whereNull('vendedor_correo'))
            ->when($buscar !== '', fn ($q) => $q->where(fn ($s) => $s
                ->where('programa_nombre', 'ilike', "%{$buscar}%")->orWhere('modulo_nombre', 'ilike', "%{$buscar}%")
                ->orWhereHas('prospecto', fn ($p) => $p->where('nombre', 'ilike', "%{$buscar}%")->orWhere('apellido', 'ilike', "%{$buscar}%")
                    ->orWhere('documento', 'ilike', "%{$buscar}%")->orWhere('telefono', 'ilike', "%{$buscar}%"))))
            ->orderByRaw('vendedor_correo is not null')
            ->orderByDesc('ultima_actividad_en')
            ->orderByDesc('nro_tarjeta')
            ->get();

        return response()->json([
            'intereses' => $tarjetas,
            'estados' => Interes::ESTADOS,
            'motivos' => MotivoPerdida::query()->orderBy('categoria')->orderBy('nombre')->get(),
        ]);
    }

    /** Ficha de la tarjeta con su historial cronológico (RF4.1): movimientos del embudo, interacciones y recordatorios. */
    public function show(Request $request, Interes $interes): JsonResponse
    {
        Alcance::autorizarTarjeta($request->attributes->get('auth_usuario'), $interes);

        $interes->load(self::CON_DETALLE + [
            'interacciones' => fn ($q) => $q->with('usuario:correo,nombre,apellido')->orderByDesc('fecha'),
            'recordatorios' => fn ($q) => $q->with('usuario:correo,nombre,apellido')->orderBy('fecha_programada'),
            'movimientos' => fn ($q) => $q->with('usuario:correo,nombre,apellido')->orderByDesc('fecha'),
            'ordenesPago' => fn ($q) => $q->with('items', 'descuentos.descuento', 'pago.comprobantes', 'cuotas.metodo')->orderByDesc('nro_orden'),
            'prospecto.metodosPago' => fn ($q) => $q->orderByDesc('nro_metodo'),
        ]);

        return response()->json(['interes' => $interes, 'faltantes_conversion' => Conversion::faltantes($interes)]);
    }

    /** CU4: mover la tarjeta a otra columna del Kanban. */
    public function mover(Request $request, Interes $interes): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        Alcance::autorizarTarjeta($usuario, $interes);

        $data = $request->validate([
            'estado' => ['required', Rule::in(Interes::ESTADOS)],
            'motivo_perdida' => ['nullable', 'required_if:estado,Perdido', 'exists:motivos_perdida,nombre', Rule::notIn(['Sin clasificar (web)'])],
            'observacion' => ['nullable', 'string', 'max:2000'],
        ], ['motivo_perdida.required_if' => 'Para marcar la tarjeta como Perdido debe elegir el motivo.'], ['motivo_perdida' => 'motivo de pérdida', 'observacion' => 'observación']);

        abort_if($interes->estado === 'Convertido', 422, 'Una tarjeta convertida ya tiene matrícula: no se puede mover.');

        DB::transaction(function () use ($interes, $data, $usuario) {
            $interes = Interes::query()->lockForUpdate()->findOrFail($interes->nro_tarjeta);

            if ($data['estado'] === 'Convertido') {
                $faltan = Conversion::faltantes($interes);
                abort_if($faltan, response()->json(['mensaje' => 'No se puede convertir todavía.', 'faltantes' => $faltan], 422));
                Conversion::procesar($interes, $usuario);

                return;
            }

            $interes->update([
                'estado' => $data['estado'],
                'motivo_perdida' => $data['estado'] === 'Perdido' ? $data['motivo_perdida'] : null,
                'observacion' => $data['observacion'] ?? $interes->observacion,
                'ultima_actividad_en' => now(),
            ]);
            $interes->prospecto->update(['estado' => $data['estado']]);

            if ($data['estado'] === 'Perdido') {
                $interes->interacciones()->create([
                    'usuario_correo' => $usuario->correo,
                    'tipo' => 'Nota comercial',
                    'descripcion' => 'Marcado como Perdido. Motivo: '.$data['motivo_perdida'].($data['observacion'] ?? '' ? '. '.$data['observacion'] : '.'),
                    'resultado' => 'Perdido',
                    'fecha' => now(),
                ]);
            }
        });

        return response()->json(['mensaje' => "Tarjeta movida a {$data['estado']}.", 'interes' => $interes->fresh()->load(self::CON_DETALLE)]);
    }

    /** CU3: asignar o reasignar. El historial no se toca: queda constancia y lo pendiente pasa al nuevo vendedor. */
    public function asignar(Request $request, Interes $interes): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        Alcance::autorizarTarjeta($usuario, $interes);
        $data = $request->validate([
            'vendedor_correo' => ['required', Rule::exists('usuarios', 'correo')->where('rol', 'vendedor')->where('estado', 'activo')],
        ], [], ['vendedor_correo' => 'vendedor']);

        DB::transaction(fn () => $this->asignarA($interes, Usuario::query()->findOrFail($data['vendedor_correo']), $usuario));

        return response()->json(['mensaje' => 'Prospecto asignado.', 'interes' => $interes->fresh()->load(self::CON_DETALLE)]);
    }

    /**
     * RF2.3 Round-Robin equitativo: cada prospecto sin vendedor va al vendedor activo con menos tarjetas abiertas;
     * todas las tarjetas de un mismo prospecto quedan con el mismo vendedor.
     */
    public function distribuir(Request $request): JsonResponse
    {
        $usuario = $request->attributes->get('auth_usuario');
        $vendedores = Usuario::query()->where('rol', 'vendedor')->where('estado', 'activo')
            ->whereDate('fecha_inicio', '<=', now())->whereDate('fecha_fin', '>=', now())->orderBy('correo')->get();
        abort_if($vendedores->isEmpty(), 422, 'No hay vendedores activos para repartir.');

        $carga = Interes::query()->whereIn('vendedor_correo', $vendedores->pluck('correo'))->whereNotIn('estado', ['Convertido', 'Perdido'])
            ->groupBy('vendedor_correo')->selectRaw('vendedor_correo, count(*) as total')->pluck('total', 'vendedor_correo')->all();
        $carga = $vendedores->mapWithKeys(fn ($v) => [$v->correo => (int) ($carga[$v->correo] ?? 0)])->all();

        $pendientes = Alcance::intereses(Interes::query(), $usuario)->whereNull('vendedor_correo')->orderBy('nro_tarjeta')->get()->groupBy('documento');

        DB::transaction(function () use ($pendientes, $vendedores, $usuario, &$carga) {
            foreach ($pendientes as $documento => $tarjetas) {
                $actual = Interes::query()->where('documento', $documento)->whereIn('vendedor_correo', array_keys($carga))->value('vendedor_correo');
                $elegido = $actual ?? array_keys($carga, min($carga))[0];
                foreach ($tarjetas as $tarjeta) {
                    $this->asignarA($tarjeta, $vendedores->firstWhere('correo', $elegido), $usuario);
                    $carga[$elegido]++;
                }
            }
        });

        $total = $pendientes->flatten()->count();

        return response()->json(['mensaje' => $total ? "{$total} tarjeta(s) repartidas entre {$vendedores->count()} vendedores." : 'No había prospectos sin asignar.', 'asignados' => $total]);
    }

    private function asignarA(Interes $interes, Usuario $vendedor, Usuario $quien): void
    {
        $anterior = $interes->vendedor;
        if ($anterior?->correo === $vendedor->correo) {
            return;
        }

        $interes->update(['vendedor_correo' => $vendedor->correo, 'fecha_asignacion' => $interes->fecha_asignacion ?? now()]);
        $interes->recordatorios()->whereIn('estado', ['Pendiente', 'Atrasada'])->update(['usuario_correo' => $vendedor->correo]);

        if ($anterior) {
            $interes->interacciones()->create([
                'usuario_correo' => $quien->correo,
                'tipo' => 'Nota comercial',
                'descripcion' => "Reasignado de {$anterior->nombre} {$anterior->apellido} a {$vendedor->nombre} {$vendedor->apellido} por {$quien->nombre} {$quien->apellido}.",
                'resultado' => 'Reasignación con historial completo',
                'fecha' => now(),
            ]);
        }
    }
}
