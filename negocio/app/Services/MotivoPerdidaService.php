<?php

namespace App\Services;

use Datos\Modelos\MotivoPerdida;
use Datos\Repositorios\MotivoPerdidaRepository;
use Illuminate\Support\Collection;
use Illuminate\Validation\ValidationException;

/** Reglas de negocio del catálogo de motivos de pérdida. */
class MotivoPerdidaService
{
    private const SISTEMA = 'Sin clasificar (web)';

    public function __construct(private readonly MotivoPerdidaRepository $motivos)
    {
    }

    public function listar(): Collection
    {
        return $this->motivos->listarConUsos();
    }

    public function crear(array $datos): MotivoPerdida
    {
        $this->validarNombreUnico($datos['nombre']);

        return $this->motivos->crear($datos);
    }

    public function actualizar(string $nombre, array $datos): MotivoPerdida
    {
        $motivo = $this->motivos->obtener($nombre);
        $this->validarEditable($motivo);
        $this->validarNombreUnico($datos['nombre'], $nombre);

        return $this->motivos->actualizar($motivo, $datos);
    }

    public function eliminar(string $nombre): void
    {
        $motivo = $this->motivos->obtener($nombre);
        $this->validarEditable($motivo);

        if ($this->motivos->estaEnUso($nombre)) {
            throw ValidationException::withMessages([
                'motivo' => 'No se puede eliminar: hay prospectos perdidos con este motivo.',
            ]);
        }

        $this->motivos->eliminar($motivo);
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
