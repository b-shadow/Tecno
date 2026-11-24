<?php

use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\CatalogoController;
use App\Http\Controllers\Api\ExportacionController;
use App\Http\Controllers\Api\InteresController;
use App\Http\Controllers\Api\MotivoController;
use App\Http\Controllers\Api\NotificacionController;
use App\Http\Controllers\Api\PagoController;
use App\Http\Controllers\Api\ProspectoController;
use App\Http\Controllers\Api\ReporteController;
use App\Http\Controllers\Api\SeguimientoController;
use App\Http\Controllers\Api\SeguridadController;
use App\Http\Controllers\Api\SitioController;
use App\Http\Controllers\Api\UsuarioController;
use Illuminate\Support\Facades\Route;

/*
 * API REST (capa 2). Cada ruta privada pasa por `auth.token` y por la matriz de acceso:
 * `acceso:recurso` exige lectura en GET, modificación en POST/PUT/PATCH y eliminación en DELETE;
 * `acceso:a|b,nivel` acepta cualquiera de los recursos con ese nivel. Ver tablas recursos y permisos.
 */

// Público
Route::get('/salud', [SitioController::class, 'salud']);
Route::post('/login', [AuthController::class, 'login'])->middleware('throttle:crm-login');
Route::get('/catalogo', [CatalogoController::class, 'programas']);
Route::post('/registro-interes', [ProspectoController::class, 'registrarInteres'])->middleware('throttle:20,1');
Route::post('/visitas', [SitioController::class, 'visita'])->middleware('throttle:120,1');
Route::get('/buscar', [SitioController::class, 'buscar'])->middleware('throttle:90,1');
Route::get('/fotos/{archivo}', [SitioController::class, 'foto']);

Route::middleware('auth.token')->group(function (): void {
    // CU1 — sesión y perfil
    Route::get('/me', [AuthController::class, 'me']);
    Route::put('/perfil', [AuthController::class, 'actualizarPerfil']);
    Route::put('/perfil/password', [AuthController::class, 'cambiarPassword']);
    Route::post('/logout', [AuthController::class, 'logout']);

    // CU1 — usuarios, matriz de acceso y bitácora
    Route::middleware('acceso:usuarios')->group(function (): void {
        Route::get('/usuarios', [UsuarioController::class, 'index']);
        Route::post('/usuarios', [UsuarioController::class, 'store']);
        Route::put('/usuarios/{usuario}', [UsuarioController::class, 'update']);
        Route::patch('/usuarios/{usuario}/estado', [UsuarioController::class, 'cambiarEstado']);
        Route::delete('/usuarios/{usuario}/foto', [UsuarioController::class, 'foto']);
    });
    Route::get('/vendedores', [UsuarioController::class, 'vendedores'])->middleware('acceso:interesados|reportes|seguimiento|usuarios,lectura');
    Route::get('/matriz', [SeguridadController::class, 'matriz'])->middleware('acceso:matriz');
    Route::put('/matriz', [SeguridadController::class, 'asignar'])->middleware('acceso:matriz');
    Route::get('/bitacora', [SeguridadController::class, 'bitacora'])->middleware('acceso:bitacora');
    Route::get('/bitacora/resumen', [SeguridadController::class, 'resumen'])->middleware('acceso:bitacora');

    // CU2 — oferta académica
    Route::post('/catalogo/sincronizar', [CatalogoController::class, 'sincronizar'])->middleware('acceso:gestion-anuncios,modificacion');

    // CU3 — prospectos y asignación
    Route::get('/prospectos', [ProspectoController::class, 'index'])->middleware('acceso:prospectos');
    Route::post('/prospectos', [ProspectoController::class, 'store'])->middleware('acceso:prospectos');
    Route::post('/prospectos/importar', [ProspectoController::class, 'importarCSV'])->middleware('acceso:prospectos');
    Route::put('/prospectos/{prospecto}', [ProspectoController::class, 'update'])->middleware('acceso:prospectos');
    Route::post('/prospectos/{prospecto}/intereses', [ProspectoController::class, 'crearInteres'])->middleware('acceso:prospectos|embudo,modificacion');
    Route::patch('/intereses/{interes}/asignar', [InteresController::class, 'asignar'])->middleware('acceso:interesados');
    Route::post('/intereses/distribuir', [InteresController::class, 'distribuir'])->middleware('acceso:interesados');

    // CU4 / CU5 — embudo Kanban y motivos de pérdida
    Route::get('/intereses', [InteresController::class, 'index'])->middleware('acceso:embudo|interesados|agenda,lectura');
    Route::get('/intereses/{interes}', [InteresController::class, 'show'])->middleware('acceso:embudo|interesados|agenda,lectura');
    Route::patch('/intereses/{interes}/estado', [InteresController::class, 'mover'])->middleware('acceso:embudo');
    Route::get('/motivos', [MotivoController::class, 'index'])->middleware('acceso:motivos|embudo,lectura');
    Route::post('/motivos', [MotivoController::class, 'store'])->middleware('acceso:motivos');
    Route::put('/motivos/{motivo}', [MotivoController::class, 'update'])->middleware('acceso:motivos');
    Route::delete('/motivos/{motivo}', [MotivoController::class, 'destroy'])->middleware('acceso:motivos');

    // CU7 — interacciones y recordatorios
    Route::post('/intereses/{interes}/interacciones', [SeguimientoController::class, 'registrarInteraccion'])->middleware('acceso:agenda|embudo,modificacion');
    Route::post('/intereses/{interes}/recordatorios', [SeguimientoController::class, 'crearRecordatorio'])->middleware('acceso:agenda');
    Route::get('/recordatorios', [SeguimientoController::class, 'recordatorios'])->middleware('acceso:agenda|inicio-vendedor,lectura');
    Route::patch('/recordatorios/{recordatorio}/completar', [SeguimientoController::class, 'completarRecordatorio'])->middleware('acceso:agenda');
    Route::patch('/recordatorios/{recordatorio}/cancelar', [SeguimientoController::class, 'cancelarRecordatorio'])->middleware('acceso:agenda');
    Route::get('/notificaciones', [NotificacionController::class, 'index'])->middleware('acceso:notificaciones');
    Route::post('/notificaciones', [NotificacionController::class, 'enviar'])->middleware('acceso:notificaciones|agenda,modificacion');
    Route::patch('/notificaciones/{notificacion}/leida', [NotificacionController::class, 'marcarLeida'])->middleware('acceso:notificaciones,lectura');

    // CU6 — pagos (métodos, órdenes, cuotas) y matrícula
    Route::get('/descuentos', [PagoController::class, 'descuentos'])->middleware('acceso:agenda');
    Route::get('/prospectos/{prospecto}/metodos-pago', [PagoController::class, 'metodos'])->middleware('acceso:agenda');
    Route::post('/prospectos/{prospecto}/metodos-pago', [PagoController::class, 'registrarMetodo'])->middleware('acceso:agenda');
    Route::patch('/metodos-pago/{metodo}/estado', [PagoController::class, 'cambiarEstadoMetodo'])->middleware('acceso:agenda');
    Route::get('/ordenes-pago', [PagoController::class, 'ordenes'])->middleware('acceso:agenda|validacion-pagos,lectura');
    Route::post('/intereses/{interes}/ordenes-pago', [PagoController::class, 'crearOrden'])->middleware('acceso:agenda');
    Route::post('/ordenes-pago/{orden}/cuotas/{cuota}/comprobante', [PagoController::class, 'registrarComprobante'])->middleware('acceso:agenda')->whereNumber('cuota');
    Route::post('/ordenes-pago/{orden}/cuotas/{cuota}/pagar', [PagoController::class, 'pagarConTarjeta'])->middleware('acceso:agenda')->whereNumber('cuota');
    Route::get('/cuotas', [PagoController::class, 'cuotas'])->middleware('acceso:validacion-pagos');
    Route::patch('/ordenes-pago/{orden}/cuotas/{cuota}/aprobar', [PagoController::class, 'aprobar'])->middleware('acceso:validacion-pagos')->whereNumber('cuota');
    Route::patch('/ordenes-pago/{orden}/cuotas/{cuota}/rechazar', [PagoController::class, 'rechazar'])->middleware('acceso:validacion-pagos')->whereNumber('cuota');
    Route::get('/comprobantes/{comprobante}', [PagoController::class, 'comprobante'])->middleware('acceso:agenda|validacion-pagos,lectura');
    Route::get('/inscripciones', [SeguimientoController::class, 'inscripciones'])->middleware('acceso:alumnos|seguimiento,lectura');
    Route::get('/exportaciones/pendientes', [ExportacionController::class, 'pendientes'])->middleware('acceso:alumnos');
    Route::post('/exportaciones', [ExportacionController::class, 'exportar'])->middleware('acceso:alumnos');
    Route::get('/exportaciones', [ExportacionController::class, 'historial'])->middleware('acceso:alumnos');
    Route::patch('/exportaciones/{exportacion}', [ExportacionController::class, 'registrarResultado'])->middleware('acceso:alumnos');

    // CU8 — ventas, comisiones, reportes y estadísticas
    Route::get('/comisiones', [SeguimientoController::class, 'comisiones'])->middleware('acceso:seguimiento');
    Route::get('/comisiones/resumen', [SeguimientoController::class, 'resumenComisiones'])->middleware('acceso:seguimiento,modificacion');
    Route::patch('/comisiones/vendedores/{vendedor}/pagar', [SeguimientoController::class, 'pagarComisiones'])->middleware('acceso:seguimiento');
    Route::get('/configuracion/comision', [SeguimientoController::class, 'configuracionComision'])->middleware('acceso:seguimiento');
    Route::put('/configuracion/comision', [SeguimientoController::class, 'actualizarConfiguracionComision'])->middleware('acceso:seguimiento');
    Route::get('/dashboard', [ReporteController::class, 'dashboard'])->middleware('acceso:dashboard|inicio-vendedor,lectura');
    Route::get('/estadisticas/vendedor', [ReporteController::class, 'estadisticasVendedor'])->middleware('acceso:inicio-vendedor');
    Route::get('/reportes/estadisticas', [ReporteController::class, 'estadisticas'])->middleware('acceso:reportes');
    Route::get('/reportes/listado', [ReporteController::class, 'listado'])->middleware('acceso:reportes');
});
