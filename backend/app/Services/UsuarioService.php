<?php

namespace App\Services;

use App\Models\Usuario;
use App\Repositories\UsuarioRepository;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;

/** Reglas de gestión de cuentas, vigencias, fotografías y asignación de programas. */
class UsuarioService
{
    public function __construct(private readonly UsuarioRepository $usuarios)
    {
    }

    public function listar(array $filtros): array
    {
        return $this->usuarios->listar($filtros);
    }

    public function vendedores(): Collection
    {
        return $this->usuarios->vendedores();
    }

    public function crear(array $datos): Usuario
    {
        return $this->usuarios->transaccion(function () use ($datos): Usuario {
            $campos = collect($datos)->except(['foto', 'programas'])->all();
            $campos['password'] = Hash::make($datos['password']);
            $usuario = $this->usuarios->crear($campos);
            $this->guardarExtras($usuario, $datos);

            return $this->usuarios->fresco($usuario, true);
        });
    }

    public function actualizar(string $correo, array $datos, string $actorCorreo): Usuario
    {
        return $this->usuarios->transaccion(function () use ($correo, $datos, $actorCorreo): Usuario {
            $this->usuarios->bloquearAdministradoresActivos();
            $usuario = $this->usuarios->obtener($correo);
            $this->conservarAdministrador($usuario, $datos + ['rol' => $usuario->rol]);
            $revocar = ! empty($datos['password']) || $datos['estado'] !== 'activo' || $datos['rol'] !== $usuario->rol;
            $campos = collect($datos)->except(['foto', 'programas', 'password'])->all();

            if (! empty($datos['password'])) {
                $campos['password'] = Hash::make($datos['password']);
            }

            $this->usuarios->actualizar($usuario, $campos);
            $this->guardarExtras($usuario->refresh(), $datos);

            if ($revocar && $usuario->correo !== $actorCorreo) {
                $this->usuarios->revocarTokens($usuario);
            }

            return $this->usuarios->fresco($usuario, true);
        });
    }

    public function cambiarEstado(string $correo, string $estado): Usuario
    {
        return $this->usuarios->transaccion(function () use ($correo, $estado): Usuario {
            $this->usuarios->bloquearAdministradoresActivos();
            $usuario = $this->usuarios->obtener($correo);
            $this->conservarAdministrador($usuario, ['estado' => $estado, 'rol' => $usuario->rol]);
            $this->usuarios->actualizar($usuario, ['estado' => $estado]);

            if ($estado === 'inactivo') {
                $this->usuarios->revocarTokens($usuario);
            }

            return $this->usuarios->fresco($usuario);
        });
    }

    public function eliminarFoto(string $correo): void
    {
        $usuario = $this->usuarios->obtener($correo);

        if ($usuario->foto && ($ruta = Fotos::ruta($usuario->foto))) {
            @unlink($ruta);
        }

        $this->usuarios->actualizar($usuario, ['foto' => null]);
    }

    private function guardarExtras(Usuario $usuario, array $datos): void
    {
        if (! empty($datos['foto'])) {
            $this->usuarios->actualizar($usuario, [
                'foto' => Fotos::guardar($datos['foto'], $usuario->apellido, $usuario->nombre, $usuario->foto),
            ]);
        }

        if ($usuario->rol === 'coordinador' && array_key_exists('programas', $datos)) {
            $this->usuarios->asignarProgramas($usuario, $datos['programas'] ?? []);
        } elseif ($usuario->rol !== 'coordinador') {
            $this->usuarios->quitarProgramas($usuario->correo);
        }
    }

    private function conservarAdministrador(Usuario $usuario, array $datos): void
    {
        $pierdeAcceso = $datos['estado'] !== 'activo' || $datos['rol'] !== 'administrador';
        if ($usuario->rol === 'administrador' && $usuario->estado === 'activo' && $pierdeAcceso
            && ! $this->usuarios->existeOtroAdministradorActivo($usuario->correo)) {
            throw ValidationException::withMessages([
                'rol' => 'Debe conservar al menos un administrador activo.',
            ]);
        }
    }
}
