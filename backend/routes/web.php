<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return response()->json([
        'system' => 'CRM Comercial Educativo',
        'status' => 'api',
    ]);
});
