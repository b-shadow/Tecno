<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\ConsultaRequest;
use App\Http\Requests\Usuario\CambiarEstadoUsuarioRequest;
use App\Http\Requests\Usuario\UsuarioRequest;
use App\Services\UsuarioService;
use Illuminate\Http\JsonResponse;

/** CU1: gestión de usuarios (rol, vigencia, estado y foto con nombre legible). */
class UsuarioController extends Controller
{
    public function __construct(private readonly UsuarioService $usuarios)
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
        return response()->json(['mensaje' => 'Usuario creado correctamente.', 'usuario' => $this->usuarios->crear($r->validated())], 201);
    }

    public function update(UsuarioRequest $r, string $usuario): JsonResponse
    {
        $actualizado = $this->usuarios->actualizar($usuario, $r->validated(), $r->usuario()->correo);

        return response()->json(['mensaje' => 'Usuario actualizado correctamente.', 'usuario' => $actualizado]);
    }

    public function cambiarEstado(CambiarEstadoUsuarioRequest $r, string $usuario): JsonResponse
    {
        $estado = $r->validated('estado');
        $actualizado = $this->usuarios->cambiarEstado($usuario, $estado);

        return response()->json(['mensaje' => $estado === 'activo' ? 'Usuario activado.' : 'Usuario desactivado.', 'usuario' => $actualizado]);
    }

    public function foto(string $usuario): JsonResponse
    {
        $this->usuarios->eliminarFoto($usuario);

        return response()->json(['mensaje' => 'Foto eliminada.']);
    }
}
