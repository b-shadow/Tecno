"""Acomodo de una hoja del diagrama de navegación (7.5), sin EA: capas de izquierda a derecha como se recorre el
sistema (actor/menú → páginas con sus formularios debajo → server pages → tablas), con puntos de quiebre en las
columnas intermedias para que ninguna línea pase sobre una caja, y puertos elegidos para que los rótulos de las
líneas que comparten un pasillo no se encimen.

Las medidas imitan EA 15 con Calibri 10 (calibradas exportando una clase de prueba): 5,7 u. por carácter, 15 u. por
renglón. EA exporta el PNG al 200 %; impresa en 25,9 × 17 cm, la letra mide 10 pt × escala (ESCALA_MIN la acota).
"""
import math

CAR, CAR_ROT, RENGLON = 5.75, 5.2, 15          # ancho por carácter (cajas / rótulos de líneas), alto de renglón
SEP_V, MARGEN = 26, 30                          # separación vertical entre cajas; margen del diagrama
ANCHO_UTIL, ALTO_UTIL = 979, 650                # 25,9 × 17,2 cm a 96 ppp: lo que ocupa la imagen en la hoja apaisada
MARCO_W, MARCO_H = 40, 70                       # lo que suma el marco «class …» de EA alrededor del contenido
ESCALA_MIN = 0.65                               # letra impresa mínima al juntar secciones: 6,5 pt
ROT_ALTO = 30                                   # alto por rótulo de dos renglones; +14 por renglón extra
CON_ESTEREOTIPO = {'form', 'bd'}                # EA escribe «Formulario» / «database»; client/server page llevan ícono


def medir(tipo, nombre, atributos, operaciones):
    if tipo == 'actor': return 60, 95
    at = [a.split('=')[0].strip() + ' {bag}' for a in atributos.split(',') if a.strip()]
    op = [o.strip() if o.strip().endswith(')') else o.strip() + '()' for o in operaciones.split(',') if o.strip()]
    titulo = CAR * 1.04 * len(nombre) + (70 if tipo in ('cliente', 'ps', 'externo') else 40)
    cuerpo = max([CAR * len(x) + 48 for x in at + op] or [0])
    w = max(150, titulo, cuerpo)
    h = (40 if tipo in CON_ESTEREOTIPO else 29) + 5 + RENGLON * len(at) + (7 + RENGLON * len(op) if op else 0) + 10
    return int(math.ceil(w / 5) * 5), int(math.ceil(h / 5) * 5)


def partir(texto, largo=200):   # EA monta un segundo renglón sobre el estereotipo: un solo renglón
    """Rótulo largo en dos renglones, cortado en la '/' o el espacio más cercano a la mitad (EA respeta el salto)."""
    if len(texto) <= largo: return [texto]
    cortes = [i for i, ch in enumerate(texto) if ch in '/ ?&|' and 4 < i < len(texto) - 4]
    if not cortes: return [texto]
    i = min(cortes, key=lambda i: abs(i - len(texto) / 2))
    return [texto[:i].rstrip(), texto[i:].lstrip() if texto[i] == ' ' else texto[i:]]


def texto_rotulo(st, texto):
    return [f'«{st}»'] + (partir(texto) if texto else [])


def ancho_rotulo(st, texto):
    return max(CAR_ROT * len(x) for x in texto_rotulo(st, texto)) + 16


def _isotonica(deseados, altos, sep):
    """y de cada elemento (en orden) lo más cerca posible de su deseado sin encimarse (regresión isotónica, PAV)."""
    off, acc = [], 0
    for h in altos: off.append(acc); acc += h + sep
    z = [d - o for d, o in zip(deseados, off)]
    bloques = []   # [suma, cantidad]
    for v in z:
        bloques.append([v, 1])
        while len(bloques) > 1 and bloques[-2][0] / bloques[-2][1] > bloques[-1][0] / bloques[-1][1]:
            s, n = bloques.pop(); bloques[-1][0] += s; bloques[-1][1] += n
    res = []
    for s, n in bloques: res += [s / n] * n
    return [v + o for v, o in zip(res, off)]


COLUMNA = {'actor': 0, 'externo': 0, 'cliente': 1, 'form': 1, 'ps': 2, 'bd': 3}
SEP_ENLACE = 48   # hueco entre dos cajas de la misma columna unidas por una línea (cabe su rótulo)


def acomodar(paginas, enlaces):
    """La variante (tablas en una o dos subcolumnas) que deja la letra impresa más grande."""
    return max((_acomodar(paginas, enlaces, p, e) for p in (False, True) for e in (True, False)),
               key=lambda a: escala(a['ancho'], a['alto']))


def _acomodar(paginas, enlaces, partir_tablas, entrada_izquierda):
    """Columnas por tipo, como se lee un diagrama WAE: actor / externo | client pages con sus formularios debajo |
    server pages | tablas (en dos subcolumnas si no caben). paginas: {clave: (tipo, nombre, atributos, operaciones)};
    enlaces: [(a, b, estereotipo, texto)]. Devuelve dict(cajas={clave: (x, y, w, h)}, lineas=[dict(enlace, puntos,
    rotulo)], ancho, alto). Las líneas entre columnas vecinas son rectas entre puertos elegidos para que los rótulos de
    un mismo pasillo no se encimen; las de una misma columna bajan por un carril lateral."""
    tipo = {k: v[0] for k, v in paginas.items()}
    medida = {k: medir(*v) for k, v in paginas.items()}
    orden = list(paginas)
    duenio = {}
    for a, b, st, _ in enlaces:
        if st == 'contiene' and b not in duenio: duenio[b] = a
    formularios = {}
    for f in orden:
        if f in duenio: formularios.setdefault(duenio[f], []).append(f)
    col = {k: COLUMNA[tipo[k]] for k in orden}
    vecinos = {}
    for a, b, st, _ in enlaces:
        if st != 'contiene': vecinos.setdefault(a, []).append(b); vecinos.setdefault(b, []).append(a)
    # páginas que en esta hoja solo enlazan (menú de entrada, página de salida): a la izquierda, junto al actor
    for k in orden:
        if entrada_izquierda and tipo[k] == 'cliente' and k not in formularios and not any(tipo[v] == 'ps' for v in vecinos.get(k, [])):
            col[k] = 0
    # server page incluido que aquí no muestra sus tablas: en la columna de las tablas, a la derecha de quien lo incluye
    for k in orden:
        if tipo[k] == 'ps' and any(st == 'include' and b == k for a, b, st, _ in enlaces)                 and not any(st == 'access' and a == k for a, b, st, _ in enlaces):
            col[k] = 3

    # columna 1: páginas en orden de recorrido desde las entradas (actor, externo, menú), cada una con sus formularios
    paginas1 = [k for k in orden if tipo[k] == 'cliente' and col[k] == 1]
    destinos = {b for a, b, st, _ in enlaces if st == 'link' and a in paginas1}
    entrada = [k for k in paginas1 if k not in destinos] or paginas1[:1]
    distancia, cola = {k: 0 for k in (entrada or paginas1[:1])}, list(entrada or paginas1[:1])
    while cola:
        u = cola.pop(0)
        for v in vecinos.get(duenio.get(u, u), []) + [x for f in formularios.get(u, []) for x in vecinos.get(f, [])]:
            v = duenio.get(v, v)
            if tipo[v] in ('cliente', 'ps') and v not in distancia:
                distancia[v] = distancia[u] + 1; cola.append(v)
    paginas1.sort(key=lambda k: (distancia.get(k, 99), orden.index(k)))
    secuencia = [x for p in paginas1 for x in [p] + formularios.get(p, [])]
    unidas = {frozenset((a, b)) for a, b, st, _ in enlaces if st != 'contiene'}
    y = {}
    acc = MARGEN
    for i, k in enumerate(secuencia):
        if i: acc += SEP_ENLACE if frozenset((secuencia[i - 1], k)) in unidas else SEP_V
        y[k] = acc; acc += medida[k][1]
    centro = lambda k: y[k] + medida[k][1] / 2

    def colocar(ks, deseado, ordenar=True):
        if ordenar: ks = sorted(ks, key=lambda k: (deseado(k), orden.index(k)))
        ys = _isotonica([deseado(k) - medida[k][1] / 2 for k in ks], [medida[k][1] for k in ks], SEP_V)
        for k, v in zip(ks, ys): y[k] = v
        return ks

    def prom(k, cols):
        vs = [centro(v) for v in vecinos.get(k, []) if col[v] in cols and v in y]
        return sum(vs) / len(vs) if vs else None

    # columna 0, columna 2 (los incluidos debajo de quien los incluye) y columna 3
    col0 = colocar([k for k in orden if col[k] == 0], lambda k: prom(k, (1,)) or MARGEN)
    incluidos = {b for a, b, st, _ in enlaces if st == 'include'}
    incluidos = {k for k in incluidos if col[k] == 2}
    ps = colocar([k for k in orden if col[k] == 2 and k not in incluidos], lambda k: prom(k, (1,)) or MARGEN)
    inc = [k for k in orden if k in incluidos]
    if inc:   # debajo de los server pages que los incluyen, en el orden de quien los incluye
        base = max(centro(k) for k in ps) if ps else MARGEN
        quien = {k: [centro(a) for a, b, st, _ in enlaces if st == 'include' and b == k and a in ps] for k in inc}
        deseo = {k: centro(k) for k in ps}
        deseo.update({k: (sum(quien[k]) / len(quien[k]) if quien[k] else base + 100) for k in inc})
        inc.sort(key=lambda k: deseo[k])
        ps = colocar(ps + inc, lambda k: deseo[k], ordenar=False)
    tablas = [k for k in orden if col[k] == 3]
    tablas = colocar(tablas, lambda k: prom(k, (2,)) or MARGEN)
    if tablas and not ps: tablas = colocar(tablas, lambda k: prom(k, (1,)) or MARGEN)
    tramo = lambda ks: (max(y[k] + medida[k][1] for k in ks) - min(y[k] for k in ks)) if ks else 0
    alto_ref = max(tramo(secuencia), tramo(ps), tramo(col0), 560)
    sub = {k: 0 for k in tablas}
    if partir_tablas and len(tablas) > 3:
        for i, k in enumerate(tablas): sub[k] = i % 2
        for s in (0, 1): colocar([k for k in tablas if sub[k] == s], lambda k: prom(k, (2,)) or MARGEN)
    minimo = min(y.values())
    for k in y: y[k] += MARGEN - minimo

    # anchos: columnas y pasillos (cada pasillo, del ancho de su rótulo más largo)
    ancho_col = {c: max([medida[k][0] for k in orden if col[k] == c] + [0]) for c in range(4)}
    ancho_sub = [max([medida[k][0] for k in tablas if sub[k] == s] + [0]) for s in (0, 1)]
    if any(sub.values()): ancho_col[3] = ancho_sub[0] + 70 + ancho_sub[1]
    misma_col = [(i, e) for i, e in enumerate(enlaces) if e[2] != 'contiene' and col[e[0]] == col[e[1]]]
    carril_izq = [(i, e) for i, e in misma_col if col[e[0]] == 1 and not (frozenset(e[:2]) in unidas and
                  abs(secuencia.index(e[0]) - secuencia.index(e[1])) == 1)]
    carril_der = [(i, e) for i, e in misma_col if col[e[0]] == 2]
    pasillo = {c: 50 for c in range(4)}
    for a, b, st, texto in enlaces:
        if st != 'contiene' and col[a] != col[b]:
            c = min(col[a], col[b])
            pasillo[c] = max(pasillo[c], ancho_rotulo(st, texto) + 26)
    izq_carril = max([ancho_rotulo(e[2], e[3]) / 2 + 14 for _, e in carril_izq] + [0])
    der_carril = max([ancho_rotulo(e[2], e[3]) / 2 + 14 for _, e in carril_der] + [0])
    if col0: pasillo[0] = max(pasillo[0], 2 * izq_carril + 10)
    pasillo[2] = max(pasillo[2], 2 * der_carril + 10) if tablas else 2 * der_carril + 10
    x_col, x = {}, MARGEN + (0 if col0 else izq_carril * 2)
    for c in range(4):
        if c == 0 and not col0: x_col[0] = x; continue
        x_col[c] = x; x += ancho_col[c] + pasillo[c]
    cajas = {}
    for k in orden:
        w, h = medida[k]
        c = col[k]
        if c == 3 and any(sub.values()):
            x0 = x_col[3] + (0 if sub[k] == 0 else ancho_sub[0] + 70)
            base = ancho_sub[sub[k]]
            cajas[k] = (x0 + (base - w) / 2, y[k], w, h)
        else:
            cajas[k] = (x_col[c] + (ancho_col[c] - w) / 2, y[k], w, h)

    # líneas entre columnas vecinas: puertos por pasillo para que los rótulos disten ROT_ALTO
    lineas = {}
    rango = lambda k: (cajas[k][1] + 10, cajas[k][1] + cajas[k][3] - 10)
    huecos_a = []   # pasos libres en la subcolumna 0 de tablas (para llegar a la 1)
    if any(sub.values()):
        a_ord = sorted((k for k in tablas if sub[k] == 0), key=lambda k: y[k])
        bordes = [MARGEN - SEP_V] + [v for k in a_ord for v in (cajas[k][1], cajas[k][1] + cajas[k][3])] + [10 ** 5]
        huecos_a = [(bordes[i] + bordes[i + 1]) / 2 for i in range(0, len(bordes), 2)]
    por_pasillo = {}
    for i, (a, b, st, texto) in enumerate(enlaces):
        if st == 'contiene' or col[a] == col[b]: continue
        por_pasillo.setdefault(min(col[a], col[b]), []).append(i)
    destino_fijo = {}
    for i, (a, b, st, texto) in enumerate(enlaces):
        if st == 'access' and sub.get(b) == 1:
            destino_fijo[i] = min(huecos_a, key=lambda g: abs(g - (cajas[b][1] + cajas[b][3] / 2)))
    puerto = {}
    for c, idx in por_pasillo.items():
        def r(i, k):
            return (destino_fijo[i],) * 2 if k == enlaces[i][1] and i in destino_fijo else rango(k)
        deseo = lambda i: (sum(r(i, enlaces[i][0])) / 2 + sum(r(i, enlaces[i][1])) / 2) / 2
        idx.sort(key=deseo)
        altos = [14 * (len(texto_rotulo(*enlaces[i][2:])) - 2) for i in idx]
        slots = _isotonica([deseo(i) - h / 2 for i, h in zip(idx, altos)], altos, ROT_ALTO)
        slots = [s + h / 2 for s, h in zip(slots, altos)]
        for i, s in zip(idx, slots):
            a, b = enlaces[i][:2]
            ra, rb = r(i, a), r(i, b)
            ya = min(max(s, ra[0]), ra[1]); yb = min(max(2 * s - ya, rb[0]), rb[1]); ya = min(max(2 * s - yb, ra[0]), ra[1])
            puerto[i] = (ya, yb)
    for c, idx in por_pasillo.items():
        for i in idx:
            a, b, st, texto = enlaces[i]
            xa, _, wa, _ = cajas[a]; xb, _, wb, _ = cajas[b]
            ya, yb = puerto[i]
            der = col[b] > col[a]
            sa, sb = (xa + wa, xb) if der else (xa, xb + wb)
            if i in destino_fijo:   # a la subcolumna 1: pasa por el hueco de la 0
                xa0 = x_col[3] - 12; xa1 = x_col[3] + ancho_sub[0] + 12
                pts = [(sa, ya), (xa0, yb), (xa1, yb), (sb, cajas[b][1] + cajas[b][3] / 2)]
                lineas[i] = dict(enlace=enlaces[i], puntos=pts, rotulo=((sa + xa0) / 2, (ya + yb) / 2), tramo=0)
            else:
                lineas[i] = dict(enlace=enlaces[i], puntos=[(sa, ya), (sb, yb)], rotulo=((sa + sb) / 2, (ya + yb) / 2), tramo=0)
    # misma columna: consecutivas = recta vertical; las demás, por un carril (izquierda en páginas, derecha en server pages)
    for j, (i, (a, b, st, texto)) in enumerate(misma_col):
        xa, ya_, wa, ha = cajas[a]; xb, yb_, wb, hb = cajas[b]
        if (i, enlaces[i]) not in carril_izq and (i, enlaces[i]) not in carril_der:
            xm = max(xa, xb) + min(wa, wb) / 2 + (12 if st == 'build' else -12 if any(
                l != i and set(enlaces[l][:2]) == {a, b} for l, _ in misma_col) else 0)
            p1, p2 = (ya_ + ha, yb_) if yb_ > ya_ else (ya_, yb_ + hb)
            lineas[i] = dict(enlace=enlaces[i], puntos=[(xm, p1), (xm, p2)], rotulo=(xm, (p1 + p2) / 2), tramo=0)
            continue
        if col[a] == 1:
            carril = x_col[1] - izq_carril - 8 * (j % 3)
            sa, sb = xa, xb
        else:
            carril = x_col[2] + ancho_col[2] + der_carril + 8 * (j % 3)
            sa, sb = xa + wa, xb + wb
        y1, y2 = ya_ + ha / 2 + 8, yb_ + hb / 2 - 8
        pts = [(sa, y1), (carril, y1), (carril, y2), (sb, y2)]
        lineas[i] = dict(enlace=enlaces[i], puntos=pts, rotulo=(carril, (y1 + y2) / 2), tramo=1)
    # página ◇— formulario
    for i, (a, b, st, _) in enumerate(enlaces):
        if st != 'contiene': continue
        xp, yp, wp, hp = cajas[a]; xf, yf, wf, hf = cajas[b]
        if secuencia.index(b) == secuencia.index(a) + 1:
            xm = max(xp, xf) + min(wp, wf) / 2
            pts = [(xm, yf), (xm, yp + hp)]
        else:
            n = formularios[a].index(b)
            carril = min(xp, xf) - 8 - 7 * n
            pts = [(xf, yf + 16), (carril, yf + 16), (carril, yp + hp - 10 - 6 * n), (xp, yp + hp - 10 - 6 * n)]
        lineas[i] = dict(enlace=enlaces[i], puntos=pts, rotulo=None, tramo=0)
    xs = [p[0] for l in lineas.values() for p in l['puntos']] + [x + w for x, _, w, _ in cajas.values()]
    ys = [p[1] for l in lineas.values() for p in l['puntos']] + [y + h for _, y, _, h in cajas.values()]
    izq = min([p[0] for l in lineas.values() for p in l['puntos']] + [x for x, _, _, _ in cajas.values()])
    if izq < MARGEN:   # un carril quedó a la izquierda del margen: correr todo
        dx = MARGEN - izq
        cajas = {k: (x + dx, yy, w, h) for k, (x, yy, w, h) in cajas.items()}
        for l in lineas.values():
            l['puntos'] = [(px + dx, py) for px, py in l['puntos']]
            if l['rotulo']: l['rotulo'] = (l['rotulo'][0] + dx, l['rotulo'][1])
        xs = [v + dx for v in xs]
    return dict(cajas=cajas, lineas=[lineas[i] for i in sorted(lineas)], ancho=max(xs) + MARGEN, alto=max(ys) + MARGEN)


def escala(ancho, alto):
    """Factor con el que la hoja impresa reproduce el diagrama (letra impresa = 10 pt × escala)."""
    return min(ANCHO_UTIL / (ancho + MARCO_W), ALTO_UTIL / (alto + MARCO_H))


def paginar(paginas, enlaces, secciones):
    """Agrupa secciones consecutivas en hojas mientras la letra impresa no baje de ESCALA_MIN. Cada hoja dibuja solo
    las relaciones de sus secciones. Devuelve [(títulos, claves, relaciones, acomodo)]."""
    def armar(claves, rel):
        return acomodar({k: paginas[k] for k in claves}, rel)
    hojas, actual, rel, titulos = [], [], [], []
    for titulo, claves, aristas in secciones:
        prueba = actual + [k for k in claves if k not in actual]
        prueba_rel = rel + [e for e in aristas if e not in rel]
        if actual:
            ac = armar(prueba, prueba_rel)
            if escala(ac['ancho'], ac['alto']) >= ESCALA_MIN:
                actual, rel, titulos = prueba, prueba_rel, titulos + [titulo]; continue
            hojas.append((titulos, actual, rel, armar(actual, rel)))
        actual, rel, titulos = list(claves), list(aristas), [titulo]
    if actual: hojas.append((titulos, actual, rel, armar(actual, rel)))
    return hojas


def vista_previa(ac, paginas, ruta):
    """PNG aproximado (PIL) para revisar el acomodo sin abrir EA."""
    from PIL import Image, ImageDraw, ImageFont
    k = 2
    im = Image.new('RGB', (int(ac['ancho'] * k), int(ac['alto'] * k)), 'white'); dr = ImageDraw.Draw(im)
    try: fuente = ImageFont.truetype('calibri.ttf', 20); chica = ImageFont.truetype('calibri.ttf', 17)
    except OSError: fuente = chica = ImageFont.load_default()
    color = {'cliente': '#f6e7d8', 'form': '#fff4e0', 'ps': '#f1e2cf', 'bd': '#d9f2e6', 'actor': 'white', 'externo': '#eeeeee'}
    for clave, (x, y, w, h) in ac['cajas'].items():
        t, nombre, at, op = paginas[clave]
        dr.rectangle([x * k, y * k, (x + w) * k, (y + h) * k], fill=color[t], outline='#555')
        dr.text((x * k + 8, y * k + 6), nombre, fill='black', font=fuente)
        yy = y * k + 40
        for a in [s.strip() for s in (at + ',' + op).split(',') if s.strip()]:
            dr.text((x * k + 20, yy), a, fill='#7a3d18', font=chica); yy += RENGLON * k
    for l in ac['lineas']:
        pts = [(px * k, py * k) for px, py in l['puntos']]
        dr.line(pts, fill='#666', width=2)
        if l['rotulo']:
            a, b, st, texto = l['enlace']
            rx, ry = l['rotulo']
            lineas_r = texto_rotulo(st, texto)
            for j, s in enumerate(lineas_r):
                w = dr.textlength(s, font=chica)
                dr.text((rx * k - w / 2, ry * k - 8.5 * len(lineas_r) + 17 * j), s, fill='#204070', font=chica)
    im.save(ruta)
