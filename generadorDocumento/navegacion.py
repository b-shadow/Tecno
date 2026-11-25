"""Diagramas de navegación (7.5), uno por actor, armados desde la MATRIZ DE ACCESO REAL (contenido.RECURSOS / PERMISOS,
migración 000003): el diagrama de un rol tiene solo las páginas de su menú y, en cada una, solo las acciones que la
interfaz le habilita (la misma condición `puede(recurso, nivel)` de las páginas React).

Todo sale del código (verificar() lo exige):
  · client page = componente React; atributos = su estado (useState / useDatos) y operaciones = sus funciones reales.
  · «Formulario» = campos que la pantalla envía y su función de envío (FUENTE dice en qué archivo están).
  · server page "ps …" = ruta de negocio/routes/api.php; atributos = parámetros de la ruta y del FormRequest / query;
    operación = método real de la clase N (navegacion.API liga cada ps con su función de presentacion/src/api/*.js).
  · «database» BD: tabla = tabla de fuentes/esquema.sql. Las «access» NO se escriben a mano: se calculan con
    codigo.metodos_datos (cadena N → D del endpoint, todas las ramas) y DATOS (qué tabla lee o escribe cada método de D).
    Regla: tabla consultada (FROM / JOIN) o escrita; las relaciones cargadas con with() y los filtros de alcance o de
    autorización (DAlcance, NAcceso::permite, token) no se dibujan. Los triggers están en 7.3.4.
  · «include» = server page que ejecuta otra parte compartida del servidor (INCLUIDAS): la conversión a matrícula
    (NConversion) y la conciliación de una sesión de Stripe (NStripe::confirmar…DesdeSesion).

Estereotipos (Conallen, REGLAS_DOCUMENTO_P2.md §5): client page → client page «link»; client page → server page «link»
con la URL y sus parámetros; «Formulario» → server page «submit» (uno por formulario); server page → client page
«build»; server page → server page «include»; server page → BD «access»;
página ◇— formulario o vista interna (agregación).

Cada diagrama se arma por SECCIONES en el orden de navegación del menú de la base de datos: la entrada del actor,
su primera vista y las opciones que su rol puede usar. Una vista cliente aparece una sola vez; los procesos y tablas
se pueden repetir cerca de la acción para conservar la lectura al cortar el diagrama en franjas.
ea/navegacion_hojas.py dibuja un diagrama por actor en EA
y insertar_navegacion.py lo corta en franjas apaisadas en 7.5, como G07.
"""
import re

from contenido import PERMISOS, RECURSOS

NIVEL = {'lectura': 1, 'modificacion': 2, 'eliminacion': 3}
CERCANA = 1000   # cada proceso y tabla se dibuja una sola vez por actor, como en G07
OPS = {'S': 'SELECT', 'I': 'INSERT', 'U': 'UPDATE', 'D': 'DELETE'}


class Diagrama:
    def __init__(self, permisos, actor):
        self.permisos, self.actor, self.paginas, self.enlaces, self.hojas = permisos, actor, {}, [], []
        self.grupo = 'entrada' if actor != 'Visitante' else 'catalogo'
        self.grupo_nodo = {}
        self.incluidas = []   # server pages incluidos que usa el diagrama (sus «access» van en su propia hoja)
        # Lo que se usa en varias secciones (páginas, server pages, tablas) se dibuja una vez en cada sección (clave#n):
        # cada sección queda junta y sus relaciones son cortas. Solo el menú es una caja única: sus enlaces a cada
        # página recorren el diagrama de punta a punta. local: clave -> instancia de la sección actual.
        self.local, self.base, self.ultima = {}, {}, {}

    def puede(self, recurso, minimo='lectura'):
        return NIVEL.get(self.permisos.get(recurso), 0) >= NIVEL[minimo]

    def hoja(self, titulo):
        self.hojas.append((titulo, [], []))   # (título, claves, relaciones que se dibujan en esta sección)
        self.local = {}

    def _en_hoja(self, *claves):
        for c in claves:
            if self.hojas and c not in self.hojas[-1][1]: self.hojas[-1][1].append(c)

    def p(self, clave, tipo, nombre, atributos='', operaciones=''):
        if tipo in ('ps', 'bd') and clave not in INCLUIDAS:
            if clave not in self.local:
                previa = self.ultima.get(clave)   # la de una sección cercana sirve (su línea no pasa de una página)
                if previa and len(self.hojas) - previa[1] <= CERCANA: self.local[clave] = previa[0]
                else: self.local[clave] = clave if clave not in self.paginas else f'{clave}#{len(self.hojas)}'
            instancia = self.local[clave]
            self.base[instancia] = clave
            self.ultima[clave] = (instancia, len(self.hojas))
        else:
            instancia = clave   # páginas, formularios y partes compartidas: una sola vez por diagrama
        self.paginas.setdefault(instancia, (tipo, nombre, atributos, operaciones))
        self.grupo_nodo.setdefault(instancia, self.grupo)
        self._en_hoja(instancia)
        return instancia

    def e(self, a, b, estereotipo, texto=''):
        a, b = self.local.get(a, a), self.local.get(b, b)
        if (a, b, estereotipo, texto) not in self.enlaces: self.enlaces.append((a, b, estereotipo, texto))
        self._en_hoja(a, b)
        if self.hojas and (a, b, estereotipo, texto) not in self.hojas[-1][2]: self.hojas[-1][2].append((a, b, estereotipo, texto))

    def abrir_formulario(self, pagina, formulario, accion):
        """Registra la acción que abre el diálogo."""
        self.e(pagina, formulario, 'link', accion)

    def ps(self, clave, nombre, atributos, operaciones):
        """Server page con sus «access» (y «include») leídos del código."""
        accesos(self, self.p(clave, 'ps', nombre, atributos, operaciones))


# ------------------------------------------------------------------ capa 3: tablas y qué hace cada método de D
COLUMNAS = {   # hasta 4 columnas por caja «database»: la clave y las que más tocan los endpoints (existen en esquema.sql)
    'usuarios': 'correo, password, rol, estado', 'api_tokens': 'token_hash, usuario_correo, expira_en',
    'bitacora': 'nro_registro, evento, usuario_correo, ip', 'recursos': 'codigo, nombre, ruta, visitas',
    'permisos': 'rol, recurso_codigo, acceso', 'roles': 'nombre, descripcion',
    'intereses': 'nro_tarjeta, documento, modulo_codigo, estado',
    'prospectos': 'documento, nombre, apellido, correo', 'motivos_perdida': 'nombre, categoria',
    'recordatorios': 'nro_recordatorio, nro_tarjeta, fecha_programada, estado', 'interacciones': 'nro_interaccion, nro_tarjeta, tipo, resultado',
    'programas': 'codigo, nombre', 'catalogo_cache': 'codigo, programa_codigo, nombre, precio',
    'metodos_pago': 'nro_metodo, documento, tipo, estado',
    'ordenes_pago': 'nro_orden, nro_tarjeta, total, estado', 'cuotas': 'nro_orden, nro_cuota, monto, estado',
    'transacciones_stripe': 'nro_transaccion, tipo, stripe_sesion, estado_interno',
    'orden_pago_descuentos': 'nro_orden, descuento_codigo, monto', 'pagos': 'nro_orden, estado, fecha_validacion',
    'descuentos': 'codigo, nombre, porcentaje, estado', 'solicitudes_compra': 'nro_solicitud, nro_orden, modulo_codigo, precio_acordado',
    'comprobantes_pago': 'nro_comprobante, nro_orden, nro_cuota, estado_revision',
    'inscripciones_comerciales': 'nro_solicitud, fecha_confirmacion', 'comisiones': 'nro_solicitud, vendedor_correo, monto, estado',
    'exportaciones': 'nro_exportacion, nro_solicitud, estado', 'configuraciones': 'clave, valor',
    'programas_responsables': 'programa_codigo, coordinador_correo', 'notificaciones': 'nro_notificacion, destinatario, tipo, estado',
}
# 'tabla:OPS' por método de la capa de datos (S/I/U/D). '' = no toca tablas o es alcance/autorización.
# 'tabla:S@rec' = solo si el rol tiene el recurso rec ('@rec1|rec2'; '@*' = hay sesión), como el if del código.
DATOS = {
    'DAcceso.permisosPorRol': '', 'DAcceso.menuPorRol': 'recursos:S permisos:S', 'DAlcance.codigosModuloCoordinador': '',
    'DAuth.usuarioPorCorreo': 'usuarios:S', 'DAuth.tokenPorPlano': '', 'DAuth.crearToken': 'api_tokens:I',
    'DAuth.actualizarUsuario': 'usuarios:U', 'DAuth.revocarOtrosTokens': 'api_tokens:D', 'DAuth.eliminarToken': 'api_tokens:D',
    'DBitacora.registrar': 'bitacora:I',
    'DCatalogo.programasAbiertos': 'programas:S catalogo_cache:S', 'DCatalogo.sincronizar': 'programas:IU catalogo_cache:IU',
    'DConversion.datosConversion': 'ordenes_pago:S pagos:S', 'DConversion.ordenAprobada': 'ordenes_pago:S pagos:S',
    'DConversion.registrarInscripcionesYComisiones': 'configuraciones:S inscripciones_comerciales:I comisiones:I',
    'DConversion.registrarInteraccion': 'interacciones:I', 'DConversion.actualizarConversion': 'intereses:U prospectos:U',
    'DExportacion.exportables': 'inscripciones_comerciales:S', 'DExportacion.exportarPendientes': 'inscripciones_comerciales:S exportaciones:I',
    'DExportacion.registrarResultado': 'exportaciones:SU', 'DExportacion.historial': 'exportaciones:S',
    'DInteres.listar': 'intereses:S', 'DInteres.motivos': 'motivos_perdida:S', 'DInteres.obtener': 'intereses:S',
    'DInteres.detalle': 'intereses:S', 'DInteres.transaccion': '', 'DInteres.bloquear': 'intereses:S', 'DInteres.guardar': 'intereses:U',
    'DInteres.actualizarEstadoProspecto': 'prospectos:U', 'DInteres.vendedorAsignado': 'usuarios:S', 'DInteres.vendedor': 'usuarios:S',
    'DInteres.vendedoresVigentes': 'usuarios:S', 'DInteres.cargaPorVendedor': 'intereses:S', 'DInteres.pendientesSinAsignar': 'intereses:S',
    'DInteres.vendedorExistenteParaDocumento': 'intereses:S', 'DInteres.actualizarRecordatoriosPendientes': 'recordatorios:U',
    'DInteres.registrarInteraccion': 'interacciones:I', 'DInteres.refrescarDetalle': 'intereses:S',
    'DMotivo.listarConUsos': 'motivos_perdida:S intereses:S', 'DMotivo.existeNombre': 'motivos_perdida:S', 'DMotivo.crear': 'motivos_perdida:I',
    'DMotivo.obtener': 'motivos_perdida:S', 'DMotivo.estaEnUso': 'intereses:S', 'DMotivo.actualizar': 'motivos_perdida:U',
    'DMotivo.eliminar': 'motivos_perdida:D',
    'DNotificacion.prospectoAsignadoA': 'prospectos:S', 'DNotificacion.crear': 'notificaciones:I', 'DNotificacion.listar': 'notificaciones:S',
    'DNotificacion.obtener': 'notificaciones:S', 'DNotificacion.marcarLeida': 'notificaciones:U',
    'DSitio.recursoPorRuta': 'recursos:S', 'DSitio.visitas': 'recursos:S', 'DSitio.buscarCatalogo': 'catalogo_cache:S programas:S',
    'DSitio.buscarIntereses': 'intereses:S@embudo|prospectos prospectos:S@embudo|prospectos', 'DSitio.buscarUsuarios': 'usuarios:S@usuarios',
    'DSitio.buscarPaginas': 'recursos:S@* permisos:S@*',
    'DSeguridad.matriz': 'roles:S recursos:S permisos:S', 'DSeguridad.guardarPermiso': 'permisos:IUD',
    'DSeguridad.bitacora': 'bitacora:S usuarios:S recursos:S', 'DSeguridad.resumen': 'bitacora:S recursos:S usuarios:S',
    'DUsuario.listar': 'usuarios:S roles:S programas:S', 'DUsuario.vendedores': 'usuarios:S', 'DUsuario.transaccion': '',
    'DUsuario.crear': 'usuarios:I', 'DUsuario.obtener': 'usuarios:S', 'DUsuario.bloquearAdministradoresActivos': 'usuarios:S',
    'DUsuario.existeOtroAdministradorActivo': 'usuarios:S', 'DUsuario.actualizar': 'usuarios:U',
    'DUsuario.asignarProgramas': 'programas_responsables:IUD', 'DUsuario.quitarProgramas': 'programas_responsables:D',
    'DUsuario.revocarTokens': 'api_tokens:D', 'DUsuario.fresco': 'usuarios:S',
    'DProspecto.obtener': 'prospectos:S', 'DProspecto.transaccion': '', 'DProspecto.encontrarPorDocumentoOCorreoBloqueado': 'prospectos:S',
    'DProspecto.buscar': 'prospectos:S', 'DProspecto.crear': 'prospectos:I', 'DProspecto.actualizar': 'prospectos:U',
    'DProspecto.estaDentroDeCartera': '', 'DProspecto.conIntereses': '', 'DProspecto.actualizado': 'prospectos:S',
    'DProspecto.existeDocumentoOCorreo': 'prospectos:S', 'DProspecto.modulosSolicitados': 'catalogo_cache:S',
    'DProspecto.vendedorExistente': 'intereses:S', 'DProspecto.crearInteres': 'intereses:SI',
    'DSeguimiento.interes': 'intereses:S', 'DSeguimiento.obtenerRecordatorio': 'recordatorios:S', 'DSeguimiento.usuario': 'usuarios:S',
    'DSeguimiento.transaccion': '', 'DSeguimiento.registrarInteraccion': 'interacciones:I', 'DSeguimiento.actualizarInteres': 'intereses:U',
    'DSeguimiento.cargarInteraccion': '', 'DSeguimiento.listarRecordatorios': 'recordatorios:SU', 'DSeguimiento.crearRecordatorio': 'recordatorios:I',
    'DSeguimiento.buscarRecordatorioBloqueado': 'recordatorios:S', 'DSeguimiento.cargarInteresRecordatorio': '',
    'DSeguimiento.insertarInteraccion': 'interacciones:I', 'DSeguimiento.recordatorio': 'recordatorios:U',
    'DSeguimiento.comisiones': 'comisiones:S', 'DSeguimiento.resumenComisiones': 'comisiones:S usuarios:S',
    'DSeguimiento.pagarComisiones': 'comisiones:U', 'DSeguimiento.porcentajeComision': 'configuraciones:S',
    'DSeguimiento.actualizarPorcentajeComision': 'configuraciones:IU', 'DSeguimiento.inscripciones': 'inscripciones_comerciales:S',
    'DPago.prospecto': 'prospectos:S', 'DPago.metodo': 'metodos_pago:S', 'DPago.interes': 'intereses:S', 'DPago.orden': 'ordenes_pago:S',
    'DPago.comprobante': 'comprobantes_pago:S', 'DPago.transaccion': '', 'DPago.descuentos': 'descuentos:S',
    'DPago.actualizarMetodo': 'metodos_pago:U', 'DPago.modulos': 'catalogo_cache:S', 'DPago.cantidadModulosAbiertos': 'catalogo_cache:S',
    'DPago.descuentosPorCodigo': 'descuentos:S', 'DPago.crearOrden': 'ordenes_pago:I', 'DPago.insertarDescuentosOrden': 'orden_pago_descuentos:I',
    'DPago.actualizarOrden': 'ordenes_pago:U', 'DPago.insertarItems': 'solicitudes_compra:I', 'DPago.insertarCuotas': 'cuotas:I',
    'DPago.crearPago': 'pagos:I', 'DPago.registrarInteraccion': 'interacciones:I', 'DPago.actualizarInteres': 'intereses:U',
    'DPago.ordenCompleta': '', 'DPago.asegurarTokenCuota': 'cuotas:SU', 'DPago.cuotaPorToken': 'cuotas:S ordenes_pago:S intereses:S',
    'DPago.cuotas': 'cuotas:S ordenes_pago:S intereses:S prospectos:S usuarios:S comprobantes_pago:S', 'DPago.cuotaBloqueada': 'cuotas:S',
    'DPago.ordenAbierta': 'ordenes_pago:S pagos:S', 'DPago.metodoConProspecto': '', 'DPago.interesDeOrden': '',
    'DPago.actualizarCuota': 'cuotas:U', 'DPago.actualizarPago': 'pagos:U', 'DPago.montoCuotasEnEstado': 'cuotas:S',
    'DPago.hayCuotasEnEstados': 'cuotas:S', 'DPago.actualizarComprobantes': 'comprobantes_pago:U', 'DPago.interesBloqueado': 'intereses:S',
    'DPago.ordenDeComprobante': 'ordenes_pago:S', 'DPago.prospectoEnCartera': '',
    'DStripe.transaccion': '', 'DStripe.ordenConDetalle': 'ordenes_pago:S', 'DStripe.ordenBloqueada': 'ordenes_pago:S',
    'DStripe.cuotaBloqueada': 'cuotas:S', 'DStripe.prospectoBloqueado': 'prospectos:S', 'DStripe.guardarClienteProspecto': 'prospectos:U',
    'DStripe.transaccionPorSesion': 'transacciones_stripe:S', 'DStripe.transaccionPorSesionBloqueada': 'transacciones_stripe:S',
    'DStripe.transaccionAbiertaPorCuota': 'transacciones_stripe:S', 'DStripe.transaccionSetupAbierta': 'transacciones_stripe:S',
    'DStripe.contarIntentosCuota': 'transacciones_stripe:S', 'DStripe.transaccionesPendientesDeOrden': 'transacciones_stripe:S',
    'DStripe.crearTransaccion': 'transacciones_stripe:I', 'DStripe.actualizarTransaccion': 'transacciones_stripe:U',
    'DStripe.registrarMetodoStripe': 'metodos_pago:SI', 'DStripe.vencimientoMetodoStripe': 'metodos_pago:S',
    'DStripe.hayTransaccionesEnEstado': 'transacciones_stripe:S',
    'DReporte.dashboard': 'intereses:S ordenes_pago:S cuotas:S recordatorios:S recursos:S bitacora:S@bitacora',
    'DReporte.estadisticas': 'intereses:S usuarios:S motivos_perdida:S prospectos:S',
    'DReporte.listado': 'intereses:S prospectos:S usuarios:S motivos_perdida:S ordenes_pago:S cuotas:S solicitudes_compra:S '
                        'inscripciones_comerciales:S comisiones:S',
    'DReporte.vendedores': 'usuarios:S',
    'DReporte.estadisticasVendedor': 'intereses:S interacciones:S comisiones:S recordatorios:S',
}


def _permite(d, condicion):
    if not condicion: return True
    if condicion == '*': return d.actor != 'Visitante'
    return any(d.puede(r) for r in condicion.split('|'))


def accesos(d, ps):
    """«access» e «include» del server page ps, leídos de la cadena N → D del endpoint (codigo.metodos_datos)."""
    import codigo
    if any(a == ps and st in ('access', 'include') for a, _, st, _ in d.enlaces): return   # ya dibujado
    base = d.base.get(ps, ps)
    if base in INCLUIDAS:
        clase, metodos = INCLUIDAS[base][0], INCLUIDAS[base][1].split()
        cadena = [x for m in metodos for x in codigo.metodos_datos(clase, m, cortes=CORTES, propio=True)]
    else:
        cadena = [x for f in API[base].split() for x in codigo.metodos_datos(*_ruta(f), cortes=CORTES)]
    ops = {}
    for x in dict.fromkeys(cadena):
        if x[0] == 'incluye':   # corte: otra parte del servidor que se dibuja aparte
            inc = next(k for k, v in INCLUIDAS.items() if x[1] in [f'{v[0]}.{m}' for m in v[1].split()])
            if inc != base:   # sus «access» se dibujan una vez, en la hoja de partes compartidas (compartidas())
                d.p(inc, 'ps', *INCLUIDAS[inc][2:])
                d.e(ps, inc, 'include', x[1].split('.')[1] + '()')
                if inc not in d.incluidas: d.incluidas.append(inc)
            continue
        for spec in DATOS[f'{x[0]}.{x[1]}'].split():
            tabla, _, resto = spec.partition(':')
            letras, _, cond = resto.partition('@')
            if _permite(d, cond): ops.setdefault(tabla, set()).update(letras)
    for tabla, letras in ops.items():   # la tabla se dibuja en la sección del server page: sus «access» quedan cortos
        d.p('bd_' + tabla, 'bd', 'BD: ' + tabla, COLUMNAS[tabla])
        d.e(ps, 'bd_' + tabla, 'access', ' / '.join(OPS[l] for l in 'SIUD' if l in letras))


def _ruta(funcion):
    import codigo
    f = codigo.funciones_api()[funcion]
    r = next(r for r in codigo.rutas_api() if r['clave'] == (f['verbo'], f['ruta']))
    return r['controlador'], r['metodo']


def url(funcion, consulta=''):
    """'intereses.mover' -> 'PATCH /intereses/{interes}/estado' (la ruta de api.php); consulta: '?buscar&estado'."""
    import codigo
    f = codigo.funciones_api()[funcion]
    r = next(r for r in codigo.rutas_api() if r['clave'] == (f['verbo'], f['ruta']))
    return f'{r["verbo"]} {r["ruta"]}{consulta}'   # la ruta tal cual en routes/api.php (Laravel antepone /api)


# ------------------------------------------------------------------ CU1: sesión, menú, perfil
def inicio_sesion(d):
    d.hoja('CU1 Inicio de sesión')
    d.p('actor', 'actor', d.actor)
    d.p('login', 'cliente', 'Login', 'form, recordar, ver, error, ayuda, enviando', 'entrar()')
    d.p('f_login', 'form', 'Iniciar Sesion', 'correo, password', 'entrar()')
    d.e('actor', 'login', 'link', '/login')
    d.e('login', 'f_login', 'contiene')
    d.ps('ps_login', 'ps Login', 'correo, password', 'login()')
    d.e('f_login', 'ps_login', 'submit', url('auth.login'))
    d.p('error', 'cliente', 'Aviso en Login', 'tipo, children', 'Aviso()')
    menu(d)
    d.e('ps_login', 'menu', 'build', '200: sesión y menú según rol')
    d.e('ps_login', 'error', 'build', '422 / 403: aviso de acceso')
    d.e('login', 'error', 'contiene')


def menu(d):
    nombre = f'Plantilla y menú de {d.actor}'
    d.p('menu', 'cliente', nombre, 'menu, cerrado, movil', 'alternar(), elegir()')


def sesion_y_perfil(d):
    d.grupo = 'sesion'
    d.hoja('CU1 Menú, búsqueda y perfil')
    menu(d)
    d.ps('ps_me', 'ps Sesion Actual', 'token', 'me()')
    d.e('menu', 'ps_me', 'link', url('auth.me'))
    d.e('ps_me', 'menu', 'build', 'usuario, menu, permisos')
    visitas(d, 'menu')
    d.p('error404', 'cliente', 'Pagina no Encontrada', 'titulo, icono', 'PError404()')
    d.p('actor', 'actor', d.actor)
    d.e('actor', 'error404', 'link', 'URL inexistente (*)')
    d.p('catalogo', 'cliente', 'Catalogo de Programas', 'datos, area, eleccion, registrando', 'coloresDeAreas(), recargar()')
    d.e('error404', 'catalogo', 'link', '/anuncios (Ir al catálogo)')
    d.grupo = 'busqueda'
    d.hoja('CU1 Búsqueda global')
    menu(d)
    d.ps('ps_buscar', 'ps Busqueda Global', 'q', 'buscar()')
    d.e('menu', 'ps_buscar', 'link', url('sitio.buscar', '?q (tras escribir 2 caracteres)'))
    d.p('resultados_busqueda', 'cliente', 'Resultados de búsqueda', 'resultados, activo, abierto', 'elegir(), tecla()')
    d.e('ps_buscar', 'resultados_busqueda', 'build', 'resultados filtrados por acceso')
    d.grupo = 'perfil'
    d.hoja('CU1 Perfil y cierre de sesión')
    menu(d)
    d.p('f_perfil', 'form', 'Mi Perfil', 'nombre, apellido, telefono, foto', 'guardar()')
    d.abrir_formulario('menu', 'f_perfil', 'Mi perfil')
    d.ps('ps_perfil', 'ps Actualizar Perfil', 'nombre, apellido, telefono, foto', 'actualizarPerfil()')
    d.e('f_perfil', 'ps_perfil', 'submit', url('auth.actualizarPerfil'))
    d.e('ps_perfil', 'menu', 'build', 'usuario')
    d.p('f_clave', 'form', 'Cambiar Contrasena', 'password_actual, password, password_confirmation', 'guardar()')
    d.abrir_formulario('menu', 'f_clave', 'Cambiar contraseña')
    d.ps('ps_clave', 'ps Cambiar Password', 'password_actual, password', 'cambiarPassword()')
    d.e('f_clave', 'ps_clave', 'submit', url('auth.cambiarPassword'))
    d.e('ps_clave', 'menu', 'build', 'mensaje')
    d.ps('ps_logout', 'ps Cerrar Sesion', 'token', 'logout()')
    d.e('menu', 'ps_logout', 'link', url('auth.logout', ' (Perfil > Cerrar sesión > Confirmar)'))
    d.p('login', 'cliente', 'Login', 'form, recordar, ver, error, ayuda, enviando', 'entrar()')
    d.e('ps_logout', 'login', 'build', 'go("/login")')


def visitas(d, plantilla):
    d.p('pie', 'cliente', 'Pie de página', 'visitas', 'Pie()')
    d.e(plantilla, 'pie', 'contiene')
    d.ps('ps_visita', 'ps Registrar Visita', 'ruta', 'visita()')
    d.e('pie', 'ps_visita', 'link', url('sitio.visita', ' ruta (pie de cada vista)'))
    d.e('ps_visita', 'pie', 'build', 'visitas')


def entrada(d, codigo):
    """Hoja de un recurso del menú: Menu → página (el enlace del menú dinámico)."""
    menu(d)
    inicio = 'inicio-vendedor' if d.puede('inicio-vendedor') else 'dashboard'
    if codigo != inicio:
        d.e('menu', codigo, 'link', RECURSOS[codigo]['ruta'])


def destinos_busqueda(d):
    """Destinos que NSitio::buscar realmente devuelve; la lista respeta el acceso del rol."""
    d.hoja('CU1 Selección de resultado de búsqueda')
    d.p('resultados_busqueda', 'cliente', 'Resultados de búsqueda', 'resultados, activo, abierto', 'elegir(), tecla()')
    d.p('catalogo', 'cliente', 'Catalogo de Programas', 'datos, area, eleccion, registrando', 'coloresDeAreas(), recargar()')
    d.e('resultados_busqueda', 'catalogo', 'link', '/anuncios?modulo={codigo}')
    if d.puede('agenda'):
        d.p('agenda', 'cliente', 'Seguimiento y Agenda', 'buscar, estado, sel, enfocar, lista', 'recargar()')
        d.e('resultados_busqueda', 'agenda', 'link', '/agenda?interes={nro_tarjeta}')
    if d.puede('usuarios'):
        d.p('usuarios', 'cliente', 'Usuarios', 'filtro, datos, editando', 'cambiarEstado(), recargar()')
        d.e('resultados_busqueda', 'usuarios', 'link', '/usuarios?buscar={correo}')
    d.e('resultados_busqueda', 'menu', 'link', 'elegir una página permitida: resultado.ruta')


def ficha(d, desde):
    d.p('ficha', 'cliente', 'Ficha del Prospecto', 'datos, pestana, editar', 'actualizar()')
    alcance = ' (tarjeta asignada)' if d.actor == 'Vendedor' else ' (según alcance del rol)'
    d.e(desde, 'ficha', 'link', '/agenda?interes={nro_tarjeta}' + alcance)


def vendedores(d, desde):
    d.ps('ps_vend', 'ps Listar Vendedores', 'token', 'vendedores()')
    d.e(desde, 'ps_vend', 'link', url('usuarios.vendedores'))
    d.e('ps_vend', desde, 'build', 'vendedores')


def usuarios(d):   # CU1
    d.hoja('CU1 Usuarios')
    d.p('usuarios', 'cliente', 'Usuarios', 'filtro, datos, editando', 'cambiarEstado(), recargar()')
    entrada(d, 'usuarios')
    d.ps('ps_usuarios', 'ps Listar Usuarios', 'buscar, rol, estado', 'index()')
    d.e('usuarios', 'ps_usuarios', 'link', url('usuarios.index', '?buscar&rol&estado'))
    d.e('ps_usuarios', 'usuarios', 'build', 'usuarios, roles, programas')
    if not d.puede('usuarios', 'modificacion'): return   # PUsuarios.jsx: editable
    d.p('f_usuario', 'form', 'Registrar / Editar Usuario',
        'nombre, apellido, correo, telefono, password, rol, fecha_inicio, fecha_fin, estado, foto, programas', 'guardar(), quitarFoto()')
    d.abrir_formulario('usuarios', 'f_usuario', 'Nuevo / Editar')
    d.ps('ps_usuario_g', 'ps Guardar Usuario', 'usuario, nombre, apellido, correo, telefono, password, rol, estado, fecha_inicio, fecha_fin, foto, programas',
         'store(), update()')
    d.e('f_usuario', 'ps_usuario_g', 'submit', 'POST /usuarios | PUT /usuarios/{usuario}')
    d.e('ps_usuario_g', 'usuarios', 'build', 'usuario')
    d.ps('ps_foto_usuario', 'ps Quitar Fotografia', 'usuario', 'foto()')
    d.e('f_usuario', 'ps_foto_usuario', 'link', url('usuarios.foto', ' (Editar > Quitar foto > Confirmar)'))
    d.e('ps_foto_usuario', 'f_usuario', 'build', 'foto eliminada, editor abierto')
    d.ps('ps_estado', 'ps Cambiar Estado', 'usuario, estado', 'cambiarEstado()')
    d.e('usuarios', 'ps_estado', 'link', url('usuarios.cambiarEstado'))
    d.e('ps_estado', 'usuarios', 'build', 'mensaje')


def matriz(d):   # CU1
    d.hoja('CU1 Matriz de acceso')
    d.p('matriz', 'cliente', 'Matriz de Acceso', 'datos', 'valor(), cambiar()')
    entrada(d, 'matriz')
    d.ps('ps_matriz', 'ps Matriz', 'token', 'matriz()')
    d.e('matriz', 'ps_matriz', 'link', url('seguridad.matriz'))
    d.e('ps_matriz', 'matriz', 'build', 'roles, recursos, permisos')
    if d.puede('matriz', 'modificacion'):
        d.ps('ps_asig_perm', 'ps Asignar Permiso', 'rol, recurso_codigo, acceso', 'asignar()')
        d.e('matriz', 'ps_asig_perm', 'link', url('seguridad.asignar', ' (cambiar selector de permiso)'))
        d.e('ps_asig_perm', 'matriz', 'build', 'mensaje')


def bitacora(d):   # CU1
    d.p('bitacora', 'cliente', 'Bitacora de Accesos', 'f, registros, resumen', 'set()')
    entrada(d, 'bitacora')
    d.ps('ps_bitacora', 'ps Listar Bitacora', 'evento, usuario, ip, desde, hasta', 'bitacora()')
    d.e('bitacora', 'ps_bitacora', 'link', url('seguridad.bitacora', '?evento&usuario&ip&desde&hasta&page'))
    d.e('ps_bitacora', 'bitacora', 'build', 'registros')
    d.ps('ps_bresumen', 'ps Resumen de Accesos', 'token', 'resumen()')
    d.e('bitacora', 'ps_bresumen', 'link', url('seguridad.resumen'))
    d.e('ps_bresumen', 'bitacora', 'build', 'eventos, recursos, ips')


# ------------------------------------------------------------------ CU2
def gestion_anuncios(d):
    d.hoja('CU2 Oferta académica')
    d.p('gestion-anuncios', 'cliente', 'Oferta Academica', 'datos, area, eleccion', 'coloresDeAreas(), recargar()')
    entrada(d, 'gestion-anuncios')
    d.ps('ps_catalogo', 'ps Catalogo', 'buscar', 'programas()')
    d.e('gestion-anuncios', 'ps_catalogo', 'link', url('catalogo.programas'))
    d.e('ps_catalogo', 'gestion-anuncios', 'build', 'programas')
    if d.puede('gestion-anuncios', 'modificacion'):   # PCatalogo.jsx: puedeSincronizar
        d.ps('ps_sinc', 'ps Sincronizar Catalogo', 'token', 'sincronizar()')
        d.e('gestion-anuncios', 'ps_sinc', 'link', url('catalogo.sincronizar'))
        d.e('ps_sinc', 'gestion-anuncios', 'build', 'mensaje')


# ------------------------------------------------------------------ CU3
def prospectos(d):
    d.hoja('CU3 Prospectos')
    d.p('prospectos', 'cliente', 'Prospectos', 'filtro, datos, modal', 'recargar()')
    entrada(d, 'prospectos')
    d.ps('ps_prosp', 'ps Listar Prospectos', 'buscar, origen', 'index()')
    d.e('prospectos', 'ps_prosp', 'link', url('prospectos.index', '?buscar&origen'))
    d.e('ps_prosp', 'prospectos', 'build', 'prospectos, origenes')
    ficha(d, 'prospectos')
    if d.puede('interesados', 'modificacion'):   # PProspectos.jsx: puedeAlta
        d.p('f_prospecto', 'form', 'Registrar Prospecto', 'documento, origen, nombre, apellido, telefono, correo, profesion, ubicacion, interes', 'guardar()')
        d.abrir_formulario('prospectos', 'f_prospecto', 'Registrar prospecto')
        d.ps('ps_alta', 'ps Registrar Prospecto', 'documento, nombre, apellido, telefono, correo, origen, profesion, ubicacion, modulo_codigo, programa_codigo', 'store()')
        d.e('f_prospecto', 'ps_alta', 'submit', url('prospectos.store'))
        d.e('ps_alta', 'prospectos', 'build', 'mensaje, prospecto')
        d.p('f_csv', 'form', 'Importar CSV', 'archivo', 'importar()')
        d.abrir_formulario('prospectos', 'f_csv', 'Importar CSV')
        d.ps('ps_csv', 'ps Importar CSV', 'csv', 'importarCSV()')
        d.e('f_csv', 'ps_csv', 'submit', url('prospectos.importarCSV'))
        d.e('ps_csv', 'prospectos', 'build', 'creados, errores')
        d.p('plantilla_csv', 'externo', 'Plantilla CSV descargada')
        d.e('f_csv', 'plantilla_csv', 'link', 'Importar CSV > Plantilla')
    if d.puede('prospectos', 'modificacion') or d.puede('embudo', 'modificacion'):   # puedeAgregarInteres
        d.hoja('CU3 Prospectos: nuevo interés')
        entrada(d, 'prospectos')
        d.p('f_nuevo_interes', 'form', 'Agregar Interes', 'interes', 'guardar()')
        d.abrir_formulario('prospectos', 'f_nuevo_interes', 'Agregar interés')
        d.ps('ps_catalogo', 'ps Catalogo', 'buscar', 'programas()')
        d.e('f_nuevo_interes', 'ps_catalogo', 'link', url('catalogo.programas'))
        d.e('ps_catalogo', 'f_nuevo_interes', 'build', 'programas')
        if 'f_prospecto' in d.paginas:
            d.e('f_prospecto', 'ps_catalogo', 'link', url('catalogo.programas'))
            d.e('ps_catalogo', 'f_prospecto', 'build', 'programas')
        d.ps('ps_nuevo_interes', 'ps Agregar Interes', 'prospecto, modulo_codigo, programa_codigo', 'crearInteres()')
        d.e('f_nuevo_interes', 'ps_nuevo_interes', 'submit', url('prospectos.crearInteres'))
        d.e('ps_nuevo_interes', 'prospectos', 'build', 'mensaje')


def listar_intereses(d, desde, consulta):
    d.ps('ps_intereses', 'ps Listar Intereses', 'buscar, estado, vendedor, sin_asignar, orden', 'index()')
    alcance = {'Coordinador': ' (programas asignados)', 'Vendedor': ' (cartera propia)'}.get(d.actor, '')
    d.e(desde, 'ps_intereses', 'link', url('intereses.index', consulta + alcance))
    d.e('ps_intereses', desde, 'build', 'intereses, estados, motivos')


def interesados(d):   # CU3: asignación manual y Round-Robin
    d.hoja('CU3 Asignación de prospectos')
    d.p('interesados', 'cliente', 'Asignacion de Prospectos', 'filtro, datos, repartiendo', 'asignar(), sinAsignar(), recargar()')
    entrada(d, 'interesados')
    listar_intereses(d, 'interesados', '?buscar&vendedor&sin_asignar&orden')
    vendedores(d, 'interesados')
    ficha(d, 'interesados')
    if d.puede('interesados', 'modificacion'):
        d.ps('ps_asignar', 'ps Asignar Interes', 'interes, vendedor_correo', 'asignar()')
        d.e('interesados', 'ps_asignar', 'link', url('intereses.asignar', ' (elegir vendedor en la fila)'))
        d.e('ps_asignar', 'interesados', 'build', 'mensaje, interes')
        d.ps('ps_repartir', 'ps Distribuir Round-Robin', 'usuario', 'distribuir()')
        d.e('interesados', 'ps_repartir', 'link', url('intereses.distribuir', ' (clic Distribuir Round Robin)'))
        d.e('ps_repartir', 'interesados', 'build', 'mensaje')


# ------------------------------------------------------------------ CU4 / CU5
def embudo(d):
    d.hoja('CU4 Embudo de ventas')
    d.p('embudo', 'cliente', 'Embudo de Ventas', 'filtros, datos, arrastrada, encima, perdida, faltantes', 'mover(), agrupar(), recargar()')
    entrada(d, 'embudo')
    listar_intereses(d, 'embudo', '?buscar' if d.actor == 'Vendedor' else '?buscar&vendedor')
    if 'inicio-vendedor' not in d.permisos: vendedores(d, 'embudo')   # PEmbudo.jsx: esVendedor no filtra
    ficha(d, 'embudo')
    if d.puede('embudo', 'modificacion'):
        d.hoja('CU4 / CU5 Mover tarjeta y marcar perdido')
        entrada(d, 'embudo')
        d.ps('ps_mover', 'ps Mover Tarjeta', 'interes, estado, motivo_perdida, observacion', 'mover()')
        d.e('embudo', 'ps_mover', 'link', url('intereses.mover'))
        d.p('f_perdida', 'form', 'Marcar como Perdido', 'motivo, observacion', 'mover()')
        d.abrir_formulario('embudo', 'f_perdida', 'Mover a Perdido')
        d.e('f_perdida', 'ps_mover', 'submit', url('intereses.mover'))
        d.e('ps_mover', 'embudo', 'build', 'mensaje, interes | 422 faltantes')
        ficha(d, 'embudo')


def motivos(d):   # CU5
    d.hoja('CU5 Motivos de pérdida')
    d.p('motivos', 'cliente', 'Motivos de Perdida', 'datos, editando', 'recargar()')
    entrada(d, 'motivos')
    d.ps('ps_motivos', 'ps Listar Motivos', 'token', 'index()')
    d.e('motivos', 'ps_motivos', 'link', url('motivos.index'))
    d.e('ps_motivos', 'motivos', 'build', 'motivos, categorias')
    if d.puede('motivos', 'modificacion'):   # PMotivos.jsx: editable
        d.p('f_motivo', 'form', 'Nuevo / Editar Motivo', 'nombre, categoria', 'guardar()')
        d.abrir_formulario('motivos', 'f_motivo', 'Nuevo / Editar')
        d.ps('ps_motivo_g', 'ps Guardar Motivo', 'motivo, nombre, categoria', 'store(), update()')
        d.e('f_motivo', 'ps_motivo_g', 'submit', 'POST /motivos | PUT /motivos/{motivo}')
        d.e('ps_motivo_g', 'motivos', 'build', 'mensaje')
    if d.puede('motivos', 'eliminacion'):   # PMotivos.jsx: borrable
        d.ps('ps_motivo_d', 'ps Eliminar Motivo', 'motivo', 'destroy()')
        d.e('motivos', 'ps_motivo_d', 'link', url('motivos.destroy'))
        d.e('ps_motivo_d', 'motivos', 'build', 'mensaje')


# ------------------------------------------------------------------ CU6
def validacion_pagos(d):
    d.hoja('CU6 Validación de pagos')
    d.p('validacion-pagos', 'cliente', 'Validacion de Pagos', 'estado, datos, revisar', 'origenDeCuota(), recargar()')
    entrada(d, 'validacion-pagos')
    d.ps('ps_cuotas', 'ps Listar Cuotas', 'estado', 'cuotas()')
    d.e('validacion-pagos', 'ps_cuotas', 'link', url('pagos.cuotas', '?estado'))
    d.e('ps_cuotas', 'validacion-pagos', 'build', 'cuotas, comprobantes')
    ficha(d, 'validacion-pagos')
    d.p('f_revisar', 'cliente', 'Modal de revisión', 'observacion, archivo', 'decidir()')
    d.abrir_formulario('validacion-pagos', 'f_revisar', 'Revisar / Ver')
    d.ps('ps_comp', 'ps Ver Comprobante', 'comprobante', 'comprobante()')
    d.e('f_revisar', 'ps_comp', 'link', url('pagos.comprobante', ' (si hay comprobante)'))
    d.e('ps_comp', 'f_revisar', 'build', 'comprobante')
    if d.puede('validacion-pagos', 'modificacion'):
        d.hoja('CU6 Aprobar o rechazar cuota')
        entrada(d, 'validacion-pagos')
        d.abrir_formulario('validacion-pagos', 'f_revisar', 'Revisar / Ver')
        for k, fn, nombre, op in (('ps_aprobar', 'pagos.aprobar', 'ps Aprobar Cuota', 'aprobar()'),
                                  ('ps_rechazar', 'pagos.rechazar', 'ps Rechazar Cuota', 'rechazar()')):
            d.ps(k, nombre, 'orden, cuota, observacion', op)
            condicion = ' (solo cuota En revisión y no Stripe)'
            if k == 'ps_rechazar':
                condicion = ' (cuota En revisión, no Stripe y observación obligatoria)'
            d.e('f_revisar', k, 'link', url(fn, condicion))
            d.e(k, 'validacion-pagos', 'build', 'mensaje')


def alumnos(d):   # CU6: matrículas y exportación al SIS
    d.hoja('CU6 Matrículas y SIS')
    d.p('alumnos', 'cliente', 'Matriculas y SIS', 'inscripciones, pendientes, enviando', 'exportar(), resultado()')
    entrada(d, 'alumnos')
    d.ps('ps_insc', 'ps Listar Inscripciones', 'usuario', 'inscripciones()')
    d.e('alumnos', 'ps_insc', 'link', url('seguimiento.inscripciones'))
    d.e('ps_insc', 'alumnos', 'build', 'inscripciones')
    d.ps('ps_pend', 'ps Exportaciones Pendientes', 'usuario', 'pendientes()')
    d.e('alumnos', 'ps_pend', 'link', url('exportaciones.pendientes'))
    d.e('ps_pend', 'alumnos', 'build', 'total, filas')
    if d.puede('alumnos', 'modificacion'):   # PMatriculas.jsx: editable
        d.ps('ps_exportar', 'ps Exportar al SIS', 'usuario', 'exportar()')
        d.e('alumnos', 'ps_exportar', 'link', url('exportaciones.exportar', ' (clic Exportar pendientes)'))
        d.e('ps_exportar', 'alumnos', 'build', 'descarga CSV; registrar resultado después')
        d.ps('ps_resultado', 'ps Registrar Resultado', 'exportacion, estado, respuesta', 'registrarResultado()')
        d.e('alumnos', 'ps_resultado', 'link', url('exportaciones.registrarResultado'))
        d.e('ps_resultado', 'alumnos', 'build', 'mensaje')


def pagos_ficha(d):   # CU6 dentro de la ficha (componentes/pagos)
    d.hoja('CU6 Plan de pagos y métodos en la ficha')
    ficha(d, 'agenda')
    if d.actor == 'Vendedor':
        d.p('f_orden', 'form', 'Generar Orden de Pago', 'modulos, dctos, formaPago, cuotas, vence', 'generarOrden(), seleccionarModulo(), alternarDescuento()')
        d.abrir_formulario('ficha', 'f_orden', 'Generar orden de pago')
        d.ps('ps_catalogo', 'ps Catalogo', 'buscar', 'programas()')
        d.e('f_orden', 'ps_catalogo', 'link', url('catalogo.programas'))
        d.e('ps_catalogo', 'f_orden', 'build', 'programas')
        d.ps('ps_desc', 'ps Listar Descuentos', 'token', 'descuentos()')
        d.e('f_orden', 'ps_desc', 'link', url('pagos.descuentos'))
        d.e('ps_desc', 'f_orden', 'build', 'descuentos')
        d.ps('ps_orden', 'ps Crear Orden', 'interes, modulos, descuentos, cuotas, primer_vencimiento', 'crearOrden()')
        d.e('f_orden', 'ps_orden', 'submit', url('pagos.crearOrden', ' (vendedor asignado; tarjeta abierta; sin orden activa)'))
        d.e('ps_orden', 'ficha', 'build', 'orden')
    d.hoja('CU6 Métodos de pago')
    ficha(d, 'agenda')
    d.ps('ps_estmetodo', 'ps Cambiar Estado Metodo', 'metodo, estado', 'cambiarEstadoMetodo()')
    d.e('ficha', 'ps_estmetodo', 'link', url('pagos.cambiarEstadoMetodo', ' (clic activar/desactivar método)'))
    d.e('ps_estmetodo', 'ficha', 'build', 'metodo')
    d.hoja('CU6 Anular orden')
    ficha(d, 'agenda')
    d.p('f_anular', 'form', 'Anular Orden', 'motivo', 'enviar()')
    d.abrir_formulario('ficha', 'f_anular', 'Detalles > Anular')
    d.ps('ps_anular_orden', 'ps Anular Orden', 'orden, motivo', 'anularOrden()')
    d.e('f_anular', 'ps_anular_orden', 'submit', url('pagos.anularOrden'))
    d.e('ps_anular_orden', 'ficha', 'build', 'mensaje, orden')
    d.hoja('CU6 Registrar tarjeta con Stripe')
    ficha(d, 'agenda')
    d.p('compartir', 'cliente', 'Compartir Enlace de Pago', 'sesion, vistaCorreo, copiado', 'compartirPorWhatsApp(), copiarEnlace()')
    d.e('ficha', 'compartir', 'link', 'Pagos > Solicitar registro de tarjeta')
    d.ps('ps_setup_stripe', 'ps Preparar Tarjeta Stripe', 'prospecto, nro_tarjeta', 'crearSetupTarjeta()')
    d.e('compartir', 'ps_setup_stripe', 'link', url('pagos.crearSetupTarjeta'))
    d.e('ps_setup_stripe', 'compartir', 'build', 'url')
    d.hoja('CU6 Enlace de pago de una cuota')
    ficha(d, 'agenda')
    d.p('compartir', 'cliente', 'Compartir Enlace de Pago', 'sesion, vistaCorreo, copiado', 'compartirPorWhatsApp(), copiarEnlace()')
    d.e('ficha', 'compartir', 'link', 'Pagos > Enviar solicitud de pago')
    d.ps('ps_checkout', 'ps Iniciar Checkout Stripe', 'orden, cuota', 'crearCheckout()')
    d.e('compartir', 'ps_checkout', 'link', url('pagos.crearCheckout'))
    d.e('ps_checkout', 'compartir', 'build', 'url, url_cuota')
    d.hoja('CU6 Enviar el enlace por correo')
    d.p('compartir', 'cliente', 'Compartir Enlace de Pago', 'sesion, vistaCorreo, copiado', 'compartirPorWhatsApp(), copiarEnlace()')
    d.p('f_correo', 'form', 'Enviar por Correo', 'destinatario, tipo, mensaje', 'enviarCorreo()')
    d.e('compartir', 'f_correo', 'contiene')
    d.ps('ps_enviar', 'ps Enviar Notificacion', 'destinatario, tipo, mensaje, enlace, texto_boton', 'enviar()')
    d.e('f_correo', 'ps_enviar', 'submit', url('notificaciones.enviar'))
    d.e('ps_enviar', 'compartir', 'build', 'mensaje')
    d.hoja('CU6 Retorno de Stripe')
    retorno_stripe(d)


def retorno_stripe(d):
    externo = lambda: d.p('stripe', 'externo', 'Stripe Checkout (externo)', 'url, session_id', 'pagar(), cancelar()')
    externo()
    d.p('pago_confirmacion', 'cliente', 'Confirmacion de Stripe', 'sessionId, token, estado', 'accionVolver()')
    d.e('stripe', 'pago_confirmacion', 'link', 'success_url ?session_id&token')
    d.ps('ps_retorno_publico', 'ps Ver Retorno Público', 'sessionId, token', 'consultarRetornoPublico()')
    d.e('pago_confirmacion', 'ps_retorno_publico', 'link', url('pagos.consultarRetornoPublico', '?token'))
    d.e('ps_retorno_publico', 'pago_confirmacion', 'build', 'estado del pago')
    d.p('catalogo', 'cliente', 'Catalogo de Programas', 'datos, area, eleccion, registrando', 'coloresDeAreas(), recargar()')
    ir_catalogo = '/anuncios' if d.actor == 'Visitante' else '/anuncios (retorno público)'
    d.e('pago_confirmacion', 'catalogo', 'link', ir_catalogo)
    d.hoja('CU6 Pago cancelado en Stripe' + (' (visitante)' if d.actor == 'Visitante' else ''))
    externo()
    d.p('pago_cancelado', 'cliente', 'Cancelacion de Stripe', 'sessionId, token, estado', 'PPagoCancelado()')
    d.e('stripe', 'pago_cancelado', 'link', 'cancel_url ?session_id&token')
    d.ps('ps_cancelar_publico', 'ps Cancelar Retorno', 'sessionId, token', 'cancelarRetornoPublico()')
    d.e('pago_cancelado', 'ps_cancelar_publico', 'link', url('pagos.cancelarRetornoPublico', ' token (cuerpo)'))
    d.e('ps_cancelar_publico', 'pago_cancelado', 'build', 'estado, url_checkout')
    d.e('pago_cancelado', 'catalogo', 'link', ir_catalogo)
    d.e('pago_cancelado', 'stripe', 'link', 'url_checkout (reintentar)')
    d.e('pago_cancelado', 'pago_confirmacion', 'link', 'Ver confirmación (si Stripe ya confirmó)')
    if d.actor != 'Visitante':
        d.hoja('CU6 Retorno autenticado sin token público')
        d.ps('ps_confirmar_checkout', 'ps Confirmar Sesion Stripe', 'sessionId', 'confirmarCheckout()')
        d.e('pago_confirmacion', 'ps_confirmar_checkout', 'link', url('pagos.confirmarCheckout', ' (sin token público)'))
        d.e('ps_confirmar_checkout', 'pago_confirmacion', 'build', 'estado del pago')
        d.ps('ps_cancelar_checkout', 'ps Cancelar Sesion Stripe', 'sessionId', 'cancelarCheckout()')
        d.e('pago_cancelado', 'ps_cancelar_checkout', 'link', url('pagos.cancelarCheckout', ' (sin token público)'))
        d.e('ps_cancelar_checkout', 'pago_cancelado', 'build', 'estado, url_checkout')
        for pagina in ('pago_confirmacion', 'pago_cancelado'):
            if d.actor == 'Administrador':
                d.e(pagina, 'agenda', 'link', '/agenda (sesión, ?interes={nro_tarjeta} si hay tarjeta)')
            else:
                d.e(pagina, 'ficha', 'link', '/agenda?interes={nro_tarjeta} (sesión y tarjeta disponible)')
                d.e(pagina, 'agenda', 'link', '/agenda (sesión sin tarjeta)')


# ------------------------------------------------------------------ CU7
def agenda(d):
    d.hoja('CU7 Seguimiento y agenda')
    d.p('agenda', 'cliente', 'Seguimiento y Agenda', 'buscar, estado, sel, enfocar, lista', 'recargar()')
    entrada(d, 'agenda')
    listar_intereses(d, 'agenda', '?buscar&estado')
    ficha(d, 'agenda')
    d.p('whatsapp', 'externo', 'WhatsApp (externo)')
    d.e('ficha', 'whatsapp', 'link', 'clic WhatsApp si hay teléfono')
    d.ps('ps_show', 'ps Ver Interes', 'interes', 'show()')
    d.e('ficha', 'ps_show', 'link', url('intereses.show'))
    d.e('ps_show', 'ficha', 'build', 'interes, faltantes_conversion')
    if not d.puede('agenda', 'modificacion'): return   # Ficha: editable = puede('agenda', 'modificacion')
    d.hoja('CU7 Contacto y recordatorios')
    ficha(d, 'agenda')
    d.p('f_contacto', 'form', 'Registrar Contacto', 'tipo, descripcion, resultado', 'guardar()')
    d.e('ficha', 'f_contacto', 'contiene')
    d.ps('ps_interac', 'ps Registrar Interaccion', 'interes, tipo, descripcion, resultado', 'registrarInteraccion()')
    d.e('f_contacto', 'ps_interac', 'submit', url('seguimiento.registrarInteraccion'))
    d.e('ps_interac', 'ficha', 'build', 'mensaje')
    d.p('f_record', 'form', 'Agendar Recordatorio', 'fecha_programada, descripcion', 'agendar()')
    d.e('ficha', 'f_record', 'contiene')
    d.ps('ps_crearrec', 'ps Crear Recordatorio', 'interes, fecha_programada, descripcion', 'crearRecordatorio()')
    d.e('f_record', 'ps_crearrec', 'submit', url('seguimiento.crearRecordatorio'))
    d.e('ps_crearrec', 'ficha', 'build', 'mensaje')
    d.p('f_realizada', 'form', 'Marcar Realizada', 'resultado')
    d.abrir_formulario('ficha', 'f_realizada', 'Marcar realizada')
    d.ps('ps_completar', 'ps Completar Recordatorio', 'recordatorio, resultado', 'completarRecordatorio()')
    d.e('f_realizada', 'ps_completar', 'submit', url('seguimiento.completarRecordatorio'))
    d.e('ps_completar', 'ficha', 'build', 'mensaje')
    d.ps('ps_cancelar', 'ps Cancelar Recordatorio', 'recordatorio', 'cancelarRecordatorio()')
    d.e('ficha', 'ps_cancelar', 'link', url('seguimiento.cancelarRecordatorio'))
    d.e('ps_cancelar', 'ficha', 'build', 'mensaje')
    d.hoja('CU7 Editar prospecto y convertir')
    ficha(d, 'agenda')
    d.p('f_editar', 'form', 'Editar Prospecto', 'nombre, apellido, correo, telefono, profesion, ubicacion, origen', 'guardar()')
    d.abrir_formulario('ficha', 'f_editar', 'Editar datos')
    d.ps('ps_update', 'ps Actualizar Prospecto', 'prospecto, nombre, apellido, correo, telefono, profesion, ubicacion, origen', 'update()')
    d.e('f_editar', 'ps_update', 'submit', url('prospectos.update'))
    d.e('ps_update', 'ficha', 'build', 'mensaje, prospecto')
    if d.puede('embudo', 'modificacion'):   # el botón Convertir llama a intereses.mover (ruta acceso:embudo)
        d.ps('ps_mover', 'ps Mover Tarjeta', 'interes, estado, motivo_perdida, observacion', 'mover()')
        d.e('ficha', 'ps_mover', 'link', url('intereses.mover') + ' estado=Convertido')
        d.e('ps_mover', 'ficha', 'build', 'mensaje, interes')
        d.p('embudo', 'cliente', 'Embudo de Ventas', 'filtros, datos, arrastrada, encima, perdida, faltantes', 'mover(), agrupar(), recargar()')
        d.e('ficha', 'embudo', 'link', '/embudo')


def inicio_vendedor(d):   # CU7: Mi día
    d.hoja('CU7 Mi día')
    d.p('inicio-vendedor', 'cliente', 'Mi Dia', 'mes, dia, completar, stats, agenda', 'clave()')
    entrada(d, 'inicio-vendedor')
    d.ps('ps_estvend', 'ps Estadisticas Vendedor', 'usuario', 'estadisticasVendedor()')
    d.e('inicio-vendedor', 'ps_estvend', 'link', url('reportes.estadisticasVendedor'))
    d.e('ps_estvend', 'inicio-vendedor', 'build', 'estadisticas')
    d.ps('ps_record', 'ps Listar Recordatorios', 'estado, desde, hasta', 'recordatorios()')
    d.e('inicio-vendedor', 'ps_record', 'link', url('seguimiento.recordatorios', '?desde&hasta'))
    d.e('ps_record', 'inicio-vendedor', 'build', 'recordatorios')
    ficha(d, 'inicio-vendedor')
    if d.puede('agenda', 'modificacion'):
        d.p('f_realizada_dia', 'form', 'Marcar Actividad Realizada', 'resultado')
        d.abrir_formulario('inicio-vendedor', 'f_realizada_dia', 'Marcar realizada')
        d.ps('ps_completar', 'ps Completar Recordatorio', 'recordatorio, resultado', 'completarRecordatorio()')
        d.e('f_realizada_dia', 'ps_completar', 'submit', url('seguimiento.completarRecordatorio'))
        d.e('ps_completar', 'inicio-vendedor', 'build', 'mensaje')


def notificaciones(d):   # CU7
    d.hoja('CU7 Notificaciones')
    d.p('notificaciones', 'cliente', 'Notificaciones', 'datos, form, enviando', 'enviar(), recargar()')
    entrada(d, 'notificaciones')
    d.ps('ps_notif', 'ps Listar Notificaciones', 'usuario', 'index()')
    d.e('notificaciones', 'ps_notif', 'link', url('notificaciones.index'))
    d.e('ps_notif', 'notificaciones', 'build', 'notificaciones')
    d.ps('ps_leida', 'ps Marcar Leida', 'notificacion', 'marcarLeida()')
    d.e('notificaciones', 'ps_leida', 'link', url('notificaciones.marcarLeida'))
    d.e('ps_leida', 'notificaciones', 'build', 'notificacion')
    if d.puede('notificaciones', 'modificacion') or d.puede('agenda', 'modificacion'):   # PNotificaciones.jsx: puedeEnviar
        d.p('f_notif', 'form', 'Enviar Notificacion', 'destinatario, tipo, mensaje', 'enviar()')
        d.e('notificaciones', 'f_notif', 'contiene')
        d.ps('ps_enviar', 'ps Enviar Notificacion', 'destinatario, tipo, mensaje, enlace, texto_boton', 'enviar()')
        d.e('f_notif', 'ps_enviar', 'submit', url('notificaciones.enviar'))
        d.e('ps_enviar', 'notificaciones', 'build', 'mensaje')


# ------------------------------------------------------------------ CU8
def dashboard(d):
    d.hoja('CU8 Dashboard')
    d.p('dashboard', 'cliente', 'Dashboard', 'datos, cargando, error', 'moneda(), miles(), dia(), recargar()')
    entrada(d, 'dashboard')
    d.ps('ps_dash', 'ps Dashboard', 'usuario', 'dashboard()')
    d.e('dashboard', 'ps_dash', 'link', url('reportes.dashboard'))
    d.e('ps_dash', 'dashboard', 'build', 'indicadores, graficos')


def reportes(d):
    d.hoja('CU8 Reportes y estadísticas')
    d.p('reportes', 'cliente', 'Reportes y Estadisticas', 'vista, f, est, rep', 'set()')
    entrada(d, 'reportes')
    filtro_vendedor = d.actor != 'Vendedor'
    parametros = 'desde, hasta' + (', vendedor' if filtro_vendedor else '') + ', programa, estado, buscar'
    filtros = 'desde&hasta' + ('&vendedor' if filtro_vendedor else '')
    d.ps('ps_est', 'ps Estadisticas', parametros, 'estadisticas()')
    d.e('reportes', 'ps_est', 'link', url('reportes.estadisticas', '?' + filtros))
    d.e('ps_est', 'reportes', 'build', 'graficos')
    d.hoja('CU8 Listados de reportes')
    entrada(d, 'reportes')
    d.ps('ps_listado', 'ps Listado', 'tipo, ' + parametros, 'listado()')
    d.e('reportes', 'ps_listado', 'link', url('reportes.listado', '?tipo&' + filtros + '&buscar'))
    d.e('ps_listado', 'reportes', 'build', 'titulo, columnas, filas')
    d.p('reporte_csv', 'externo', 'Reporte CSV descargado')
    d.e('reportes', 'reporte_csv', 'link', 'clic Exportar CSV con filas del listado')
    if 'inicio-vendedor' not in d.permisos: vendedores(d, 'reportes')   # PReportes.jsx: el vendedor no filtra


def seguimiento(d):   # CU8: ventas y comisiones
    d.hoja('CU8 Ventas y comisiones')
    d.p('seguimiento', 'cliente', 'Ventas y Comisiones', 'comisiones, resumen, porcentaje', 'recargar()')
    entrada(d, 'seguimiento')
    d.ps('ps_comis', 'ps Listar Comisiones', 'usuario', 'comisiones()')
    d.e('seguimiento', 'ps_comis', 'link', url('seguimiento.comisiones'))
    d.e('ps_comis', 'seguimiento', 'build', 'comisiones, porcentaje')
    if d.puede('seguimiento', 'modificacion'):   # PComisiones.jsx: gestiona
        d.ps('ps_resumen', 'ps Resumen Comisiones', 'usuario', 'resumenComisiones()')
        d.e('seguimiento', 'ps_resumen', 'link', url('seguimiento.resumenComisiones'))
        d.e('ps_resumen', 'seguimiento', 'build', 'vendedores')
        d.ps('ps_pagar', 'ps Pagar Comisiones', 'vendedor', 'pagarComisiones()')
        d.e('seguimiento', 'ps_pagar', 'link', url('seguimiento.pagarComisiones'))
        d.e('ps_pagar', 'seguimiento', 'build', 'mensaje')
    if d.actor == 'Administrador':   # PComisiones.jsx: rol === 'administrador'
        d.p('f_porcentaje', 'form', 'Porcentaje de Comision', 'porcentaje')
        d.e('seguimiento', 'f_porcentaje', 'contiene')
        d.ps('ps_porcentaje', 'ps Configurar Comision', 'porcentaje', 'actualizarConfiguracionComision()')
        d.e('f_porcentaje', 'ps_porcentaje', 'submit', url('seguimiento.actualizarConfiguracionComision'))
        d.e('ps_porcentaje', 'seguimiento', 'build', 'mensaje, porcentaje')


# ------------------------------------------------------------------ diagramas por actor
# El menú real se ordena por recursos.orden; CU6 dentro de agenda va inmediatamente después de la ficha.
BLOQUES = [('dashboard', dashboard), ('inicio-vendedor', inicio_vendedor), ('embudo', embudo),
           ('prospectos', prospectos), ('interesados', interesados), ('agenda', agenda),
           ('agenda-pagos', pagos_ficha), ('motivos', motivos), ('validacion-pagos', validacion_pagos),
           ('alumnos', alumnos), ('gestion-anuncios', gestion_anuncios), ('seguimiento', seguimiento),
           ('reportes', reportes), ('notificaciones', notificaciones), ('usuarios', usuarios),
           ('matriz', matriz), ('bitacora', bitacora)]


def rol(nombre_rol, actor):
    d = Diagrama(PERMISOS[nombre_rol], actor)
    inicio_sesion(d)
    inicio = 'inicio-vendedor' if d.puede('inicio-vendedor') else 'dashboard'
    d.grupo = inicio
    d.p(inicio, 'cliente', 'Mi Dia' if inicio == 'inicio-vendedor' else 'Dashboard',
        'mes, dia, completar, stats, agenda' if inicio == 'inicio-vendedor' else 'datos, cargando, error',
        'clave()' if inicio == 'inicio-vendedor' else 'moneda(), miles(), dia(), recargar()')
    d.e('menu', inicio, 'link', RECURSOS[inicio]['ruta'] + ' (primera vista tras iniciar sesión)')
    sesion_y_perfil(d)
    for codigo, bloque in BLOQUES:
        d.grupo = codigo
        if codigo == 'bitacora' and d.permisos.get('bitacora'):
            d.hoja('CU1 Bitácora de accesos'); bloque(d)
        elif codigo == 'agenda-pagos':
            if d.puede('agenda', 'modificacion'): bloque(d)
        elif codigo in d.permisos and codigo != 'bitacora':
            bloque(d)
    d.grupo = 'busqueda'
    destinos_busqueda(d)
    d.grupo = 'compartidas'
    compartidas(d)
    return d


def compartidas(d):
    """Hoja final: cada parte compartida del servidor («include») con las tablas que lee o escribe."""
    if not d.incluidas: return
    d.hoja('Partes compartidas del servidor')
    i = 0
    while i < len(d.incluidas):   # una parte compartida puede incluir otra (Stripe → conversión); una por sección
        if i: d.hoja('Partes compartidas del servidor')
        d.ps(d.incluidas[i], *INCLUIDAS[d.incluidas[i]][2:]); i += 1


def visitante():
    """CU2 público: catálogo (/anuncios) con búsqueda, registro de interés y enlace al login; CU6 público: pago de una
    cuota o registro de tarjeta con el enlace autorizado por token (lo abre el prospecto, sin sesión)."""
    d = Diagrama({}, 'Visitante')
    d.hoja('CU2 Catálogo y registro de interés')
    d.p('actor', 'actor', 'Visitante')
    d.p('catalogo', 'cliente', 'Catalogo de Programas', 'datos, area, eleccion, registrando', 'coloresDeAreas(), recargar()')
    d.e('actor', 'catalogo', 'link', '/anuncios')
    d.ps('ps_catalogo', 'ps Catalogo', 'buscar', 'programas()')
    d.e('catalogo', 'ps_catalogo', 'link', url('catalogo.programas'))
    d.e('ps_catalogo', 'catalogo', 'build', 'programas')
    d.p('registro_interes', 'cliente', 'Registro de interés', 'form, modulosSeleccionados, estado, enviando', 'alternarModulo(), enviar()')
    d.e('catalogo', 'registro_interes', 'link', 'elegir programa o módulo > Me interesa')
    d.e('registro_interes', 'catalogo', 'link', 'Volver a la malla')
    d.p('f_interes', 'form', 'Formulario de interés', 'nombre, apellido, documento, telefono, correo, profesion, ubicacion, modulosSeleccionados',
        'enviar(), alternarModulo()')
    d.e('registro_interes', 'f_interes', 'contiene')
    d.ps('ps_registro', 'ps Registrar Interes', 'nombre, apellido, documento, telefono, correo, profesion, ubicacion, modulo_codigos',
         'registrarInteres()')
    d.e('f_interes', 'ps_registro', 'submit', url('catalogo.registrarInteres'))
    d.e('ps_registro', 'registro_interes', 'build', 'aviso de éxito o errores en el formulario')
    d.p('login', 'cliente', 'Login', 'form, recordar, ver, error, enviando', 'entrar()')
    d.e('catalogo', 'login', 'link', '/login')
    d.grupo = 'publico'
    d.hoja('CU2 Búsqueda, visitas y página no encontrada')
    d.p('catalogo', 'cliente', 'Catalogo de Programas', 'datos, area, eleccion, registrando', 'coloresDeAreas(), recargar()')
    d.ps('ps_buscar', 'ps Busqueda Global', 'q', 'buscar()')
    d.e('catalogo', 'ps_buscar', 'link', url('sitio.buscar', '?q (tras escribir 2 caracteres)'))
    d.p('resultados_busqueda', 'cliente', 'Resultados de búsqueda', 'resultados, activo, abierto', 'elegir(), tecla()')
    d.e('ps_buscar', 'resultados_busqueda', 'build', 'resultados del catálogo')
    d.e('resultados_busqueda', 'catalogo', 'link', '/anuncios?modulo={codigo}')
    visitas(d, 'catalogo')
    d.p('error404', 'cliente', 'Pagina no Encontrada', 'titulo, icono', 'PError404()')
    d.e('actor', 'error404', 'link', 'URL inexistente (*)')
    d.e('error404', 'catalogo', 'link', '/anuncios (Ir al catálogo)')
    d.grupo = 'pago'
    d.hoja('CU6 Pago público de una cuota')
    d.p('actor', 'actor', 'Visitante')
    d.p('pago_cuota', 'cliente', 'Pago Publico de Cuota', 'token, estado', 'PPagoCuota()')
    d.e('actor', 'pago_cuota', 'link', '/pagos/cuota?token')
    d.ps('ps_cuota_publica', 'ps Abrir Enlace Publico de Cuota', 'token', 'abrirEnlaceCuotaPublico()')
    d.e('pago_cuota', 'ps_cuota_publica', 'link', url('pagos.abrirEnlaceCuotaPublico'))
    d.e('ps_cuota_publica', 'pago_cuota', 'build', 'estado_link, url_checkout')
    d.p('stripe', 'externo', 'Stripe Checkout (externo)', 'url, session_id', 'pagar(), cancelar()')
    d.e('pago_cuota', 'stripe', 'link', 'Cuota pendiente y URL disponible (redirige salvo sin_redirigir; botón Ir a pagar)')
    d.e('pago_cuota', 'catalogo', 'link', '/anuncios (Volver al catálogo)')
    d.hoja('CU6 Enlace público para registrar tarjeta')
    d.p('actor', 'actor', 'Visitante')
    d.p('stripe', 'externo', 'Stripe Checkout (externo)', 'url, session_id', 'pagar(), cancelar()')
    d.e('actor', 'stripe', 'link', 'enlace Stripe Setup compartido por el vendedor')
    d.hoja('CU6 Retorno de Stripe al visitante')
    retorno_stripe(d)
    compartidas(d)
    return d


# Un diagrama por actor del Capítulo V, en el orden de 7.5 (contenido.ACTORES)
DIAGRAMAS = {'Administrador': lambda: rol('administrador', 'Administrador'),
             'Coordinador': lambda: rol('coordinador', 'Coordinador'),
             'Vendedor': lambda: rol('vendedor', 'Vendedor'),
             'Visitante': visitante}
ACTORES = {a: (lambda f=f: (lambda d: (d.paginas, d.enlaces))(f())) for a, f in DIAGRAMAS.items()}


def hojas(actor):
    """(paginas, enlaces, [(título, [claves], [relaciones])]) del actor: cada sección con lo que se dibuja en ella."""
    d = DIAGRAMAS[actor]()
    return d.paginas, d.enlaces, d.hojas


def hojas_visuales(actor):
    """Vista de navegación: pantallas, formularios, acciones y una tabla representativa por recurso.

    El modelo exhaustivo de rutas y tablas sigue disponible en hojas() y verificar(); el dibujo de 7.5
    prioriza lo que el actor puede recorrer, como los diagramas del documento G07.
    """
    d = DIAGRAMAS[actor]()
    paginas, enlaces = d.paginas, d.enlaces
    conservar = {k for k, (tipo, *_resto) in paginas.items() if tipo in ('actor', 'cliente', 'form', 'externo')}
    acciones_clave = {
        'ps_login', 'ps_me', 'ps_logout', 'ps_buscar', 'ps_visita', 'ps_dash', 'ps_estvend',
        'ps_usuarios', 'ps_matriz', 'ps_catalogo', 'ps_prosp', 'ps_intereses', 'ps_show',
        'ps_repartir', 'ps_mover', 'ps_sinc', 'ps_cuotas', 'ps_exportar', 'ps_resultado',
        'ps_estmetodo', 'ps_setup_stripe', 'ps_checkout', 'ps_cuota_publica',
        'ps_retorno_publico', 'ps_cancelar_publico', 'ps_confirmar_checkout', 'ps_cancelar_checkout',
        'ps_comp', 'ps_aprobar', 'ps_rechazar', 'ps_foto_usuario', 'ps_leida', 'ps_pagar', 'ps_est', 'ps_listado', 'ps_comis',
    }
    for a, b, st, texto in enlaces:
        if paginas[b][0] != 'ps' or a not in conservar or st not in ('link', 'submit'):
            continue
        if st == 'submit' or b in acciones_clave:
            conservar.add(b)
    tablas_clave = {'bd_usuarios', 'bd_programas', 'bd_cuotas'}
    acceso_representativo = {}
    for a, b, st, _ in enlaces:
        if st == 'access' and a in conservar and b in tablas_clave and b not in acceso_representativo:
            conservar.add(b); acceso_representativo[b] = (a, b)
    claves = [k for k in paginas if k in conservar]
    # Los atributos siguen siendo del código, con el detalle adecuado para una figura de navegación.
    visual = {k: (tipo, nombre, ', '.join(atributos.split(', ')[:3]), ', '.join(operaciones.split(', ')[:2]))
              for k in claves for tipo, nombre, atributos, operaciones in (paginas[k],)}
    relaciones = [e for e in enlaces if e[0] in visual and e[1] in visual and
                  (e[2] != 'access' or (e[0], e[1]) == acceso_representativo.get(e[1]))]
    acciones_agenda = {'f_realizada', 'ps_completar', 'ps_cancelar', 'f_editar', 'ps_update'}
    enlaces_pago = {'compartir', 'ps_setup_stripe', 'ps_checkout', 'f_correo', 'ps_enviar',
                    'stripe', 'pago_confirmacion', 'ps_confirmar_checkout', 'pago_cancelado', 'ps_cancelar_checkout'}
    grupos = {k: ('agenda' if k == 'ficha' else
                  'agenda-acciones' if d.grupo_nodo[k] == 'agenda' and k in acciones_agenda else
                  'pagos-enlaces' if d.grupo_nodo[k] == 'agenda-pagos' and k in enlaces_pago else d.grupo_nodo[k])
              for k in claves}
    return visual, relaciones, grupos


def vista_administrador():
    """Vista de navegación del administrador con accesos representativos a tablas reales."""
    paginas, enlaces, _ = hojas('Administrador')
    visuales, relaciones, _ = hojas_visuales('Administrador')
    visuales = {k: v for k, v in visuales.items() if v[0] != 'bd'}
    tablas = {
        ('ps_login', 'bd_usuarios'), ('ps_intereses', 'bd_intereses'),
        ('ps_sinc', 'bd_programas'), ('ps_cuotas', 'bd_cuotas'),
        ('ps_comis', 'bd_comisiones'),
    }
    accesos = [e for e in enlaces if e[:2] in tablas and e[2] == 'access']
    assert {e[:2] for e in accesos} == tablas, 'Revisar los accesos de navegación del administrador'
    visuales.update({b: paginas[b] for _, b, _, _ in accesos})
    return visuales, [e for e in relaciones if e[2] != 'access'] + accesos


def vista_rol(actor):
    """Navegación visible de 7.5, con accesos representativos a tablas concretas."""
    if actor == 'Administrador':
        return vista_administrador()
    paginas, enlaces, _ = hojas(actor)
    internos = set(INCLUIDAS)
    visuales = {k: v for k, v in paginas.items() if v[0] != 'bd' and k not in internos}
    tablas = {
        'Coordinador': {('ps_login', 'bd_usuarios'), ('ps_intereses', 'bd_intereses'),
                        ('ps_cuotas', 'bd_cuotas'), ('ps_comis', 'bd_comisiones')},
        'Vendedor': {('ps_login', 'bd_usuarios'), ('ps_intereses', 'bd_intereses'),
                      ('ps_orden', 'bd_ordenes_pago'), ('ps_record', 'bd_recordatorios')},
        'Visitante': {('ps_catalogo', 'bd_programas'), ('ps_registro', 'bd_prospectos'),
                       ('ps_cuota_publica', 'bd_cuotas')},
    }[actor]
    accesos = [e for e in enlaces if e[2] == 'access' and e[:2] in tablas]
    assert {e[:2] for e in accesos} == tablas, f'{actor}: revisar las tablas representativas'
    relaciones = [e for e in enlaces if e[0] in visuales and e[1] in visuales]
    visuales.update({b: paginas[b] for _, b, _, _ in accesos})
    for k, (tipo, nombre, atributos, operaciones) in list(visuales.items()):
        if tipo == 'form':
            operaciones = ''
        elif tipo != 'bd':
            atributos = ', '.join(atributos.split(', ')[:4])
            operaciones = ', '.join(operaciones.split(', ')[:2])
        visuales[k] = (tipo, nombre, atributos, operaciones)
    return visuales, relaciones + accesos


# ------------------------------------------------------------------ coherencia con el código (documento_p2.py la exige)
# Cada «server page» es una o más funciones de presentacion/src/api/<area>.js (cada una = una ruta de api.php = un
# método de la clase N con el mismo nombre). verificar() lo comprueba todo contra el código que lee codigo.py.
API = {
    'ps_login': 'auth.login', 'ps_me': 'auth.me', 'ps_perfil': 'auth.actualizarPerfil', 'ps_clave': 'auth.cambiarPassword',
    'ps_logout': 'auth.logout', 'ps_visita': 'sitio.visita', 'ps_buscar': 'sitio.buscar',
    'ps_usuarios': 'usuarios.index', 'ps_usuario_g': 'usuarios.store usuarios.update', 'ps_estado': 'usuarios.cambiarEstado',
    'ps_foto_usuario': 'usuarios.foto',
    'ps_vend': 'usuarios.vendedores', 'ps_matriz': 'seguridad.matriz', 'ps_asig_perm': 'seguridad.asignar',
    'ps_bitacora': 'seguridad.bitacora', 'ps_bresumen': 'seguridad.resumen',
    'ps_catalogo': 'catalogo.programas', 'ps_sinc': 'catalogo.sincronizar', 'ps_registro': 'catalogo.registrarInteres',
    'ps_prosp': 'prospectos.index', 'ps_alta': 'prospectos.store', 'ps_csv': 'prospectos.importarCSV', 'ps_update': 'prospectos.update',
    'ps_nuevo_interes': 'prospectos.crearInteres',
    'ps_intereses': 'intereses.index', 'ps_show': 'intereses.show', 'ps_mover': 'intereses.mover',
    'ps_asignar': 'intereses.asignar', 'ps_repartir': 'intereses.distribuir',
    'ps_motivos': 'motivos.index', 'ps_motivo_g': 'motivos.store motivos.update', 'ps_motivo_d': 'motivos.destroy',
    'ps_desc': 'pagos.descuentos', 'ps_estmetodo': 'pagos.cambiarEstadoMetodo', 'ps_orden': 'pagos.crearOrden',
    'ps_cuota_publica': 'pagos.abrirEnlaceCuotaPublico', 'ps_retorno_publico': 'pagos.consultarRetornoPublico',
    'ps_cancelar_publico': 'pagos.cancelarRetornoPublico',
    'ps_setup_stripe': 'pagos.crearSetupTarjeta', 'ps_checkout': 'pagos.crearCheckout',
    'ps_confirmar_checkout': 'pagos.confirmarCheckout', 'ps_cancelar_checkout': 'pagos.cancelarCheckout',
    'ps_anular_orden': 'pagos.anularOrden',
    'ps_cuotas': 'pagos.cuotas', 'ps_comp': 'pagos.comprobante', 'ps_aprobar': 'pagos.aprobar', 'ps_rechazar': 'pagos.rechazar',
    'ps_insc': 'seguimiento.inscripciones', 'ps_pend': 'exportaciones.pendientes', 'ps_exportar': 'exportaciones.exportar',
    'ps_resultado': 'exportaciones.registrarResultado',
    'ps_interac': 'seguimiento.registrarInteraccion', 'ps_crearrec': 'seguimiento.crearRecordatorio',
    'ps_record': 'seguimiento.recordatorios', 'ps_completar': 'seguimiento.completarRecordatorio',
    'ps_cancelar': 'seguimiento.cancelarRecordatorio', 'ps_notif': 'notificaciones.index', 'ps_enviar': 'notificaciones.enviar',
    'ps_leida': 'notificaciones.marcarLeida',
    'ps_comis': 'seguimiento.comisiones', 'ps_resumen': 'seguimiento.resumenComisiones', 'ps_pagar': 'seguimiento.pagarComisiones',
    'ps_porcentaje': 'seguimiento.actualizarConfiguracionComision', 'ps_dash': 'reportes.dashboard',
    'ps_estvend': 'reportes.estadisticasVendedor', 'ps_est': 'reportes.estadisticas', 'ps_listado': 'reportes.listado',
}
# Partes compartidas del servidor que varios server pages ejecutan («include»): clave -> (clase N, métodos, nombre, atributos,
# operaciones). Al recorrer la cadena de un endpoint, la llamada a uno de estos métodos se dibuja como «include».
INCLUIDAS = {
    'ps_conversion': ('NConversion', 'faltantes procesar', 'ps Conversion a Matricula', 'interes, usuario', 'faltantes(), procesar()'),
    'ps_conf_pago': ('NStripe', 'confirmarPagoDesdeSesion', 'ps Confirmar Pago Stripe', 'sesion, txInicial, actor', 'confirmarPagoDesdeSesion()'),
    'ps_conf_setup': ('NStripe', 'confirmarSetupDesdeSesion', 'ps Confirmar Setup Stripe', 'sesion, txInicial', 'confirmarSetupDesdeSesion()'),
}
CORTES = {f'{c}.{m}' for c, ms, *_ in INCLUIDAS.values() for m in ms.split()}
# client page / formulario -> archivos de presentacion/src donde están sus atributos y operaciones (verificar() los busca)
FUENTE = {
    'login': 'paginas/PLogin.jsx', 'f_login': 'paginas/PLogin.jsx', 'error': 'paginas/PLogin.jsx componentes/ui.jsx',
    'exito': 'componentes/ui.jsx', 'pie': 'plantilla/AppShell.jsx componentes/Shell.jsx',
    'menu': 'plantilla/AppShell.jsx componentes/Shell.jsx', 'resultados_busqueda': 'componentes/Shell.jsx',
    'f_perfil': 'componentes/Shell.jsx', 'f_clave': 'componentes/Shell.jsx', 'error404': 'paginas/PError404.jsx componentes/ui.jsx',
    'catalogo': 'paginas/PCatalogo.jsx componentes/ui.jsx', 'registro_interes': 'paginas/PCatalogo.jsx',
    'gestion-anuncios': 'paginas/PCatalogo.jsx componentes/ui.jsx',
    'f_interes': 'paginas/PCatalogo.jsx',
    'usuarios': 'paginas/PUsuarios.jsx componentes/ui.jsx', 'f_usuario': 'paginas/PUsuarios.jsx',
    'matriz': 'paginas/PMatriz.jsx', 'f_permiso': 'paginas/PMatriz.jsx', 'bitacora': 'paginas/PBitacora.jsx',
    'prospectos': 'paginas/PProspectos.jsx componentes/ui.jsx', 'f_prospecto': 'paginas/PProspectos.jsx',
    'f_csv': 'paginas/PProspectos.jsx', 'f_nuevo_interes': 'paginas/PProspectos.jsx',
    'interesados': 'paginas/PAsignacion.jsx componentes/ui.jsx', 'f_asignar': 'paginas/PAsignacion.jsx api/intereses.js',
    'embudo': 'paginas/PEmbudo.jsx componentes/ui.jsx', 'f_perdida': 'paginas/PEmbudo.jsx',
    'motivos': 'paginas/PMotivos.jsx componentes/ui.jsx', 'f_motivo': 'paginas/PMotivos.jsx',
    'validacion-pagos': 'paginas/PValidacionPagos.jsx componentes/ui.jsx', 'f_revisar': 'paginas/PValidacionPagos.jsx',
    'alumnos': 'paginas/PMatriculas.jsx', 'agenda': 'paginas/PAgenda.jsx componentes/ui.jsx', 'ficha': 'paginas/PAgenda.jsx',
    'f_contacto': 'paginas/PAgenda.jsx', 'f_record': 'paginas/PAgenda.jsx', 'f_realizada': 'paginas/PAgenda.jsx',
    'f_editar': 'paginas/PAgenda.jsx', 'f_orden': 'componentes/pagos/FormularioOrdenPago.jsx',
    'f_anular': 'componentes/pagos/PlanPagos.jsx', 'compartir': 'componentes/pagos/ModalCompartirPago.jsx',
    'f_correo': 'componentes/pagos/ModalCompartirPago.jsx',
    'inicio-vendedor': 'paginas/PMiDia.jsx', 'f_realizada_dia': 'paginas/PMiDia.jsx',
    'notificaciones': 'paginas/PNotificaciones.jsx componentes/ui.jsx', 'f_notif': 'paginas/PNotificaciones.jsx',
    'dashboard': 'paginas/PDashboard.jsx componentes/ui.jsx', 'reportes': 'paginas/PReportes.jsx',
    'seguimiento': 'paginas/PComisiones.jsx componentes/ui.jsx', 'f_porcentaje': 'paginas/PComisiones.jsx',
    'pago_cuota': 'paginas/PPagoCuota.jsx', 'pago_confirmacion': 'paginas/PPagoConfirmacion.jsx',
    'pago_cancelado': 'paginas/PPagoCancelado.jsx',
}
SHELL = ('plantilla/AppShell.jsx', 'componentes/Shell.jsx')   # envuelven toda página: contador, búsqueda, perfil
ESTEREOTIPO_VALIDO = {   # (tipo origen, tipo destino) admitidos por cada estereotipo (Conallen; REGLAS §5)
    'link': {('actor', 'cliente'), ('actor', 'externo'), ('cliente', 'cliente'), ('cliente', 'form'), ('cliente', 'ps'), ('form', 'ps'), ('form', 'externo'),
             ('cliente', 'externo'), ('externo', 'cliente')},
    'submit': {('form', 'ps')}, 'build': {('ps', 'cliente'), ('ps', 'form')}, 'include': {('ps', 'ps')}, 'access': {('ps', 'bd')},
    'contiene': {('cliente', 'form'), ('cliente', 'cliente')},
}


def _definida(nombre, texto):
    """¿La operación existe en el código? función, const de función, componente o el recargar() de useDatos."""
    if nombre == 'recargar': return bool(re.search(r'\brecargar\b', texto))
    return bool(re.search(rf'(?:function\s+{nombre}\s*\(|const\s+{nombre}\s*=)', texto))


def verificar():
    """Errores de coherencia entre los diagramas de navegación y el código (vacío = todo cuadra)."""
    import codigo
    F, U, router = codigo.funciones_api(), codigo.usos_api(), codigo.paginas_router()
    rutas = {r['clave']: r for r in codigo.rutas_api()}
    C = codigo.clases_php()
    _, con_auth = codigo.usos_servicio_auth()
    archivo = {k: f'paginas/{router[r["ruta"]]}.jsx' for k, r in RECURSOS.items() if r['ruta'] in router}
    errores, usadas, archivos_vistos = [], set(), set()

    # Los controles anteriores cotejan nombres de API. Estos cotejan el recorrido del actor y el menú real.
    for actor, construir in DIAGRAMAS.items():
        d = construir()
        relaciones = {(a.split('#')[0], b.split('#')[0], st) for a, b, st, _ in d.enlaces}
        if actor == 'Visitante':
            for destino in ('catalogo', 'pago_cuota', 'stripe'):
                if ('actor', destino, 'link') not in relaciones:
                    errores.append(f'Visitante: falta la entrada pública a {destino}')
        else:
            inicio = 'inicio-vendedor' if actor == 'Vendedor' else 'dashboard'
            if ('actor', 'login', 'link') not in relaciones:
                errores.append(f'{actor}: la navegación no comienza en Login')
            if ('menu', inicio, 'link') not in relaciones:
                errores.append(f'{actor}: falta la primera vista {inicio} tras iniciar sesión')
            permisos = PERMISOS[actor.lower()]
            for recurso in permisos:
                if recurso not in ('catalogo', 'login') and ('menu', recurso, 'link') not in relaciones:
                    errores.append(f'{actor}: {recurso} tiene permiso pero no aparece en el menú')
            ajenos = [k for k, (tipo, *_resto) in d.paginas.items()
                      if tipo == 'cliente' and k in RECURSOS and not RECURSOS[k].get('publico') and k not in permisos]
            if ajenos:
                errores.append(f'{actor}: páginas sin permiso en el diagrama: {ajenos}')
        if any(a == 'menu' and b == 'error404' for a, b, *_ in d.enlaces):
            errores.append(f'{actor}: la página 404 no es un enlace del menú')

    def usos(arch):
        # Las llamadas de pagos viven en componentes importados por PAgenda: se siguen los imports locales.
        pending = [arch]; seen = set(); u = set()
        while pending:
            current = pending.pop()
            if current in seen: continue
            seen.add(current); u.update(U.get(current, ()))
            path = codigo.PRE / current
            if not path.exists(): continue
            for rel in re.findall(r"(?:from\s*|import\s*)['\"]([^'\"]+)['\"]", path.read_text(encoding='utf-8')):
                if not rel.startswith('.'): continue
                target = (path.parent / rel).resolve()
                for candidate in (target, target.with_suffix('.jsx'), target.with_suffix('.js')):
                    if candidate.suffix in ('.js', '.jsx') and candidate.is_file() and candidate.is_relative_to(codigo.PRE.resolve()):
                        pending.append(candidate.relative_to(codigo.PRE.resolve()).as_posix()); break
        if arch.rsplit('/', 1)[-1] in con_auth or arch in SHELL: u |= U.get('servicios/auth.js', set())
        for s in SHELL: u |= {x for x in U.get(s, ()) if x.startswith(('sitio.', 'auth.'))}
        return u

    for actor in DIAGRAMAS:
        paginas, enlaces, hs = hojas(actor)
        claves_hojas = {c for _, cs, _ in hs for c in cs}
        if set(paginas) - claves_hojas: errores.append(f'{actor}: elementos fuera de toda hoja: {sorted(set(paginas) - claves_hojas)}')
        for a, b, st, _ in enlaces:
            if (paginas[a][0], paginas[b][0]) not in ESTEREOTIPO_VALIDO[st]:
                errores.append(f'{actor}: «{st}» no va de {paginas[a][0]} a {paginas[b][0]} ({paginas[a][1]} → {paginas[b][1]})')
        for k, (tipo, nombre, at, op) in paginas.items():
            k = k.split('#')[0]   # server page o tabla repetida en otra sección: se verifica igual que la original
            if tipo in ('cliente', 'form'):
                fuentes = (FUENTE.get(k) or archivo.get(k) or '').split()
                if k in archivo and archivo[k] not in fuentes: fuentes.insert(0, archivo[k])
                if not fuentes or not all((codigo.PRE / f).exists() for f in fuentes):
                    errores.append(f'{actor}: "{nombre}" ({k}) no tiene archivo en presentacion/src'); continue
                archivos_vistos.update(f for f in fuentes if f.startswith('paginas/'))
                texto = '\n'.join((codigo.PRE / f).read_text(encoding='utf-8') for f in fuentes)
                for o in [x.strip().removesuffix('()') for x in op.split(',') if x.strip()]:
                    if not _definida(o, texto): errores.append(f'{actor}: "{nombre}".{o}() no está definida en {" / ".join(fuentes)}')
                for x in [x.split('=')[0].strip() for x in at.split(',') if x.strip()]:
                    if not re.search(rf'\b{x}\b', texto): errores.append(f'{actor}: "{nombre}" atributo {x} no aparece en {" / ".join(fuentes)}')
            if tipo == 'cliente' and not (at and op): errores.append(f'{actor}: "{nombre}" sin atributos u operaciones')
            if tipo == 'ps' and k in INCLUIDAS:
                clase, metodos = INCLUIDAS[k][:2]
                faltan = [m for m in metodos.split() if m not in C[clase]['metodos']]
                if faltan: errores.append(f'{actor}: "{nombre}": {clase} no tiene {faltan}')
                continue
            if tipo != 'ps': continue
            if k not in API: errores.append(f'{actor}: "{nombre}" no está ligado a ninguna función de api/ (navegacion.API)'); continue
            funcs = API[k].split()
            nombres_op = {o.strip().removesuffix('()') for o in op.split(',')}
            permitidos = set()
            for fn in funcs:
                usadas.add(fn)
                if fn not in F: errores.append(f'{actor}: "{nombre}" usa api/{fn}, que no existe'); continue
                r = rutas.get((F[fn]['verbo'], F[fn]['ruta']))
                if not r: errores.append(f'{actor}: "{nombre}": {F[fn]["verbo"]} {F[fn]["ruta"]} no está en routes/api.php'); continue
                m = C.get(r['controlador'], {}).get('metodos', {}).get(r['metodo'])
                if not m: errores.append(f'{actor}: "{nombre}": {r["controlador"]}@{r["metodo"]} no existe'); continue
                permitidos |= set(re.findall(r'\{(\w+)\}', r['ruta']))
                for q in [q for q in re.findall(r'(\w+Request) \$', m['params']) if q in C]:
                    permitidos |= set(C[q]['campos'])
                    for cl, mt in re.findall(r'(\w+)::(\w+)\(\)', C[q]['metodos'].get('rules', {}).get('cuerpo', '')):
                        if mt in C.get(cl, {}).get('metodos', {}):   # reglas sumadas: + NProspecto::reglasPersona()
                            permitidos |= set(re.findall(r"^\s*'(\w+)' =>", C[cl]['metodos'][mt]['cuerpo'], re.M))
                permitidos |= set(re.findall(r"\$\w+->(?:query|input|string|integer|validated)\('(\w+)'", m['cuerpo']))
                for lista in re.findall(r'->only\(\[([^\]]*)\]', m['cuerpo']): permitidos |= set(re.findall(r"'(\w+)'", lista))
                if 'self::FILTROS' in m['cuerpo']:
                    permitidos |= set(re.findall(r"'(\w+)'", re.search(r'FILTROS = \[([^\]]*)\]', codigo._leer(C[r['controlador']]['archivo'])).group(1)))
                permitidos |= {p.split()[-1].lstrip('$') for p in m['params'].split(',') if p.strip()}
                permitidos |= {'token'} | ({'usuario'} if 'ConsultaRequest' in m['params'] else set())   # Bearer / $r->usuario()
            metodos = {rutas[(F[f]['verbo'], F[f]['ruta'])]['metodo'] for f in funcs if f in F and (F[f]['verbo'], F[f]['ruta']) in rutas}
            if metodos and nombres_op != metodos:
                errores.append(f'{actor}: "{nombre}" dice {sorted(nombres_op)} pero el método de negocio es {sorted(metodos)}')
            extra = [a.strip() for a in at.split(',') if a.strip() and a.strip() not in permitidos]
            if extra: errores.append(f'{actor}: "{nombre}" tiene parámetros que el endpoint no recibe: {extra}')
            for a, b, st, texto in enlaces:   # la página (o la del formulario) que llama al server page lo llama de verdad
                if b != k or st not in ('submit', 'link'): continue
                pagina = a if paginas[a][0] == 'cliente' else next(
                    (x for x, y, s, _ in enlaces if y == a and paginas[x][0] == 'cliente' and s in ('contiene', 'link')), None)
                fuentes = (FUENTE.get(pagina) or archivo.get(pagina) or '').split() if pagina else []
                if fuentes and not any(set(funcs) & usos(f) for f in fuentes):
                    errores.append(f'{actor}: {" / ".join(fuentes)} no llama a api/{"/".join(funcs)} ("{paginas[a][1]}" → "{nombre}")')
                if texto and not any(texto.startswith(url(f).split(' ')[0]) for f in funcs) and '|' not in texto:
                    errores.append(f'{actor}: el enlace a "{nombre}" dice "{texto}" y no es la ruta real')
    # cada método de D que alcanza un endpoint debe estar descrito en DATOS
    for k, fns in API.items():
        for fn in fns.split():
            for x in codigo.metodos_datos(*_ruta(fn), cortes=CORTES):
                if x[0] != 'incluye' and f'{x[0]}.{x[1]}' not in DATOS: errores.append(f'navegacion.DATOS no describe {x[0]}.{x[1]} ({k})')
    for k, (clase, metodos, *_) in INCLUIDAS.items():
        for m in metodos.split():
            for x in codigo.metodos_datos(clase, m, cortes=CORTES, propio=True):
                if x[0] != 'incluye' and f'{x[0]}.{x[1]}' not in DATOS: errores.append(f'navegacion.DATOS no describe {x[0]}.{x[1]} ({k})')
    llamadas = set().union(*U.values())
    errores += [f'api/{fn} la usa la interfaz pero no aparece en ningún diagrama de navegación' for fn in sorted(llamadas - usadas)]
    errores += [f'{p} no aparece en ningún diagrama de navegación' for p in
                sorted(f'paginas/{f.name}' for f in (codigo.PRE / 'paginas').glob('*.jsx')) if p not in archivos_vistos]
    return sorted(set(errores), key=errores.index)


if __name__ == '__main__':
    for e in verificar(): print(e)
    for actor in DIAGRAMAS:
        paginas, enlaces, hs = hojas(actor)
        print(f'{actor}: {len(paginas)} elementos, {len(enlaces)} relaciones, {len(hs)} hojas')
