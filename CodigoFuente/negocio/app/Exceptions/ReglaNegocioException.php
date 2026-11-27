<?php

namespace App\Exceptions;

use RuntimeException;

/**
 * Regla de negocio incumplida. La lanzan las clases N (capa 2, negocio);
 * bootstrap/app.php la convierte en una respuesta JSON con el mensaje en español.
 */
class ReglaNegocioException extends RuntimeException
{
    public function __construct(string $mensaje, public readonly int $estado = 422, public readonly array $datos = [])
    {
        parent::__construct($mensaje);
    }

    /** Lanza la excepción si se cumple la condición. */
    public static function si(bool $condicion, string $mensaje, int $estado = 422, array $datos = []): void
    {
        if ($condicion) {
            throw new self($mensaje, $estado, $datos);
        }
    }
}
