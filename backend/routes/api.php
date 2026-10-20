<?php

use App\Http\Controllers\Api\SystemController;
use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\CatalogoController;
use App\Http\Controllers\Api\ExportacionController;
use App\Http\Controllers\Api\InteresController;
use App\Http\Controllers\Api\NotificacionController;
use App\Http\Controllers\Api\OrdenPagoController;
use App\Http\Controllers\Api\PagoController;
use App\Http\Controllers\Api\ProspectoController;
use App\Http\Controllers\Api\ReporteController;
use App\Http\Controllers\Api\SeguimientoController;
use App\Http\Controllers\Api\UsuarioController;
use Illuminate\Support\Facades\Route;

Route::get('/health', [SystemController::class, 'health']);
Route::post('/login', [AuthController::class, 'login']);
Route::get('/ofertas', [CatalogoController::class, 'ofertas']);
Route::get('/ofertas/{anuncio}', [CatalogoController::class, 'oferta']);
Route::post('/registro-interes', [ProspectoController::class, 'registrarInteres']);

Route::middleware('auth.token')->group(function (): void {
    Route::get('/me', [AuthController::class, 'me']);
    Route::put('/perfil', [AuthController::class, 'actualizarPerfil']);
    Route::put('/perfil/password', [AuthController::class, 'cambiarPassword']);
    Route::post('/logout', [AuthController::class, 'logout']);

    Route::get('/usuarios', [UsuarioController::class, 'index']);
    Route::post('/usuarios', [UsuarioController::class, 'store']);
    Route::put('/usuarios/{usuario}', [UsuarioController::class, 'update']);
    Route::patch('/usuarios/{usuario}/estado', [UsuarioController::class, 'cambiarEstado']);

    Route::get('/anuncios', [CatalogoController::class, 'anuncios']);

    Route::get('/prospectos', [ProspectoController::class, 'index']);
    Route::post('/prospectos', [ProspectoController::class, 'store']);
    Route::put('/prospectos/{prospecto}', [ProspectoController::class, 'update']);
    Route::patch('/prospectos/{prospecto}/asignar', [ProspectoController::class, 'asignarVendedor']);
    Route::patch('/prospectos/{prospecto}/estado', [ProspectoController::class, 'cambiarEstado']);
    Route::post('/prospectos/importar', [ProspectoController::class, 'importarCSV']);
    Route::post('/intereses', [ProspectoController::class, 'crearInteres']);
    Route::get('/intereses', [InteresController::class, 'index']);
    Route::get('/intereses/{interes}', [InteresController::class, 'show']);
    Route::patch('/intereses/{interes}/tomar', [InteresController::class, 'tomar']);
    Route::patch('/intereses/{interes}/estado', [InteresController::class, 'cambiarEstado']);
    Route::get('/prospectos/{prospecto}/intereses', [ProspectoController::class, 'intereses']);
    Route::post('/solicitudes-compra', [ProspectoController::class, 'crearSolicitud']);
    Route::get('/solicitudes-compra', [PagoController::class, 'solicitudes']);
    Route::get('/pagos', [PagoController::class, 'consultarPagos']);
    Route::post('/pagos/generar', [PagoController::class, 'generarPagoQR']);
    Route::get('/pagos/{pago}', [PagoController::class, 'show']);
    Route::post('/comprobantes', [PagoController::class, 'registrarComprobante']);
    Route::get('/comprobantes/{pago}', [PagoController::class, 'comprobantes']);
    Route::patch('/pagos/{pago}/aprobar', [PagoController::class, 'aprobar']);
    Route::patch('/pagos/{pago}/rechazar', [PagoController::class, 'rechazar']);

    Route::get('/prospectos/{prospecto}/interacciones', [SeguimientoController::class, 'interacciones']);
    Route::post('/interacciones', [SeguimientoController::class, 'registrarInteraccion']);
    Route::get('/recordatorios', [SeguimientoController::class, 'recordatorios']);
    Route::post('/recordatorios', [SeguimientoController::class, 'crearRecordatorio']);
    Route::patch('/recordatorios/{recordatorio}/completar', [SeguimientoController::class, 'completarRecordatorio']);
    Route::patch('/recordatorios/{recordatorio}/cancelar', [SeguimientoController::class, 'cancelarRecordatorio']);
    Route::post('/inscripciones/confirmar', [SeguimientoController::class, 'confirmarInscripcion']);
    Route::get('/inscripciones', [SeguimientoController::class, 'inscripciones']);
    Route::get('/comisiones', [SeguimientoController::class, 'comisiones']);
    Route::get('/comisiones/resumen', [SeguimientoController::class, 'resumenComisiones']);
    Route::patch('/comisiones/vendedores/{vendedor}/pagar', [SeguimientoController::class, 'pagarComisiones']);

    Route::get('/descuentos', [OrdenPagoController::class, 'descuentos']);
    Route::get('/ordenes-pago', [OrdenPagoController::class, 'index']);
    Route::post('/intereses/{interes}/ordenes-pago', [OrdenPagoController::class, 'store']);

    Route::get('/dashboard/metricas', [ReporteController::class, 'dashboard']);
    Route::get('/reportes/administrativos', [ReporteController::class, 'administrativo']);
    Route::get('/reportes/comerciales', [ReporteController::class, 'comercial']);
    Route::get('/reportes/listado', [ReporteController::class, 'listado']);
    Route::get('/estadisticas/vendedor', [ReporteController::class, 'estadisticasVendedor']);
    Route::post('/notificaciones/enviar', [NotificacionController::class, 'enviarCorreo']);
    Route::get('/notificaciones', [NotificacionController::class, 'listarNotificaciones']);
    Route::patch('/notificaciones/{notificacion}/leida', [NotificacionController::class, 'marcarLeida']);
    Route::get('/exportaciones/preparar', [ExportacionController::class, 'prepararDatosExportacion']);
    Route::post('/exportaciones/academico', [ExportacionController::class, 'exportarInscripciones']);
    Route::patch('/exportaciones/{exportacion}', [ExportacionController::class, 'registrarResultadoExportacion']);
    Route::get('/exportaciones', [ExportacionController::class, 'exportaciones']);
});
