<?php

namespace App\Http\Requests;

use Closure;
use Datos\Modelos\Usuario;
use Illuminate\Foundation\Http\FormRequest;

/**
 * Base de las peticiones de la API: las reglas de forma y los mensajes en español viven en cada subclase.
 * El permiso ya lo resolvieron los middleware auth.token y acceso: (matriz rol × recurso).
 */
abstract class ApiRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** Usuario autenticado por TokenAuthMiddleware (null en rutas públicas). */
    public function usuario(): ?Usuario
    {
        return $this->attributes->get('auth_usuario');
    }

    /**
     * Regla que consulta la BD a través de la capa de datos (los exists/unique de Laravel irían directo a la BD):
     * $cumple recibe el valor y responde con un método de una clase D*; si no cumple, $mensaje en español.
     */
    protected function segun(callable $cumple, string $mensaje = 'validation.exists'): Closure
    {
        return function (string $atributo, mixed $valor, Closure $fail) use ($cumple, $mensaje): void {
            if (! is_scalar($valor) || ! $cumple((string) $valor)) {
                $fail($mensaje)->translate();
            }
        };
    }

    /** Navegador del cliente, recortado a la columna de la bitácora. */
    public function navegador(): ?string
    {
        return mb_substr((string) $this->userAgent(), 0, 255) ?: null;
    }
}
