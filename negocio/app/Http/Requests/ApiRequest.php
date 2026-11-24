<?php

namespace App\Http\Requests;

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

    /** Navegador del cliente, recortado a la columna de la bitácora. */
    public function navegador(): ?string
    {
        return mb_substr((string) $this->userAgent(), 0, 255) ?: null;
    }
}
