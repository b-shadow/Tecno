<?php

namespace Datos;

use Datos\Modelos\Interes;
use Datos\Modelos\MotivoPerdida;
use Datos\Modelos\Usuario;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Persistencia de tarjetas, vendedores, estados e interacciones del embudo. */
class DInteres
{
    private const DETALLE = ['prospecto', 'vendedor:correo,nombre,apellido,telefono', 'ordenesPago.pago', 'ordenesPago.cuotas'];

    public function listar(Usuario $usuario, array $filtros): Collection
    {
        return $this->consultaAlcance($usuario)
            ->with(self::DETALLE)
            ->when($filtros['estado'] ?? null, fn ($query, $estado) => $query->where('estado', $estado))
            ->when($filtros['vendedor'] ?? null, fn ($query, $correo) => $query->where('vendedor_correo', $correo))
            ->when($filtros['sin_asignar'] ?? null, fn ($query) => $query->whereNull('vendedor_correo'))
            ->when(($filtros['buscar'] ?? '') !== '', function ($query) use ($filtros) {
                $like = DAlcance::escaparLike((string) $filtros['buscar']);

                return $query->where(fn ($subquery) => $subquery
                    ->where('programa_nombre', 'ilike', $like)
                    ->orWhere('modulo_nombre', 'ilike', $like)
                    ->orWhereHas('prospecto', fn ($prospecto) => $prospecto
                        ->where('nombre', 'ilike', $like)
                        ->orWhere('apellido', 'ilike', $like)
                        ->orWhereRaw("trim(nombre || ' ' || apellido) ilike ?", [$like])
                        ->orWhere('documento', 'ilike', $like)
                        ->orWhere('correo', 'ilike', $like)
                        ->orWhere('telefono', 'ilike', $like)));
            })
            ->when(
                ($filtros['orden'] ?? null) === 'registro',
                fn ($query) => $query->orderByDesc('fecha')->orderByDesc('nro_tarjeta'),
                fn ($query) => $query->orderByRaw('vendedor_correo is not null')->orderByDesc('ultima_actividad_en')->orderByDesc('nro_tarjeta'),
            )
            ->get();
    }

    public function motivos(): Collection
    {
        return MotivoPerdida::query()->orderBy('categoria')->orderBy('nombre')->get();
    }

    public function obtener(int $numero): Interes
    {
        return Interes::query()->findOrFail($numero);
    }

    public function detalle(int $numero): Interes
    {
        return Interes::query()->with(self::DETALLE + [
            'interacciones' => fn ($query) => $query->with('usuario:correo,nombre,apellido')->orderByDesc('fecha'),
            'recordatorios' => fn ($query) => $query->with('usuario:correo,nombre,apellido')->orderBy('fecha_programada'),
            'movimientos' => fn ($query) => $query->with('usuario:correo,nombre,apellido')->orderByDesc('fecha'),
            'ordenesPago' => fn ($query) => $query->with('items', 'descuentos.descuento', 'pago.comprobantes', 'cuotas.metodo', 'anuladaPor:correo,nombre,apellido', 'transaccionesStripe')->orderByDesc('nro_orden'),
            'prospecto.metodosPago' => fn ($query) => $query->orderByDesc('nro_metodo'),
            'prospecto.transaccionesStripe' => fn ($query) => $query->where('tipo', 'setup')->orderByDesc('nro_transaccion')->limit(3),
        ])->findOrFail($numero);
    }

    public function transaccion(callable $operacion): mixed
    {
        return DB::transaction($operacion);
    }

    public function bloquear(int $numero): Interes
    {
        return Interes::query()->lockForUpdate()->findOrFail($numero);
    }

    public function guardar(Interes $interes, array $datos): void
    {
        $interes->update($datos);
    }

    public function actualizarEstadoProspecto(Interes $interes, string $estado): void
    {
        $interes->prospecto->update(['estado' => $estado]);
    }

    public function vendedorAsignado(Interes $interes): ?Usuario
    {
        return $interes->vendedor;
    }

    public function vendedor(string $correo): Usuario
    {
        return Usuario::query()->findOrFail($correo);
    }

    public function vendedoresVigentes(): Collection
    {
        return Usuario::query()->where('rol', 'vendedor')->where('estado', 'activo')
            ->whereDate('fecha_inicio', '<=', now())->whereDate('fecha_fin', '>=', now())->orderBy('correo')->get();
    }

    public function cargaPorVendedor(array $correos): array
    {
        return Interes::query()->whereIn('vendedor_correo', $correos)->whereNotIn('estado', ['Convertido', 'Perdido'])
            ->groupBy('vendedor_correo')->selectRaw('vendedor_correo, count(*) as total')
            ->pluck('total', 'vendedor_correo')->all();
    }

    public function pendientesSinAsignar(Usuario $usuario): Collection
    {
        return $this->consultaAlcance($usuario)->whereNull('vendedor_correo')->orderBy('nro_tarjeta')->get()->groupBy('documento');
    }

    public function vendedorExistenteParaDocumento(string $documento, array $correos): ?string
    {
        return Interes::query()->where('documento', $documento)->whereIn('vendedor_correo', $correos)->value('vendedor_correo');
    }

    public function actualizarRecordatoriosPendientes(Interes $interes, string $vendedor): void
    {
        $interes->recordatorios()->whereIn('estado', ['Pendiente', 'Atrasada'])->update(['usuario_correo' => $vendedor]);
    }

    public function registrarInteraccion(Interes $interes, array $datos): void
    {
        $interes->interacciones()->create($datos);
    }

    public function refrescarDetalle(Interes $interes): Interes
    {
        return $interes->fresh()->load(self::DETALLE);
    }

    private function consultaAlcance(Usuario $usuario)
    {
        return Interes::query()
            ->when($usuario->rol === 'vendedor', fn ($query) => $query->where('vendedor_correo', $usuario->correo))
            ->when($usuario->rol === 'coordinador', fn ($query) => $query->whereIn('modulo_codigo', DAlcance::codigosModuloCoordinador($usuario->correo)));
    }
}
