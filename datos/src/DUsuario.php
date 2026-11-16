<?php

namespace Datos;

use Datos\Modelos\Programa;
use Datos\Modelos\ProgramaResponsable;
use Datos\Modelos\Usuario;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/** Consultas y escrituras de persistencia de usuarios. */
class DUsuario
{
    public function listar(array $filtros): array
    {
        return [
            'usuarios' => Usuario::query()
                ->with('programasACargo:programa_codigo,coordinador_correo')
                ->when(trim((string) ($filtros['buscar'] ?? '')) !== '', function ($query) use ($filtros) {
                    $like = DAlcance::escaparLike((string) $filtros['buscar']);

                    return $query->where(fn ($subquery) => $subquery
                        ->where('nombre', 'ilike', $like)
                        ->orWhere('apellido', 'ilike', $like)
                        ->orWhere('correo', 'ilike', $like));
                })
                ->when($filtros['rol'] ?? null, fn ($query, $rol) => $query->where('rol', $rol))
                ->when($filtros['estado'] ?? null, fn ($query, $estado) => $query->where('estado', $estado))
                ->orderBy('rol')->orderBy('nombre')->get(),
            'roles' => DB::table('roles')->orderBy('nombre')->get(['nombre', 'descripcion']),
            'programas' => Programa::query()->orderBy('nombre')->get(['codigo', 'nombre']),
        ];
    }

    public function vendedores(): Collection
    {
        return Usuario::query()->where('rol', 'vendedor')->where('estado', 'activo')
            ->orderBy('nombre')->get(['correo', 'nombre', 'apellido', 'foto']);
    }

    public function transaccion(callable $operacion): mixed
    {
        return DB::transaction($operacion);
    }

    public function crear(array $datos): Usuario
    {
        return Usuario::query()->create($datos);
    }

    public function obtener(string $correo): Usuario
    {
        return Usuario::query()->findOrFail($correo);
    }

    public function bloquearAdministradoresActivos(): void
    {
        Usuario::query()->where('rol', 'administrador')->orderBy('correo')->lockForUpdate()->get(['correo']);
    }

    public function existeOtroAdministradorActivo(string $correo): bool
    {
        return Usuario::query()->where('rol', 'administrador')->where('estado', 'activo')->whereKeyNot($correo)->exists();
    }

    public function actualizar(Usuario $usuario, array $datos): void
    {
        $usuario->update($datos);
    }

    public function asignarProgramas(Usuario $usuario, array $codigos): void
    {
        ProgramaResponsable::query()->where('coordinador_correo', $usuario->correo)
            ->whereNotIn('programa_codigo', $codigos)->delete();

        foreach ($codigos as $codigo) {
            ProgramaResponsable::query()->updateOrCreate(
                ['programa_codigo' => $codigo],
                ['coordinador_correo' => $usuario->correo],
            );
        }
    }

    public function quitarProgramas(string $correo): void
    {
        ProgramaResponsable::query()->where('coordinador_correo', $correo)->delete();
    }

    public function revocarTokens(Usuario $usuario, ?string $excepto = null): void
    {
        $usuario->tokens()->when($excepto, fn ($query, $hash) => $query->whereKeyNot($hash))->delete();
    }

    public function fresco(Usuario $usuario, bool $conProgramas = false): Usuario
    {
        return $usuario->fresh($conProgramas ? ['programasACargo'] : []) ?? $usuario;
    }

    /** Regla del formulario de asignación: el correo es de un vendedor activo. */
    public function esVendedorActivo(string $correo): bool
    {
        return Usuario::query()->whereKey($correo)->where('rol', 'vendedor')->where('estado', 'activo')->exists();
    }

    public function existeCorreo(string $correo): bool
    {
        return Usuario::query()->whereKey($correo)->exists();
    }
}
