<?php

namespace App\Http\Middleware;

use App\Models\ApiToken;
use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Symfony\Component\HttpFoundation\Response;

/** Autenticación por token (API REST): token vigente y credencial vigente (clase 03: estado, fecha_inicio, fecha_fin). */
class TokenAuthMiddleware
{
    public function handle(Request $request, Closure $next): Response
    {
        $plainToken = $request->bearerToken();

        if (! $plainToken) {
            return response()->json(['mensaje' => 'Debe iniciar sesión para continuar.'], 401);
        }

        $token = ApiToken::query()->with('usuario')->find(hash('sha256', $plainToken));

        if (! $token || ($token->expira_en && $token->expira_en->isPast())) {
            return response()->json(['mensaje' => 'Su sesión expiró. Vuelva a iniciar sesión.'], 401);
        }

        if (! $token->usuario || ! $token->usuario->vigente()) {
            $token->delete();

            return response()->json(['mensaje' => 'Su cuenta está inactiva o fuera de vigencia.'], 401);
        }

        $token->forceFill(['ultimo_uso_en' => now()])->save();
        // El trigger de historial del embudo (movimientos_interes) registra quién movió cada tarjeta.
        DB::select("select set_config('crm.usuario_correo', ?, false)", [$token->usuario->correo]);
        $request->attributes->set('auth_usuario', $token->usuario);
        $request->attributes->set('auth_token', $token);

        return $next($request);
    }
}
