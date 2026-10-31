<?php

namespace App\Negocio;

use App\Exceptions\ReglaNegocioException;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Interes\AsignarInteresRequest;
use App\Http\Requests\Interes\MoverInteresRequest;
use Datos\DInteres;
use Datos\Modelos\Interes;
use Datos\Modelos\Usuario;
use Illuminate\Http\JsonResponse;

/** Capa de negocio — CU3 (asignación y Round-Robin), CU4 (embudo Kanban) y CU5 (pérdida con motivo). */
class NInteres
{
    public function __construct(private readonly DInteres $intereses)
    {
    }

    public function index(ConsultaRequest $r): JsonResponse
    {
        return response()->json([
            'intereses' => $this->intereses->listar($r->usuario(), $r->only(['buscar', 'estado', 'vendedor', 'sin_asignar'])),
            'estados' => Interes::ESTADOS,
            'motivos' => $this->intereses->motivos(),
        ]);
    }

    public function show(ConsultaRequest $r, int $interes): JsonResponse
    {
        $registro = $this->intereses->detalle($interes);
        NAlcance::autorizarTarjeta($r->usuario(), $registro);

        return response()->json(['interes' => $registro, 'faltantes_conversion' => NConversion::faltantes($registro)]);
    }

    public function mover(MoverInteresRequest $r, int $interes): JsonResponse
    {
        $usuario = $r->usuario();
        $datos = $r->validated();
        $registro = $this->intereses->obtener($interes);
        NAlcance::autorizarTarjeta($usuario, $registro);
        ReglaNegocioException::si($registro->estado === 'Convertido', 'Una tarjeta convertida ya tiene matrícula: no se puede mover.');

        $this->intereses->transaccion(function () use ($usuario, $interes, $datos): void {
            $tarjeta = $this->intereses->bloquear($interes);

            if ($datos['estado'] === 'Convertido') {
                $faltan = NConversion::faltantes($tarjeta);
                ReglaNegocioException::si((bool) $faltan, 'No se puede convertir todavía.', 422, ['faltantes' => $faltan]);
                NConversion::procesar($tarjeta, $usuario);

                return;
            }

            $this->intereses->guardar($tarjeta, [
                'estado' => $datos['estado'],
                'motivo_perdida' => $datos['estado'] === 'Perdido' ? $datos['motivo_perdida'] : null,
                'observacion' => $datos['observacion'] ?? $tarjeta->observacion,
                'ultima_actividad_en' => now(),
            ]);
            $this->intereses->actualizarEstadoProspecto($tarjeta, $datos['estado']);

            if ($datos['estado'] === 'Perdido') {
                $this->intereses->registrarInteraccion($tarjeta, [
                    'usuario_correo' => $usuario->correo,
                    'tipo' => 'Nota comercial',
                    'descripcion' => 'Marcado como Perdido. Motivo: '.$datos['motivo_perdida'].($datos['observacion'] ?? '' ? '. '.$datos['observacion'] : '.'),
                    'resultado' => 'Perdido',
                    'fecha' => now(),
                ]);
            }
        });

        return response()->json([
            'mensaje' => "Tarjeta movida a {$datos['estado']}.",
            'interes' => $this->intereses->refrescarDetalle($registro),
        ]);
    }

    public function asignar(AsignarInteresRequest $r, int $interes): JsonResponse
    {
        $usuario = $r->usuario();
        $registro = $this->intereses->obtener($interes);
        NAlcance::autorizarTarjeta($usuario, $registro);
        $vendedor = $this->intereses->vendedor($r->validated('vendedor_correo'));

        $this->intereses->transaccion(fn () => $this->asignarA($registro, $vendedor, $usuario));

        return response()->json(['mensaje' => 'Prospecto asignado.', 'interes' => $this->intereses->refrescarDetalle($registro)]);
    }

    public function distribuir(ConsultaRequest $r): JsonResponse
    {
        $usuario = $r->usuario();
        $vendedores = $this->intereses->vendedoresVigentes();
        ReglaNegocioException::si($vendedores->isEmpty(), 'No hay vendedores activos para repartir.');

        $cargaBase = $this->intereses->cargaPorVendedor($vendedores->pluck('correo')->all());
        $carga = $vendedores->mapWithKeys(fn ($vendedor) => [
            $vendedor->correo => (int) ($cargaBase[$vendedor->correo] ?? 0),
        ])->all();
        $pendientes = $this->intereses->pendientesSinAsignar($usuario);

        $this->intereses->transaccion(function () use ($usuario, $pendientes, $vendedores, &$carga): void {
            foreach ($pendientes as $documento => $tarjetas) {
                $actual = $this->intereses->vendedorExistenteParaDocumento($documento, array_keys($carga));
                $elegido = $actual ?? array_keys($carga, min($carga))[0];
                foreach ($tarjetas as $tarjeta) {
                    $this->asignarA($tarjeta, $vendedores->firstWhere('correo', $elegido), $usuario);
                    $carga[$elegido]++;
                }
            }
        });

        $total = $pendientes->flatten()->count();

        return response()->json([
            'mensaje' => $total
                ? "{$total} tarjeta(s) repartidas entre {$vendedores->count()} vendedores."
                : 'No había prospectos sin asignar.',
            'asignados' => $total,
        ]);
    }

    private function asignarA(Interes $interes, Usuario $vendedor, Usuario $quien): void
    {
        $anterior = $this->intereses->vendedorAsignado($interes);
        if ($anterior?->correo === $vendedor->correo) {
            return;
        }

        $this->intereses->guardar($interes, [
            'vendedor_correo' => $vendedor->correo,
            'fecha_asignacion' => $interes->fecha_asignacion ?? now(),
        ]);
        $this->intereses->actualizarRecordatoriosPendientes($interes, $vendedor->correo);

        if ($anterior) {
            $this->intereses->registrarInteraccion($interes, [
                'usuario_correo' => $quien->correo,
                'tipo' => 'Nota comercial',
                'descripcion' => "Reasignado de {$anterior->nombre} {$anterior->apellido} a {$vendedor->nombre} {$vendedor->apellido} por {$quien->nombre} {$quien->apellido}.",
                'resultado' => 'Reasignación con historial completo',
                'fecha' => now(),
            ]);
        }
    }
}
