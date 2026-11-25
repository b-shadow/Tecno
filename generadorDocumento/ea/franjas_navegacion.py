"""Un diagrama de navegación grande por actor (como G07), pensado para cortarse en franjas apaisadas: secciones en
el orden de implementación (login → menú → CU1 … CU8), cada una en una banda con sus columnas alineadas
(páginas | server pages | tablas de la sección), así que toda franja muestra clases. Las relaciones de navegación que
cruzan secciones (menú → página, página → ficha, server pages compartidos) siguen de una franja a la siguiente, cada
una por su propio carril y con su «estereotipo» y texto junto a la caja: ninguna línea comparte tramo con otra ni
cruza una caja. Los cortes caen entre cajas.
"""
import math

CAR, RENGLON = 5.75, 15   # medidas de EA 15 con Calibri 10: ancho por carácter y alto de renglón de una caja
PAGINA = ('actor', 'cliente', 'form', 'externo')   # tipos de la columna de páginas
CON_ESTEREOTIPO = {'form', 'bd'}   # EA escribe «Formulario» / «database»; client page y server page llevan ícono

MARGEN = 40
SEP_CAJAS = 15          # entre cajas de una misma columna
SEP_BANDA = 30          # entre secciones (hueco seguro para cortar)
PASO_CARRIL = 7         # distancia entre carriles verticales
TEXTO_EA = 5.0          # ancho real por carácter de los rótulos de EA a 9 pt
ALTO_FILA = 11          # alto de un renglón de rótulo (letra 9 de EA)
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
    """Acomodo del diagrama de un actor. Cada sección (en orden de implementación) ocupa una banda horizontal con sus
    tres columnas alineadas: páginas (con sus formularios debajo) | server pages | tablas de esa sección. Cada relación
    tiene su propio puerto en cada caja y su propio carril vertical (ninguna comparte tramo con otra), así que se puede
    seguir de punta a punta. cortes_y: alturas donde se parte en franjas; ninguna caja queda atravesada."""
    tipo = {k: v[0] for k, v in paginas.items()}
    col = {k: {'ps': 'B', 'bd': 'C'}.get(t, 'A') for k, t in tipo.items()}
    duenio = {}
    for a, b, st, _ in enlaces:
        if st == 'contiene' and b not in duenio: duenio[b] = a
    formularios = {}
    for _, claves, _ in secciones:
        for k in claves:
            if k in duenio and k not in formularios.setdefault(duenio[k], []): formularios[duenio[k]].append(k)

    def filas_de(i):
        a, b, _, texto = enlaces[i]
        return renglones(texto)

    def alto_rotulo(i):   # «estereotipo» arriba de la línea y el texto (uno o más renglones) debajo
        return ALTO_FILA * (1 + max(1, len(filas_de(i)))) + 8

    # ---------------------------------------------------------------- 1. lados y rótulo de cada relación
    def lados(a, b):
        ca, cb = col[a], col[b]
        if ca == cb == 'A': return 'izq', 'izq'
        if ca == cb == 'B': return 'der', 'der'
        return ('der', 'izq') if ca < cb else ('izq', 'der')
    extremos, rotulado = {}, {}   # (clave, lado) -> [(i, 'a'|'b', con_rotulo)]
    for i, (a, b, st, texto) in enumerate(enlaces):
        if st == 'contiene': continue
        la, lb = lados(a, b)
        if col[a] == 'A' and col[b] == 'B': r = 'a'          # link / submit: rótulo junto a la página
        elif col[a] == 'B' and col[b] == 'A': r = 'b'        # build: junto a la página que arma
        elif col[a] == 'B': r = 'a'                          # access / include: junto al server page
        else: r = 'b' if a == 'menu' or tipo[a] == 'actor' else 'a'   # entre páginas: el menú rotula en el destino
        rotulado[i] = r
        extremos.setdefault((a, la), []).append((i, 'a', r == 'a'))
        extremos.setdefault((b, lb), []).append((i, 'b', r == 'b'))
    tronco = {}   # i -> (clave, lado) de la caja de la que sale o a la que llega el tronco compartido
    for i, (a, b, st, _) in enumerate(enlaces):
        if st == 'contiene': continue
        la, lb = lados(a, b)
        if st in ('include', 'access'): tronco[i] = (b, lb)   # todas llegan a la misma caja, en un solo sentido
        elif col[a] == col[b] == 'A' and a == 'menu': tronco[i] = (a, la)
        elif col[a] == col[b] == 'A' and b == 'ficha': tronco[i] = (b, lb)
    alto_puerto = lambda i, rot: alto_rotulo(i) if rot else 14

    # ---------------------------------------------------------------- 2. tamaños: el contenido o los puertos
    medida = {}
    for k, v in paginas.items():
        w, h = medir(*v)
        for lado in ('izq', 'der'):
            xs = extremos.get((k, lado), [])
            propios = sum(alto_puerto(i, rot) for i, _, rot in xs if tronco.get(i) != (k, lado))
            h = max(h, propios + (14 if any(tronco.get(i) == (k, lado) for i, _, _ in xs) else 0) + 20)
        medida[k] = (w, h)

    # ---------------------------------------------------------------- 3. bandas por sección
    def actua(k, rel):
        return any(k in (a, b) and (st in ('submit', 'contiene', 'access', 'include') or
                                     (st in ('link', 'build') and 'ps' in (tipo[a], tipo[b]))) for a, b, st, _ in rel)
    casa = {}
    for n, (_, claves, rel) in enumerate(secciones):   # un server page va donde están sus tablas
        for a, b, st, _ in rel:
            if st == 'access' and a not in casa: casa[a] = n
    for n, (_, claves, rel) in enumerate(secciones):
        for k in claves:
            if k not in casa and (actua(k, rel) or tipo[k] in ('actor', 'externo')): casa[k] = n
    for n, (_, claves, _) in enumerate(secciones):
        for k in claves: casa.setdefault(k, n)
    for f, p in duenio.items(): casa[f] = casa[p]
    orden = list(dict.fromkeys(k for _, claves, _ in secciones for k in claves))
    vecinos = {}
    for a, b, st, _ in enlaces:
        vecinos.setdefault(a, []).append(b); vecinos.setdefault(b, []).append(a)
    y = {}
    centro = lambda k: y[k] + medida[k][1] / 2

    def sin_cruzar(y0, h):
        for c in cortes_y:
            if y0 < c + 14 and y0 + h > c - 14: return c + 24
        return y0

    def colocar(ks, deseo, piso):
        if not ks: return piso
        ys = _isotonica([deseo(k) - medida[k][1] / 2 for k in ks], [medida[k][1] for k in ks], SEP_CAJAS)
        corr, previo = max(0, piso - ys[0]), piso - SEP_CAJAS
        for k, v in zip(ks, ys):
            y[k] = sin_cruzar(max(v + corr, previo + SEP_CAJAS), medida[k][1]); previo = y[k] + medida[k][1]
        return previo

    cima = MARGEN
    for n in range(len(secciones)):
        nuevos = [k for k in orden if casa[k] == n and k not in duenio]
        if not nuevos: continue
        acc = cima
        for k in [k for k in nuevos if col[k] == 'A']:
            y[k] = sin_cruzar(acc, medida[k][1]); acc = y[k] + medida[k][1] + SEP_CAJAS
            for f in formularios.get(k, []):
                y[f] = sin_cruzar(acc, medida[f][1]); acc = y[f] + medida[f][1] + SEP_CAJAS
        fondo = acc - SEP_CAJAS
        prom = lambda k, c: [centro(v) for v in vecinos.get(k, []) if col[v] == c and v in y and casa[v] == n]
        bs = [k for k in nuevos if col[k] == 'B']
        deseo_b = {k: (sum(prom(k, 'A')) / len(prom(k, 'A')) if prom(k, 'A') else
                       sum(prom(k, 'B')) / len(prom(k, 'B')) if prom(k, 'B') else cima) for k in bs}
        bs.sort(key=lambda k: (deseo_b[k], orden.index(k)))
        fondo = max(fondo, colocar(bs, lambda k: deseo_b[k], cima))
        cs = [k for k in nuevos if col[k] == 'C']
        deseo_c = {k: (sum(prom(k, 'B')) / len(prom(k, 'B')) if prom(k, 'B') else cima) for k in cs}
        cs.sort(key=lambda k: (deseo_c[k], orden.index(k)))
        fondo = max(fondo, colocar(cs, lambda k: deseo_c[k], cima))
        cima = sin_cruzar(fondo + SEP_BANDA, 0)

    # ---------------------------------------------------------------- 4. un puerto por extremo
    puerto = {}
    otro = lambda i, e: enlaces[i][1] if e == 'a' else enlaces[i][0]
    for (k, lado), xs in extremos.items():
        del_tronco = [(i, e) for i, e, _ in xs if tronco.get(i) == (k, lado)]
        xs = sorted([x for x in xs if tronco.get(x[0]) != (k, lado)], key=lambda t: (centro(otro(t[0], t[1])), t[0]))
        items = [(i, e, rot) for i, e, rot in xs]
        if del_tronco:   # el tronco entra o sale por un solo puerto, en el lado de la caja más cercano a sus ramas
            prom = sum(centro(otro(i, e)) for i, e in del_tronco) / len(del_tronco)
            items.insert(sum(1 for i, e, _ in xs if centro(otro(i, e)) < prom), ('T', None, False))
        total = sum(14 if it[0] == 'T' else alto_puerto(it[0], it[2]) for it in items)
        yy = y[k] + max(10, (medida[k][1] - total) / 2)
        for i, e, rot in items:
            if i == 'T':
                for t in del_tronco: puerto[t] = yy + 7
                yy += 14; continue
            puerto[(i, e)] = yy + (ALTO_FILA + 3 if rot else 7)   # con rótulo: el estereotipo arriba de la línea
            yy += alto_puerto(i, rot)

    # ---------------------------------------------------------------- 5. columnas y un carril por relación
    ancho = {c: max([medida[k][0] for k in paginas if col[k] == c] + [0]) for c in 'ABC'}
    canal = {}
    zona_rot = {'L': 0, 'AB': 0, 'BC': 0}
    for i, (a, b, st, texto) in enumerate(enlaces):
        if st == 'contiene': continue
        canal[i] = 'L' if col[a] == col[b] == 'A' else 'AB' if 'A' in (col[a], col[b]) else 'BC'
        w = max([ancho_texto(f'«{st}»')] + [ancho_texto(s) for s in filas_de(i)])
        zona_rot[canal[i]] = max(zona_rot[canal[i]], w + 16)
    grupo = {i: (tronco[i] if i in tronco else i) for i in canal}   # lo que ocupa un carril
    tramo = {}
    for i in canal:
        g = grupo[i]
        ys = (puerto[(i, 'a')], puerto[(i, 'b')])
        tramo[g] = (min(ys + (tramo.get(g, (1e9, 0))[0],)), max(ys + (tramo.get(g, (0, -1e9))[1],)))
    carril_g, n_carriles = {}, {}
    for c in ('L', 'AB', 'BC'):
        fin_carril = []
        gs = list(dict.fromkeys(grupo[i] for i in canal if canal[i] == c))
        gs = [g for g in gs if tramo[g][1] - tramo[g][0] >= 0.5]
        for g in sorted(gs, key=lambda g: (tramo[g][0], -tramo[g][1])):
            ini, fin = tramo[g]
            j = next((j for j, f in enumerate(fin_carril) if f + 10 < ini), None)
            if j is None: fin_carril.append(fin); j = len(fin_carril) - 1
            else: fin_carril[j] = fin
            carril_g[g] = j
        n_carriles[c] = len(fin_carril)
    carril = {i: carril_g.get(grupo[i], 0) for i in canal}
    ancho_canal = {c: zona_rot[c] + n_carriles[c] * PASO_CARRIL + 20 for c in ('L', 'AB', 'BC')}
    ancho_canal['L'] += HUECO_AGREGACION
    xA = MARGEN + ancho_canal['L']
    xB = xA + ancho['A'] + ancho_canal['AB']
    xC = xB + ancho['B'] + ancho_canal['BC']
    x_col = {'A': xA, 'B': xB, 'C': xC}

    def x_carril(i):   # los carriles quedan del lado opuesto a la zona de rótulos de cada pasillo
        c, j = canal[i], carril[i]
        if c == 'L': return MARGEN + 8 + j * PASO_CARRIL
        if c == 'AB': return xB - 12 - j * PASO_CARRIL
        return xC - 12 - j * PASO_CARRIL

    cajas = {}
    for k in paginas:
        w, h = medida[k]
        x0 = x_col[col[k]]
        cajas[k] = (x0 + (ancho['B'] - w) / 2 if col[k] == 'B' else x0, y[k], w, h)

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
        pa, pb = (borde(a, la), puerto[(i, 'a')]), (borde(b, lb), puerto[(i, 'b')])
        if abs(pa[1] - pb[1]) < 0.5: pts = [pa, pb]
        else:
            xl = x_carril(i)
            pts = [pa, (xl, pa[1]), (xl, pb[1]), pb]
        r = rotulado[i]
        k_rot, lado_rot = (a, la) if r == 'a' else (b, lb)
        x_rot, y_rot = (pa if r == 'a' else pb)
        hacia_der = lado_rot == 'der'
        x0 = x_rot + 12 if hacia_der else x_rot - 12 - (HUECO_AGREGACION if col[k_rot] == 'A' and lado_rot == 'izq' else 0)
        filas = filas_de(i)
        real = lambda t: TEXTO_EA * len(t)   # ancho con que EA dibuja el rótulo
        w_st, w_nom = real(f'«{st}»'), max([real(f) for f in filas] + [0])
        x_st, x_nom = (x0, x0) if hacia_der else (x0 - w_st, x0 - w_nom)   # junto a la caja, alineado a su borde
        lineas.append(dict(enlace=enlaces[i], puntos=pts, rotulos=dict(
            estereotipo=((x_st + w_st / 2, y_rot - 2 - ALTO_FILA / 2), w_st), nombre=(x_nom, y_rot + 2, filas))))
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
