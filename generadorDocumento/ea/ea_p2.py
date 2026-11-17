"""Construye en Enterprise Architect 15 Trial (COM) los diagramas del documento P2 y los exporta a ../diagramas/.

  python ea/ea_p2.py                     todos los diagramas (repositorio nuevo: ea/crm-p2.eapx)
  python ea/ea_p2.py --solo datos|nav|clases|org    solo esos (los PNG de los demás quedan como estaban)
  python ea/ea_p2.py --guardar-posiciones
        después de acomodar cajas a mano en EA (abrir crm-p2.eapx, mover, guardar y cerrar EA): copia las posiciones a
        posiciones.json; las próximas regeneraciones las respetan. Para volver al acomodo automático de un diagrama,
        borrar su entrada de posiciones.json.

Notación y reglas: REGLAS_DOCUMENTO_P2.md §4–§6. Datos: ../esquema.py (BD real) y ../navegacion.py.
La clase EA y el acomodo de cajas están en ea_base.py (extraídos del P1; este generador no depende de otra carpeta)."""
import json, pathlib, re, sys
import win32com.client

AQUI = pathlib.Path(__file__).resolve().parent
DOC = AQUI.parent
SALIDA = DOC / 'diagramas'
EAPX = AQUI / 'crm-p2.eapx'
POSICIONES = AQUI / 'posiciones.json'
sys.path[:0] = [str(DOC), str(AQUI)]
import codigo, contenido, esquema, navegacion  # noqa: E402
import ea_base  # noqa: E402

ea_base.EAPX, ea_base.SALIDA = EAPX, SALIDA   # la clase EA escribe donde le indica su módulo
SEMILLA_CONCEPTUAL = 5
VERDE_BD = 0xE0ECCF          # COLORREF 0xBBGGRR: verde claro de las cajas «database» de G07
ESTEREOTIPO = {'cliente': 'client page', 'form': 'Formulario', 'ps': 'server page', 'bd': 'database'}


def lista(texto):
    return [x.strip() for x in texto.split(',') if x.strip()]


def cargar_posiciones():
    return json.loads(POSICIONES.read_text(encoding='utf-8')) if POSICIONES.exists() else {}


def colocar(ea, d, elementos, medidas, guardadas):
    """Usa las posiciones guardadas si están todas; si no, acomodo automático de EA (y luego las guardadas encima)."""
    for i, (k, e) in enumerate(elementos.items()):
        w, h = medidas[k]
        x, y = 30 + (i % 8) * 260, 30 + (i // 8) * 220
        o = d.DiagramObjects.AddNew(f'l={x};r={x + w};t={-y};b={-y - h};', ''); o.ElementID = e.ElementID; o.Update()
    d.Update()
    if not all(e.Name in guardadas for e in elementos.values()):
        ea.pi.LayoutDiagramEx(d.DiagramGUID, 0x40000000 | 0x00080000, 4, 40, 60, True)
        ea.r.ReloadDiagram(d.DiagramID)
    if guardadas:
        d.DiagramObjects.Refresh()
        por_id = {e.ElementID: e.Name for e in elementos.values()}
        for o in d.DiagramObjects:
            p = guardadas.get(por_id.get(o.ElementID))
            if p: o.left, o.top, o.right, o.bottom = p; o.Update()
        d.Update()


# ------------------------------------------------------------------------------------------------ 7.1 Conceptual
def conceptual(ea, pkg):
    """Una clase por tabla con sus atributos solo por nombre y la PK identificada con «PK» y subrayado.
    Las FK no se
    listan: son asociaciones con multiplicidad. Las N-N son clase de asociación con línea punteada (clase 06)."""
    T, F, NN, pk, uq = esquema.tablas(), esquema.fks(), esquema.intermedias(), esquema.pks(), esquema.unicas()
    fkcols = esquema.columnas_fk()
    attrs = {t: [c for c, *_ in cols if c in pk[t] or (t, c) not in fkcols] for t, cols in T.items()}
    ent = {}
    for t in T:
        e = ea.elemento(pkg, t, 'Class')
        for i, c in enumerate(attrs[t]):
            a = e.Attributes.AddNew(c, ''); a.Visibility = 'Public'; a.Pos = i
            # El estereotipo «PK» hace explícita la clave sin cambiar el nombre real de la columna.
            if c in pk[t]: a.Stereotype = 'PK'
            a.IsStatic = c in pk[t]
            a.Update()
        e.Update(); ent[t] = e
    relaciones = []
    for inter, (a, b) in NN.items():
        c = ea.conector(ent[a], ent[b], 'Association', card=('0..*', '0..*'))
        if not ent[inter].CreateAssociationClass(c.ConnectorID): raise SystemExit('EA no creó la clase de asociación ' + inter)
        relaciones += [(a, b), (inter, a), (inter, b)]   # la clase de asociación cerca de sus dos entidades
    pares = {}
    for h, cs, p, _ in F:
        pares[(h, p)] = pares.get((h, p), 0) + 1
    for h, cs, p, _ in F:
        if h in NN: continue
        nulo = any(not nn for c, _, nn, _ in T[h] if c in cs)
        hija = '0..1' if set(cs) == set(pk[h]) or (len(cs) == 1 and (h, cs[0]) in uq) else '0..*'
        rol = ', '.join(cs) if pares[(h, p)] > 1 else ''   # solo si hay dos relaciones entre las mismas tablas
        ea.conector(ent[h], ent[p], 'Association', rol, card=(hija, '0..1' if nulo else '1'))
        relaciones.append((h, p))
    d = ea.diagrama(pkg, 'Diseño Conceptual de Base de Datos', 'Logical')
    medidas = {t: (int(44 + 5.0 * max(len(t), *(len(x) + 4 for x in attrs[t]))),
                   40 + 12 * (len(attrs[t]) + len(pk[t]))) for t in T}
    guardadas = cargar_posiciones().get(d.Name, {})
    if all(t in guardadas for t in T):
        for t, (l, tp, r, b) in guardadas.items():
            if t in ent:
                o = d.DiagramObjects.AddNew(f'l={l};r={r};t={tp};b={b};', ''); o.ElementID = ent[t].ElementID; o.Update()
    else:
        # que el acomodo busque la letra más grande en UNA página vertical con márgenes de 1 cm (19,5 × 21,4 cm bajo los
        # títulos): EA exporta el PNG al doble y su texto mide ~20 px
        # Semilla 5 con sin_atravesar: la mejor de 16 variantes medidas (0 líneas sobre cajas, 7 cruces, letra 3,9 pt).
        ea_base.efectivo = lambda w, h: 20 * min(553 / (2 * w + 80), 607 / (2 * h + 80))
        pos, *_ = ea_base.acomodar(medidas, relaciones, gx=45, gy=55, semilla=SEMILLA_CONCEPTUAL, sin_atravesar=True)
        pos, *_ = ea_base.despejar_cajas(pos, relaciones)
        for t, (x, y, w, h) in pos.items():
            ea.poner(d, ent[t], x, y, w, h)
    d.Update(); ea.r.ReloadDiagram(d.DiagramID)
    # sin ea_base.colocar_asociaciones: el acomodo ya deja cada N-N junto a sus dos tablas (aristas inter-a, inter-b) y
    # reubicarla la ponía sobre otras relaciones
    # sin ea_base.rutar_enlaces: su ruta puede pasar por dentro de la caja de origen (pasó con roles → usuarios)
    auditar_conceptual(ea, d)
    ea.exportar(d, 'conceptual.png')


def auditar_conceptual(ea, d):
    """Mide el diagrama tal como quedó en EA: relaciones (y líneas punteadas de las N-N) que pasan sobre una caja que no
    es de sus extremos, cruces entre relaciones y multiplicidades contra la BD. Falla si alguna línea tapa una caja."""
    d.DiagramObjects.Refresh(); d.DiagramLinks.Refresh()
    caja = {o.ElementID: (o.left, -o.top, o.right, -o.bottom) for o in d.DiagramObjects}
    nombre = {i: ea.r.GetElementByID(i).Name for i in caja}
    centro = lambda r: ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
    lineas = []   # (descripción, p1, p2, ids que puede tocar)
    for l in d.DiagramLinks:
        c = ea.r.GetConnectorByID(l.ConnectorID)
        if c.ClientID in caja and c.SupplierID in caja:
            a, b = centro(caja[c.ClientID]), centro(caja[c.SupplierID])
            lineas.append((f'{nombre[c.ClientID]} - {nombre[c.SupplierID]}', a, b, {c.ClientID, c.SupplierID}))
    for i in caja:
        e = ea.r.GetElementByID(i)
        if e.AssociationClassConnectorID:
            c = ea.r.GetConnectorByID(e.AssociationClassConnectorID)
            a, b = centro(caja[c.ClientID]), centro(caja[c.SupplierID])
            medio = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            lineas.append((f'{e.Name} (punteada)', centro(caja[i]), medio, {i, c.ClientID, c.SupplierID}))
    tapan = [(t, nombre[i]) for t, a, b, ok in lineas for i, r in caja.items()
             if i not in ok and ea_base._atraviesa(a, b, (r[0] - 8, r[1] - 8, r[2] + 8, r[3] + 8))]
    cruces = [(t1, t2) for k, (t1, a, b, o1) in enumerate(lineas) for t2, c_, d_, o2 in lineas[k + 1:]
              if not (o1 & o2) and ea_base._cruzan(a, b, c_, d_)]
    print(f'   auditoría conceptual: {len(caja)} tablas, {len(lineas)} líneas, {len(tapan)} sobre cajas, {len(cruces)} cruces')
    for t, n in tapan: print('     SOBRE CAJA:', t, 'pasa por', n)
    for t1, t2 in cruces: print('     cruce:', t1, '×', t2)
    assert len(caja) == len(esquema.tablas()), 'faltan tablas en el diagrama'
    assert not tapan, 'hay relaciones que pasan sobre cajas: mover a mano en EA y guardar posiciones'


# ------------------------------------------------------------------------------------------------ 7.5 Navegación
def comprobar_navegacion(actor, paginas, enlaces):
    T = esquema.tablas()
    for k, (tipo, nombre, at, _) in paginas.items():
        if tipo != 'bd': continue
        cols = {c for t in nombre.removeprefix('BD: ').split(' / ') for c, *_ in T[t.strip()]}
        falta = [a for a in lista(at) if a not in cols]
        assert not falta, f'{actor}: {nombre} lista columnas que no existen en la BD: {falta}'
    for a, b, st, _ in enlaces:
        assert a in paginas and b in paginas, f'{actor}: enlace a una página no declarada: {a} -> {b}'
        assert st in ('link', 'submit', 'build', 'access', 'contiene'), f'{actor}: estereotipo desconocido {st}'
    vacias = [n for t, n, at, op in paginas.values() if t in ('cliente', 'ps') and not (at and op)]
    assert not vacias, f'{actor}: clases sin atributos u operaciones (el docente las rechaza): {vacias}'
    sueltas = set(paginas) - {x for a, b, *_ in enlaces for x in (a, b)}
    assert not sueltas, f'{actor}: páginas sin relación: {sueltas}'


def navegacion_actor(ea, raiz, actor, paginas, enlaces):
    comprobar_navegacion(actor, paginas, enlaces)
    pkg = ea.paquete(raiz, f'Navegacion {actor}')
    el, medidas = {}, {}
    for k, (tipo, nombre, at, op) in paginas.items():
        if tipo == 'actor':
            el[k] = ea.elemento(pkg, nombre, 'Actor'); medidas[k] = (45, 90); continue
        e = ea.elemento(pkg, nombre, 'Class', ESTEREOTIPO[tipo])
        for i, a in enumerate(lista(at)):
            n, _, val = a.partition(' = ')
            x = e.Attributes.AddNew(n.strip(), ''); x.Visibility = 'Private'; x.Pos = i
            x.IsCollection = x.AllowDuplicates = not val   # {bag} como G07; un texto fijo (mensaje = "…") no es colección
            if val: x.Default = val
            x.Update()
        for o in lista(op):
            m = e.Methods.AddNew(o.removesuffix('()'), ''); m.Visibility = 'Public'; m.Update()
        e.Update(); el[k] = e
        filas = len(lista(at)) + len(lista(op)) + (1 if tipo in ('form', 'bd') else 0)
        largo = max([len(nombre)] + [len(a) + 8 for a in lista(at) + lista(op)])
        medidas[k] = (max(150, 7 * largo + 40), 50 + 15 * filas)
    for a, b, st, texto in enlaces:
        if st == 'contiene':   # el formulario es parte de su página (agregación, rombo en la página)
            ea.conector(el[b], el[a], 'Aggregation')
        else:
            ea.conector(el[a], el[b], 'Association', texto, st, dirigido=True)
    d = ea.diagrama(pkg, f'Diagrama de Navegacion - {actor}', 'Logical')
    colocar(ea, d, el, medidas, cargar_posiciones().get(d.Name, {}))
    d.DiagramObjects.Refresh()
    for o in d.DiagramObjects:
        if paginas[next(k for k, e in el.items() if e.ElementID == o.ElementID)][0] == 'bd':
            o.BackgroundColor = VERDE_BD; o.Update()
    ea.exportar(d, f'nav-{actor.lower()}.png')


def diagramas_navegacion(ea, raiz):
    for actor, datos in navegacion.ACTORES.items():
        navegacion_actor(ea, raiz, actor, *datos())


# ------------------------------------------------------------------------------------------------ 5.3.2 Clases (3 capas)
CAPAS = {'Presentacion': 'Presentación', 'Negocio': 'Negocio', 'Datos': 'Datos'}
# filas de cada capa, de arriba abajo: página → módulo api/ | controller → request y service | repository → model
# filas de cada capa, de arriba abajo: página P → módulo api/ | clase N → requests | clase D → modelos (tablas)
# Los «request» (validación) no se dibujan: ya están como tipo del parámetro en la firma de cada método de N.
FILAS = [('Presentacion', ('client page',)), ('Presentacion', ('module',)), ('Negocio', ('negocio',)),
         ('Datos', ('datos',)), ('Datos', ('model',))]
# solo el nombre: las funciones del módulo api/ van en el mensaje que le llega de la página, los campos del request en
# las firmas de N y las columnas de los modelos en 7.1–7.3 (Diseño de Datos)
PLEGADAS = ('module', 'model')
SEPARACION = 120   # alto libre entre filas: el mensaje del «use» va entre ellas sin tocar las cajas
ANCHO_MAX = 1500   # ancho de una fila antes de partirla (que el diagrama quepa en una página vertical)


def _miembro(texto):
    """'+store(r: MotivoRequest): JsonResponse' -> ('Public', 'store', [('r', 'MotivoRequest', '')], 'JsonResponse')."""
    vis = {'+': 'Public', '-': 'Private', '#': 'Protected'}.get(texto[0], 'Public')
    m = re.match(r'[+#-]?(\w+)\((.*)\)(?::\s*(.+))?$', texto)
    params = []
    for p in [x.strip() for x in m.group(2).split(',') if x.strip()]:
        nombre, _, defecto = p.partition('=')
        nombre, _, tipo = nombre.partition(':')
        params.append((nombre.strip(), tipo.strip(), defecto.strip()))
    return vis, m.group(1), params, (m.group(3) or '').strip()


def clases_cu(ea, raiz, solo_cu=None):
    """Un diagrama de clases por CU con las 3 capas reales (REGLAS §4 5.3.2 y §6b), leído del código por codigo.py:
    «client page» → «module» api/<area>.js → «controller» → «request» / «service» → «repository» → «model»."""
    for cu, titulo in contenido.CU.items():
        if solo_cu and cu != solo_cu: continue
        clases, deps, errores = codigo.cadena(cu)
        assert not errores, errores
        pkg = ea.paquete(raiz, f'{cu} Clases')
        capas = {c: ea.paquete(pkg, n) for c, n in CAPAS.items()}
        el, medidas = {}, {}
        clases = {n: x for n, x in clases.items() if x['estereotipo'] != 'request'}
        deps = {k: v for k, v in deps.items() if k[0] in clases and k[1] in clases}
        for n, x in clases.items():
            if x['estereotipo'] in PLEGADAS: x = dict(x, atributos=[], metodos=[])
            e = ea.elemento(capas[x['capa']], n, 'Class', x['estereotipo'])
            for i, a in enumerate(x['atributos']):
                nombre, _, tipo = a.partition(': ')
                at = e.Attributes.AddNew(nombre, tipo); at.Visibility = 'Private'; at.Pos = i; at.Update()
            for i, texto in enumerate(x['metodos']):
                vis, nombre, params, ret = _miembro(texto)
                m = e.Methods.AddNew(nombre, ret); m.Visibility = vis; m.Pos = i; m.Update()
                for j, (pn, pt, pd) in enumerate(params):
                    p = m.Parameters.AddNew(pn, pt); p.Position = j
                    if pd: p.Default = pd
                    p.Update()
            e.Update(); el[n] = e
            largo = max([len(n) + 4] + [len(a) + 2 for a in x['atributos']] + [len(t) for t in x['metodos']])
            medidas[n] = (max(120, int(6.3 * largo) + 24), (40 if x['estereotipo'] in PLEGADAS else 46) + 14 * (len(x['atributos']) + len(x['metodos'])))
        for (a, b), mensajes in sorted(deps.items()):   # el mensaje de cada «use»: lo que a llama de b
            texto = '\r\n'.join(', '.join(mensajes[i:i + 2]) for i in range(0, len(mensajes), 2))
            # «use» como primera línea del mensaje: EA dibuja el estereotipo del conector encima del texto
            ea.conector(el[a], el[b], 'Dependency', '«use»' + ('\r\n' + texto if texto else ''))
        marcos_el = {c: ea.elemento(capas[c], f'Capa {n}', 'Boundary') for c, n in CAPAS.items()}
        for viejo in SALIDA.glob(f'cls-{cu.lower()}*.*'): viejo.unlink()   # el CU pudo tener otra cantidad de áreas
        grupos = [('', list(clases))]   # un solo diagrama por CU, como G07 (las áreas van en columnas)
        for k, (area, sub) in enumerate(grupos, 1):
            solo = len(grupos) == 1
            sc = {n: clases[n] for n in sub}
            sd = {par: v for par, v in deps.items() if par[0] in sc and par[1] in sc}
            d = ea.diagrama(pkg, f'{cu}. {titulo}' if solo else f'{cu}. {titulo} ({k}/{len(grupos)}: {area})', 'Logical')
            estilo = re.sub(r'OpParams=\d;?', '', d.ExtendedStyle or '')
            d.ExtendedStyle = estilo + ('' if estilo.endswith(';') or not estilo else ';') + 'OpParams=2;'; d.Update()   # parámetros con nombre y tipo
            pos, marcos = ubicar(sc, sd, medidas)
            ancho = max(x + w for x, _, w, _ in pos.values()) + 25
            for capa, (y0, y1) in marcos.items():   # primero los marcos: quedan detrás de las clases
                ea.poner(d, marcos_el[capa], 15, y0 - 38, ancho, y1 - y0 + 18)
            for n, (x, y_, w, h) in pos.items():
                ea.poner(d, el[n], x, y_, w, h)
            ea.exportar(d, f'cls-{cu.lower()}.png' if solo else f'cls-{cu.lower()}-{k}.png')


def areas(clases, deps):
    """Una figura por área del CU (cada N que atiende a un módulo api/): su columna completa y lo que esa columna usa
    directamente de fuera (N auxiliares, D o tablas compartidas). [(nombre de la N, [clases])]."""
    res = []
    for col in columnas(clases, deps):
        entradas = [n for n in col[FILA['negocio']] if any(a for a, b in deps if b == n and clases[a]['estereotipo'] == 'module')]
        if not entradas: continue   # la columna de auxiliares: aparecen dentro de las áreas que las usan
        miembros = {n for fila in col for n in fila}
        extra = {b for a, b in deps if a in miembros and b not in miembros}
        res.append((entradas[0], [n for n in clases if n in miembros | extra]))
    return res


def ubicar(clases, deps, medidas):
    """Posiciones: una columna por área (página → api → N → D → tablas, alineadas) y filas por capa. (pos, marcos)."""
    cols = columnas(clases, deps)
    # páginas separadas (sus mensajes convergen en el mismo módulo) y tablas en una sola fila (si se apilan, las
    # flechas a las de abajo pasan por encima de las de arriba); el resto, dentro del ancho de la columna
    sep = {FILA['client page']: 160}
    sin_corte = {FILA['model'], FILA['client page']}
    anchos = [max(medidas[n][0] for fila in col for n in fila) for col in cols]
    celdas = [[flujo(col[i], 10 ** 6 if i in sin_corte else anchos[c], medidas, sep.get(i, 25)) for i in range(len(FILAS))]
              for c, col in enumerate(cols)]
    anchos = [max([anchos[c]] + [celda[2] for celda in celdas[c]]) for c in range(len(cols))]
    altos = [max(celdas[c][i][1] for c in range(len(cols))) for i in range(len(FILAS))]
    xs, x = [], 40
    for a in anchos: xs.append(x); x += a + 70
    y, pos, marcos, capa_ant = 30, {}, {}, None
    for i, (capa, _) in enumerate(FILAS):
        if not altos[i]: continue
        if capa != capa_ant: y += 40; capa_ant = capa   # espacio para el nombre de la capa
        for c in range(len(cols)):
            for n, (dx, dy) in celdas[c][i][0].items(): pos[n] = (xs[c] + dx, y + dy, *medidas[n])
        marcos.setdefault(capa, [y, 0])[1] = y + altos[i] + 40   # el marco cierra bajo la última fila de la capa
        y += altos[i] + SEPARACION
    return pos, marcos


FILA = {st: i for i, (_, sts) in enumerate(FILAS) for st in sts}


def columnas(clases, deps):
    """Una columna por área: cada N que recibe una petición de un módulo api/ con sus módulos y páginas encima y sus D y
    tablas debajo (lo compartido queda en la primera columna que lo usa). Las N auxiliares (alcance, conversión…) que
    solo usan otras N van en la última columna con sus D. Devuelve [[fila0, fila1, …] por columna]."""
    usa = {n: [b for a, b in deps if a == n] for n in clases}
    usado_por = {n: [a for a, b in deps if b == n] for n in clases}
    puesto, cols = set(), []

    def nueva(ns):
        col = [[] for _ in FILAS]
        for n in ns:
            if n in puesto: continue
            puesto.add(n); col[FILA[clases[n]['estereotipo']]].append(n)
        return col

    def debajo(ns):   # D que usan las N, y tablas que usan esas D
        ds = [d for n in ns for d in usa[n] if clases[d]['estereotipo'] == 'datos']
        return ds + [m for d in ds for m in usa[d] if clases[m]['estereotipo'] == 'model']

    entradas = [n for n in clases if clases[n]['estereotipo'] == 'negocio'
                and any(clases[a]['estereotipo'] == 'module' for a in usado_por[n])]
    for n in entradas:
        mods = [a for a in usado_por[n] if clases[a]['estereotipo'] == 'module']
        mods += [a for m in mods for a in usado_por[m] if clases[a]['estereotipo'] == 'module']   # servicios/auth.js
        pags = [a for m in mods for a in usado_por[m] if clases[a]['estereotipo'] == 'client page']
        cols.append(nueva(pags + mods + [n] + debajo([n])))
    resto = [n for n in clases if n not in puesto]
    resto_n = [n for n in resto if clases[n]['estereotipo'] == 'negocio']
    cols.append(nueva(resto_n + debajo(resto_n) + resto))
    return [c for c in cols if any(c)]


def flujo(nombres, ancho, medidas, sep=25):
    """Coloca las cajas de una celda de izquierda a derecha dentro del ancho de su columna.
    ({n: (dx, dy)}, alto, ancho usado)."""
    res, x, y, alto, usado = {}, 0, 0, 0, 0
    for n in nombres:
        w, h = medidas[n]
        if x and x + w > ancho: x, y, alto = 0, y + alto + sep, 0
        res[n] = (x, y); usado = max(usado, x + w); x += w + sep; alto = max(alto, h)
    return res, (y + alto if nombres else 0), usado


# ------------------------------------------------------------------------------------------------ 2.5 Organigrama
def organigrama(ea, raiz):
    """Área comercial de UNEXO (contenido.ORGANIGRAMA_CARGOS): una caja por cargo, unida a su superior."""
    pkg = ea.paquete(raiz, 'Organigrama')
    el = {c: ea.elemento(pkg, c, 'Class') for c, _ in contenido.ORGANIGRAMA_CARGOS}
    for c, jefe in contenido.ORGANIGRAMA_CARGOS:
        if jefe: ea.conector(el[jefe], el[c], 'Association')
    d = ea.diagrama(pkg, contenido.ORGANIGRAMA, 'Logical')
    for i, (c, _) in enumerate(contenido.ORGANIGRAMA_CARGOS):
        ea.poner(d, el[c], 60, 40 + i * 110, 200, 60)
    ea.exportar(d, 'organigrama.png')


# ------------------------------------------------------------------------------------------------ posiciones
def guardar_posiciones():
    r = win32com.client.Dispatch('EA.Repository')
    if not r.OpenFile(str(EAPX)): raise SystemExit('EA no abrió ' + str(EAPX))
    pos = cargar_posiciones()

    def recorrer(p):
        for d in p.Diagrams:
            pos[d.Name] = {r.GetElementByID(o.ElementID).Name: [o.left, o.top, o.right, o.bottom] for o in d.DiagramObjects}
        for h in p.Packages: recorrer(h)
    for m in r.Models: recorrer(m)
    r.CloseFile(); r.Exit()
    POSICIONES.write_text(json.dumps(pos, ensure_ascii=False, indent=1), encoding='utf-8')
    print('posiciones guardadas de', len(pos), 'diagramas en', POSICIONES)


PARTES = {'datos': lambda ea, m: conceptual(ea, ea.paquete(m, 'Diseño de Datos')),
          'nav': lambda ea, m: diagramas_navegacion(ea, ea.paquete(m, 'Diseño de Navegacion')),
          'clases': lambda ea, m: clases_cu(ea, ea.paquete(m, 'Análisis de clases')),
          'org': lambda ea, m: organigrama(ea, ea.paquete(m, 'Organización'))}


def main():
    if '--guardar-posiciones' in sys.argv: return guardar_posiciones()
    if EAPX.exists() and '--recrear' not in sys.argv:
        raise SystemExit('El EAPX existente contiene diagramas y cambios manuales. '
                         'Use ea_faltantes.py para completar/exportar los diagramas, '
                         'o --recrear solo después de respaldar crm-p2.eapx.')
    solo = sys.argv[sys.argv.index('--solo') + 1].split(',') if '--solo' in sys.argv else list(PARTES)
    SALIDA.mkdir(exist_ok=True)
    ea = ea_base.EA('CRM vía web (P2, Grupo 05 SA)')
    try:
        for parte in solo: PARTES[parte](ea, ea.modelo)
    finally:
        ea.cerrar()
    print('exportados:', ', '.join(ea.exportados))


if __name__ == '__main__':
    main()
