<?php

use Illuminate\Support\Facades\Route;

// Paginas Vue servidas por Inertia (MVC-MVVM). Los datos los piden a la API REST de routes/api.php;
// las reglas de acceso por rol estan en resources/js/access.js y cada endpoint las valida de nuevo.
// url() conserva el prefijo cuando Apache publica la app en /crm o /proyecto2.
foreach (['/' => '/anuncios', '/ofertas' => '/anuncios', '/chats' => '/agenda',
    '/pagos' => '/agenda', '/estadisticas-vendedor' => '/inicio-vendedor',
    '/comisiones' => '/seguimiento', '/exportaciones' => '/alumnos'] as $origen => $destino) {
    Route::get($origen, fn () => redirect(url($destino)));
}

Route::inertia('/inicio', 'HomeView');
Route::inertia('/anuncios', 'OfertasView');
Route::inertia('/login', 'LoginView');
Route::inertia('/dashboard', 'DashboardView');
Route::inertia('/inicio-vendedor', 'VendedorInicioView');
Route::inertia('/usuarios', 'UsuariosView');
Route::inertia('/gestion-anuncios', 'OfertasView');
Route::inertia('/prospectos', 'ProspectosView');
Route::inertia('/validacion-pagos', 'ValidacionPagosView');
Route::inertia('/alumnos', 'AlumnosView');
Route::inertia('/seguimiento', 'SeguimientoView');
Route::inertia('/interesados', 'InteresadosView');
Route::inertia('/agenda', 'AgendaView');
Route::inertia('/reportes', 'DashboardReportesView');
Route::inertia('/reportes-comerciales', 'ReportesComercialesView');
Route::inertia('/notificaciones', 'NotificacionesView');
