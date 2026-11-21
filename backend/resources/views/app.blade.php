<!DOCTYPE html>
<html lang="es">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="app-base" content="{{ url('/') }}">
        <link rel="icon" type="image/png" href="{{ asset('favicon.png') }}">
        <meta name="theme-color" content="#083456">
        <title inertia>UNEXO · CRM Comercial Educativo</title>

        @viteReactRefresh
        @vite('resources/js/app.jsx')
        @inertiaHead
    </head>
    <body>
        @inertia
    </body>
</html>
