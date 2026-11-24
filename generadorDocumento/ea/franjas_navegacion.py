"""Un diagrama de navegación grande por actor (como G07), pensado para cortarse en franjas apaisadas sin perder la
continuidad: cada elemento aparece una sola vez, en el orden de implementación (login → menú → CU1 … CU8), y las
relaciones pasan de una franja a la siguiente.

Columnas: páginas (actor, client pages con sus formularios debajo, página externa) | server pages | tablas.
Cada relación es ortogonal: sale horizontal del extremo que lleva el rótulo («estereotipo» arriba de la línea, texto
debajo, pegados a la caja), baja o sube por el carril vertical de la caja del otro extremo y entra horizontal. Todas
las relaciones que llegan a una misma caja comparten su carril (como un bus), así que ningún carril pisa otro, ninguna
línea cruza una caja y los rótulos no se enciman. Los cortes de las franjas caen en huecos sin cajas ni rótulos.
"""
import math

CAR, RENGLON = 5.75, 15   # medidas de EA 15 con Calibri 10: ancho por carácter y alto de renglón de una caja
PAGINA = ('actor', 'cliente', 'form', 'externo')   # tipos de la columna de páginas
CON_ESTEREOTIPO = {'form', 'bd'}   # EA escribe «Formulario» / «database»; client page y server page llevan ícono

MARGEN = 40
SEP_CAJAS = 30          # entre cajas de una misma columna
SEP_BANDA = 60          # entre secciones (hueco seguro para cortar)
PASO_CARRIL = 7         # distancia entre carriles verticales
ALTO_FILA = 14          # alto de un renglón de rótulo (letra 9 de EA)
LARGO_NOMBRE = 20       # caracteres por renglón del texto de una relación
HUECO_AGREGACION = 22   # franja junto a la izquierda de las páginas para las agregaciones con su formulario


def medir(tipo, nombre, atributos, operaciones):
    if tipo == 'actor': return 60, 95
    at = [a.split('=')[0].strip() + ' {bag}' for a in atributos.split(',') if a.strip()]
    op = [o.strip() if o.strip().endswith(')') else o.strip() + '()' for o in operaciones.split(',') if o.strip()]
    titulo = CAR * 1.04 * len(nombre) + (70 if tipo in ('cliente', 'ps', 'externo') else 40)
    cuerpo = max([CAR * len(x) + 48 for x in at + op] or [0])
    w = max(150, titulo, cuerpo)
    h = (40 if tipo in CON_ESTEREOTIPO else 29) + 5 + RENGLON * len(at) + (7 + RENGLON * len(op) if op else 0) + 10
    return int(math.ceil(w / 5) * 5), int(math.ceil(h / 5) * 5)


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


def renglones(texto):
    """Texto de la relación partido en renglones de hasta LARGO_NOMBRE (en '/', '?', '&', ' ')."""
    if not texto: return []
    res, resto = [], texto
    while len(resto) > LARGO_NOMBRE:
        cortes = [i for i, ch in enumerate(resto[:LARGO_NOMBRE + 1]) if ch in '/?& ' and i > 3]
        i = max(cortes) if cortes else LARGO_NOMBRE
        res.append(resto[:i].rstrip()); resto = resto[i:].lstrip() if resto[i:i + 1] == ' ' else resto[i:]
    return res + [resto]


def ancho_texto(s):
    return 6.1 * len(s) + 10   # rótulos de EA a 9 pt: algo más anchos que el texto de las cajas


def armar(paginas, enlaces, secciones, cortes_y=()):
    """cortes_y: alturas fijas donde se parte en franjas; ninguna caja queda atravesada (baja a la franja siguiente)."""
    tipo = {k: v[0] for k, v in paginas.items()}
    col = {k: {'ps': 'B', 'bd': 'C'}.get(t, 'A') for k, t in tipo.items()}
    duenio = {}
    for a, b, st, _ in enlaces:
        if st == 'contiene' and b not in duenio: duenio[b] = a
    formularios = {}
    for _, claves, _ in secciones:
        for k in claves:
            if k in duenio and k not in formularios.setdefault(duenio[k], []): formularios[duenio[k]].append(k)

    # ---------------------------------------------------------------- 1. de qué lado va cada extremo y cuál lleva rótulo
    # lado: ('der' / 'izq'); el extremo con rótulo sale en su propio puerto, el otro entra al bus de su caja
    def lados(a, b):
        ca, cb = col[a], col[b]
        if ca == cb == 'A': return 'izq', 'izq'
        if ca == cb == 'B': return 'der', 'der'
        if ca < cb: return 'der', 'izq'
        return 'izq', 'der'
    extremos = {}   # (clave, lado) -> [(i, 'a' | 'b', con_rotulo)]
    rotulado = {}
    for i, (a, b, st, texto) in enumerate(enlaces):
        if st == 'contiene': continue
        la, lb = lados(a, b)
        if col[a] == 'A' and col[b] == 'B': r = 'a'          # link / submit: rótulo junto a la página
        elif col[a] == 'B' and col[b] == 'A': r = 'b'        # build: rótulo junto a la página que arma
        elif col[a] == 'B': r = 'a'                          # access / include: junto al server page
        else:                                                # entre páginas: en la punta con menos rótulos
            na = sum(1 for x in extremos.get((a, la), []) if x[2])
            nb = sum(1 for x in extremos.get((b, lb), []) if x[2])
            r = 'a' if na <= nb else 'b'
        rotulado[i] = r
        extremos.setdefault((a, la), []).append((i, 'a', r == 'a'))
        extremos.setdefault((b, lb), []).append((i, 'b', r == 'b'))

    def filas_de(i):
        a, b, _, texto = enlaces[i]
        return [texto] if tipo[a] in PAGINA and tipo[b] in PAGINA else renglones(texto)   # pasillo izquierdo: un renglón

    def alto_rotulo(i):
        return ALTO_FILA * (1 + max(1, len(filas_de(i)))) + 10

    # ---------------------------------------------------------------- 2. tamaños: contenido o los puertos que necesita
    medida = {}
    for k, v in paginas.items():
        w, h = medir(*v)
        for lado in ('izq', 'der'):
            xs = extremos.get((k, lado), [])
            necesita = sum(alto_rotulo(i) for i, _, rot in xs if rot) + (24 if any(not rot for *_, rot in xs) else 0) + 24
            h = max(h, necesita)
        medida[k] = (w, h)

    # ---------------------------------------------------------------- 3. bandas: cada elemento en la primera sección donde actúa
    def actua(k, rel):
        return any(k in (a, b) and (st in ('submit', 'contiene', 'access', 'include') or
                                     (st in ('link', 'build') and 'ps' in (tipo[a], tipo[b]))) for a, b, st, _ in rel)
    casa = {}
    for n, (_, claves, rel) in enumerate(secciones):
        for k in claves:
            if k not in casa and (actua(k, rel) or tipo[k] in ('actor', 'externo')): casa[k] = n
    for n, (_, claves, _) in enumerate(secciones):
        for k in claves: casa.setdefault(k, n)
    for f, p in duenio.items(): casa[f] = casa[p]
    orden = [k for _, claves, _ in secciones for k in claves]
    orden = list(dict.fromkeys(orden))
    y, cima = {}, MARGEN
    vecinos = {}
    for a, b, st, _ in enlaces:
        vecinos.setdefault(a, []).append(b); vecinos.setdefault(b, []).append(a)
    centro = lambda k: y[k] + medida[k][1] / 2

    def sin_cruzar(y0, h):
        for c in cortes_y:
            if y0 < c + 14 and y0 + h > c - 14: return c + 24
        return y0

    def colocar(ks, deseo, piso):
        """y de cada caja lo más cerca de su deseo, en ese orden, sin encimarse y desde piso (regresión isotónica)."""
        if not ks: return piso
        ys = _isotonica([deseo(k) - medida[k][1] / 2 for k in ks], [medida[k][1] for k in ks], SEP_CAJAS)
        corr = max(0, piso - ys[0])
        previo = piso - SEP_CAJAS
        for k, v in zip(ks, ys):
            y[k] = sin_cruzar(max(v + corr, previo + SEP_CAJAS), medida[k][1]); previo = y[k] + medida[k][1]
        return previo

    piso = {'A': MARGEN, 'B': MARGEN, 'C': MARGEN}   # cada columna se apila sola: no espera el fondo de las otras
    for n in range(len(secciones)):
        nuevos = [k for k in orden if casa[k] == n and k not in duenio]
        if not nuevos: continue
        acc = piso['A']   # columna A: apilada en orden, cada página con sus formularios debajo
        for k in [k for k in nuevos if col[k] == 'A']:
            y[k] = sin_cruzar(acc, medida[k][1]); acc = y[k] + medida[k][1] + SEP_CAJAS
            for f in formularios.get(k, []):
                y[f] = sin_cruzar(acc, medida[f][1]); acc = y[f] + medida[f][1] + SEP_CAJAS
        piso['A'] = acc
        prom = lambda k, c: [centro(v) for v in vecinos.get(k, []) if col[v] == c and v in y]
        bs = [k for k in nuevos if col[k] == 'B']
        deseo_b = {k: (sum(prom(k, 'A')) / len(prom(k, 'A')) if prom(k, 'A') else
                       sum(prom(k, 'B')) / len(prom(k, 'B')) if prom(k, 'B') else piso['B']) for k in bs}
        bs.sort(key=lambda k: (deseo_b[k], orden.index(k)))
        if bs: piso['B'] = colocar(bs, lambda k: deseo_b[k], piso['B']) + SEP_CAJAS
        cs = [k for k in nuevos if col[k] == 'C']
        deseo_c = {k: (sum(prom(k, 'B')) / len(prom(k, 'B')) if prom(k, 'B') else piso['C']) for k in cs}
        cs.sort(key=lambda k: (deseo_c[k], orden.index(k)))
        if cs: piso['C'] = colocar(cs, lambda k: deseo_c[k], piso['C']) + SEP_CAJAS

    # ---------------------------------------------------------------- 4. puertos de cada lado de cada caja
    puerto, bus = {}, {}   # puerto[(i, 'a'|'b')] = y; bus[(clave, lado)] = y
    for (k, lado), xs in extremos.items():
        otro = lambda i, e: enlaces[i][1] if e == 'a' else enlaces[i][0]
        con = sorted([(i, e) for i, e, rot in xs if rot], key=lambda t: centro(otro(*t)))
        sin = [(i, e) for i, e, rot in xs if not rot]
        items = [('r', t) for t in con]
        if sin:   # el bus se ubica entre los rótulos según dónde están, en promedio, sus otros extremos
            prom_bus = sum(centro(otro(*t)) for t in sin) / len(sin)
            pos = sum(1 for t in con if centro(otro(*t)) < prom_bus)
            items.insert(pos, ('b', None))
        alto = lambda it: alto_rotulo(it[1][0]) if it[0] == 'r' else 24
        total = sum(alto(it) for it in items)
        h = medida[k][1]
        yy = y[k] + max(12, (h - total) / 2)
        for it in items:
            if it[0] == 'r':   # la línea va a 1 renglón del borde superior de su bloque: estereotipo arriba, texto abajo
                puerto[it[1]] = yy + ALTO_FILA + 4
            else:
                bus[(k, lado)] = yy + 12
                for t in sin: puerto[t] = yy + 12
            yy += alto(it)

    # ---------------------------------------------------------------- 5. columnas y carriles
    ancho = {c: max([medida[k][0] for k in paginas if col[k] == c] + [0]) for c in 'ABC'}
    zona_rot = {c: 0 for c in ('L', 'AB', 'BC')}
    for i, (a, b, st, texto) in enumerate(enlaces):
        if st == 'contiene': continue
        canal = 'L' if col[a] == col[b] == 'A' else 'AB' if 'A' in (col[a], col[b]) else 'BC'
        w = max([ancho_texto(f'«{st}»')] + [ancho_texto(s) for s in filas_de(i)])
        zona_rot[canal] = max(zona_rot[canal], w + 10)
    # buses: intervalo vertical que recorre cada uno
    canal_bus, tramo = {}, {}
    for (k, lado), yb in bus.items():
        ys = [yb]
        for i, e, rot in extremos[(k, lado)]:
            if not rot: ys.append(puerto[(i, 'b' if e == 'a' else 'a')])
        tramo[(k, lado)] = (min(ys), max(ys))
        canal_bus[(k, lado)] = 'L' if col[k] == 'A' and lado == 'izq' else 'AB' if col[k] in 'AB' and (
            (col[k] == 'B' and lado == 'izq') or (col[k] == 'A' and lado == 'der')) else 'BC'
    carril = {}
    n_carriles = {}
    for canal in ('L', 'AB', 'BC'):
        libres = []   # [fin del último intervalo] por carril
        for kb in sorted([kb for kb in bus if canal_bus[kb] == canal], key=lambda kb: tramo[kb]):
            ini, fin = tramo[kb]
            j = next((j for j, f in enumerate(libres) if f + 14 < ini), None)
            if j is None: libres.append(fin); j = len(libres) - 1
            else: libres[j] = fin
            carril[kb] = j
        n_carriles[canal] = len(libres)
    ancho_canal = {c: zona_rot[c] + n_carriles[c] * PASO_CARRIL + 24 for c in ('L', 'AB', 'BC')}
    ancho_canal['L'] += HUECO_AGREGACION
    xA = MARGEN + ancho_canal['L']
    xB = xA + ancho['A'] + ancho_canal['AB']
    xC = xB + ancho['B'] + ancho_canal['BC']
    x_col = {'A': xA, 'B': xB, 'C': xC}

    def x_carril(kb):
        canal, j = canal_bus[kb], carril[kb]
        if canal == 'L': return MARGEN + 10 + j * PASO_CARRIL                    # carriles a la izquierda, rótulos junto a las páginas
        if canal == 'AB': return xB - 14 - j * PASO_CARRIL                      # rótulos junto a las páginas, carriles junto a los server pages
        return xC - 14 - j * PASO_CARRIL                                         # rótulos junto a los server pages, carriles junto a las tablas

    cajas = {}
    for k in paginas:
        w, h = medida[k]
        x0 = x_col[col[k]] if col[k] != 'C' else xC
        cajas[k] = (x0 + (ancho[col[k]] - w) / 2 if col[k] == 'B' else x0, y[k], w, h)

    def borde(k, lado):
        x, _, w, _ = cajas[k]
        return x + w if lado == 'der' else x

    # ---------------------------------------------------------------- 6. trazado y rótulos
    lineas = []
    for i, (a, b, st, texto) in enumerate(enlaces):
        if st == 'contiene':
            xp, yp, wp, hp = cajas[a]; xf, yf, wf, hf = cajas[b]
            fs = formularios[a]
            if fs.index(b) == 0:
                xm = xf + min(wp, wf) / 2
                pts = [(xm, yf), (xm, yp + hp)]
            else:
                xl = xA - 8 - 6 * fs.index(b)
                pts = [(xf, yf + 18), (xl, yf + 18), (xl, yp + hp - 12 - 5 * fs.index(b)), (xp, yp + hp - 12 - 5 * fs.index(b))]
            lineas.append(dict(enlace=enlaces[i], puntos=pts, rotulos=None)); continue
        la, lb = lados(a, b)
        r = rotulado[i]
        k_rot, lado_rot = (a, la) if r == 'a' else (b, lb)
        k_bus, lado_bus = (b, lb) if r == 'a' else (a, la)
        y_rot, y_bus = puerto[(i, r)], bus[(k_bus, lado_bus)]
        x_rot, x_bus, xl = borde(k_rot, lado_rot), borde(k_bus, lado_bus), x_carril((k_bus, lado_bus))
        tramo_pts = [(x_rot, y_rot), (xl, y_rot), (xl, y_bus), (x_bus, y_bus)]
        if abs(y_rot - y_bus) < 0.5: tramo_pts = [(x_rot, y_rot), (x_bus, y_bus)]
        pts = tramo_pts if r == 'a' else list(reversed(tramo_pts))
        # rótulo: estereotipo arriba de la línea y texto debajo, pegados a la caja del extremo con rótulo
        hacia_der = lado_rot == 'der'
        x0 = x_rot + 12 if hacia_der else x_rot - 12 - (HUECO_AGREGACION if col[k_rot] == 'A' and lado_rot == 'izq' else 0)
        filas = filas_de(i)
        w_st = ancho_texto(f'«{st}»'); w_nom = max([ancho_texto(s) for s in filas] + [0])
        c_st = (x0 + w_st / 2 if hacia_der else x0 - w_st / 2, y_rot - ALTO_FILA / 2 - 2)
        lineas.append(dict(enlace=enlaces[i], puntos=pts, rotulos=dict(estereotipo=(c_st, w_st), nombre=(x0, y_rot, hacia_der, filas))))
    ancho_total = xC + ancho['C'] + MARGEN
    alto_total = max(yy + h for _, yy, _, h in cajas.values()) + MARGEN
    return dict(cajas=cajas, lineas=lineas, ancho=ancho_total, alto=alto_total)


ANCHO_UTIL, ALTO_UTIL, ALTO_TITULOS = 979, 630, 75   # hoja apaisada útil (25,9 × 16,7 cm a 96 ppp, con holgura) y lo que ocupan 7.5 / 7.5.n
RECORTE_EA = 36   # el EMF de EA mide el ancho del diagrama menos esto (sus márgenes son más chicos que MARGEN)


def armar_en_franjas(paginas, enlaces, secciones, con_titulo_75=False):
    """Dos pasadas: la primera mide el ancho (y con él la escala de impresión); la segunda acomoda sabiendo dónde
    caen los cortes. Devuelve (acomodo, cortes [0, y1, …, alto], escala)."""
    ac = armar(paginas, enlaces, secciones)
    for _ in range(2):
        escala = ANCHO_UTIL / (ac['ancho'] - RECORTE_EA)   # el EMF ocupa los 25,9 cm de ancho
        primera = (ALTO_UTIL - ALTO_TITULOS * (2 if con_titulo_75 else 1)) / escala
        siguientes = ALTO_UTIL / escala
        cortes_y = [primera + j * siguientes for j in range(int(ac['alto'] / siguientes) + 3)]
        ac = armar(paginas, enlaces, secciones, cortes_y)
    cortes_y = [c for c in cortes_y if c < ac['alto'] - 40]
    return ac, [0] + cortes_y + [ac['alto']], escala
