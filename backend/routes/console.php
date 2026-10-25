<?php

use Illuminate\Foundation\Inspiring;
use Illuminate\Support\Facades\Artisan;

Artisan::command('inspire', function () {
    $this->comment(Inspiring::quote());
})->purpose('Display an inspiring quote');

// El control de migraciones de Laravel vive en el esquema `laravel` para no dejar una tabla
// sin relaciones en `public` (clase 46). Correr una vez antes de `php artisan migrate`.
Artisan::command('crm:preparar-bd', function () {
    \Illuminate\Support\Facades\DB::statement('CREATE SCHEMA IF NOT EXISTS laravel');
    $this->info('Esquema laravel listo.');
})->purpose('Crea el esquema que guarda el control de migraciones');
