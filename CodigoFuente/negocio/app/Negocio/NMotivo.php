<?php

namespace App\Negocio;

use App\Http\Requests\Motivo\MotivoRequest;
use Datos\DMotivo;
use Datos\Modelos\MotivoPerdida;
use Illuminate\Http\JsonResponse;
use Illuminate\Validation\ValidationException;

/** Capa de negocio — CU5: motivos de pérdida y su clasificación por categoría (RF3.3). */
class NMotivo
{
    private const SISTEMA = 'Sin clasificar (web)';

    public function __construct(private readonly DMotivo $motivos)
    {
    }

    public function index(): JsonResponse
    {
        return response()->json(['motivos' => $this->motivos->listarConUsos(), 'categorias' => MotivoPerdida::CATEGORIAS]);
    }

    public function store(MotivoRequest $r): JsonResponse
    {
        $datos = $r->validated();
        $this->validarNombreUnico($datos['nombre']);

        return response()->json(['mensaje' => 'Motivo registrado.', 'motivo' => $this->motivos->crear($datos)], 201);
    }

    /** Renombrar se propaga a las tarjetas (FK ON UPDATE CASCADE). */
    public function update(MotivoRequest $r, string $motivo): JsonResponse
    {
        $datos = $r->validated();
        $registro = $this->motivos->obtener($motivo);
        $this->validarEditable($registro);
        $this->validarNombreUnico($datos['nombre'], $motivo);
        $this->motivos->actualizar($registro, $datos);

        return response()->json(['mensaje' => 'Motivo actualizado.']);
    }

    public function destroy(string $motivo): JsonResponse
    {
        $registro = $this->motivos->obtener($motivo);
        $this->validarEditable($registro);

        if ($this->motivos->estaEnUso($motivo)) {
            throw ValidationException::withMessages([
                'motivo' => 'No se puede eliminar: hay prospectos perdidos con este motivo.',
            ]);
        }

        $this->motivos->eliminar($registro);

        return response()->json(['mensaje' => 'Motivo eliminado.']);
    }

    private function validarEditable(MotivoPerdida $motivo): void
    {
        if ($motivo->nombre === self::SISTEMA) {
            throw ValidationException::withMessages([
                'motivo' => 'Este motivo lo usa el sistema y no se puede cambiar ni eliminar.',
            ]);
        }
    }

    private function validarNombreUnico(string $nombre, ?string $excepto = null): void
    {
        if ($this->motivos->existeNombre($nombre, $excepto)) {
            throw ValidationException::withMessages(['nombre' => 'El motivo ya está registrado.']);
        }
    }
}
