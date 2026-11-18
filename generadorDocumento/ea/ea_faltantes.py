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
        disponibles = [(dato, metodo) for dato, metodo in codigo._llamadas(origen_datos,
                                                                            llamada_stripe[1] if origen_datos == 'NStripe' else r['metodo'], php)
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
    """6.1 calcado de G07 (pág. 62): servidor tecnoweb, router, switch, una PC por actor, BD y pasarela.
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
    # Cuadrícula: arriba el servidor; franja central router + switch, a la altura del centro de la columna de PCs
    # (así las cuatro líneas del switch entran por el lado izquierdo de cada PC); abajo la BD y la pasarela (G07).
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

    PC_W, PC_H, PC_GAP = 240, 210, 15
    alto = 4 * PC_H + 3 * PC_GAP                                      # la columna de PCs marca el alto (885)
    SRV = (40, 40, 500, 350)
    SO = dentro(*SRV)
    WEB = dentro(*SO)
    BD = (40, 40 + alto - 350, 500, 350)                              # termina con la última PC
    SO_BD = dentro(*BD)
    PG = dentro(*SO_BD)
    PAS = (700, BD[1], 400, 350)                                      # abajo, junto a la BD, como G07
    API = dentro(*PAS)
    centro = round(40 + alto / 2)                                     # centro de la columna de PCs
    ROUTER = (700, centro - 40, 130, 80)                              # alineado con la pasarela
    SWITCH = (950, centro - 40, 130, 80)
    PC_X = SWITCH[0] + SWITCH[2] // 2 + 280   # a 280 del centro del switch: las líneas entran por el lado izquierdo
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
    for i, (actor, _) in enumerate(C.ACTORES):   # una PC por rol, como «PC Cliente» y «PC Administrador» de G07
        pc = (PC_X, 40 + i * (PC_H + PC_GAP), PC_W, PC_H)
        so_pc = dentro(*pc)
        espec += [(actor, f'PC {actor}', 'Device', None, *pc, NARANJA),
                  (actor + 'so', 'S. O. Windows, Linux, MacOS', 'Device', actor, *so_pc, AZUL),
                  (actor + 'nav', 'Navegador web (Chrome, Firefox, Edge)', 'Component', actor + 'so',
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
    enlaces += [('switch', a, 'TCP/IP') for a, _ in C.ACTORES]
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
    ea = ea_base.EA.abrir_existente()
    try:
        _, actores, casos = requisitos(ea, ea.modelo)
        paquetes(ea, ea.modelo, actores, casos)
        col = paquete(ea, ea.modelo, 'Análisis de Colaboración')
        seq = paquete(ea, ea.modelo, 'Diseño de Secuencia')
        for cu in C.CU:
            diagrama_interaccion(ea, col, cu, 'Comunicación', f'com-{cu.lower()}.png')
            diagrama_interaccion(ea, seq, cu, 'Secuencia', f'sd-{cu.lower()}.png')
    finally:
        ea.cerrar()
    print(f'Exportados {len(ea.exportados)} diagramas PNG y EMF en {ea_base.SALIDA}')
    solo_despliegue()   # aparte: necesita abrir EA con la letra de rótulos a 11 pt


if __name__ == '__main__': main()
