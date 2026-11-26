"""Posiciones por flujo para los diagramas de navegación de la sección 7.5."""
from ea import navegacion_administrador as trazado

ENTRADA = (
    'actor login f_login ps_login bd_usuarios',
    'error404 ps_logout error menu ps_me',
    'f_clave ps_clave pie f_perfil ps_perfil',
)

FILAS = {
    'Coordinador': ENTRADA + (
        'dashboard ps_dash ps_visita ps_buscar resultados_busqueda',
        'ps_pagar bd_comisiones ps_comis seguimiento ps_resumen',
        'ps_est reporte_csv reportes ps_listado gestion-anuncios',
        'f_motivo ps_motivo_g motivos ps_motivos catalogo',
        'f_csv ps_csv prospectos ps_prosp plantilla_csv',
        'ps_nuevo_interes f_nuevo_interes ps_catalogo f_prospecto ps_alta',
        'ps_repartir ps_asignar interesados ps_vend agenda',
        'f_perdida embudo ps_mover ps_intereses bd_intereses',
        'f_editar ps_update ficha ps_show whatsapp',
        'f_realizada ps_completar ps_estmetodo f_contacto ps_interac',
        'ps_cancelar f_revisar validacion-pagos f_record ps_crearrec',
        'ps_aprobar ps_rechazar ps_comp ps_cuotas bd_cuotas',
        'ps_pend ps_insc alumnos ps_exportar ps_resultado',
        'f_anular ps_anular_orden compartir f_correo ps_setup_stripe',
        'ps_notif ps_leida notificaciones f_notif ps_enviar',
        'ps_checkout stripe pago_confirmacion ps_retorno_publico ps_confirmar_checkout',
        '- - pago_cancelado ps_cancelar_publico ps_cancelar_checkout',
    ),
    'Vendedor': ENTRADA + (
        'ps_estvend inicio-vendedor ps_visita ps_buscar resultados_busqueda',
        'ps_record bd_recordatorios f_realizada_dia ps_completar catalogo',
        'reporte_csv ps_listado reportes ps_est -',
        'seguimiento ps_comis prospectos ps_prosp ps_catalogo',
        'f_nuevo_interes ps_nuevo_interes agenda ps_intereses bd_intereses',
        'f_perdida embudo ps_mover ficha ps_show',
        'ps_update f_editar f_contacto ps_interac whatsapp',
        'ps_cancelar f_realizada f_record ps_crearrec ps_estmetodo',
        'ps_desc f_orden ps_orden bd_ordenes_pago -',
        'f_anular ps_anular_orden compartir f_correo ps_setup_stripe',
        'ps_notif ps_leida notificaciones f_notif ps_enviar',
        'ps_checkout stripe pago_confirmacion ps_retorno_publico ps_confirmar_checkout',
        '- - pago_cancelado ps_cancelar_publico ps_cancelar_checkout',
    ),
    'Visitante': (
        'error404 actor catalogo ps_catalogo bd_programas',
        'login pie ps_visita resultados_busqueda ps_buscar',
        '- registro_interes f_interes ps_registro bd_prospectos',
        'bd_cuotas ps_cuota_publica pago_cuota stripe pago_confirmacion',
        '- - pago_cancelado ps_cancelar_publico ps_retorno_publico',
    ),
}


MENSAJES_STRIPE = {
    ('stripe', 'pago_confirmacion', 'link'): 'success_url',
    ('stripe', 'pago_cancelado', 'link'): 'cancel_url',
    ('pago_cancelado', 'stripe', 'link'): 'Reintentar con URL, sin confirmar ni expirar',
    ('pago_confirmacion', 'ps_retorno_publico', 'link'): 'Con token',
    ('pago_cancelado', 'ps_cancelar_publico', 'link'): 'Con token',
}

MENSAJES_INTERNOS = {
    ('embudo', 'ps_mover', 'link'): 'Mover tarjeta',
    ('ficha', 'ps_mover', 'link'): 'Convertir',
    ('ps_mover', 'embudo', 'build'): '422: faltantes',
    ('pago_confirmacion', 'ps_confirmar_checkout', 'link'): 'Sesión sin token',
    ('pago_cancelado', 'ps_cancelar_checkout', 'link'): 'Sesión sin token',
    ('f_nuevo_interes', 'ps_catalogo', 'link'): 'Cargar opciones',
    ('menu', 'notificaciones', 'link'): 'Notificaciones',
    ('notificaciones', 'ps_notif', 'link'): 'Listar avisos',
    ('notificaciones', 'ps_leida', 'link'): 'Marcar leída',
}

MENSAJES_REVISION_Y_PROSPECTOS = {
    ('f_revisar', 'ps_comp', 'link'): 'Si hay comprobante',
    ('ps_comp', 'f_revisar', 'build'): 'Mostrar archivo',
    ('f_revisar', 'ps_aprobar', 'link'): 'Aprobar pago',
    ('f_revisar', 'ps_rechazar', 'link'): 'Rechazar + motivo',
    ('validacion-pagos', 'f_revisar', 'link'): 'Revisar / Ver',
    ('f_prospecto', 'ps_catalogo', 'link'): 'Cargar catálogo',
    ('f_csv', 'plantilla_csv', 'link'): 'Descargar plantilla',
}

MENSAJES_ADMINISTRADOR = MENSAJES_STRIPE | MENSAJES_REVISION_Y_PROSPECTOS | {
    ('error404', 'catalogo', 'link'): 'Ir al catálogo',
    ('prospectos', 'f_prospecto', 'link'): 'Registrar',
    ('f_nuevo_interes', 'ps_catalogo', 'link'): 'Cargar opciones',
    ('f_usuario', 'ps_foto_usuario', 'link'): 'Confirmar quitar foto',
    ('ps_foto_usuario', 'f_usuario', 'build'): 'Foto eliminada',
    ('pago_confirmacion', 'ps_confirmar_checkout', 'link'): 'Sesión sin token',
    ('pago_cancelado', 'ps_cancelar_checkout', 'link'): 'Sesión sin token',
    ('agenda', 'ficha', 'link'): '?interes',
    ('ficha', 'ps_estmetodo', 'link'): 'PATCH estado',
    ('agenda', 'ps_intereses', 'link'): '?buscar&estado',
    ('prospectos', 'ps_prosp', 'link'): '?buscar&origen',
}

# Separa los conectores cercanos para dejar espacio a sus rótulos.
RUTAS_ADMINISTRADOR = {
    ('agenda', 'ficha'): ((1034, 3674), (968, 3674)),
    ('agenda', 'ps_intereses'): ((1122, 3586), (1122, 3410)),
    ('ficha', 'ps_estmetodo'): ((902, 3696), (902, 3850)),
    ('f_revisar', 'ps_comp'): ((484, 4224), (418, 4224), (418, 4488), (374, 4488)),
    ('ps_comp', 'f_revisar'): ((374, 4466), (396, 4466), (396, 4246), (484, 4246)),
    ('pago_cancelado', 'ps_cancelar_publico'): ((924, 5566), (924, 5522), (1122, 5522), (1122, 5588)),
    ('ps_cancelar_publico', 'pago_cancelado'): ((1012, 5654), (946, 5654)),
}

MENSAJES_POR_ROL = {
    'Coordinador': MENSAJES_REVISION_Y_PROSPECTOS | {
        ('interesados', 'ps_asignar', 'link'): 'Asignar vendedor',
    },
    'Vendedor': {
        ('ficha', 'ps_show', 'link'): 'Consultar ficha',
    },
    'Visitante': {
        ('pago_cuota', 'stripe', 'link'): 'Pendiente y con URL',
        ('pago_cuota', 'catalogo', 'link'): 'Volver al catálogo',
    },
}

# Separa los puertos horizontales de solicitudes y respuestas en los pasillos
# estrechos. Las cajas conservan sus coordenadas.
ALTURAS_CONECTORES = {
    'Coordinador': {
        ('embudo', 'ps_mover'): 3454, ('ps_mover', 'embudo'): 3498,
        ('f_prospecto', 'ps_catalogo'): 2816, ('ps_catalogo', 'f_prospecto'): 2860,
        ('pago_confirmacion', 'ps_retorno_publico'): 6138, ('ps_retorno_publico', 'pago_confirmacion'): 6160,
        ('pago_cancelado', 'ps_cancelar_publico'): 6468, ('ps_cancelar_publico', 'pago_cancelado'): 6490,
    },
    'Vendedor': {
        ('embudo', 'ps_mover'): 2970, ('ps_mover', 'embudo'): 3058,
        ('ficha', 'ps_mover'): 2970, ('ps_mover', 'ficha'): 3036,
        ('ficha', 'ps_show'): 2992, ('ps_show', 'ficha'): 3036,
        ('pago_confirmacion', 'ps_retorno_publico'): 5148, ('ps_retorno_publico', 'pago_confirmacion'): 5148,
        ('pago_cancelado', 'ps_cancelar_publico'): 5500, ('ps_cancelar_publico', 'pago_cancelado'): 5500,
    },
    'Visitante': {
        ('stripe', 'pago_confirmacion'): 1276,
        ('pago_cuota', 'stripe'): 1210,
    },
}

# Mantiene el enlace largo del menú en un corredor lateral y lo rotula
# cerca de su llegada para distinguirlo de las llamadas de las filas intermedias.
RUTAS_NOTIFICACIONES = {
    'Coordinador': ((1188, 594), (1188, 616), (22, 616), (22, 5720), (792, 5720), (792, 5742)),
    'Vendedor': ((1188, 616), (1188, 638), (22, 638), (22, 4686), (792, 4686), (792, 4708)),
}

def armar(actor, paginas, enlaces):
    if actor == 'Administrador':
        return trazado.armar(paginas, enlaces, cortes=(), mensajes=MENSAJES_ADMINISTRADOR,
                             rutas=RUTAS_ADMINISTRADOR)
    desfases = {'actor': (1, 0), 'ps_login': (0, 1), 'error': (-1, 0),
                'f_perfil': (0, -1), 'stripe': (0, 1), 'agenda': (0, 1)}
    tamanos = {'ficha': (12, 10), 'ps_est': (8, 6), 'ps_listado': (7, 6)} if actor == 'Vendedor' else {}
    if actor == 'Coordinador':
        tamanos = {'f_revisar': (7, 4)}
    mensajes = MENSAJES_STRIPE | MENSAJES_POR_ROL[actor]
    if actor != 'Visitante':
        mensajes |= MENSAJES_INTERNOS
    rutas = {('menu', 'notificaciones'): RUTAS_NOTIFICACIONES[actor]} if actor in RUTAS_NOTIFICACIONES else {}
    return trazado.armar(paginas, enlaces, filas=FILAS[actor], desfases=desfases,
                         tamanos=tamanos, cortes=(), paso_fila=16 if actor == 'Vendedor' else 15,
                         mensajes=mensajes, alturas=ALTURAS_CONECTORES[actor],
                         rutas=rutas)
