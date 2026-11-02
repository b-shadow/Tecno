<?php

namespace Datos;

use Datos\Modelos\CatalogoCache;
use Datos\Modelos\Interes;
use Datos\Modelos\Prospecto;
use Datos\Modelos\Usuario;
use Datos\DAlcance;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Acceso a PostgreSQL para prospectos y sus intereses comerciales. */
class DProspecto
{
    /** El prospecto de la ruta /prospectos/{documento} (404 si no existe). */
    public function obtener(string $documento): Prospecto
    {
        return Prospecto::query()->findOrFail($documento);
    }

    public function transaccion(callable $operacion): mixed
    {
        return DB::transaction($operacion);
    }

    public function encontrarPorDocumentoOCorreoBloqueado(string $documento, string $correo): ?Prospecto
    {
        return Prospecto::query()->lockForUpdate()->find($documento)
            ?? Prospecto::query()->whereRaw('lower(correo) = ?', [$correo])->lockForUpdate()->first();
    }

    public function buscar(Usuario $usuario, string $texto, ?string $origen): Collection
    {
        return DAlcance::prospectos(Prospecto::query(), $usuario)
            ->with(['intereses' => fn ($q) => DAlcance::intereses($q, $usuario)->with('vendedor:correo,nombre,apellido')])
            ->when(trim($texto) !== '', function ($q) use ($texto) {
                $like = DAlcance::escaparLike($texto);

                return $q->where(fn ($s) => $s
                    ->where('nombre', 'ilike', $like)->orWhere('apellido', 'ilike', $like)
                    ->orWhere('correo', 'ilike', $like)->orWhere('documento', 'ilike', $like)
                    ->orWhere('telefono', 'ilike', $like));
            })
            ->when($origen, fn ($q, $valor) => $q->where('origen', $valor))
            ->orderByDesc('fecha_registro')->get();
    }

    public function crear(array $datos): Prospecto
    {
        return Prospecto::query()->create($datos);
    }

    public function actualizar(Prospecto $prospecto, array $datos): Prospecto
    {
        $prospecto->update($datos);

        return $prospecto;
    }

    public function estaDentroDeCartera(Prospecto $prospecto, Usuario $usuario): bool
    {
        return DAlcance::prospectos(Prospecto::query()->whereKey($prospecto->documento), $usuario)->exists();
    }

    public function conIntereses(Prospecto $prospecto): Prospecto
    {
        return $prospecto->load('intereses');
    }

    public function actualizado(Prospecto $prospecto): Prospecto
    {
        return $prospecto->fresh();
    }

    public function existeDocumentoOCorreo(string $documento, string $correo): bool
    {
        return Prospecto::query()->whereKey($documento)->orWhereRaw('lower(correo) = ?', [$correo])->exists();
    }

    public function modulosSolicitados(array $datos): Collection
    {
        if (! empty($datos['modulo_codigos'])) {
            return CatalogoCache::query()->where('estado', 'abierto')->whereIn('codigo', $datos['modulo_codigos'])->with('programa')->get();
        }

        return CatalogoCache::query()->where('estado', 'abierto')
            ->when(! empty($datos['modulo_codigo']), fn ($q) => $q->whereKey($datos['modulo_codigo']))
            ->when(empty($datos['modulo_codigo']), fn ($q) => $q->where('programa_codigo', $datos['programa_codigo'] ?? ''))
            ->with('programa')->get();
    }

    public function vendedorExistente(Prospecto $prospecto): ?string
    {
        return $prospecto->intereses()->whereNotNull('vendedor_correo')->value('vendedor_correo');
    }

    public function crearInteres(Prospecto $prospecto, CatalogoCache $modulo, ?string $vendedor): Interes
    {
        return Interes::query()->firstOrCreate(
            ['documento' => $prospecto->documento, 'modulo_codigo' => $modulo->codigo],
            [
                'anuncio_codigo' => $modulo->anuncio_codigo,
                'programa_nombre' => $modulo->programa->nombre,
                'modulo_nombre' => $modulo->nombre,
                'modulo_descripcion' => $modulo->descripcion,
                'precio' => $modulo->precio,
                'estado' => 'Nuevo', 'fecha' => now(), 'vendedor_correo' => $vendedor,
                'fecha_asignacion' => $vendedor ? now() : null,
            ],
        );
    }
}
