<?php

namespace App\Negocio;

use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Usuario\CambiarEstadoUsuarioRequest;
use App\Http\Requests\Usuario\UsuarioRequest;
use Datos\DUsuario;
use Datos\Modelos\Usuario;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;

/** Capa de negocio — CU1: cuentas de usuario (rol, vigencia, estado, foto con nombre legible y programas a cargo). */
class NUsuario
{
    public function __construct(private readonly DUsuario $usuarios)
    {
    }

    public function index(ConsultaRequest $r): JsonResponse
    {
        return response()->json($this->usuarios->listar($r->only(['buscar', 'rol', 'estado'])));
    }

    public function vendedores(): JsonResponse
    {
        return response()->json(['vendedores' => $this->usuarios->vendedores()]);
    }

    public function store(UsuarioRequest $r): JsonResponse
    {
        $datos = $r->validated();
        $usuario = $this->usuarios->transaccion(function () use ($datos): Usuario {
            $campos = collect($datos)->except(['foto', 'programas'])->all();
            $campos['password'] = Hash::make($datos['password']);
            $usuario = $this->usuarios->crear($campos);
            $this->guardarExtras($usuario, $datos);

            return $this->usuarios->fresco($usuario, true);
        });

        return response()->json(['mensaje' => 'Usuario creado correctamente.', 'usuario' => $usuario], 201);
    }

    public function update(UsuarioRequest $r, string $usuario): JsonResponse
    {
        $datos = $r->validated();
        $actorCorreo = $r->usuario()->correo;
        $actualizado = $this->usuarios->transaccion(function () use ($usuario, $datos, $actorCorreo): Usuario {
            $this->usuarios->bloquearAdministradoresActivos();
            $registro = $this->usuarios->obtener($usuario);
            $this->conservarAdministrador($registro, $datos + ['rol' => $registro->rol]);
            $revocar = ! empty($datos['password']) || $datos['estado'] !== 'activo' || $datos['rol'] !== $registro->rol;
            $campos = collect($datos)->except(['foto', 'programas', 'password'])->all();

            if (! empty($datos['password'])) {
                $campos['password'] = Hash::make($datos['password']);
            }

            $this->usuarios->actualizar($registro, $campos);
            $this->guardarExtras($this->usuarios->fresco($registro), $datos);

            if ($revocar && $registro->correo !== $actorCorreo) {
                $this->usuarios->revocarTokens($registro);
            }

            return $this->usuarios->fresco($registro, true);
        });

        return response()->json(['mensaje' => 'Usuario actualizado correctamente.', 'usuario' => $actualizado]);
    }

    public function cambiarEstado(CambiarEstadoUsuarioRequest $r, string $usuario): JsonResponse
    {
        $estado = $r->validated('estado');
        $actualizado = $this->usuarios->transaccion(function () use ($usuario, $estado): Usuario {
            $this->usuarios->bloquearAdministradoresActivos();
            $registro = $this->usuarios->obtener($usuario);
            $this->conservarAdministrador($registro, ['estado' => $estado, 'rol' => $registro->rol]);
            $this->usuarios->actualizar($registro, ['estado' => $estado]);

            if ($estado === 'inactivo') {
                $this->usuarios->revocarTokens($registro);
            }

            return $this->usuarios->fresco($registro);
        });

        return response()->json(['mensaje' => $estado === 'activo' ? 'Usuario activado.' : 'Usuario desactivado.', 'usuario' => $actualizado]);
    }

    public function foto(string $usuario): JsonResponse
    {
        $registro = $this->usuarios->obtener($usuario);

        if ($registro->foto && ($ruta = NFoto::ruta($registro->foto))) {
            @unlink($ruta);
        }

        $this->usuarios->actualizar($registro, ['foto' => null]);

        return response()->json(['mensaje' => 'Foto eliminada.']);
    }

    private function guardarExtras(Usuario $usuario, array $datos): void
    {
        if (! empty($datos['foto'])) {
            $this->usuarios->actualizar($usuario, [
                'foto' => NFoto::guardar($datos['foto'], $usuario->apellido, $usuario->nombre, $usuario->foto),
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
