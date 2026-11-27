<?php

namespace App\Providers;

use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        // Fuerza bruta: por correo+IP, por IP (muchas cuentas desde un equipo) y por correo (una cuenta desde muchas IP).
        RateLimiter::for('crm-login', function (Request $request) {
            $correo = mb_strtolower((string) $request->input('correo'));

            return [
                Limit::perMinute(10)->by('par:'.$correo.'|'.$request->ip()),
                Limit::perMinute(30)->by('ip:'.$request->ip()),
                Limit::perMinute(20)->by('correo:'.$correo),
            ];
        });
    }
}
