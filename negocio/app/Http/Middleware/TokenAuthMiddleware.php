<?php

namespace App\Http\Middleware;

use App\Services\AuthService;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

/** Autenticación por token (API REST). Las reglas de vigencia están en AuthService::autenticarToken. */
class TokenAuthMiddleware
{
    public function __construct(private readonly AuthService $auth)
    {
    }

    public function handle(Request $request, Closure $next): Response
    {
        $plano = $request->bearerToken();
        if (! $plano) {
            return response()->json(['mensaje' => 'Debe iniciar sesión para continuar.'], 401);
        }

        $token = $this->auth->autenticarToken($plano);
        $request->attributes->set('auth_usuario', $token->usuario);
        $request->attributes->set('auth_token', $token);

        return $next($request);
    }
}
