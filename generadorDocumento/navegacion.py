"""Diagramas de navegación (7.5), uno por actor, armados desde la MATRIZ DE ACCESO REAL (contenido.RECURSOS / PERMISOS,
que salen de la migración 000003 de crm-web). Cada recurso del menú es un bloque; el diagrama de un rol tiene solo los
recursos que su permiso le da, y dentro de cada bloque solo las acciones que la interfaz le habilita con ese nivel
(misma condición `puede(recurso, nivel)` que usan las páginas React). Así el diagrama coincide con el menú del rol.

Notación (REGLAS_DOCUMENTO_P2.md §5):
  'cliente' = client page (pantalla React)            'form' = «Formulario» (campos que envía)
  'ps'      = server page "ps …" (endpoint de la API)  'bd'   = «database» BD: tabla (columnas que toca)
Enlace: (origen, destino, estereotipo, texto); estereotipo link | submit | build | access | contiene.
Fuente: crm-web/presentacion/src/paginas/*.jsx, componentes/Shell.jsx, servicios/access.js, negocio/routes/api.php,
app/Http/Controllers/Api/*, app/Services/Conversion.php. Las columnas de cada 'bd' se verifican contra la BD real.
Regenerar: python ea/ea_p2.py --solo nav
"""
from contenido import PERMISOS, RECURSOS

NIVEL = {'lectura': 1, 'modificacion': 2, 'eliminacion': 3}


class Diagrama:
    def __init__(self, permisos):
        self.permisos, self.paginas, self.enlaces = permisos, {}, []

    def puede(self, recurso, minimo='lectura'):
        return NIVEL.get(self.permisos.get(recurso), 0) >= NIVEL[minimo]

    def p(self, clave, tipo, nombre, atributos='', operaciones=''):
        self.paginas.setdefault(clave, (tipo, nombre, atributos, operaciones))   # tablas y pantallas compartidas: una vez

    def e(self, a, b, estereotipo, texto=''):
        if (a, b, estereotipo, texto) not in self.enlaces: self.enlaces.append((a, b, estereotipo, texto))


# ------------------------------------------------------------------ tablas (capa 3)
def bd(d, *claves):
    T = {'usuarios': 'correo, password, rol, estado, fecha_inicio, fecha_fin, nombre, apellido, telefono, foto',
         'api_tokens': 'token_hash, usuario_correo, expira_en, ultimo_uso_en',
         'bitacora': 'evento, usuario_correo, correo_intentado, recurso_codigo, ip, navegador, fecha',
         'recursos': 'codigo, nombre, ruta, orden, visitas', 'permisos': 'rol, recurso_codigo, acceso',
         'roles': 'nombre, descripcion',
         'intereses': 'nro_tarjeta, documento, modulo_nombre, estado, vendedor_correo, fecha_asignacion, motivo_perdida, observacion',
         'prospectos': 'documento, nombre, apellido, telefono, correo, origen, profesion, ubicacion, estado',
         'motivos_perdida': 'nombre, categoria',
         'recordatorios': 'nro_recordatorio, nro_tarjeta, fecha_programada, descripcion, estado, fecha_realizada',
         'interacciones': 'nro_interaccion, nro_tarjeta, tipo, descripcion, resultado, fecha',
         'programas': 'codigo, nombre', 'catalogo_cache': 'codigo, programa_codigo, nombre, descripcion, precio, estado',
         'metodos_pago': 'nro_metodo, documento, tipo, titular, marca, ultimos_digitos, vencimiento, estado',
         'ordenes_pago': 'nro_orden, nro_tarjeta, subtotal, descuento_total, total, vendedor_correo',
         'cuotas': 'nro_orden, nro_cuota, monto, fecha_vencimiento, estado, fecha_pago',
         'orden_pago_descuentos': 'nro_orden, descuento_codigo, porcentaje, monto', 'pagos': 'nro_orden, codigo_qr, estado',
         'descuentos': 'codigo, nombre, porcentaje, estado',
         'comprobantes_pago': 'nro_comprobante, nro_orden, nro_cuota, archivo, remitente, hora_pago, estado_revision, observacion',
         'inscripciones_comerciales': 'nro_solicitud, fecha_confirmacion',
         'comisiones': 'nro_solicitud, vendedor_correo, porcentaje, monto, estado, fecha_pago',
         'exportaciones': 'nro_exportacion, nro_solicitud, estado, respuesta, fecha_exportacion',
         'configuraciones': 'clave, valor', 'programas_responsables': 'programa_codigo, coordinador_correo',
         'notificaciones': 'nro_notificacion, destinatario, tipo, mensaje, estado, usuario_correo'}
    for c in claves: d.p('bd_' + c, 'bd', 'BD: ' + c, T[c])


def acceso(d, ps, operacion, *tablas):
    bd(d, *tablas)
    for t in tablas: d.e(ps, 'bd_' + t, 'access', operacion)


# ------------------------------------------------------------------ CU1: sesión, menú dinámico y perfil (todo rol privado)
def sesion(d, actor):
    d.p('actor', 'actor', actor)
    d.p('login', 'cliente', 'Login', 'redirect', 'mostrarClave()')
    d.p('f_login', 'form', 'Iniciar Sesion', 'correo, password, recordar', 'ingresar()')
    d.p('ps_login', 'ps', 'ps Login', 'correo, password', 'login()')
    d.p('error', 'cliente', 'PC Message', 'mensaje = "Correo o contraseña incorrectos."', 'cerrar()')
    d.p('menu', 'cliente', f'Menu {actor}', 'menu, permisos, visitas', 'navegar(), buscar(), cambiarTema(), abrirPerfil()')
    d.p('ps_visita', 'ps', 'ps Registrar Visita', 'ruta', 'visita()')
    d.p('ps_buscar', 'ps', 'ps Busqueda Global', 'q', 'buscar()')
    d.p('f_perfil', 'form', 'Mi Perfil', 'nombre, apellido, telefono, foto', 'guardar()')
    d.p('ps_perfil', 'ps', 'ps Actualizar Perfil', 'nombre, apellido, telefono, foto', 'actualizarPerfil()')
    d.p('f_clave', 'form', 'Cambiar Contrasena', 'password_actual, password, password_confirmation', 'guardar()')
    d.p('ps_clave', 'ps', 'ps Cambiar Password', 'password_actual, password', 'cambiarPassword()')
    d.p('ps_logout', 'ps', 'ps Cerrar Sesion', 'token', 'logout()')
    d.e('actor', 'login', 'link', 'usa el sistema')
    d.e('login', 'f_login', 'contiene')
    d.e('f_login', 'ps_login', 'submit', 'login()')
    acceso(d, 'ps_login', 'SELECT correo', 'usuarios')
    acceso(d, 'ps_login', 'INSERT token', 'api_tokens')
    acceso(d, 'ps_login', 'INSERT login', 'bitacora')
    acceso(d, 'ps_login', 'SELECT menu', 'recursos', 'permisos')
    d.e('ps_login', 'error', 'build', 'auth fallido')
    d.e('error', 'login', 'link', 'volver')
    d.e('ps_login', 'menu', 'build', 'auth ok')
    # menú dinámico: un enlace por recurso permitido, en el orden de la tabla recursos (el primero es la página de inicio)
    for codigo in sorted(d.permisos, key=list(RECURSOS).index):   # mismo orden que la tabla recursos
        d.e('menu', codigo, 'link', RECURSOS[codigo]['ruta'])
    d.e('menu', 'ps_visita', 'submit', 'visita()')
    acceso(d, 'ps_visita', 'INSERT visita', 'bitacora')
    acceso(d, 'ps_visita', 'UPDATE visitas', 'recursos')
    d.e('ps_visita', 'menu', 'build', 'contador')
    d.e('menu', 'ps_buscar', 'submit', 'buscar()')
    # SitioController@buscar: módulos del catálogo y páginas del rol; prospectos si ve embudo/prospectos; usuarios si los gestiona
    acceso(d, 'ps_buscar', 'SELECT', 'catalogo_cache', 'programas', 'recursos', 'permisos')
    if d.puede('embudo') or d.puede('prospectos'): acceso(d, 'ps_buscar', 'SELECT', 'intereses', 'prospectos')
    if d.puede('usuarios'): acceso(d, 'ps_buscar', 'SELECT', 'usuarios')
    d.e('ps_buscar', 'menu', 'build', 'JSON resultados')
    d.e('menu', 'f_perfil', 'link', 'mi perfil')
    d.e('f_perfil', 'ps_perfil', 'submit', 'guardar()')
    acceso(d, 'ps_perfil', 'UPDATE perfil', 'usuarios')
    d.e('menu', 'f_clave', 'link', 'cambiar contraseña')
    d.e('f_clave', 'ps_clave', 'submit', 'guardar()')
    acceso(d, 'ps_clave', 'UPDATE password', 'usuarios')
    acceso(d, 'ps_clave', 'DELETE otras sesiones', 'api_tokens')
    d.e('menu', 'ps_logout', 'link', 'cerrar sesión')
    acceso(d, 'ps_logout', 'DELETE token', 'api_tokens')
    acceso(d, 'ps_logout', 'INSERT logout', 'bitacora')
    d.e('ps_logout', 'login', 'build', 'redirect login')


def ps_vendedores(d, desde):
    d.p('ps_vend', 'ps', 'ps Listar Vendedores', 'estado', 'vendedores()')
    d.e(desde, 'ps_vend', 'submit', 'cargar()')
    acceso(d, 'ps_vend', 'SELECT vendedores', 'usuarios')


def ficha(d):
    """Ficha de una tarjeta (/agenda?interes=n): a ella enlazan Mi día, Embudo, Prospectos, Asignación y Validación."""
    d.p('ficha', 'cliente', 'Ficha del Prospecto', 'interes, historial, recordatorios, ordenes', 'whatsapp(), convertir(), editar()')
    d.p('ps_show', 'ps', 'ps Ver Interes', 'nro_tarjeta', 'show()')
    d.e('ficha', 'ps_show', 'submit', 'cargar()')
    acceso(d, 'ps_show', 'SELECT', 'intereses')
    d.e('ps_show', 'ficha', 'build', 'JSON ficha')


# ------------------------------------------------------------------ bloques por recurso del menú
def dashboard(d):   # CU8
    d.p('dashboard', 'cliente', 'Dashboard', 'indicadores, graficos, accesos', 'actualizar()')
    d.p('ps_dash', 'ps', 'ps Dashboard', 'rol, correo', 'dashboard()')
    d.e('dashboard', 'ps_dash', 'submit', 'cargar()')
    acceso(d, 'ps_dash', 'SELECT', 'intereses', 'cuotas', 'recordatorios', 'bitacora', 'recursos')
    d.e('ps_dash', 'dashboard', 'build', 'JSON graficos')


def inicio_vendedor(d):   # CU7 / CU8
    d.p('inicio-vendedor', 'cliente', 'Mi Dia', 'estadisticas, calendario, actividades', 'cambiarMes(), elegirDia(), abrirFicha()')
    d.p('ps_estvend', 'ps', 'ps Estadisticas Vendedor', 'vendedor_correo', 'estadisticasVendedor()')
    d.p('ps_record', 'ps', 'ps Listar Recordatorios', 'desde, hasta', 'recordatorios()')
    d.e('inicio-vendedor', 'ps_estvend', 'submit', 'cargar()')
    acceso(d, 'ps_estvend', 'SELECT cartera', 'intereses', 'interacciones', 'recordatorios', 'comisiones')
    d.e('ps_estvend', 'inicio-vendedor', 'build', 'JSON estadisticas')
    d.e('inicio-vendedor', 'ps_record', 'submit', 'cargar()')
    acceso(d, 'ps_record', 'SELECT agenda', 'recordatorios')
    d.e('ps_record', 'inicio-vendedor', 'build', 'JSON agenda')
    if d.puede('agenda', 'modificacion'): completar(d, 'inicio-vendedor')
    ficha(d); d.e('inicio-vendedor', 'ficha', 'link', 'interes=nro_tarjeta')


def completar(d, desde):
    d.p('f_realizada', 'form', 'Marcar Realizada', 'resultado', 'guardar()')
    d.p('ps_completar', 'ps', 'ps Completar Recordatorio', 'nro_recordatorio, resultado', 'completarRecordatorio()')
    d.e(desde, 'f_realizada', 'link', 'realizada')
    d.e('f_realizada', 'ps_completar', 'submit', 'guardar()')
    acceso(d, 'ps_completar', 'UPDATE estado', 'recordatorios')
    acceso(d, 'ps_completar', 'INSERT resultado', 'interacciones')


def listar_intereses(d, desde):
    d.p('ps_intereses', 'ps', 'ps Listar Intereses', 'buscar, estado, vendedor', 'index()')
    d.e(desde, 'ps_intereses', 'submit', 'filtrar()')
    acceso(d, 'ps_intereses', 'SELECT', 'intereses', 'prospectos')
    d.e('ps_intereses', desde, 'build', 'JSON tarjetas')


def embudo(d):   # CU4 / CU5
    d.p('embudo', 'cliente', 'Embudo de Ventas', 'intereses, estados, buscar', 'arrastrar(), moverA(), abrirFicha()')
    listar_intereses(d, 'embudo')
    if d.permisos.get('embudo') and 'inicio-vendedor' not in d.permisos: ps_vendedores(d, 'embudo')   # filtro por vendedor
    if d.puede('embudo', 'modificacion'):
        d.p('ps_mover', 'ps', 'ps Mover Tarjeta', 'nro_tarjeta, estado, motivo_perdida, observacion', 'mover()')
        d.p('f_perdida', 'form', 'Marcar como Perdido', 'motivo_perdida, observacion', 'guardar()')
        d.p('ps_motivos', 'ps', 'ps Listar Motivos', 'nombre', 'index()')
        d.e('embudo', 'ps_mover', 'submit', 'moverA()')
        d.e('embudo', 'f_perdida', 'link', 'perdido')
        d.e('f_perdida', 'ps_motivos', 'submit', 'cargar()')
        acceso(d, 'ps_motivos', 'SELECT', 'motivos_perdida')
        d.e('f_perdida', 'ps_mover', 'submit', 'guardar()')
        acceso(d, 'ps_mover', 'UPDATE estado', 'intereses', 'prospectos')
        d.e('ps_mover', 'embudo', 'build', 'redirect back')
    ficha(d); d.e('embudo', 'ficha', 'link', 'interes=nro_tarjeta')


def prospectos(d):   # CU3
    d.p('prospectos', 'cliente', 'Prospectos', 'prospectos, buscar, origen', 'filtrar(), abrirFicha()')
    d.p('ps_prosp', 'ps', 'ps Listar Prospectos', 'buscar, origen', 'index()')
    d.e('prospectos', 'ps_prosp', 'submit', 'filtrar()')
    acceso(d, 'ps_prosp', 'SELECT', 'prospectos', 'intereses')
    d.e('ps_prosp', 'prospectos', 'build', 'JSON prospectos')
    if d.puede('interesados', 'modificacion'):   # Prospectos.jsx: puedeAlta = puede('interesados', 'modificacion')
        catalogo_api(d)
        d.p('f_prospecto', 'form', 'Registrar Prospecto', 'documento, nombre, apellido, telefono, correo, origen, profesion, ubicacion, interes', 'guardar()')
        d.p('ps_alta', 'ps', 'ps Registrar Prospecto', 'documento, nombre, apellido, telefono, correo, origen', 'store()')
        d.p('f_csv', 'form', 'Importar CSV', 'archivo', 'importar()')
        d.p('ps_csv', 'ps', 'ps Importar CSV', 'csv', 'importarCSV()')
        d.e('prospectos', 'f_prospecto', 'link', 'registrar')
        d.e('f_prospecto', 'ps_catalogo', 'submit', 'cargar()')
        d.e('f_prospecto', 'ps_alta', 'submit', 'guardar()')
        acceso(d, 'ps_alta', 'INSERT', 'prospectos', 'intereses')
        d.e('ps_alta', 'prospectos', 'build', 'redirect back')
        d.e('prospectos', 'f_csv', 'link', 'importar CSV')
        d.e('f_csv', 'ps_csv', 'submit', 'importar()')
        acceso(d, 'ps_csv', 'INSERT', 'prospectos', 'intereses')
        d.e('ps_csv', 'prospectos', 'build', 'redirect back')
    ficha(d); d.e('prospectos', 'ficha', 'link', 'interes=nro_tarjeta')


def interesados(d):   # CU3: asignación manual y Round-Robin
    d.p('interesados', 'cliente', 'Asignacion de Prospectos', 'tarjetas, buscar, vendedor, sin_asignar', 'filtrar(), asignar(), repartir()')
    listar_intereses(d, 'interesados')
    ps_vendedores(d, 'interesados')
    if d.puede('interesados', 'modificacion'):
        d.p('ps_asignar', 'ps', 'ps Asignar Interes', 'nro_tarjeta, vendedor_correo', 'asignar()')
        d.p('ps_repartir', 'ps', 'ps Distribuir Round-Robin', 'programa_codigo', 'distribuir()')
        d.e('interesados', 'ps_asignar', 'submit', 'asignar()')
        acceso(d, 'ps_asignar', 'UPDATE vendedor_correo', 'intereses', 'recordatorios')
        d.e('interesados', 'ps_repartir', 'submit', 'repartir()')
        acceso(d, 'ps_repartir', 'UPDATE vendedor_correo', 'intereses')
        d.e('ps_asignar', 'interesados', 'build', 'redirect back')
        d.e('ps_repartir', 'interesados', 'build', 'redirect back')
    ficha(d); d.e('interesados', 'ficha', 'link', 'interes=nro_tarjeta')


def agenda(d):   # CU7 y pagos de CU6
    d.p('agenda', 'cliente', 'Seguimiento y Agenda', 'tarjetas, buscar, estado', 'elegirTarjeta()')
    listar_intereses(d, 'agenda')
    ficha(d); d.e('agenda', 'ficha', 'link', 'interes=nro_tarjeta')
    if not d.puede('agenda', 'modificacion'): return   # Agenda.jsx: editable = puede('agenda', 'modificacion')
    completar(d, 'ficha')
    catalogo_api(d)
    formularios = [
        ('f_contacto', 'Registrar Contacto', 'tipo, descripcion, resultado', 'contiene', '',
         'ps_interac', 'ps Registrar Interaccion', 'nro_tarjeta, tipo, descripcion, resultado', 'registrarInteraccion()', 'INSERT', ('interacciones',)),
        ('f_record', 'Agendar Recordatorio', 'fecha_programada, descripcion', 'contiene', '',
         'ps_crearrec', 'ps Crear Recordatorio', 'nro_tarjeta, fecha_programada, descripcion', 'crearRecordatorio()', 'INSERT', ('recordatorios',)),
        ('f_editar', 'Editar Prospecto', 'nombre, apellido, correo, telefono, profesion, ubicacion, origen', 'link', 'editar',
         'ps_update', 'ps Actualizar Prospecto', 'documento, nombre, apellido, correo, telefono', 'update()', 'UPDATE', ('prospectos',)),
        ('f_metodo', 'Registrar Metodo de Pago', 'tipo, titular, numero, vencimiento', 'link', 'metodo de pago',
         'ps_metodo', 'ps Registrar Metodo', 'documento, tipo, titular, numero, vencimiento', 'registrarMetodo()', 'INSERT', ('metodos_pago',)),
        ('f_orden', 'Generar Orden de Pago', 'modulos, descuentos, cuotas, primer_vencimiento', 'link', 'generar orden',
         'ps_orden', 'ps Crear Orden', 'nro_tarjeta, modulos, descuentos, cuotas', 'crearOrden()', 'INSERT',
         ('ordenes_pago', 'cuotas', 'orden_pago_descuentos', 'pagos')),
        ('f_comprob', 'Subir Comprobante', 'archivo, nro_metodo, remitente, hora_pago, observacion', 'link', 'comprobante',
         'ps_comprob', 'ps Registrar Comprobante', 'nro_orden, nro_cuota, archivo', 'registrarComprobante()', 'INSERT', ('comprobantes_pago',)),
        ('f_tarjeta', 'Cobrar con Tarjeta', 'nro_metodo', 'link', 'cobrar con tarjeta',
         'ps_tarjeta', 'ps Pagar con Tarjeta', 'nro_orden, nro_cuota, nro_metodo', 'pagarConTarjeta()', 'UPDATE', ('cuotas',)),
    ]
    for f, fn, fa, rel, txt, ps, psn, psa, op, sql, tablas in formularios:
        d.p(f, 'form', fn, fa, 'guardar()'); d.p(ps, 'ps', psn, psa, op)
        d.e('ficha', f, rel, txt); d.e(f, ps, 'submit', 'guardar()')
        acceso(d, ps, sql, *tablas)
        d.e(ps, 'ficha', 'build', 'redirect back')
    d.p('ps_cancelar', 'ps', 'ps Cancelar Recordatorio', 'nro_recordatorio', 'cancelarRecordatorio()')
    d.e('ficha', 'ps_cancelar', 'submit', 'cancelar()')
    acceso(d, 'ps_cancelar', 'UPDATE estado', 'recordatorios')
    d.p('ps_desc', 'ps', 'ps Listar Descuentos', 'estado', 'descuentos()')
    d.e('f_orden', 'ps_catalogo', 'submit', 'cargar()')
    d.e('f_orden', 'ps_desc', 'submit', 'cargar()')
    acceso(d, 'ps_desc', 'SELECT', 'descuentos')
    if d.puede('embudo', 'modificacion'): d.e('ficha', 'ps_mover', 'submit', 'convertir()')


def catalogo_api(d):
    d.p('ps_catalogo', 'ps', 'ps Catalogo', 'programas', 'programas()')
    acceso(d, 'ps_catalogo', 'SELECT', 'programas', 'catalogo_cache')


def motivos(d):   # CU5
    d.p('motivos', 'cliente', 'Motivos de Perdida', 'motivos, usos', 'nuevo(), editar(), eliminar()')
    d.p('ps_motivos', 'ps', 'ps Listar Motivos', 'nombre', 'index()')
    d.e('motivos', 'ps_motivos', 'submit', 'cargar()')
    acceso(d, 'ps_motivos', 'SELECT', 'motivos_perdida', 'intereses')
    d.e('ps_motivos', 'motivos', 'build', 'JSON motivos')
    if d.puede('motivos', 'modificacion'):
        d.p('f_motivo', 'form', 'Nuevo / Editar Motivo', 'nombre, categoria', 'guardar()')
        d.p('ps_motivo_g', 'ps', 'ps Guardar Motivo', 'nombre, categoria', 'store(), update()')
        d.e('motivos', 'f_motivo', 'link', 'nuevo / editar')
        d.e('f_motivo', 'ps_motivo_g', 'submit', 'guardar()')
        acceso(d, 'ps_motivo_g', 'INSERT / UPDATE', 'motivos_perdida')
        d.e('ps_motivo_g', 'motivos', 'build', 'redirect back')
    if d.puede('motivos', 'eliminacion'):   # Motivos.jsx: borrable = puede('motivos', 'eliminacion')
        d.p('ps_motivo_d', 'ps', 'ps Eliminar Motivo', 'nombre', 'destroy()')
        d.e('motivos', 'ps_motivo_d', 'submit', 'eliminar()')
        acceso(d, 'ps_motivo_d', 'DELETE', 'motivos_perdida')


def validacion_pagos(d):   # CU6
    d.p('validacion-pagos', 'cliente', 'Validacion de Pagos', 'cuotas, estado', 'filtrar(), revisar(), abrirFicha()')
    d.p('ps_cuotas', 'ps', 'ps Listar Cuotas', 'estado', 'cuotas()')
    d.p('ps_comp', 'ps', 'ps Ver Comprobante', 'nro_comprobante', 'comprobante()')
    d.e('validacion-pagos', 'ps_cuotas', 'submit', 'filtrar()')
    acceso(d, 'ps_cuotas', 'SELECT', 'cuotas', 'comprobantes_pago')
    d.e('ps_cuotas', 'validacion-pagos', 'build', 'JSON cuotas')
    d.p('f_revisar', 'form', 'Revisar Comprobante', 'observacion', 'aprobar(), rechazar()')
    d.e('validacion-pagos', 'f_revisar', 'link', 'revisar')
    d.e('f_revisar', 'ps_comp', 'submit', 'cargar()')
    acceso(d, 'ps_comp', 'SELECT archivo', 'comprobantes_pago')
    if d.puede('validacion-pagos', 'modificacion'):
        d.p('ps_aprobar', 'ps', 'ps Aprobar Cuota', 'nro_orden, nro_cuota, observacion', 'aprobar()')
        d.p('ps_rechazar', 'ps', 'ps Rechazar Cuota', 'nro_orden, nro_cuota, observacion', 'rechazar()')
        d.e('f_revisar', 'ps_aprobar', 'submit', 'aprobar()')
        d.e('f_revisar', 'ps_rechazar', 'submit', 'rechazar()')
        acceso(d, 'ps_aprobar', 'UPDATE estado', 'cuotas', 'comprobantes_pago', 'pagos', 'intereses')
        acceso(d, 'ps_aprobar', 'INSERT conversion', 'inscripciones_comerciales', 'comisiones')
        acceso(d, 'ps_rechazar', 'UPDATE estado', 'cuotas', 'comprobantes_pago')
        d.e('ps_aprobar', 'validacion-pagos', 'build', 'redirect back')
        d.e('ps_rechazar', 'validacion-pagos', 'build', 'redirect back')
    ficha(d); d.e('validacion-pagos', 'ficha', 'link', 'interes=nro_tarjeta')


def alumnos(d):   # CU6: matrículas y exportación al SIS
    d.p('alumnos', 'cliente', 'Matriculas y SIS', 'inscripciones, pendientes', 'exportar(), registrarResultado(), descargarCsv()')
    d.p('ps_insc', 'ps', 'ps Listar Inscripciones', 'programa', 'inscripciones()')
    d.p('ps_pend', 'ps', 'ps Exportaciones Pendientes', 'estado', 'pendientes()')
    d.e('alumnos', 'ps_insc', 'submit', 'cargar()')
    acceso(d, 'ps_insc', 'SELECT', 'inscripciones_comerciales')
    d.e('ps_insc', 'alumnos', 'build', 'JSON inscripciones')
    d.e('alumnos', 'ps_pend', 'submit', 'cargar()')
    acceso(d, 'ps_pend', 'SELECT', 'exportaciones')
    if d.puede('alumnos', 'modificacion'):
        d.p('ps_exportar', 'ps', 'ps Exportar al SIS', 'nro_solicitud', 'exportar()')
        d.p('ps_resultado', 'ps', 'ps Registrar Resultado', 'nro_exportacion, estado', 'registrarResultado()')
        d.e('alumnos', 'ps_exportar', 'submit', 'exportar()')
        acceso(d, 'ps_exportar', 'INSERT', 'exportaciones')
        d.e('alumnos', 'ps_resultado', 'submit', 'registrarResultado()')
        acceso(d, 'ps_resultado', 'UPDATE estado', 'exportaciones')
        d.e('ps_exportar', 'alumnos', 'build', 'redirect back')


def gestion_anuncios(d):   # CU2: la misma malla del catálogo dentro del panel
    d.p('gestion-anuncios', 'cliente', 'Oferta Academica', 'programas, area, modulos', 'filtrarArea(), elegirPrograma()')
    catalogo_api(d)
    d.e('gestion-anuncios', 'ps_catalogo', 'submit', 'cargar()')
    d.e('ps_catalogo', 'gestion-anuncios', 'build', 'JSON programas')
    if d.puede('gestion-anuncios', 'modificacion'):   # Catalogo.jsx: puedeSincronizar
        d.p('ps_sinc', 'ps', 'ps Sincronizar Catalogo', 'programas', 'sincronizar()')
        d.e('gestion-anuncios', 'ps_sinc', 'submit', 'sincronizar()')
        acceso(d, 'ps_sinc', 'INSERT / UPDATE', 'programas', 'catalogo_cache')
        d.e('ps_sinc', 'gestion-anuncios', 'build', 'redirect back')


def seguimiento(d):   # CU8: ventas y comisiones
    d.p('seguimiento', 'cliente', 'Ventas y Comisiones', 'comisiones, total', 'listar()')
    d.p('ps_comis', 'ps', 'ps Listar Comisiones', 'vendedor_correo', 'comisiones()')
    d.e('seguimiento', 'ps_comis', 'submit', 'cargar()')
    acceso(d, 'ps_comis', 'SELECT', 'comisiones')
    d.e('ps_comis', 'seguimiento', 'build', 'JSON comisiones')
    if d.puede('seguimiento', 'modificacion'):   # Comisiones.jsx: gestiona
        d.p('ps_resumen', 'ps', 'ps Resumen Comisiones', 'vendedor', 'resumenComisiones()')
        d.p('ps_pagar', 'ps', 'ps Pagar Comisiones', 'vendedor_correo', 'pagarComisiones()')
        d.p('f_porcentaje', 'form', 'Porcentaje de Comision', 'porcentaje', 'guardar()')
        d.p('ps_porcentaje', 'ps', 'ps Configurar Comision', 'porcentaje', 'actualizarConfiguracionComision()')
        d.e('seguimiento', 'ps_resumen', 'submit', 'cargar()')
        acceso(d, 'ps_resumen', 'SELECT', 'comisiones', 'usuarios')
        d.e('seguimiento', 'ps_pagar', 'submit', 'pagar()')
        acceso(d, 'ps_pagar', 'UPDATE estado', 'comisiones')
        d.e('seguimiento', 'f_porcentaje', 'contiene')
        d.e('f_porcentaje', 'ps_porcentaje', 'submit', 'guardar()')
        acceso(d, 'ps_porcentaje', 'UPDATE valor', 'configuraciones')
        d.e('ps_pagar', 'seguimiento', 'build', 'redirect back')


def reportes(d):   # CU8
    d.p('reportes', 'cliente', 'Reportes y Estadisticas', 'tipo, desde, hasta, estado, buscar', 'filtrar(), cambiarVista(), descargarCsv()')
    d.p('ps_est', 'ps', 'ps Estadisticas', 'desde, hasta, vendedor', 'estadisticas()')
    d.p('ps_listado', 'ps', 'ps Listado', 'tipo, desde, hasta, estado, buscar', 'listado()')
    d.e('reportes', 'ps_est', 'submit', 'filtrar()')
    acceso(d, 'ps_est', 'SELECT', 'intereses')
    d.e('ps_est', 'reportes', 'build', 'JSON graficos')
    d.e('reportes', 'ps_listado', 'submit', 'filtrar()')
    acceso(d, 'ps_listado', 'SELECT', 'intereses', 'usuarios')
    d.e('ps_listado', 'reportes', 'build', 'JSON listado')
    if 'inicio-vendedor' not in d.permisos: ps_vendedores(d, 'reportes')   # Reportes.jsx: el vendedor no filtra vendedores


def notificaciones(d):   # CU7
    d.p('notificaciones', 'cliente', 'Notificaciones', 'notificaciones', 'marcarLeida()')
    d.p('ps_notif', 'ps', 'ps Listar Notificaciones', 'usuario_correo', 'index()')
    d.p('ps_leida', 'ps', 'ps Marcar Leida', 'nro_notificacion', 'marcarLeida()')
    d.e('notificaciones', 'ps_notif', 'submit', 'cargar()')
    acceso(d, 'ps_notif', 'SELECT', 'notificaciones')
    d.e('ps_notif', 'notificaciones', 'build', 'JSON notificaciones')
    d.e('notificaciones', 'ps_leida', 'submit', 'marcarLeida()')
    acceso(d, 'ps_leida', 'UPDATE estado', 'notificaciones')
    if d.puede('notificaciones', 'modificacion') or d.puede('agenda', 'modificacion'):   # Notificaciones.jsx: puedeEnviar
        d.p('f_notif', 'form', 'Enviar Notificacion', 'destinatario, tipo, mensaje', 'enviar()')
        d.p('ps_enviar', 'ps', 'ps Enviar Notificacion', 'destinatario, tipo, mensaje', 'enviar()')
        d.e('notificaciones', 'f_notif', 'contiene')
        d.e('f_notif', 'ps_enviar', 'submit', 'enviar()')
        acceso(d, 'ps_enviar', 'INSERT', 'notificaciones')
        d.e('ps_enviar', 'notificaciones', 'build', 'redirect back')


def usuarios(d):   # CU1
    d.p('usuarios', 'cliente', 'Usuarios', 'usuarios, buscar, rol, estado', 'filtrar(), nuevo(), editar(), cambiarEstado()')
    d.p('ps_usuarios', 'ps', 'ps Listar Usuarios', 'buscar, rol, estado', 'index()')
    d.e('usuarios', 'ps_usuarios', 'submit', 'filtrar()')
    acceso(d, 'ps_usuarios', 'SELECT', 'usuarios', 'roles', 'programas')
    d.e('ps_usuarios', 'usuarios', 'build', 'JSON usuarios')
    if d.puede('usuarios', 'modificacion'):   # Usuarios.jsx: editable
        d.p('f_usuario', 'form', 'Registrar / Editar Usuario', 'nombre, apellido, correo, telefono, password, rol, estado, fecha_inicio, fecha_fin, programas, foto', 'guardar()')
        d.p('ps_usuario_g', 'ps', 'ps Guardar Usuario', 'correo, rol, estado, fecha_inicio, fecha_fin, foto', 'store(), update()')
        d.p('ps_estado', 'ps', 'ps Cambiar Estado', 'correo, estado', 'cambiarEstado()')
        d.e('usuarios', 'f_usuario', 'link', 'nuevo / editar')
        d.e('f_usuario', 'ps_usuario_g', 'submit', 'guardar()')
        acceso(d, 'ps_usuario_g', 'INSERT / UPDATE', 'usuarios', 'programas_responsables')
        d.e('ps_usuario_g', 'usuarios', 'build', 'redirect back')
        d.e('usuarios', 'ps_estado', 'submit', 'cambiarEstado()')
        acceso(d, 'ps_estado', 'UPDATE estado', 'usuarios')


def matriz(d):   # CU1
    d.p('matriz', 'cliente', 'Matriz de Acceso', 'roles, recursos, permisos', 'asignar()')
    d.p('ps_matriz', 'ps', 'ps Matriz', 'rol', 'matriz()')
    d.e('matriz', 'ps_matriz', 'submit', 'cargar()')
    acceso(d, 'ps_matriz', 'SELECT', 'roles', 'recursos', 'permisos')
    d.e('ps_matriz', 'matriz', 'build', 'JSON matriz')
    if d.puede('matriz', 'modificacion'):
        d.p('ps_asig_perm', 'ps', 'ps Asignar Permiso', 'rol, recurso_codigo, acceso', 'asignar()')
        d.e('matriz', 'ps_asig_perm', 'submit', 'asignar()')
        acceso(d, 'ps_asig_perm', 'INSERT / UPDATE / DELETE', 'permisos')
        d.e('ps_asig_perm', 'matriz', 'build', 'redirect back')


def bitacora(d):   # CU1
    d.p('bitacora', 'cliente', 'Bitacora de Accesos', 'evento, usuario, ip, desde, hasta', 'filtrar(), paginar()')
    d.p('ps_bitacora', 'ps', 'ps Listar Bitacora', 'evento, usuario, ip, desde, hasta', 'bitacora()')
    d.p('ps_bresumen', 'ps', 'ps Resumen de Accesos', 'desde', 'resumen()')
    d.e('bitacora', 'ps_bitacora', 'submit', 'filtrar()')
    acceso(d, 'ps_bitacora', 'SELECT', 'bitacora', 'usuarios')
    d.e('ps_bitacora', 'bitacora', 'build', 'JSON registros')
    d.e('bitacora', 'ps_bresumen', 'submit', 'cargar()')
    acceso(d, 'ps_bresumen', 'SELECT', 'bitacora', 'recursos')
    d.e('ps_bresumen', 'bitacora', 'build', 'JSON resumen')


BLOQUES = {'dashboard': dashboard, 'inicio-vendedor': inicio_vendedor, 'embudo': embudo, 'prospectos': prospectos,
           'interesados': interesados, 'agenda': agenda, 'motivos': motivos, 'validacion-pagos': validacion_pagos,
           'alumnos': alumnos, 'gestion-anuncios': gestion_anuncios, 'seguimiento': seguimiento, 'reportes': reportes,
           'notificaciones': notificaciones, 'usuarios': usuarios, 'matriz': matriz, 'bitacora': bitacora}


def rol(nombre_rol, actor):
    d = Diagrama(PERMISOS[nombre_rol])
    sesion(d, actor)
    for codigo in d.permisos: BLOQUES[codigo](d)
    return d.paginas, d.enlaces


def visitante():
    """CU2 público: catálogo (/anuncios) con búsqueda, registro de interés y enlace al login."""
    d = Diagrama({})
    d.p('actor', 'actor', 'Visitante')
    d.p('catalogo', 'cliente', 'Catalogo de Programas', 'programas, area, eleccion, visitas', 'filtrarArea(), elegirPrograma(), elegirModulo(), buscar()')
    catalogo_api(d)
    d.p('ps_visita', 'ps', 'ps Registrar Visita', 'ruta', 'visita()')
    d.p('ps_buscar', 'ps', 'ps Busqueda Global', 'q', 'buscar()')
    d.p('f_interes', 'form', 'Me Interesa', 'nombre, apellido, documento, telefono, correo, profesion, ubicacion', 'enviar()')
    d.p('ps_registro', 'ps', 'ps Registrar Interes', 'nombre, apellido, documento, telefono, correo, modulo_codigo, programa_codigo', 'registrarInteres()')
    d.p('exito', 'cliente', 'PC Message', 'mensaje = "Su interés fue registrado."', 'volver()')
    d.p('login', 'cliente', 'Login', 'redirect', 'mostrarClave()')
    d.e('actor', 'catalogo', 'link', 'usa el sistema')
    d.e('catalogo', 'ps_catalogo', 'submit', 'cargar()')
    d.e('ps_catalogo', 'catalogo', 'build', 'JSON programas')
    d.e('catalogo', 'ps_visita', 'submit', 'visita()')
    acceso(d, 'ps_visita', 'INSERT visita', 'bitacora')
    acceso(d, 'ps_visita', 'UPDATE visitas', 'recursos')
    d.e('catalogo', 'ps_buscar', 'submit', 'buscar()')
    acceso(d, 'ps_buscar', 'SELECT', 'programas', 'catalogo_cache')
    d.e('ps_buscar', 'catalogo', 'build', 'JSON resultados')
    d.e('catalogo', 'f_interes', 'link', 'me interesa')
    d.e('f_interes', 'ps_registro', 'submit', 'enviar()')
    acceso(d, 'ps_registro', 'INSERT', 'prospectos', 'intereses')
    d.e('ps_registro', 'exito', 'build', 'registro ok')
    d.e('exito', 'catalogo', 'link', 'volver')
    d.e('catalogo', 'login', 'link', 'iniciar sesión')
    return d.paginas, d.enlaces


# Un diagrama por actor del Capítulo V, en el orden de 7.5 (contenido.ACTORES)
ACTORES = {'Administrador': lambda: rol('administrador', 'Administrador'),
           'Coordinador': lambda: rol('coordinador', 'Coordinador'),
           'Vendedor': lambda: rol('vendedor', 'Vendedor'),
           'Visitante': visitante}
