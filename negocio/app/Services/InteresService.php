<?php

namespace App\Services;

use App\Exceptions\ReglaNegocioException;
use Datos\Modelos\Interes;
use Datos\Modelos\Usuario;
use Datos\Repositorios\InteresRepository;

/** Reglas de negocio del embudo, transiciones y asignación de prospectos. */
class InteresService
{
    public function __construct(private readonly InteresRepository $intereses)
    {
    }

    public function listar(Usuario $usuario, array $filtros): array
    {
        return [
            'intereses' => $this->intereses->listar($usuario, $filtros),
            'estados' => Interes::ESTADOS,
            'motivos' => $this->intereses->motivos(),
        ];
    }

    public function detalle(Usuario $usuario, int $numero): array
    {
        $interes = $this->intereses->detalle($numero);
        AlcanceService::autorizarTarjeta($usuario, $interes);

        return ['interes' => $interes, 'faltantes_conversion' => ConversionService::faltantes($interes)];
    }

    public function mover(Usuario $usuario, int $numero, array $datos): Interes
    {
        $interes = $this->intereses->obtener($numero);
        AlcanceService::autorizarTarjeta($usuario, $interes);
        ReglaNegocioException::si($interes->estado === 'Convertido', 'Una tarjeta convertida ya tiene matrícula: no se puede mover.');

        $this->intereses->transaccion(function () use ($usuario, $numero, $datos): void {
            $interes = $this->intereses->bloquear($numero);

            if ($datos['estado'] === 'Convertido') {
                $faltan = ConversionService::faltantes($interes);
                ReglaNegocioException::si((bool) $faltan, 'No se puede convertir todavía.', 422, ['faltantes' => $faltan]);
                ConversionService::procesar($interes, $usuario);

                return;
            }

            $this->intereses->guardar($interes, [
                'estado' => $datos['estado'],
                'motivo_perdida' => $datos['estado'] === 'Perdido' ? $datos['motivo_perdida'] : null,
                'observacion' => $datos['observacion'] ?? $interes->observacion,
                'ultima_actividad_en' => now(),
            ]);
            $this->intereses->actualizarEstadoProspecto($interes, $datos['estado']);

            if ($datos['estado'] === 'Perdido') {
                $this->intereses->registrarInteraccion($interes, [
                    'usuario_correo' => $usuario->correo,
                    'tipo' => 'Nota comercial',
                    'descripcion' => 'Marcado como Perdido. Motivo: '.$datos['motivo_perdida'].($datos['observacion'] ?? '' ? '. '.$datos['observacion'] : '.'),
                    'resultado' => 'Perdido',
                    'fecha' => now(),
                ]);
            }
        });

        return $this->intereses->refrescarDetalle($interes);
    }

    public function asignar(Usuario $usuario, int $numero, string $correoVendedor): Interes
    {
        $interes = $this->intereses->obtener($numero);
        AlcanceService::autorizarTarjeta($usuario, $interes);
        $vendedor = $this->intereses->vendedor($correoVendedor);

        $this->intereses->transaccion(fn () => $this->asignarA($interes, $vendedor, $usuario));

        return $this->intereses->refrescarDetalle($interes);
    }

    public function distribuir(Usuario $usuario): array
    {
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

        return [
            'mensaje' => $total
                ? "{$total} tarjeta(s) repartidas entre {$vendedores->count()} vendedores."
                : 'No había prospectos sin asignar.',
            'asignados' => $total,
        ];
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
