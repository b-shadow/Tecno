"""Construye en Enterprise Architect 15 Trial (COM) los diagramas del documento P2 y los exporta a ../diagramas/.

  python ea/ea_p2.py                     todos los diagramas (repositorio nuevo: ea/crm-p2.eapx)
  python ea/ea_p2.py --solo datos|nav    solo esos (los PNG de los demás quedan como estaban)
  python ea/ea_p2.py --guardar-posiciones
        después de acomodar cajas a mano en EA (abrir crm-p2.eapx, mover, guardar y cerrar EA): copia las posiciones a
        posiciones.json; las próximas regeneraciones las respetan. Para volver al acomodo automático de un diagrama,
        borrar su entrada de posiciones.json.

Notación y reglas: REGLAS_DOCUMENTO_P2.md §4–§6. Datos: ../esquema.py (BD real) y ../navegacion.py.
La clase EA y el acomodo de cajas están en ea_base.py (extraídos del P1; este generador no depende de otra carpeta)."""
import json, pathlib, sys
import win32com.client

AQUI = pathlib.Path(__file__).resolve().parent
DOC = AQUI.parent
SALIDA = DOC / 'diagramas'
EAPX = AQUI / 'crm-p2.eapx'
POSICIONES = AQUI / 'posiciones.json'
sys.path[:0] = [str(DOC), str(AQUI)]
import esquema, navegacion  # noqa: E402
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
    """Una clase por tabla con sus atributos solo por nombre (sin tipos ni marcas PK/FK, como G07 pág. 63); la PK va
    subrayada (docente, revisión del P1). Las FK no se
    listan: son asociaciones con multiplicidad. Las N-N son clase de asociación con línea punteada (clase 06)."""
    T, F, NN, pk, uq = esquema.tablas(), esquema.fks(), esquema.intermedias(), esquema.pks(), esquema.unicas()
    fkcols = esquema.columnas_fk()
    attrs = {t: [c for c, *_ in cols if c in pk[t] or (t, c) not in fkcols] for t, cols in T.items()}
    ent = {}
    for t in T:
        e = ea.elemento(pkg, t, 'Class')
        for i, c in enumerate(attrs[t]):
            a = e.Attributes.AddNew(c, ''); a.Visibility = 'Public'; a.Pos = i
            # PK subrayada (pedido del docente en la revisión del P1). EA solo subraya un atributo static: IsID pinta "{id}"
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
    medidas = {t: (int(44 + 5.0 * max(len(t), *(len(x) + 4 for x in attrs[t]))), 40 + 12 * len(attrs[t])) for t in T}
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
          'nav': lambda ea, m: diagramas_navegacion(ea, ea.paquete(m, 'Diseño de Navegacion'))}


def main():
    if '--guardar-posiciones' in sys.argv: return guardar_posiciones()
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
