"""Completa en el EAPX de P2 los diagramas que el documento ya solicita.

Usa la notación del generador de proyectocorreo/doc/ea/ea_p1.py y extrae
actores, CU, paquetes y llamadas entre capas de contenido.py y codigo.py.
No recrea el proyecto ni borra diagramas que se hayan movido manualmente.
"""
import json
import pathlib
import re
import sys
import uuid

HERE = pathlib.Path(__file__).resolve().parent
DOC = HERE.parent
sys.path[:0] = [str(DOC), str(HERE)]

import codigo
import contenido as C
import ea_base
from rutas import CRM_WEB

PREFERIDAS = {
    'CU1': ['POST /login', 'POST /usuarios', 'PUT /matriz'],
    'CU2': ['GET /catalogo', 'POST /registro-interes'],
    'CU3': ['POST /prospectos', 'PATCH /intereses/{interes}/asignar'],
    'CU4': ['PATCH /intereses/{interes}/estado'],
    'CU5': ['PATCH /intereses/{interes}/estado', 'POST /motivos'],
    'CU6': ['POST /intereses/{interes}/ordenes-pago', 'POST /ordenes-pago/{orden}/cuotas/{cuota}/checkout',
            'GET /pagos/stripe/sesiones/{sessionId}', 'POST /exportaciones'],
    'CU7': ['POST /intereses/{interes}/interacciones', 'POST /intereses/{interes}/recordatorios', 'GET /notificaciones'],
    'CU8': ['GET /reportes/estadisticas', 'GET /comisiones/resumen'],
}

# Métodos D realmente invocados por cada método N. Se comprueban contra
# codigo._llamadas al generar; si el código cambia, la generación falla.
PREFERIDAS_D = {
    'CU1': [['usuarioPorCorreo', 'crearToken'], ['crear'], ['guardarPermiso']],
    'CU2': [['programasAbiertos'], ['crear']],
    'CU3': [['crear'], ['transaccion', 'refrescarDetalle']],
    'CU4': [['guardar', 'actualizarEstadoProspecto']],
    'CU5': [['guardar', 'actualizarEstadoProspecto'], ['crear']],
    'CU6': [['crearOrden', 'insertarCuotas'], ['ordenConDetalle', 'crearTransaccion'],
            ['transaccionPorSesion'], ['exportarPendientes']],
    'CU7': [['registrarInteraccion'], ['crearRecordatorio'], ['listar']],
    'CU8': [['estadisticas'], ['resumenComisiones']],
}

ea_base.EAPX = HERE / 'crm-p2.eapx'
ea_base.SALIDA = DOC / 'diagramas'


def paquete(ea, padre, nombre):
    return next((p for p in padre.Packages if p.Name == nombre), None) or ea.paquete(padre, nombre)


def elemento(ea, pkg, nombre, tipo):
    return next((e for e in pkg.Elements if e.Name == nombre and e.Type == tipo), None) or ea.elemento(pkg, nombre, tipo)


def diagrama(ea, pkg, nombre, tipo, archivo, refrescar=False):
    """Conserva diagramas manuales salvo los recorridos cuyo código cambió."""
    anterior = next((d for d in pkg.Diagrams if d.Name == nombre), None)
    if anterior:
        if not refrescar:
            ea.exportar(anterior, archivo)
            return None
        indice = next(i for i in range(pkg.Diagrams.Count) if pkg.Diagrams.GetAt(i).DiagramID == anterior.DiagramID)
        pkg.Diagrams.DeleteAt(indice, False)
        pkg.Diagrams.Refresh()
    return ea.diagrama(pkg, nombre, tipo)


def requisitos(ea, modelo):
    req = paquete(ea, modelo, 'Captura de Requisitos')
    actores = {a: elemento(ea, req, a, 'Actor') for a, _ in C.ACTORES}
    casos = {cu: elemento(ea, req, f'{cu}: {C.DETALLE[cu]["gestionar"]}', 'UseCase') for cu in C.CU}
    for cu, caso in casos.items():
        for a in C.actores_cu(cu):
            if not any(c.SupplierID == caso.ElementID and c.Type == 'Association' for c in actores[a].Connectors):
                ea.conector(actores[a], caso, 'Association')

    d = diagrama(ea, req, 'Actores del sistema', 'Use Case', 'actores.png')
    if d:
        sistema = ea.elemento(req, 'CRM Comercial Educativo', 'Boundary')
        ea.poner(d, sistema, 310, 25, 320, 490, seq=50)
        for i, a in enumerate(actores.values()):
            ea.poner(d, a, 70, 55 + i * 112, 78, 80)
            ea.conector(a, sistema, 'Association')
        ea.exportar(d, 'actores.png')

    for cu, nombre in C.CU.items():
        d = diagrama(ea, req, f'{cu}: {nombre}', 'Use Case', f'uc-{cu.lower()}.png')
        if d:
            ac = C.actores_cu(cu)
            for i, a in enumerate(ac):
                ea.poner(d, actores[a], 50, 45 + i * 116, 65, 82)
            ea.poner(d, casos[cu], 355, 45 + (len(ac) - 1) * 58, 240, 95)
            ea.exportar(d, f'uc-{cu.lower()}.png')

    d = diagrama(ea, req, 'Diagrama general de casos de uso', 'Use Case', 'uc-general.png')
    if d:
        marco = ea.elemento(req, 'CRM Comercial Educativo: tres capas', 'Boundary')
        ea.poner(d, marco, 390, 15, 390, 8 * 105 + 40, seq=50)
        for i, cu in enumerate(C.CU): ea.poner(d, casos[cu], 445, 55 + i * 105, 270, 72, seq=1)
        for i, a in enumerate(actores.values()):
            x = 45 if i < 2 else 980
            y = 170 + (i % 2) * 420
            ea.poner(d, a, x, y, 78, 88)
        ea.exportar(d, 'uc-general.png')
    return req, actores, casos


def paquetes(ea, modelo, actores, casos):
    raiz = paquete(ea, modelo, 'Análisis de Paquetes')
    ps = {n: paquete(ea, raiz, n) for n in C.PAQUETES}
    d = diagrama(ea, raiz, 'Paquetes del sistema', 'Package', 'paquetes.png')
    if d:
        for i, p in enumerate(ps.values()):
            ea.poner(d, p, 35 + (i % 3) * 230, 45 + (i // 3) * 175, 190, 105)
        ea.exportar(d, 'paquetes.png')
    for i, (n, spec) in enumerate(C.PAQUETES.items(), 1):
        d = diagrama(ea, raiz, f'{n}: casos de uso', 'Package', f'paquete-{i}.png')
        if not d: continue
        p = ps[n]; cus = spec['cu']
        ea.poner(d, p, 45, 55 + (len(cus) - 1) * 58, 235, 100)
        for j, cu in enumerate(cus):
            ea.conector(p, casos[cu], 'Dependency', st='trace', dirigido=True)
            ea.poner(d, casos[cu], 455, 45 + j * 118, 270, 80)
        ea.exportar(d, f'paquete-{i}.png')


def interacciones(cu):
    """Recorrido representativo P→N→D por área; cada método se extrae del código."""
    clases, deps, errores = codigo.cadena(cu)
    if errores: raise ValueError('; '.join(errores))
    if cu == 'CU6':
        clases['StripeClient'] = {'estereotipo': 'external', 'capa': 'Externa'}
    if cu == 'CU5':
        # Marcar Perdido se realiza en el embudo (ruta clasificada como CU4),
        # pero su formulario y NInteres implementan la pérdida con motivo.
        extra, _, errores = codigo.cadena('CU4')
        if errores: raise ValueError('; '.join(errores))
        clases.update(extra)
    rutas = [r for r in codigo.rutas_api() if
             (r['cu'] == cu or (cu == 'CU5' and r['ruta'] == '/intereses/{interes}/estado'))
             and f'{r["verbo"]} {r["ruta"]}' in PREFERIDAS[cu]]
    rutas.sort(key=lambda r: PREFERIDAS[cu].index(f'{r["verbo"]} {r["ruta"]}'))
    php = codigo.clases_php()
    funciones = codigo.funciones_api()
    usos = codigo.usos_api()
    pasos = []
    if len(rutas) != len(PREFERIDAS[cu]):
        raise ValueError(f'{cu}: faltan rutas verificadas para la secuencia: {PREFERIDAS[cu]}')
    for indice, r in enumerate(rutas):
        n = r['controlador']
        fn = next((k for k, f in funciones.items() if f['verbo'] == r['verbo'] and
                   f['ruta'] == codigo.norm(r['ruta'])), None)
        if not fn: continue
        api = f'api/{fn.split(".")[0]}.js'
        paginas = [a.rsplit('/', 1)[-1] for a, fns in usos.items()
                   if fn in fns and a.rsplit('/', 1)[-1] in clases]
        pagina = next((p for p in paginas if p == {'CU2': 'PCatalogo.jsx', 'CU4': 'PEmbudo.jsx',
                                                  'CU5': 'PEmbudo.jsx'}.get(cu)),
                      paginas[0] if paginas else ('PLogin.jsx' if r['ruta'] == '/login' else api))
        actor = ('Coordinador' if cu == 'CU6' and
                 ('/aprobar' in r['ruta'] or r['ruta'] == '/exportaciones') else
                 'Administrador' if cu == 'CU5' and r['ruta'] == '/motivos' else
                 C.DETALLE[cu]['iniciador'])
        pasos.append((f'@{actor}', pagina, f'abrir {pagina}' if pagina != api else 'iniciar'))
        if pagina != api: pasos.append((pagina, api, f'{funciones[fn]["nombre"]}()'))
        etiqueta = f'{r["verbo"]} {r["ruta"]}'
        if cu == 'CU5' and r['ruta'] == '/intereses/{interes}/estado': etiqueta += ' (Perdido + motivo)'
        pasos.append((api, n, etiqueta))
        origen_datos = n
        if cu == 'CU6' and r['metodo'] in ('crearCheckout', 'confirmarCheckout'):
            llamada_stripe = next(((dato, metodo) for dato, metodo in codigo._llamadas(n, r['metodo'], php)
                                   if dato == 'NStripe'), None)
            if llamada_stripe is None:
                raise ValueError(f'{cu}: {n}::{r["metodo"]} ya no delega en NStripe')
            pasos.append((n, 'NStripe', f'{llamada_stripe[1]}()'))
            origen_datos = 'NStripe'
        # llamadas en orden real, entrando a los auxiliares (NStripe crea la transacción dentro de uno de ellos)
        disponibles = [(dato, metodo) for _, dato, metodo in codigo.llamadas_en_orden(
                           origen_datos, llamada_stripe[1] if origen_datos == 'NStripe' else r['metodo'])
                       if dato in clases and clases[dato]['estereotipo'] == 'datos']
        for nombre_metodo in PREFERIDAS_D[cu][indice]:
            real = next(((dato, metodo) for dato, metodo in disponibles if metodo == nombre_metodo), None)
            if real is None:
                raise ValueError(f'{cu}: {n}::{r["metodo"]} ya no llama a {nombre_metodo}() en la capa D')
            dato, metodo = real
            pasos.append((origen_datos, dato, f'{metodo}()'))
            if cu == 'CU6' and r['metodo'] == 'crearCheckout' and metodo == 'ordenConDetalle':
                pasos.append(('NStripe', 'StripeClient', 'checkout.sessions.create()'))
            if cu == 'CU6' and r['metodo'] == 'confirmarCheckout' and metodo == 'transaccionPorSesion':
                pasos.append(('NStripe', 'StripeClient', 'checkout.sessions.retrieve()'))
    if not pasos: raise ValueError(f'{cu} no tiene rutas de secuencia verificadas')
    return clases, pasos


# ------------------------------------------------------------------------------------------------ 7.4 Secuencia
# Recorridos principales de cada CU: ruta de la API y, en orden, los mensajes que salen de su método N ('N' = la clase
# N de la ruta). Cada mensaje se comprueba contra codigo.llamadas_en_orden: si el código deja de hacerlo, o lo hace en
# otro orden, la generación falla. Se dibuja el camino feliz; las validaciones y ramas de error quedan fuera.
RECORRIDOS = {
    'CU1': [('POST /login', [('N', 'DAuth', 'usuarioPorCorreo'), ('N', 'DAuth', 'crearToken'),
                             ('N', 'DBitacora', 'registrar'), ('N', 'NAcceso', 'menu'), ('NAcceso', 'DAcceso', 'menuPorRol')]),
            ('POST /usuarios', [('N', 'DUsuario', 'crear'), ('N', 'DUsuario', 'fresco')]),
            ('PUT /matriz', [('N', 'DSeguridad', 'guardarPermiso')])],
    'CU2': [('GET /catalogo', [('N', 'DCatalogo', 'programasAbiertos')]),
            ('POST /registro-interes', [('N', 'DProspecto', 'encontrarPorDocumentoOCorreoBloqueado'),
                                        ('N', 'DProspecto', 'crear'), ('N', 'DProspecto', 'crearInteres')])],
    'CU3': [('POST /prospectos', [('N', 'DProspecto', 'crear'), ('N', 'DProspecto', 'crearInteres'),
                                  ('N', 'DProspecto', 'conIntereses')]),
            ('PATCH /intereses/{interes}/asignar', [('N', 'DInteres', 'obtener'), ('N', 'DInteres', 'vendedor'),
                                                    ('N', 'DInteres', 'guardar'), ('N', 'DInteres', 'registrarInteraccion'),
                                                    ('N', 'DInteres', 'refrescarDetalle')])],
    'CU4': [('PATCH /intereses/{interes}/estado', [('N', 'DInteres', 'obtener'), ('N', 'DInteres', 'bloquear'),
                                                   ('N', 'DInteres', 'guardar'), ('N', 'DInteres', 'actualizarEstadoProspecto'),
                                                   ('N', 'DInteres', 'registrarInteraccion'), ('N', 'DInteres', 'refrescarDetalle')])],
    'CU5': [('PATCH /intereses/{interes}/estado', [('N', 'DInteres', 'obtener'), ('N', 'DInteres', 'guardar'),
                                                   ('N', 'DInteres', 'actualizarEstadoProspecto'),
                                                   ('N', 'DInteres', 'registrarInteraccion')]),
            ('POST /motivos', [('N', 'DMotivo', 'existeNombre'), ('N', 'DMotivo', 'crear')])],
    'CU6': [('POST /intereses/{interes}/ordenes-pago', [('N', 'DPago', 'interesBloqueado'), ('N', 'DPago', 'crearOrden'),
                                                        ('N', 'DPago', 'insertarItems'), ('N', 'DPago', 'insertarCuotas'),
                                                        ('N', 'DPago', 'crearPago')]),
            ('POST /ordenes-pago/{orden}/cuotas/{cuota}/checkout', [
                ('N', 'NStripe', 'iniciarCheckoutCuota'), ('NStripe', 'DStripe', 'ordenConDetalle'),
                ('NStripe', 'DPago', 'asegurarTokenCuota'), ('NStripe', 'StripeClient', 'checkout.sessions.create'),
                ('NStripe', 'DStripe', 'crearTransaccion')]),
            ('GET /pagos/stripe/sesiones/{sessionId}', [
                ('N', 'NStripe', 'verificarSesion'), ('NStripe', 'DStripe', 'transaccionPorSesion'),
                ('NStripe', 'StripeClient', 'checkout.sessions.retrieve'), ('NStripe', 'NPago', 'estadoCuota'),
                ('NStripe', 'DStripe', 'actualizarTransaccion'), ('NStripe', 'DPago', 'actualizarInteres')]),
            ('POST /exportaciones', [('N', 'DExportacion', 'exportarPendientes')])],
    'CU7': [('POST /intereses/{interes}/interacciones', [('N', 'DSeguimiento', 'registrarInteraccion'),
                                                         ('N', 'DSeguimiento', 'actualizarInteres')]),
            ('POST /intereses/{interes}/recordatorios', [('N', 'DSeguimiento', 'crearRecordatorio'),
                                                         ('N', 'DSeguimiento', 'actualizarInteres')]),
            ('GET /notificaciones', [('N', 'DNotificacion', 'listar')])],
    'CU8': [('GET /reportes/estadisticas', [('N', 'DReporte', 'estadisticas')]),
            ('GET /comisiones/resumen', [('N', 'DSeguimiento', 'resumenComisiones')])],
}
# Quién inicia cada recorrido cuando no es el iniciador del CU (contenido.DETALLE).
ACTOR_RUTA = {('CU5', 'POST /motivos'): 'Administrador', ('CU6', 'POST /exportaciones'): 'Coordinador'}
PAGINA_PREFERIDA = {'CU2': 'PCatalogo.jsx', 'CU4': 'PEmbudo.jsx', 'CU5': 'PEmbudo.jsx'}
PASO_SEQ = 35           # separación vertical fija de los mensajes en EA 15
PRIMERO_SEQ = 133       # altura del primer mensaje con las líneas de vida arriba en 35
IZQUIERDA_SEQ = 120     # centro del primer actor (a 12 pt): a su izquierda va la pestaña opt


def mensajes_secuencia(cu):
    """[(guarda, [(origen, destino, rótulo, 'call'|'return'|'self')])] por recorrido; la guarda del marco opt es la
    función de api/*.js que lo dispara. Los extremos son
    nombres de línea de vida: '@Actor', 'Pantalla', 'HTTP', 'Negocio', 'Datos', 'Stripe'."""
    php, rutas, funciones, usos = codigo.clases_php(), codigo.rutas_api(), codigo.funciones_api(), codigo.usos_api()
    clases, _, errores = codigo.cadena(cu)
    if errores: raise ValueError('; '.join(errores))
    if cu == 'CU5': clases.update(codigo.cadena('CU4')[0])   # «Perdido + motivo» se marca en PEmbudo.jsx (pantalla de CU4)
    capa = lambda c: 'Stripe' if c == 'StripeClient' else 'Negocio' if php[c]['estereotipo'] == 'negocio' else 'Datos'

    def retorno(c, m):
        firma = php[c]['metodos'][m]['firma']
        t = re.search(r'\):\s*([?\w\\|]+)$', firma)
        return t.group(1).rsplit('\\', 1)[-1] if t else 'resultado'

    escenas = []
    for ruta, pasos in RECORRIDOS[cu]:
        r = next((r for r in rutas if f'{r["verbo"]} {r["ruta"]}' == ruta), None)
        if not r: raise ValueError(f'{cu}: la ruta {ruta} ya no existe en api.php')
        n, met = r['controlador'], r['metodo']
        reales = codigo.llamadas_en_orden(n, met)
        i = 0
        for o, d, m in pasos:   # subsecuencia: cada mensaje existe y después del anterior
            o = n if o == 'N' else o
            while i < len(reales) and reales[i] != (o, d, m): i += 1
            if i == len(reales): raise ValueError(f'{cu} {ruta}: {o} ya no llama a {d}::{m}() en ese orden')
            i += 1
        fn = next((k for k, f in funciones.items() if f['verbo'] == r['verbo'] and f['ruta'] == codigo.norm(r['ruta'])), None)
        if not fn: raise ValueError(f'{cu}: ninguna función de api/*.js llama a {ruta}')
        api = f'{fn.split(".")[0]}.js'
        paginas = [a.rsplit('/', 1)[-1] for a, fns in usos.items() if fn in fns and a.rsplit('/', 1)[-1] in clases]
        if r['ruta'] == '/login': paginas = ['PLogin.jsx']
        if not paginas: raise ValueError(f'{cu}: ninguna página del CU llama a {fn}')
        pagina = PAGINA_PREFERIDA.get(cu) if PAGINA_PREFERIDA.get(cu) in paginas else paginas[0]
        actor = '@' + ACTOR_RUTA.get((cu, ruta), C.DETALLE[cu]['iniciador'])
        msj = [(actor, 'Pantalla', f'usar {pagina}', 'call'),
               ('Pantalla', 'HTTP', f'{api}::{funciones[fn]["nombre"]}()', 'call'),
               ('HTTP', 'Negocio', f'{n}::{met}()', 'call')]
        for o, d, m in pasos:
            if capa(d) == 'Negocio': msj.append(('Negocio', 'Negocio', f'{d}::{m}()', 'self'))
            elif capa(d) == 'Stripe': msj += [('Negocio', 'Stripe', f'{m}()', 'call'), ('Stripe', 'Negocio', 'Session', 'return')]
            else: msj += [('Negocio', 'Datos', f'{d}::{m}()', 'call'), ('Datos', 'Negocio', retorno(d, m), 'return')]
        msj += [('Negocio', 'HTTP', retorno(n, met), 'return'), ('HTTP', 'Pantalla', 'respuesta JSON', 'return'),
                ('Pantalla', actor, 'resultado mostrado', 'return')]
        escenas.append((funciones[fn]['nombre'], msj))   # guarda del opt: la acción que dispara el recorrido
    return escenas


def geometria_secuencia(cu, pt):
    """Acomodo del sd de un CU con letra de pt puntos, sin abrir EA: líneas de vida con su x, marcos opt y medidas.
    La separación entre líneas de vida se ajusta al nombre y al rótulo más largo que pasa entre ellas."""
    escenas = mensajes_secuencia(cu)
    actores = list(dict.fromkeys(a for _, msj in escenas for x in msj for a in x[:2] if a.startswith('@')))
    capas = [('Pantalla', 'Pantalla React'), ('HTTP', 'Cliente HTTP (Axios)'), ('Negocio', 'Negocio Laravel'),
             ('Datos', 'Datos PostgreSQL')]
    if any(x[1] == 'Stripe' for _, msj in escenas for x in msj): capas.append(('Stripe', 'Pasarela Stripe'))
    vidas = [(a, a[1:]) for a in actores] + capas
    idx = {k: i for i, (k, _) in enumerate(vidas)}
    letra = lambda texto, f=0.58: len(texto) * f * pt   # ancho en unidades de EA con Calibri a pt puntos
    cabecera = lambda k: max(70 if k.startswith('@') else 110, letra(dict(vidas)[k], 0.62) + 30)
    hueco = [(cabecera(vidas[i][0]) + cabecera(vidas[i + 1][0])) / 2 + 20 for i in range(len(vidas) - 1)]
    for a, b, texto, tipo in sorted((x for _, msj in escenas for x in msj), key=lambda x: abs(idx[x[0]] - idx[x[1]])):
        i, j = sorted((idx[a], idx[b]))
        if tipo == 'self': j = min(i + 1, len(hueco))   # el rótulo del automensaje va a la derecha
        falta = letra(texto) + 40 - sum(hueco[i:j])
        if falta > 0: hueco[j - 1] += falta
    # el primer actor, a la derecha de la guarda más larga: ninguna guarda cruza una línea de vida
    xs = [max(IZQUIERDA_SEQ * pt / 12, 32 + max(letra(f'[{g}]') for g, _ in escenas))]
    for h in hueco: xs.append(xs[-1] + h)
    # EA 15 acomoda solo los mensajes (no respeta PtStartY): el primero a 98 de la cabecera y luego cada 35, también
    # los automensajes. Los marcos opt se calculan con esa misma regla y quedan contiguos, como en G07.
    marcos, y = [], PRIMERO_SEQ
    for ruta, msj in escenas:
        arriba = y - 28                                   # el rótulo del primer mensaje queda bajo el borde
        for _ in msj: ultimo = y; y += PASO_SEQ
        marcos.append((ruta, arriba, ultimo + 7))
    der = xs[-1] + max(70, cabecera(vidas[-1][0]) / 2 + 15)
    return dict(escenas=escenas, vidas=[(k, t, x, cabecera(k)) for (k, t), x in zip(vidas, xs)], marcos=marcos,
                alto=ultimo + 10, ancho=der + 15, der=der)


def letra_secuencia(cu, alto_cm):
    """Letra de EA (11-16 pt) que deja más grande el texto impreso del sd en la hoja (19,5 × alto_cm): EA no agranda la
    separación entre mensajes, así que un sd alto gana con letra grande y uno ancho no."""
    def impreso(pt):
        g = geometria_secuencia(cu, pt)
        return pt * min(19.5 / (g['ancho'] + 20), alto_cm / (g['alto'] + 60))
    return max(range(11, 17), key=impreso)


def secuencia(ea, raiz, cu, archivo, pt):
    """sd del CU en una sola hoja: una línea de vida por capa (actor, pantalla React, cliente HTTP, negocio Laravel,
    datos PostgreSQL y, en CU6, la pasarela Stripe), cada mensaje con la clase y el método reales y un marco opt por
    recorrido con la acción de api/*.js como guarda. pt: letra de nombres y rótulos (la de los rótulos la fija EA al abrir)."""
    g = geometria_secuencia(cu, pt)
    nombre = f'{cu}. {C.CU[cu]}: Secuencia (recorridos principales)'
    anterior = next((x for x in raiz.Diagrams if x.Name == nombre), None)
    if anterior:   # sus marcos opt quedarían sueltos en el paquete al rehacer el diagrama
        viejos = {o.ElementID for o in anterior.DiagramObjects if ea.r.GetElementByID(o.ElementID).Type == 'InteractionFragment'}
        for i in reversed(range(raiz.Elements.Count)):
            if raiz.Elements.GetAt(i).ElementID in viejos: raiz.Elements.DeleteAt(i, False)
        raiz.Elements.Refresh()
    d = diagrama(ea, raiz, nombre, 'Sequence', archivo, refrescar=True)
    d.StyleEx = 'SuppressBrackets=1;'; d.Update()
    estilo = f"ObjectStyle='font=Calibri;fontsz={pt * 10};'"
    elementos = {}
    for k, texto, x, w in g['vidas']:
        tipo = 'Actor' if k.startswith('@') else 'Sequence'   # línea de vida UML: cabecera rectangular de una línea
        e = elementos[k] = elemento(ea, raiz, texto, tipo)   # la misma línea de vida en los ocho diagramas
        if e.Stereotype: e.Stereotype = ''; e.Update()      # sin ícono de robustez (tapaba el primer mensaje), como G07
        ea.poner(d, e, round(x - w / 2), 35, round(w), g['alto'])
        ea.r.Execute(f'UPDATE t_diagramobjects SET {estilo} WHERE Diagram_ID={d.DiagramID} AND Object_ID={e.ElementID}')
    n = 0
    for _, msj in g['escenas']:
        for a, b, texto, tipo in msj:
            n += 1
            ea.mensaje_seq(d, elementos[a], elementos[b], texto.replace("'", '´'), n, 'return' if tipo == 'return' else 'call')
    for ruta, arriba, abajo in g['marcos']:
        fr = ea.elemento(raiz, '', 'InteractionFragment')
        fr.Subtype = 1   # opt
        fr.Update()
        parte = fr.Partitions.AddNew('x', ''); parte.Size = 100; fr.Update()
        guid = '{' + str(uuid.uuid4()).upper() + '}'
        ea.r.Execute(f"UPDATE t_xref SET Description='@PAR;Name={ruta};Size={abajo - arriba};GUID={guid};@ENDPAR;' "
                     f"WHERE Client='{fr.ElementGUID}' AND Name='Partitions'")
        ea.poner(d, fr, 15, arriba, round(g['der'] - 15), abajo - arriba, seq=60)
        ea.r.Execute(f'UPDATE t_diagramobjects SET {estilo} WHERE Diagram_ID={d.DiagramID} AND Object_ID={fr.ElementID}')
    d.Update(); ea.r.ReloadDiagram(d.DiagramID)
    ea.exportar(d, archivo)


def con_letra_rotulos(pt, tarea):
    """EA toma la letra de los rótulos de las líneas (opción FONTSIZE13 del registro, 8 pt por defecto) al abrir: se
    sube a pt mientras corre tarea() y se restaura al terminar."""
    import winreg
    clave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Sparx Systems\EA400\EA\OPTIONS', 0,
                           winreg.KEY_READ | winreg.KEY_SET_VALUE)
    antes = winreg.QueryValueEx(clave, 'FONTSIZE13')
    winreg.SetValueEx(clave, 'FONTSIZE13', 0, antes[1], pt if antes[1] == winreg.REG_DWORD else str(pt))
    try: return tarea()
    finally: winreg.SetValueEx(clave, 'FONTSIZE13', 0, antes[1], antes[0]); winreg.CloseKey(clave)


# Alto útil de la hoja para cada sd (cm), el mismo que usan documento_p2.py y actualizar_secuencias.py.
from formato_g07 import ALTO_SD  # noqa: E402
ALTO_SEQ = {cu: ALTO_SD[0] if i == 0 else ALTO_SD[1] for i, cu in enumerate(C.CU)}


def solo_secuencias(cus=None):
    """Rehace los sd de 7.4 (todos o los de cus), agrupados por letra: una sesión de EA por cada letra de rótulos."""
    grupos = {}
    for cu in cus or C.CU:
        grupos.setdefault(letra_secuencia(cu, ALTO_SEQ[cu]), []).append(cu)
    for pt, lista in sorted(grupos.items()):
        def tarea(lista=lista, pt=pt):
            ea = ea_base.EA.abrir_existente()
            try:
                seq = paquete(ea, ea.modelo, 'Diseño de Secuencia')
                # El respaldo documental contiene cientos de elementos auxiliares en
                # este paquete. EA de 32 bits falla al enumerarlos para cada línea
                # de vida; una subcarpeta conserva los originales y permite
                # regenerar las ocho secuencias verificadas contra el código.
                if seq.Elements.Count >= 100:
                    seq = paquete(ea, seq, 'Secuencias 7.4 integradas')
                for cu in lista: secuencia(ea, seq, cu, f'sd-{cu.lower()}.png', pt)
            finally: ea.cerrar()
        print(f'  letra {pt} pt: {", ".join(lista)}')
        con_letra_rotulos(pt, tarea)


def diagrama_interaccion(ea, raiz, cu, tipo, archivo):
    clases, pasos = interacciones(cu)
    nombre = f'{cu}. {C.CU[cu]}: {tipo} (recorridos principales)'
    d = diagrama(ea, raiz, nombre, 'Sequence' if tipo == 'Secuencia' else 'Collaboration', archivo,
                 refrescar=(cu == 'CU6'))
    if not d: return
    d.StyleEx = 'SuppressBrackets=1;'; d.Update()
    if tipo == 'Secuencia':
        php = codigo.clases_php()
        nombres_actores = list(dict.fromkeys(a[1:] for a, _, _ in pasos if a.startswith('@')))
        actores = {n: ea.elemento(raiz, n, 'Actor') for n in nombres_actores}
        # Una línea de vida por responsabilidad mantiene legibles las ocho
        # secuencias en la hoja vertical. Cada flecha conserva el nombre de la
        # clase y método concretos del código, aunque el CU use varias clases N/D.
        vidas = [('Pantalla React', 'boundary'), ('Cliente HTTP', 'boundary'),
                 ('Negocio Laravel', 'control'), ('Datos PostgreSQL', 'entity')]
        if cu == 'CU6': vidas.append(('Pasarela Stripe', 'boundary'))
        objetos = {n: ea.elemento(raiz, n, 'Object', st) for n, st in vidas}
        def grupo(n):
            if n.startswith('@'): return actores[n[1:]]
            x = clases[n]
            if x['estereotipo'] == 'external': return objetos['Pasarela Stripe']
            if x['estereotipo'] == 'client page': return objetos['Pantalla React']
            if x['capa'] == 'Presentacion': return objetos['Cliente HTTP']
            if x['capa'] == 'Negocio': return objetos['Negocio Laravel']
            return objetos['Datos PostgreSQL']
        escenas = []
        for paso in pasos:
            if paso[0].startswith('@'): escenas.append([])
            escenas[-1].append(paso)

        def retorno_php(nombre, metodo):
            firma = php.get(nombre, {}).get('metodos', {}).get(metodo, {}).get('firma', '')
            m = re.search(r'\):\s*([?\w\\|]+)$', firma)
            return m.group(1) if m else 'resultado'

        mensajes, marcos = [], []
        for j, escena in enumerate(escenas):
            inicio = len(mensajes) + 1
            ruta = PREFERIDAS[cu][j]
            for a, b, txt in escena:
                if not a.startswith('@') and a.startswith('api/'):
                    met = next((r['metodo'] for r in codigo.rutas_api() if
                                r['controlador'] == b and f'{r["verbo"]} {r["ruta"]}' == ruta), None)
                    etiqueta = f'{b}::{met}()' if met else txt
                elif not a.startswith('@') and a in php and b in php:
                    etiqueta = f'{b}::{txt}'
                elif not a.startswith('@') and a in clases and clases[a]['estereotipo'] == 'client page':
                    etiqueta = f'{b.rsplit("/", 1)[-1]}::{txt}'
                else: etiqueta = txt
                mensajes.append((a, b, etiqueta, 'call'))
                if not a.startswith('@') and b in clases and clases[b]['estereotipo'] == 'external':
                    mensajes.append((b, a, 'Checkout Session', 'return'))
                elif not a.startswith('@') and a in php and b in php and clases[b]['estereotipo'] == 'datos':
                    metodo = txt.partition('(')[0]
                    mensajes.append((b, a, retorno_php(b, metodo), 'return'))
            for a, b, txt in reversed(escena):
                if not a.startswith('@') and b in clases and clases[b]['estereotipo'] == 'external':
                    continue
                if not a.startswith('@') and a in php and b in php and clases[b]['estereotipo'] == 'datos':
                    continue  # la clase D ya respondió justo después de su llamada
                if a.startswith('@'): etiqueta = 'resultado mostrado'
                elif a in php and b in php:
                    etiqueta = retorno_php(b, txt.partition('(')[0])
                elif a.startswith('api/'):
                    controlador = b
                    metodo = next((r['metodo'] for r in codigo.rutas_api() if
                                   r['controlador'] == controlador and
                                   f'{r["verbo"]} {r["ruta"]}' == ruta), None)
                    etiqueta = retorno_php(controlador, metodo) if metodo else 'respuesta JSON'
                else: etiqueta = 'respuesta JSON'
                mensajes.append((b, a, etiqueta, 'return'))
            metodo_guardia = next((r['metodo'] for r in codigo.rutas_api() if
                                   f'{r["verbo"]} {r["ruta"]}' == ruta), ruta)
            marcos.append((f'{metodo_guardia}()', inicio, len(mensajes)))

        # En EA 15 los mensajes usan una separación vertical fija de 35.
        alto = 190 + len(mensajes) * 35
        for i, a in enumerate(actores.values()): ea.poner(d, a, 35 + i * 85, 35, 65, alto)
        for i, (n, _) in enumerate(vidas):
            ea.poner(d, objetos[n], 240 + i * 230, 35, 140, alto)
        for i, (a, b, mensaje, clase_mensaje) in enumerate(mensajes, 1):
            ea.mensaje_seq(d, grupo(a), grupo(b), mensaje.replace("'", '´'), i, clase_mensaje)
        for guarda, inicio, fin in marcos:
            fr = ea.elemento(raiz, '', 'InteractionFragment')
            fr.Subtype = 1  # opt, igual que el generador del P1
            fr.Update()
            parte = fr.Partitions.AddNew('x', ''); parte.Size = 100; fr.Update()
            y = 133 + (inicio - 1) * 35 - 26
            h = (fin - inicio + 1) * 35 + 34
            guid = '{' + str(uuid.uuid4()).upper() + '}'
            descripcion = f'@PAR;Name={guarda};Size={h};GUID={guid};@ENDPAR;'
            ea.r.Execute(f"UPDATE t_xref SET Description='{descripcion}' "
                         f"WHERE Client='{fr.ElementGUID}' AND Name='Partitions'")
            ea.poner(d, fr, 15, y, 1100 + (230 if cu == 'CU6' else 0), h, seq=60)
    else:
        # Una fila por recorrido evita cruces entre pantallas o actores cuando
        # el CU abarca varias acciones. Los objetos y enlaces son los del P1.
        escenas = []
        for paso in pasos:
            if paso[0].startswith('@'): escenas.append([])
            escenas[-1].append(paso)
        numero = 0
        for fila, escena in enumerate(escenas):
            y = 65 + fila * 210
            nombres = list(dict.fromkeys([x for a, b, _ in escena for x in (a, b)]))
            objetos = {}
            for col, n in enumerate(nombres):
                tipo_obj = 'Actor' if n.startswith('@') else 'Object'
                st = '' if tipo_obj == 'Actor' else {
                    'client page': 'boundary', 'module': 'boundary', 'negocio': 'control',
                     'datos': 'entity', 'model': 'entity', 'external': 'boundary'}.get(clases[n]['estereotipo'], 'control')
                e = ea.elemento(raiz, n.lstrip('@'), tipo_obj, st)
                objetos[n] = e
                ea.poner(d, e, 35 + col * 220, y, 65, 65)
            for a, b, txt in escena:
                numero += 1
                enlace = ea.conector(objetos[a], objetos[b], 'Association')
                corto = txt if len(txt) <= 36 else txt[:33] + '...'
                ea.mensaje_com(d, enlace, objetos[a], objetos[b], corto.replace("'", '´'), str(numero), numero, 0)
    ea.exportar(d, archivo)


def despliegue(ea, modelo):
    """6.1 calcado de G07 (pág. 62): servidor tecnoweb, router, switch, PC Administrador y PC Cliente, BD y pasarela.
    Cada valor es real: versiones de los lock, PostgreSQL 18.6 (medido en el P1), Apache + PHP 8.4 y la ruta
    del P2 (P2_WEB.md); de Stripe, solo los recursos que llama negocio/app/Negocio/NStripe.php
    (checkout->sessions, customers, Webhook::constructEvent)."""
    for i in range(modelo.Packages.Count):   # se rehace entero: sus elementos no aparecen en otros diagramas
        if modelo.Packages.GetAt(i).Name == 'Diseño de Despliegue':
            modelo.Packages.DeleteAt(i, False); modelo.Packages.Refresh(); break
    raiz = ea.paquete(modelo, 'Diseño de Despliegue')
    d = ea.diagrama(raiz, 'Diagrama de Despliegue', 'Deployment')
    laravel = next(p['version'].lstrip('v') for p in json.loads((CRM_WEB / 'negocio/composer.lock').read_text(encoding='utf-8'))['packages']
                   if p['name'] == 'laravel/framework')
    react = json.loads((CRM_WEB / 'presentacion/package-lock.json').read_text(encoding='utf-8'))['packages']['node_modules/react']['version']
    NARANJA, AZUL, AZUL2, ROSA, VERDE = 0x9CD4FF, 0xF8E8D8, 0xF0D4B8, 0xCCC8F8, 0xE0ECCF   # COLORREF 0xBBGGRR
    # Cuadrícula: arriba el servidor; franja central router + switch, centrada con las dos PCs; abajo la BD y la
    # pasarela (G07).
    # Letra de 11 pt para imprimir; las medidas están pensadas para ella: cada caja anidada deja CAB arriba para
    # el rótulo «estereotipo» + nombre (dos líneas) y PAD a los lados y abajo, y ningún nombre obliga a EA a
    # agrandar una caja (si lo hiciera, las anidadas se montarían).
    CAB, PAD = 60, 20
    LETRA = 110   # décimas de punto

    def dentro(x, y, w, h):
        return x + PAD, y + CAB, w - 2 * PAD, h - CAB - PAD

    def fila(x, y, w, h, n, ancho, alto):
        """n cajas de ancho × alto con el mismo espacio entre ellas, centradas bajo el rótulo de (x, y, w, h)."""
        hueco = (w - n * ancho) / (n + 1)
        arriba = round(y + CAB + (h - CAB - PAD - alto) / 2)
        return [(round(x + hueco + i * (ancho + hueco)), arriba, ancho, alto) for i in range(n)]

    # Equipos de usuario como G07 y como pide el docente en la clase de diseño («usuarios dentro de la red» y
    # «usuarios de internet»): se agrupan por tipo de acceso, no uno por rol. Deben cubrir todos los actores.
    PCS = [('adm', 'PC Administrador', ['Administrador', 'Coordinador', 'Vendedor']),   # panel con sesión
           ('cli', 'PC Cliente', ['Visitante'])]                                       # catálogo público, sin sesión
    assert sorted(a for _, _, g in PCS for a in g) == sorted(a for a, _ in C.ACTORES), 'PCs ≠ actores de contenido'
    PC_W, PC_H, PC_GAP = 240, 210, 15
    SRV = (40, 40, 500, 350)
    SO = dentro(*SRV)
    WEB = dentro(*SO)
    BD = (40, 520, 500, 310)
    SO_BD = dentro(*BD)
    PG = dentro(*SO_BD)
    PAS = (700, BD[1], 400, 310)                                      # abajo, junto a la BD, como G07
    API = dentro(*PAS)
    centro = (SRV[1] + SRV[3] + BD[1]) // 2                           # franja entre el servidor y la BD
    ROUTER = (700, centro - 40, 130, 80)                              # alineado con la pasarela
    SWITCH = (950, centro - 40, 130, 80)
    PC_X = SWITCH[0] + SWITCH[2] // 2 + 215
    PC_Y = centro - (len(PCS) * PC_H + (len(PCS) - 1) * PC_GAP) // 2   # PCs centradas con el switch
    espec = [
        ('srv', 'www.tecnoweb.org.bo', 'Device', None, *SRV, NARANJA),
        ('so', 'Sistema Operativo Fedora Linux', 'Device', 'srv', *SO, AZUL),
        ('web', 'Apache con PHP 8.4 (/inf513/grupo05sa/proyecto2)', 'ExecutionEnvironment', 'so', *WEB, AZUL),
        *[(k, n, 'Component', 'web', *r, ROSA) for (k, n), r in zip(
            [('p', f'presentacion (React {react})'), ('n', f'negocio (Laravel {laravel}, API REST)'),
             ('d', 'datos (paquete Composer)')], fila(*WEB, 3, 125, 95))],
        ('router', 'Router', 'Device', None, *ROUTER, NARANJA),
        ('switch', 'Switch', 'Device', None, *SWITCH, NARANJA),
        ('pas', 'Pasarela de Pago Stripe', 'Device', None, *PAS, AZUL2),
        ('api', 'API REST Stripe (Sandbox)', 'ExecutionEnvironment', 'pas', *API, AZUL),
        *[(k, n, 'Component', 'api', *r, ROSA) for (k, n), r in zip(
            [('chk', 'Checkout Sessions'), ('cus', 'Customers'), ('whk', 'Webhooks firmados')], fila(*API, 3, 105, 70))],
        ('bd', 'Database Server db.tecnoweb.org.bo', 'Device', None, *BD, AZUL2),
        ('so_bd', 'Sistema Operativo Linux', 'Device', 'bd', *SO_BD, AZUL),
        ('pg', 'PostgreSQL 18.6', 'ExecutionEnvironment', 'so_bd', *PG, AZUL),
        ('base', 'db_grupo05sa (esquema public)', 'Artifact', 'pg', *fila(*PG, 1, 250, 60)[0], VERDE),
    ]
    for i, (k, nombre, _) in enumerate(PCS):
        pc = (PC_X, PC_Y + i * (PC_H + PC_GAP), PC_W, PC_H)
        so_pc = dentro(*pc)
        espec += [(k, nombre, 'Device', None, *pc, NARANJA),
                  (k + 'so', 'S. O. Windows, Linux, MacOS', 'Device', k, *so_pc, AZUL),
                  (k + 'nav', 'Navegador web (Chrome, Firefox, Edge)', 'Component', k + 'so',
                   *fila(*so_pc, 1, 170, 55)[0], ROSA)]
    caja = {k: (x, y, w, h) for k, _, _, _, x, y, w, h, _ in espec}
    for k, _, _, padre, x, y, w, h, _ in espec:   # ninguna caja se sale de su padre
        if padre:
            px, py, pw, ph = caja[padre]
            assert px < x and py < y and x + w < px + pw and y + h < py + ph, f'{k} se sale de {padre}'
    el, nivel = {}, {}
    for k, nombre, tipo, padre, x, y, w, h, color in espec:
        nivel[k] = nivel[padre] + 1 if padre else 0
        el[k] = ea.elemento(raiz, nombre, tipo, padre=el.get(padre))
        ea.poner(d, el[k], x, y, w, h, seq=10 - 2 * nivel[k])   # lo anidado, delante
        # color y letra grande (el diagrama se imprime en una página apaisada): fontsz va en décimas de punto
        ea.r.Execute(f"UPDATE t_diagramobjects SET ObjectStyle='BCol={color};font=Calibri;fontsz={LETRA};' "
                     f"WHERE Diagram_ID={d.DiagramID} AND Object_ID={el[k].ElementID}")
    # Enlaces y rótulos de G07: solo servidor-router lleva el protocolo web; la pasarela cuelga solo del servidor
    enlaces = [('srv', 'router', 'HTTPS'), ('router', 'switch', 'TCP/IP'), ('srv', 'bd', 'TCP/IP'), ('srv', 'pas', 'TCP/IP')]
    enlaces += [('switch', k, 'TCP/IP') for k, _, _ in PCS]
    for a, b, protocolo in enlaces:
        c = ea.conector(el[a], el[b], 'CommunicationPath', protocolo)
        c.Direction = 'Unspecified'; c.Update()   # sin flecha, como G07
    ea.exportar(d, 'despliegue.png')


def solo_despliegue():
    """Rehace solo 6.1. Los rótulos de las líneas usan la letra por defecto de EA (opción del usuario, 8 pt):
    se sube a 11 pt mientras se exporta este diagrama, para imprimirlo legible, y se restaura al terminar."""
    import winreg
    clave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Sparx Systems\EA400\EA\OPTIONS', 0,
                           winreg.KEY_READ | winreg.KEY_SET_VALUE)
    antes = winreg.QueryValueEx(clave, 'FONTSIZE13')
    winreg.SetValueEx(clave, 'FONTSIZE13', 0, antes[1], 11 if antes[1] == winreg.REG_DWORD else '11')
    try:
        ea = ea_base.EA.abrir_existente()
        try: despliegue(ea, ea.modelo)
        finally: ea.cerrar()
    finally:
        winreg.SetValueEx(clave, 'FONTSIZE13', 0, antes[1], antes[0]); winreg.CloseKey(clave)


def main():
    ea_base.SALIDA.mkdir(exist_ok=True)
    if sys.argv[1:] == ['--despliegue']:   # solo 6.1
        return solo_despliegue()
    if sys.argv[1:2] == ['--secuencias']:  # solo 7.4 (opcional: CU1 CU6 ...)
        return solo_secuencias(sys.argv[2:])
    ea = ea_base.EA.abrir_existente()
    try:
        _, actores, casos = requisitos(ea, ea.modelo)
        paquetes(ea, ea.modelo, actores, casos)
        col = paquete(ea, ea.modelo, 'Análisis de Colaboración')
        seq = paquete(ea, ea.modelo, 'Diseño de Secuencia')
        for cu in C.CU:
            diagrama_interaccion(ea, col, cu, 'Comunicación', f'com-{cu.lower()}.png')
    finally:
        ea.cerrar()
    print(f'Exportados {len(ea.exportados)} diagramas PNG y EMF en {ea_base.SALIDA}')
    solo_secuencias()   # aparte: cada letra de rótulos necesita su propia sesión de EA
    solo_despliegue()   # aparte: necesita abrir EA con la letra de rótulos a 11 pt


if __name__ == '__main__': main()
