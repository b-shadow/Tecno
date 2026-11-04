<?php

use App\Negocio\NAuth;
use App\Negocio\NCatalogo;
use App\Negocio\NExportacion;
use App\Negocio\NInteres;
use App\Negocio\NMotivo;
use App\Negocio\NNotificacion;
use App\Negocio\NPago;
use App\Negocio\NProspecto;
use App\Negocio\NReporte;
use App\Negocio\NSeguimiento;
use App\Negocio\NSeguridad;
use App\Negocio\NSitio;
use App\Negocio\NUsuario;
use Illuminate\Support\Facades\Route;

/*
 * API REST (capa 2). Cada ruta privada pasa por `auth.token` y por la matriz de acceso:
 * `acceso:recurso` exige lectura en GET, modificación en POST/PUT/PATCH y eliminación en DELETE;
 * `acceso:a|b,nivel` acepta cualquiera de los recursos con ese nivel. Ver tablas recursos y permisos.
 */

// Público
Route::get('/salud', [NSitio::class, 'salud']);
Route::post('/login', [NAuth::class, 'login'])->middleware('throttle:crm-login');
Route::get('/catalogo', [NCatalogo::class, 'programas']);
Route::post('/registro-interes', [NProspecto::class, 'registrarInteres'])->middleware('throttle:20,1');
Route::post('/visitas', [NSitio::class, 'visita'])->middleware('throttle:120,1');
Route::get('/buscar', [NSitio::class, 'buscar'])->middleware('throttle:90,1');
Route::get('/fotos/{archivo}', [NSitio::class, 'foto']);

// CU6 — webhook oficial de Stripe (autenticado por firma HMAC Stripe-Signature)
Route::post('/stripe/webhook', [NPago::class, 'webhook']);

Route::middleware('auth.token')->group(function (): void {
    // CU1 — sesión y perfil
    Route::get('/me', [NAuth::class, 'me']);
    Route::put('/perfil', [NAuth::class, 'actualizarPerfil']);
    Route::put('/perfil/password', [NAuth::class, 'cambiarPassword']);
    Route::post('/logout', [NAuth::class, 'logout']);

    // CU1 — usuarios, matriz de acceso y bitácora
    Route::middleware('acceso:usuarios')->group(function (): void {
        Route::get('/usuarios', [NUsuario::class, 'index']);
        Route::post('/usuarios', [NUsuario::class, 'store']);
        Route::put('/usuarios/{usuario}', [NUsuario::class, 'update']);
        Route::patch('/usuarios/{usuario}/estado', [NUsuario::class, 'cambiarEstado']);
        Route::delete('/usuarios/{usuario}/foto', [NUsuario::class, 'foto']);
    });
    Route::get('/vendedores', [NUsuario::class, 'vendedores'])->middleware('acceso:interesados|reportes|seguimiento|usuarios,lectura');
    Route::get('/matriz', [NSeguridad::class, 'matriz'])->middleware('acceso:matriz');
    Route::put('/matriz', [NSeguridad::class, 'asignar'])->middleware('acceso:matriz');
    Route::get('/bitacora', [NSeguridad::class, 'bitacora'])->middleware('acceso:bitacora');
    Route::get('/bitacora/resumen', [NSeguridad::class, 'resumen'])->middleware('acceso:bitacora');

    // CU2 — oferta académica
    Route::post('/catalogo/sincronizar', [NCatalogo::class, 'sincronizar'])->middleware('acceso:gestion-anuncios,modificacion');

    // CU3 — prospectos y asignación
    Route::get('/prospectos', [NProspecto::class, 'index'])->middleware('acceso:prospectos');
    Route::post('/prospectos', [NProspecto::class, 'store'])->middleware('acceso:prospectos');
    Route::post('/prospectos/importar', [NProspecto::class, 'importarCSV'])->middleware('acceso:prospectos');
    Route::put('/prospectos/{prospecto}', [NProspecto::class, 'update'])->middleware('acceso:prospectos');
    Route::post('/prospectos/{prospecto}/intereses', [NProspecto::class, 'crearInteres'])->middleware('acceso:prospectos|embudo,modificacion');
    Route::patch('/intereses/{interes}/asignar', [NInteres::class, 'asignar'])->middleware('acceso:interesados');
    Route::post('/intereses/distribuir', [NInteres::class, 'distribuir'])->middleware('acceso:interesados');

    // CU4 / CU5 — embudo Kanban y motivos de pérdida
    Route::get('/intereses', [NInteres::class, 'index'])->middleware('acceso:embudo|interesados|agenda,lectura');
    Route::get('/intereses/{interes}', [NInteres::class, 'show'])->middleware('acceso:embudo|interesados|agenda,lectura');
    Route::patch('/intereses/{interes}/estado', [NInteres::class, 'mover'])->middleware('acceso:embudo');
    Route::get('/motivos', [NMotivo::class, 'index'])->middleware('acceso:motivos|embudo,lectura');
    Route::post('/motivos', [NMotivo::class, 'store'])->middleware('acceso:motivos');
    Route::put('/motivos/{motivo}', [NMotivo::class, 'update'])->middleware('acceso:motivos');
    Route::delete('/motivos/{motivo}', [NMotivo::class, 'destroy'])->middleware('acceso:motivos');

    // CU7 — interacciones y recordatorios
    Route::post('/intereses/{interes}/interacciones', [NSeguimiento::class, 'registrarInteraccion'])->middleware('acceso:agenda|embudo,modificacion');
    Route::post('/intereses/{interes}/recordatorios', [NSeguimiento::class, 'crearRecordatorio'])->middleware('acceso:agenda');
    Route::get('/recordatorios', [NSeguimiento::class, 'recordatorios'])->middleware('acceso:agenda|inicio-vendedor,lectura');
    Route::patch('/recordatorios/{recordatorio}/completar', [NSeguimiento::class, 'completarRecordatorio'])->middleware('acceso:agenda');
    Route::patch('/recordatorios/{recordatorio}/cancelar', [NSeguimiento::class, 'cancelarRecordatorio'])->middleware('acceso:agenda');
    Route::get('/notificaciones', [NNotificacion::class, 'index'])->middleware('acceso:notificaciones');
    Route::post('/notificaciones', [NNotificacion::class, 'enviar'])->middleware('acceso:notificaciones|agenda,modificacion');
    Route::patch('/notificaciones/{notificacion}/leida', [NNotificacion::class, 'marcarLeida'])->middleware('acceso:notificaciones,lectura');

    // CU6 — pagos (métodos, órdenes, cuotas), Stripe Checkout Sandbox y matrícula
    Route::get('/descuentos', [NPago::class, 'descuentos'])->middleware('acceso:agenda');
    Route::get('/prospectos/{prospecto}/metodos-pago', [NPago::class, 'metodos'])->middleware('acceso:agenda');
    Route::post('/prospectos/{prospecto}/metodos-pago', [NPago::class, 'registrarMetodo'])->middleware('acceso:agenda');
    Route::post('/prospectos/{prospecto}/metodos-pago/stripe-setup', [NPago::class, 'crearSetupTarjeta'])->middleware('acceso:agenda');
    Route::patch('/metodos-pago/{metodo}/estado', [NPago::class, 'cambiarEstadoMetodo'])->middleware('acceso:agenda');
    Route::get('/ordenes-pago', [NPago::class, 'ordenes'])->middleware('acceso:agenda|validacion-pagos,lectura');
    Route::post('/intereses/{interes}/ordenes-pago', [NPago::class, 'crearOrden'])->middleware('acceso:agenda');
    Route::patch('/ordenes-pago/{orden}/anular', [NPago::class, 'anularOrden'])->middleware('acceso:agenda')->whereNumber('orden');
    Route::post('/ordenes-pago/{orden}/cuotas/{cuota}/comprobante', [NPago::class, 'registrarComprobante'])->middleware('acceso:agenda')->whereNumber('cuota');
    Route::post('/ordenes-pago/{orden}/cuotas/{cuota}/checkout', [NPago::class, 'crearCheckout'])->middleware('acceso:agenda')->whereNumber('cuota');
    Route::get('/pagos/stripe/sesiones/{sessionId}', [NPago::class, 'confirmarCheckout'])->middleware('acceso:agenda|validacion-pagos,lectura');
    Route::post('/pagos/stripe/sesiones/{sessionId}/cancelar', [NPago::class, 'cancelarCheckout'])->middleware('acceso:agenda');
    Route::get('/cuotas', [NPago::class, 'cuotas'])->middleware('acceso:validacion-pagos');
    Route::patch('/ordenes-pago/{orden}/cuotas/{cuota}/aprobar', [NPago::class, 'aprobar'])->middleware('acceso:validacion-pagos')->whereNumber('cuota');
    Route::patch('/ordenes-pago/{orden}/cuotas/{cuota}/rechazar', [NPago::class, 'rechazar'])->middleware('acceso:validacion-pagos')->whereNumber('cuota');
    Route::get('/comprobantes/{comprobante}', [NPago::class, 'comprobante'])->middleware('acceso:agenda|validacion-pagos,lectura');
    Route::get('/inscripciones', [NSeguimiento::class, 'inscripciones'])->middleware('acceso:alumnos|seguimiento,lectura');
    Route::get('/exportaciones/pendientes', [NExportacion::class, 'pendientes'])->middleware('acceso:alumnos');
    Route::post('/exportaciones', [NExportacion::class, 'exportar'])->middleware('acceso:alumnos');
    Route::get('/exportaciones', [NExportacion::class, 'historial'])->middleware('acceso:alumnos');
    Route::patch('/exportaciones/{exportacion}', [NExportacion::class, 'registrarResultado'])->middleware('acceso:alumnos');

    // CU8 — ventas, comisiones, reportes y estadísticas
    Route::get('/comisiones', [NSeguimiento::class, 'comisiones'])->middleware('acceso:seguimiento');
    Route::get('/comisiones/resumen', [NSeguimiento::class, 'resumenComisiones'])->middleware('acceso:seguimiento,modificacion');
    Route::patch('/comisiones/vendedores/{vendedor}/pagar', [NSeguimiento::class, 'pagarComisiones'])->middleware('acceso:seguimiento');
    Route::get('/configuracion/comision', [NSeguimiento::class, 'configuracionComision'])->middleware('acceso:seguimiento');
    Route::put('/configuracion/comision', [NSeguimiento::class, 'actualizarConfiguracionComision'])->middleware('acceso:seguimiento');
    Route::get('/dashboard', [NReporte::class, 'dashboard'])->middleware('acceso:dashboard|inicio-vendedor,lectura');
    Route::get('/estadisticas/vendedor', [NReporte::class, 'estadisticasVendedor'])->middleware('acceso:inicio-vendedor');
    Route::get('/reportes/estadisticas', [NReporte::class, 'estadisticas'])->middleware('acceso:reportes');
    Route::get('/reportes/listado', [NReporte::class, 'listado'])->middleware('acceso:reportes');
});
