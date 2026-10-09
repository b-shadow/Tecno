<?php

namespace App\Http\Middleware;

use App\Models\ApiToken;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class TokenAuthMiddleware
{
    public function handle(Request $request, Closure $next): Response
    {
        $plainToken = $request->bearerToken();

        if (! $plainToken) {
            return response()->json(['mensaje' => 'Token de acceso requerido.'], 401);
        }

        $token = ApiToken::query()
            ->with('usuario')
            ->where('token_hash', hash('sha256', $plainToken))
            ->first();

        if (! $token || ($token->expira_en && $token->expira_en->isPast())) {
            return response()->json(['mensaje' => 'Token de acceso invalido.'], 401);
        }

        if (! $token->usuario || $token->usuario->estado !== 'activo') {
            return response()->json(['mensaje' => 'Usuario inactivo o no disponible.'], 403);
        }

        $token->forceFill(['ultimo_uso_en' => now()])->save();
        $request->attributes->set('auth_usuario', $token->usuario);
        $request->attributes->set('auth_token', $token);

        return $next($request);
    }
}
