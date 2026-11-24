<?php

namespace App\Http\Middleware;

use Datos\Modelos\Bitacora;
use App\Services\Acceso;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

/**
 * Matriz de acceso (enunciado 4): `acceso:recurso` exige el nivel según el método HTTP
 * (GET lectura, POST/PUT/PATCH modificación, DELETE eliminación); `acceso:a|b,lectura` acepta cualquiera de los recursos.
 * Un intento sin permiso queda en la bitácora como acceso_denegado.
 */
class AccesoRecurso
{
    public function handle(Request $request, Closure $next, string $recursos, ?string $nivel = null): Response
    {
        $usuario = $request->attributes->get('auth_usuario');
        $nivel ??= match ($request->method()) {
            'GET', 'HEAD' => 'lectura',
            'DELETE' => 'eliminacion',
            default => 'modificacion',
        };
        $lista = explode('|', $recursos);

        foreach ($lista as $recurso) {
            if (Acceso::permite($usuario, $recurso, $nivel)) {
                return $next($request);
            }
        }

        Bitacora::registrar('acceso_denegado', $request, $usuario?->correo, $lista[0]);

        return response()->json(['mensaje' => 'No tiene permiso para realizar esta acción.'], 403);
    }
}
