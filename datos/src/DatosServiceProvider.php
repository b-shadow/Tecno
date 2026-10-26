<?php

namespace Datos;

use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\ServiceProvider;

/**
 * Capa 3 (persistencia). La capa de negocio la carga como paquete de Composer: aquí viven las migraciones
 * (tablas, triggers y contadores de PostgreSQL), los modelos y los repositorios, y nada más toca la BD.
 */
class DatosServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        $this->loadMigrationsFrom(dirname(__DIR__).'/migraciones');

        if ($this->app->runningInConsole()) {
            // El control de migraciones de Laravel vive en el esquema `laravel` para no dejar una tabla sin
            // relaciones en `public` (clase 46). Correr una vez antes de `php artisan migrate`.
            Artisan::command('crm:preparar-bd', function () {
                DB::statement('CREATE SCHEMA IF NOT EXISTS laravel');
                $this->info('Esquema laravel listo.');
            })->purpose('Crea el esquema que guarda el control de migraciones');
        }
    }
}
