<?php

use Illuminate\Support\Facades\Route;

// Capa de presentación: páginas React servidas por Inertia sobre la plantilla Blade (resources/views/app.blade.php).
// Los datos los pide cada página a la API REST (routes/api.php), que valida la matriz de acceso en cada llamada.
// url() conserva el prefijo cuando Apache publica la app en /inf513/grupo05sa/proyecto2.
foreach (['/' => '/anuncios', '/ofertas' => '/anuncios', '/inicio' => '/anuncios', '/chats' => '/agenda', '/pagos' => '/agenda',
    '/estadisticas-vendedor' => '/inicio-vendedor', '/comisiones' => '/seguimiento', '/exportaciones' => '/alumnos',
    '/reportes-comerciales' => '/reportes'] as $origen => $destino) {
    Route::get($origen, fn () => redirect(url($destino)));
}

$paginas = [
    '/anuncios' => 'Catalogo', '/gestion-anuncios' => 'Catalogo', '/login' => 'Login',
    '/dashboard' => 'Dashboard', '/inicio-vendedor' => 'MiDia', '/embudo' => 'Embudo',
    '/prospectos' => 'Prospectos', '/interesados' => 'Asignacion', '/agenda' => 'Agenda', '/motivos-perdida' => 'Motivos',
    '/validacion-pagos' => 'ValidacionPagos', '/alumnos' => 'Matriculas', '/seguimiento' => 'Comisiones',
    '/reportes' => 'Reportes', '/notificaciones' => 'Notificaciones',
    '/usuarios' => 'Usuarios', '/matriz-acceso' => 'Matriz', '/bitacora' => 'Bitacora',
];
foreach ($paginas as $ruta => $pagina) {
    Route::inertia($ruta, $pagina);
}
