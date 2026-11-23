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
from formato_g07 import ALTO_COM, ALTO_SD
from rutas import CRM_WEB

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


# ------------------------------------------------------------------------------------------------ 5.3 Análisis
# 5.3.1 (colaboración) y 5.3.2 (clases) dibujan los recorridos de 7.4 (RECORRIDOS, comprobados contra el código): las
# tres vistas de un CU muestran las mismas clases y los mismos métodos. Cada diagrama va entero en su hoja carta, con 1 cm
# de margen lateral, vertical o apaisada según cuál lo deja más grande (formato_g07.apaisada). Todas las medidas son
# múltiplos de la letra PT_ANALISIS para que impresa quede legible.
PT_ANALISIS = 12
CAPAS = {'Presentacion': 'Presentación', 'Negocio': 'Negocio', 'Datos': 'Datos'}
CM_EA = 96 / 2.54   # unidades de EA (1/96 de pulgada) por centímetro
HOJAS = [(25.9 * CM_EA, ALTO_COM[1] * CM_EA), (19.5 * CM_EA, ALTO_SD[1] * CM_EA)]   # apaisada y vertical, bajo «CUn. …»


def impresa(ancho, alto, pt=PT_ANALISIS):
    """Letra impresa (pt) de un diagrama de ancho × alto unidades en la hoja que lo deja más grande."""
    return pt * max(min(w / ancho, h / alto) for w, h in HOJAS)
COLORES_COM = [0x000000, 0x0000C0, 0x008000, 0xC00000]   # COLORREF 0xBBGGRR: negro, rojo, verde, azul (uno por recorrido)


def ancho_texto(texto, pt, negrita=False):
    """Ancho aproximado en unidades de EA de un texto en Calibri a pt puntos (medido en las exportaciones)."""
    return len(texto) * pt * (0.6 if negrita else 0.53)


def con_letra(ea, d, e, pt):
    ea.r.Execute(f"UPDATE t_diagramobjects SET ObjectStyle='font=Calibri;fontsz={pt * 10};' "
                 f"WHERE Diagram_ID={d.DiagramID} AND Object_ID={e.ElementID}")


def piezas(cu):
    """Objetos y llamadas de los recorridos del CU: ({nombre: tipo}, [[(origen, destino, método)] por recorrido]) con
    tipo actor | pagina | api | negocio | datos | externa (la pasarela Stripe) | model. El actor llama a su página con
    la acción de api/*.js que dispara el recorrido."""
    php = codigo.clases_php()
    tipo, escenas = {}, []
    for r in recorridos(cu):
        api = f'api/{r["api"]}'
        llamadas = [('@' + r['actor'], r['pagina'], r['fn']), (r['pagina'], api, r['fn']), (api, r['n'], r['met'])]
        llamadas += r['pasos']
        for o, d, _ in llamadas:
            for x in (o, d):
                tipo.setdefault(x, 'actor' if x.startswith('@') else 'pagina' if x.endswith('.jsx') else
                                'api' if x.startswith('api/') else php[x]['estereotipo'] if x in php else 'externa')
        escenas.append(llamadas)
    return tipo, escenas


def borrar_paquete(modelo, nombre):
    for i in range(modelo.Packages.Count):
        if modelo.Packages.GetAt(i).Name == nombre:
            modelo.Packages.DeleteAt(i, False); modelo.Packages.Refresh(); return


def colaboracion(ea, raiz, cu, archivo, pt=PT_ANALISIS):
    """5.3.1 como G07: actor → página «boundary» → módulo api/ «boundary» → clase N «control» → clase D «entity» (y la
    pasarela Stripe), cada objeto una sola vez y los mensajes numerados de cada recorrido (k, k.1, k.2…) apilados sobre
    su enlace, con el método real. Una columna por capa; el renglón de cada objeto lo elige acomodo_colaboracion."""
    tipo, escenas = piezas(cu)
    columna = {'actor': 0, 'pagina': 1, 'api': 2, 'negocio': 3, 'datos': 5, 'externa': 5}
    entradas = {llamadas[2][1] for llamadas in escenas}   # la clase N de cada ruta
    col = {x: 4 if t == 'negocio' and x not in entradas else columna[t] for x, t in tipo.items()}
    usadas = sorted(set(col.values()))
    col = {x: usadas.index(c) for x, c in col.items()}   # sin columnas vacías (la 4 solo existe si una N llama a otra)
    # mensajes: k = número de recorrido; en cada uno, k, k.1, k.2… en el orden del código
    mensajes = []
    for k, llamadas in enumerate(escenas, 1):
        for i, (o, d, m) in enumerate(llamadas):
            mensajes.append((k, o, d, f'{m}()', f'{k}' if i == 0 else f'{k}.{i}'))
    paso = round(1.9 * pt)                     # separación de los rótulos apilados
    icono, nombre_alto = 5 * pt, round(1.8 * pt)
    fila = icono + nombre_alto + 2 * pt
    # x: ancho de cada columna (ícono o nombre) y hueco a la siguiente según el rótulo más largo que pasa entre ellas
    ncol = len(usadas)
    ancho_col = [max([icono] + [ancho_texto(x.lstrip('@'), pt) for x in tipo if col[x] == c]) for c in range(ncol)]
    hueco = [3 * pt] * (ncol - 1)
    rotulo = lambda texto, numero: ancho_texto(f'{numero}: {texto}', pt) + 3.5 * pt   # texto + flecha
    for _, o, d, texto, numero in sorted(mensajes, key=lambda m: abs(col[m[1]] - col[m[2]])):
        a, b = sorted((col[o], col[d]))
        if a == b: continue
        falta = rotulo(texto, numero) + 2 * pt - (sum(hueco[a:b]) + sum(ancho_col[a + 1:b]))
        if falta > 0:
            for j in range(a, b): hueco[j] += falta / (b - a)
    xs, x = [], 0
    for c in range(ncol):
        xs.append(x + ancho_col[c] / 2)
        if c < ncol - 1: x += ancho_col[c] + hueco[c]
    centro, rects = acomodo_colaboracion(cu, tipo, col, xs, mensajes, pt, fila, paso, icono, nombre_alto, rotulo)
    izquierda, arriba = min(r[0] for r in rects), min(r[1] for r in rects)
    centro = {x_: (cx - izquierda + 2 * pt, cy - arriba + 2 * pt) for x_, (cx, cy) in centro.items()}
    ancho = max(r[2] for r in rects) - izquierda + 4 * pt
    alto = max(r[3] for r in rects) - arriba + 4 * pt

    nombre = f'{cu}. {C.CU[cu]}'
    d = ea.diagrama(raiz, nombre, 'Collaboration')
    d.StyleEx = 'SuppressBrackets=1;'; d.Update()
    objetos = {}
    for x_, t in tipo.items():
        if t == 'actor': e = ea.elemento(raiz, x_[1:], 'Actor')
        else: e = ea.elemento(raiz, x_, 'Object', {'negocio': 'control', 'datos': 'entity'}.get(t, 'boundary'))
        objetos[x_] = e
        cx, cy = centro[x_]
        w, h = (round(0.75 * icono), round(1.3 * icono)) if t == 'actor' else (icono, icono)
        ea.poner(d, e, round(cx - w / 2), round(cy - h / 2), w, h)
        con_letra(ea, d, e, pt)
    enlaces, apilado = {}, {}
    for n, (k, o, d_, texto, numero) in enumerate(mensajes, 1):
        par = frozenset((o, d_))
        if par not in enlaces: enlaces[par] = ea.conector(objetos[o], objetos[d_], 'Association')
        c = apilado.get(par, 0); apilado[par] = c + 1
        mensaje_com(ea, d, enlaces[par], objetos[o], objetos[d_], texto, numero, n, c, paso, COLORES_COM[(k - 1) % 4])
    # EA recorta la imagen a los objetos y no cuenta los rótulos: dos marcas invisibles en las esquinas los mantienen dentro
    for x_, y_ in ((pt, pt), (ancho - 2 * pt, alto - 2 * pt)):
        marca = ea.elemento(raiz, '', 'Boundary')
        ea.poner(d, marca, round(x_), round(y_), 10, 10)
        ea.r.Execute(f"UPDATE t_diagramobjects SET ObjectStyle='BCol=16777215;LCol=16777215;LWth=0;' "
                     f"WHERE Diagram_ID={d.DiagramID} AND Object_ID={marca.ElementID}")
    ea.exportar(d, archivo)
    return ancho, alto


def _choca(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _corta(p, q, r):
    """¿El segmento p-q pasa por el rectángulo r (x0, y0, x1, y1)? (Liang-Barsky)"""
    t0, t1, dx, dy = 0.0, 1.0, q[0] - p[0], q[1] - p[1]
    for a, b in ((-dx, p[0] - r[0]), (dx, r[2] - p[0]), (-dy, p[1] - r[1]), (dy, r[3] - p[1])):
        if a == 0:
            if b < 0: return False
        else:
            s = b / a
            if a < 0: t0 = max(t0, s)
            else: t1 = min(t1, s)
            if t0 > t1: return False
    return True


def _cruzan(a, b, c, d):
    giro = lambda p, q, r: (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return giro(a, b, c) * giro(a, b, d) < 0 and giro(c, d, a) * giro(c, d, b) < 0


def acomodo_colaboracion(cu, tipo, col, xs, mensajes, pt, fila, paso, icono, nombre_alto, rotulo):
    """Renglón de cada objeto (la columna es la de su capa). Búsqueda local desde una banda por recorrido y desde 15
    arranques al azar (semilla fija): sin rótulos encimados, sin rótulos sobre objetos ni líneas, sin enlaces que pasen
    por un objeto, con pocos cruces, con los enlaces de varios mensajes horizontales y lo más bajo posible. EA pone cada
    rótulo centrado en el punto medio de su enlace, apilados hacia arriba desde 18 unidades.
    Devuelve ({objeto: centro}, [rectángulos de objetos y rótulos])."""
    import random
    objetos = list(tipo)
    ancho = {x: max(icono, ancho_texto(x.lstrip('@'), pt)) for x in objetos}
    extremos, rotulos, pila = {}, [], {}
    for _, o, d, texto, numero in mensajes:
        par = frozenset((o, d)); extremos.setdefault(par, (o, d))
        rotulos.append((par, pila.get(par, 0), rotulo(texto, numero))); pila[par] = pila.get(par, 0) + 1
    alto_rotulo = 1.7 * pt
    renglon = {}   # punto de partida: cada recorrido en su banda, debajo de los anteriores
    for k in sorted({m[0] for m in mensajes}):
        base = max(renglon.values()) + 1 if renglon else 0
        for _, o, d, _, _ in (m for m in mensajes if m[0] == k):
            for x in (o, d):
                if x in renglon: continue
                r = base
                while any(col[y] == col[x] and renglon[y] == r for y in renglon): r += 1
                renglon[x] = r
    medio = {x: (0.65 if tipo[x] == 'actor' else 0.5) * icono for x in objetos}   # medio alto de la figura

    def geometria(ren):
        c = {x: (xs[col[x]], ren[x] * fila) for x in objetos}
        cajas = {x: (cx - ancho[x] / 2, cy - medio[x], cx + ancho[x] / 2, cy + medio[x] + nombre_alto) for x, (cx, cy) in c.items()}
        rots = []
        for par, s, w in rotulos:
            a, b = extremos[par]
            mx, my = (c[a][0] + c[b][0]) / 2, (c[a][1] + c[b][1]) / 2 - 18 - paso * s
            rots.append((par, (mx - w / 2, my - alto_rotulo / 2, mx + w / 2, my + alto_rotulo / 2)))
        return c, cajas, rots

    def costo(ren):
        c, cajas, rots = geometria(ren)
        k = 0
        segs = {par: (c[a], c[b]) for par, (a, b) in extremos.items()}
        for i, (par, r) in enumerate(rots):
            k += 100 * sum(1 for q, s in rots[i + 1:] if q != par and _choca(r, s))
            k += 100 * sum(1 for x, caja in cajas.items() if _choca(r, caja))
            k += 20 * sum(1 for q, (p1, p2) in segs.items() if q != par and _corta(p1, p2, r))
        pares = list(segs.items())
        for i, (par, (p1, p2)) in enumerate(pares):
            k += 100 * sum(1 for x, (x0, y0, x1, y1) in cajas.items() if x not in par and _corta(p1, p2, (x0 + 2, y0 + 2, x1 - 2, y1 - 2)))
            k += 10 * sum(1 for q, (p3, p4) in pares[i + 1:] if not (q & par) and _cruzan(p1, p2, p3, p4))
        # en un enlace diagonal EA monta la flecha de cada mensaje sobre su texto: cuantos más mensajes, más horizontal
        diagonal = sum((10 * (pila[par] - 1) + 2) * abs(ren[a] - ren[b]) for par, (a, b) in extremos.items())
        return k * 1000 + diagonal + 3 * (max(ren.values()) - min(ren.values()))   # sin choques, recto y bajo

    def mover(ren, x, r):
        """ren con x en el renglón r (si estaba ocupado en su columna, el otro pasa al renglón de x)."""
        ren = dict(ren)
        otro = next((y for y in objetos if y != x and col[y] == col[x] and ren[y] == r), None)
        if otro: ren[otro] = ren[x]
        ren[x] = r
        return ren

    def escalar(ren):
        """Búsqueda local: aplica el mejor cambio de renglón de un objeto mientras alguno mejore."""
        actual = costo(ren)
        while True:
            c, x, r = min((costo(mover(ren, x, r)), x, r) for x in objetos for r in range(alto_max) if r != ren[x])
            if c >= actual: return actual, ren
            actual, ren = c, mover(ren, x, r)

    rng = random.Random(cu)
    alto_max = max(renglon.values()) + 3
    inicios = [renglon]
    for _ in range(15):   # arranques al azar (semilla fija: el acomodo no cambia entre corridas)
        ren = {}
        for c in set(col.values()):
            xs_ = [x for x in objetos if col[x] == c]
            ren.update(zip(xs_, rng.sample(range(alto_max), len(xs_))))
        inicios.append(ren)
    mejor = min((escalar(ren) for ren in inicios), key=lambda a: a[0])
    c, cajas, rots = geometria(mejor[1])
    if mejor[0] >= 20000: print(f'     aviso {cu}: el acomodo de colaboración conserva choques (costo {mejor[0] // 1000})')
    return c, list(cajas.values()) + [r for _, r in rots]


def mensaje_com(ea, d, enlace, a, b, texto, numero, n, apilado, paso, color):
    """ea_base.mensaje_com con la separación de la pila proporcional a la letra."""
    c = ea.mensaje_com(d, enlace, a, b, texto, numero, n, 0, color)
    sy = 18 + paso * apilado
    ea.r.Execute(f"UPDATE t_connector SET PDATA5='SX=-15;SY={sy};EX=15;EY={sy};EDGE=2;' WHERE Connector_ID={c.ConnectorID}")


def clases_analisis(ea, raiz, cu, archivo, pt=PT_ANALISIS):
    """5.3.2: clases del CU en sus 3 capas con los métodos que usan sus recorridos, como G07: dependencias sin rótulo,
    parámetros solo con su nombre y sin tipo de retorno. Las páginas y las tablas («model») van solo con su nombre: las
    columnas de cada tabla están en 7.1–7.3. Toda clase se une a otra; la generación falla si alguna queda suelta."""
    php, funciones = codigo.clases_php(), codigo.funciones_api()
    tipo, escenas = piezas(cu)
    metodos, deps = {}, []
    for llamadas in escenas:
        for o, d, m in llamadas:
            if tipo[d] in ('actor', 'externa'): continue   # el actor y el SDK de Stripe no son clases del sistema
            ms = metodos.setdefault(d, [])
            if tipo[d] != 'pagina' and m not in ms: ms.append(m)
            if tipo[o] != 'actor' and (o, d) not in deps: deps.append((o, d))
            if tipo[d] == 'datos':
                for mod in codigo.modelos(d, m):
                    tipo[mod] = 'model'; metodos.setdefault(mod, [])
                    if (d, mod) not in deps: deps.append((d, mod))
    sueltas = [x for x in metodos if not any(x in par for par in deps)]
    assert not sueltas, f'{cu}: clases sin relación en 5.3.2: {sueltas}'
    llega = {x for x in metodos if tipo[x] in ('datos', 'model')}
    for _ in metodos: llega |= {a for a, b in deps if b in llega}
    assert all(x in llega for x in metodos), f'{cu}: clases que no llegan a la capa de datos: {set(metodos) - llega}'

    def firma(x, m):
        """(visibilidad, [(parámetro, tipo)], retorno) del método real."""
        if tipo[x] == 'api':
            f = next(f for f in funciones.values() if f'api/{f["modulo"]}.js' == x and f['nombre'] == m)
            return 'Public', [(p, '') for p in f['params']], ''
        info = php[x]['metodos'][m]
        ps = [codigo._param(p).partition(': ') for p in info['params'].split(',') if p.strip()]
        vis = {'+': 'Public', '-': 'Private', '#': 'Protected'}[info['vis']]
        return vis, [(n, t) for n, _, t in ps], retorno(x, m)

    capa = {'pagina': 'Presentacion', 'api': 'Presentacion', 'negocio': 'Negocio', 'datos': 'Datos', 'model': 'Datos'}
    estereotipo = {'pagina': 'client page', 'api': 'module', 'negocio': 'negocio', 'datos': 'datos', 'model': 'model'}
    pkg = ea.paquete(raiz, f'{cu} Clases')
    paquetes = {c: ea.paquete(pkg, n) for c, n in CAPAS.items()}
    el, medida = {}, {}
    for x, ms in metodos.items():
        e = ea.elemento(paquetes[capa[tipo[x]]], x, 'Class', estereotipo[tipo[x]])
        textos = []
        for i, m in enumerate(ms):
            vis, ps, ret = firma(x, m)
            op = e.Methods.AddNew(m, ret); op.Visibility = vis; op.Pos = i; op.Update()
            for j, (pn, pt_) in enumerate(ps):
                p = op.Parameters.AddNew(pn, pt_); p.Position = j; p.Update()
            textos.append(f'{m}({", ".join(pn for pn, _ in ps)})')
        e.Update(); el[x] = e
        w = max([ancho_texto(x, pt, True) + (2.5 * pt if tipo[x] == 'pagina' else 0),   # el ícono de client page
                 ancho_texto(f'«{estereotipo[tipo[x]]}»', pt) + 2 * pt]
                + [ancho_texto(t, pt) + 3 * pt for t in textos]) + 2 * pt
        medida[x] = (round(w), round(4 * pt + (1.65 * pt * len(textos) + 1.2 * pt if textos else 0)))
    for a, b in deps: ea.conector(el[a], el[b], 'Dependency')   # sin rótulo, como G07
    # filas de arriba abajo; en cada una, las cajas cerca del promedio de las que se unen con ellas
    entradas = {llamadas[2][1] for llamadas in escenas}
    capa_fila = ['Presentacion', 'Presentacion', 'Negocio', 'Negocio', 'Datos', 'Datos']
    vecinos = {x: [b if a == x else a for a, b in deps if x in (a, b)] for x in metodos}
    margen, sep = 2 * pt, 2.5 * pt

    def acomodar(ancho_max, juntas, zigzag):
        """Filas de hasta ancho_max (una fila más ancha se parte en dos de la misma capa); en cada fila, las cajas cerca
        del promedio de las que se unen con ellas. juntas: las N auxiliares en la fila de las N de las rutas. zigzag:
        la fila partida se reparte alternando cajas, así las de abajo quedan entre las de arriba.
        (x, y, marcos de capa, ancho, alto, líneas que pasan por encima de una caja)."""
        filas = [[x for x in metodos if tipo[x] == 'pagina'], [x for x in metodos if tipo[x] == 'api'],
                 [x for x in metodos if x in entradas or (juntas and tipo[x] == 'negocio')],
                 [x for x in metodos if tipo[x] == 'negocio' and x not in entradas and not juntas],
                 [x for x in metodos if tipo[x] == 'datos'], [x for x in metodos if tipo[x] == 'model']]
        xi = {}
        centro = lambda x: xi[x] + medida[x][0] / 2

        def baricentro(partidas):
            for _, f in partidas:
                p = 0
                for x in f: xi[x] = p; p += medida[x][0] + sep
            for vuelta in range(8):
                for _, f in (partidas if vuelta % 2 == 0 else partidas[::-1]):
                    quiere = {x: sum(map(centro, vecinos[x])) / len(vecinos[x]) for x in f}
                    f.sort(key=lambda x: quiere[x])
                    p = -1e9
                    for x in f: xi[x] = max(quiere[x] - medida[x][0] / 2, p); p = xi[x] + medida[x][0] + sep
                    corrida = sum(centro(x) - quiere[x] for x in f) / len(f)
                    for x in f: xi[x] -= corrida

        enteras = [(c, f) for c, f in zip(capa_fila, filas) if f]
        baricentro(enteras)   # el orden de cada fila entera decide dónde se parte
        partidas = []
        for c, f in enteras:
            trozos, actual, usado = [], [], 0
            for x in f:
                if actual and usado + medida[x][0] > ancho_max: trozos.append(actual); actual, usado = [], 0
                actual.append(x); usado += medida[x][0] + sep
            trozos.append(actual)
            if zigzag: trozos = [f[i::len(trozos)] for i in range(len(trozos))]
            partidas += [(c, trozo) for trozo in trozos]
        baricentro(partidas)
        izquierda = min(xi.values())
        for x in xi: xi[x] += 2 * margen - izquierda
        derecha = max(xi[x] + medida[x][0] for x in xi) + margen
        ys, y, marcos, anterior = {}, 3 * pt, {}, None   # marcos de capa detrás de las clases
        for c, f in partidas:
            if c != anterior:
                if anterior: y += 3 * pt
                marcos[c] = [y, 0]; y += 2.5 * pt; anterior = c
            alto = max(medida[x][1] for x in f)
            for x in f: ys[x] = y + (alto - medida[x][1]) / 2
            y += alto + 3.5 * pt
            marcos[c][1] = y - 1.5 * pt
        caja = {x: (xi[x] + 2, ys[x] + 2, xi[x] + medida[x][0] - 2, ys[x] + medida[x][1] - 2) for x in xi}
        centro = {x: ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2) for x, r in caja.items()}
        encima = sum(1 for a, b in deps for x, r in caja.items() if x not in (a, b) and _corta(centro[a], centro[b], r))
        return xi, ys, marcos, derecha + margen, y, encima

    # sin líneas sobre cajas y, entre esos acomodos, el que deja más grande la letra impresa
    minimo = max(w for w, _ in medida.values())
    xi, ys, marcos, ancho, alto, encima = min(
        (acomodar(minimo + i * 50, juntas, zigzag) for i in range(40) for juntas in (False, True) for zigzag in (False, True)),
        key=lambda a: (a[5], -impresa(a[3], a[4])))
    if encima: print(f'     aviso {cu}: {encima} dependencias pasan sobre otra clase')
    derecha = ancho - margen
    nombre = f'{cu}. {C.CU[cu]}'
    d = ea.diagrama(pkg, nombre, 'Logical')
    d.ExtendedStyle = (d.ExtendedStyle or '').rstrip(';') + ';OpParams=3;'   # parámetros solo con su nombre (G07)
    d.StyleEx = 'ShowOpRetType=0;'   # sin tipo de retorno (G07)
    d.HighlightImports = False   # sin «Presentación::» delante del nombre
    d.Update()
    for c, (y0, y1) in marcos.items():
        e = ea.elemento(paquetes[c], f'Capa {CAPAS[c]}', 'Boundary')
        ea.poner(d, e, round(margen), round(y0), round(derecha - margen), round(y1 - y0))
        con_letra(ea, d, e, pt)
    for x, e in el.items():
        ea.poner(d, e, round(xi[x]), round(ys[x]), *medida[x])
        con_letra(ea, d, e, pt)
    ea.exportar(d, archivo)
    return ancho, alto


def solo_analisis():
    """Rehace 5.3.1 y 5.3.2 desde los recorridos del código, en un subpaquete propio de cada paquete de análisis: el
    subpaquete se rehace entero y las vistas del respaldo de Leonardo (en el paquete padre) no se tocan. Los rótulos de
    los mensajes se dibujan a PT_ANALISIS."""
    SUB = 'Un diagrama por CU (5.3)'
    def tarea():
        ea = ea_base.EA.abrir_existente()
        try:
            col, cls = paquete(ea, ea.modelo, 'Análisis de Colaboración'), paquete(ea, ea.modelo, 'Análisis de clases')
            borrar_paquete(col, SUB); borrar_paquete(cls, SUB)
            col, cls = ea.paquete(col, SUB), ea.paquete(cls, SUB)
            for cu in C.CU:
                for archivo, dibujar, p in ((f'com-{cu.lower()}.png', colaboracion, col), (f'cls-{cu.lower()}.png', clases_analisis, cls)):
                    w, h = dibujar(ea, p, cu, archivo)
                    print(f'     {archivo}: {w:.0f} × {h:.0f}, impresa a {impresa(w, h):.1f} pt')
        finally: ea.cerrar()
    con_letra_rotulos(PT_ANALISIS, tarea)


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


def recorridos(cu):
    """RECORRIDOS[cu] comprobados contra el código, con sus extremos resueltos: [dict(ruta, actor, pagina, api ('pagos.js'),
    fn (función de api/*.js), n y met (clase N y método de la ruta), pasos [(origen, destino, método)])]. Es la fuente
    común de 5.3.1 (colaboración), 5.3.2 (clases) y 7.4 (secuencia): las tres vistas muestran lo mismo."""
    rutas, funciones, usos = codigo.rutas_api(), codigo.funciones_api(), codigo.usos_api()
    clases, _, errores = codigo.cadena(cu)
    if errores: raise ValueError('; '.join(errores))
    if cu == 'CU5': clases.update(codigo.cadena('CU4')[0])   # «Perdido + motivo» se marca en PEmbudo.jsx (pantalla de CU4)
    res = []
    for ruta, pasos in RECORRIDOS[cu]:
        r = next((r for r in rutas if f'{r["verbo"]} {r["ruta"]}' == ruta), None)
        if not r: raise ValueError(f'{cu}: la ruta {ruta} ya no existe en api.php')
        n, met = r['controlador'], r['metodo']
        reales = codigo.llamadas_en_orden(n, met)
        pasos = [(n if o == 'N' else o, d, m) for o, d, m in pasos]
        i = 0
        for paso in pasos:   # subsecuencia: cada mensaje existe y después del anterior
            while i < len(reales) and reales[i] != paso: i += 1
            if i == len(reales): raise ValueError(f'{cu} {ruta}: {paso[0]} ya no llama a {paso[1]}::{paso[2]}() en ese orden')
            i += 1
        fn = next((k for k, f in funciones.items() if f['verbo'] == r['verbo'] and f['ruta'] == codigo.norm(r['ruta'])), None)
        if not fn: raise ValueError(f'{cu}: ninguna función de api/*.js llama a {ruta}')
        paginas = [a.rsplit('/', 1)[-1] for a, fns in usos.items() if fn in fns and a.rsplit('/', 1)[-1] in clases]
        if r['ruta'] == '/login': paginas = ['PLogin.jsx']
        if not paginas: raise ValueError(f'{cu}: ninguna página del CU llama a {fn}')
        res.append(dict(ruta=ruta, actor=ACTOR_RUTA.get((cu, ruta), C.DETALLE[cu]['iniciador']),
                        pagina=PAGINA_PREFERIDA.get(cu) if PAGINA_PREFERIDA.get(cu) in paginas else paginas[0],
                        api=f'{fn.split(".")[0]}.js', fn=funciones[fn]['nombre'], params=funciones[fn]['params'],
                        n=n, met=met, pasos=pasos))
    return res


def retorno(c, m):
    """Tipo de retorno declarado en PHP (sin espacio de nombres) o 'resultado'."""
    t = re.search(r'\):\s*([?\w\\|]+)$', codigo.clases_php()[c]['metodos'][m]['firma'])
    return t.group(1).rsplit('\\', 1)[-1] if t else 'resultado'


def mensajes_secuencia(cu):
    """[(guarda, [(origen, destino, rótulo, 'call'|'return'|'self')])] por recorrido; la guarda del marco opt es la
    función de api/*.js que lo dispara. Los extremos son
    nombres de línea de vida: '@Actor', 'Pantalla', 'HTTP', 'Negocio', 'Datos', 'Stripe'."""
    php = codigo.clases_php()
    capa = lambda c: 'Stripe' if c == 'StripeClient' else 'Negocio' if php[c]['estereotipo'] == 'negocio' else 'Datos'
    escenas = []
    for r in recorridos(cu):
        actor = '@' + r['actor']
        msj = [(actor, 'Pantalla', f'usar {r["pagina"]}', 'call'),
               ('Pantalla', 'HTTP', f'{r["api"]}::{r["fn"]}()', 'call'),
               ('HTTP', 'Negocio', f'{r["n"]}::{r["met"]}()', 'call')]
        for o, d, m in r['pasos']:
            if capa(d) == 'Negocio': msj.append(('Negocio', 'Negocio', f'{d}::{m}()', 'self'))
            elif capa(d) == 'Stripe': msj += [('Negocio', 'Stripe', f'{m}()', 'call'), ('Stripe', 'Negocio', 'Session', 'return')]
            else: msj += [('Negocio', 'Datos', f'{d}::{m}()', 'call'), ('Datos', 'Negocio', retorno(d, m), 'return')]
        msj += [('Negocio', 'HTTP', retorno(r['n'], r['met']), 'return'), ('HTTP', 'Pantalla', 'respuesta JSON', 'return'),
                ('Pantalla', actor, 'resultado mostrado', 'return')]
        escenas.append((r['fn'], msj))   # guarda del opt: la acción que dispara el recorrido
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
    if sys.argv[1:] == ['--analisis']:     # solo 5.3.1 y 5.3.2
        return solo_analisis()
    ea = ea_base.EA.abrir_existente()
    try:
        _, actores, casos = requisitos(ea, ea.modelo)
        paquetes(ea, ea.modelo, actores, casos)
    finally:
        ea.cerrar()
    print(f'Exportados {len(ea.exportados)} diagramas PNG y EMF en {ea_base.SALIDA}')
    solo_analisis()     # aparte: los rótulos de colaboración necesitan abrir EA con su letra
    solo_secuencias()   # aparte: cada letra de rótulos necesita su propia sesión de EA
    solo_despliegue()   # aparte: necesita abrir EA con la letra de rótulos a 11 pt


if __name__ == '__main__': main()
