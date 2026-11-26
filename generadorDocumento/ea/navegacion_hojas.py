"""7.5 en Enterprise Architect, como G07: un diagrama de navegación grande por actor («Diagrama de Navegacion -
<Actor>», en su paquete «Navegacion <Actor>») que el documento corta en franjas apaisadas.

  python ea/navegacion_hojas.py                 # los cuatro actores
  python ea/navegacion_hojas.py Vendedor        # solo uno
  python ea/navegacion_hojas.py --simular       # sin EA: dimensiones y elementos de cada actor

Sincroniza los elementos del paquete con navegacion.py y escribe cada relación con sus quiebres por COM.
Cada rol usa un lienzo distribuido por flujos. La posición de los rótulos se guarda en
t_diagramlinks.Geometry. Exporta el EMF y el PNG por actor y actualiza el manifiesto
nav-franjas.json. insertar_navegacion.py calcula los cortes a partir del EMF.
"""
import json
import sys
import winreg
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI)); sys.path.insert(0, str(AQUI.parent))
import navegacion as N  # noqa: E402
from rutas import DIAGRAMAS  # noqa: E402

EAPX = AQUI / 'crm-p2.eapx'
ESTEREOTIPO = {'cliente': 'client page', 'externo': 'client page', 'form': 'Formulario', 'ps': 'server page', 'bd': 'database'}
VERDE_BD, GRIS_EXTERNO = 0xE0ECCF, 0xEEEEEE   # COLORREF 0xBBGGRR, como G07
SUBPAQUETE = 'Hojas 7.5'   # versiones anteriores (se borran si quedaron)
DESPLAZA = 80        # margen extra: ningún rótulo queda en coordenadas negativas (el EMF de EA las recorta)
FUENTE_ROTULOS = 9   # pt de los rótulos de las líneas (preferencia FONTSIZE13 de EA; se restaura al terminar)


def lista(texto):
    return [x.strip() for x in texto.split(',') if x.strip()]


def paquete_actor(r, actor):
    def buscar(p):
        if p.Name == f'Navegacion {actor}': return p
        for h in p.Packages:
            x = buscar(h)
            if x: return x
    for m in r.Models:
        x = buscar(m)
        if x: return x
    raise SystemExit(f'No está el paquete «Navegacion {actor}» en el EAPX')


def sincronizar(r, pkg, paginas, enlaces, nombres_visibles=None):
    """Elementos y relaciones del paquete del actor = navegacion.py (crea, actualiza y borra lo que sobra)."""
    # cada caja se reconoce por su clave de navegacion.py (Alias): una página o tabla repetida en otra sección es
    # otra caja con el mismo nombre
    existentes = {e.Alias: e for e in pkg.Elements if e.Alias}
    actores = [e for e in pkg.Elements if e.Type == 'Actor']
    el = {}
    for k, (tipo, nombre, at, op) in paginas.items():
        e = existentes.get(k) or (actores[0] if tipo == 'actor' and actores and
                                   all(x.ElementID != actores[0].ElementID for x in el.values()) else None)
        if e is None:
            e = pkg.Elements.AddNew(nombre, 'Actor' if tipo == 'actor' else 'Note' if tipo == 'nota' else 'Class'); e.Update()
        e.Name, e.Alias = nombre, k; e.Update()
        if tipo == 'nota': e.Notes = at; e.Update()
        if tipo not in ('actor', 'nota'):
            base = k.split('#')[0]
            e.StereotypeEx = ESTEREOTIPO[tipo]
            e.Notes = ('Server page: ' + (N.API.get(base) or N.INCLUIDAS.get(base, ('',))[0] + ' (parte compartida, «include»)')
                       if tipo == 'ps' else f'{ESTEREOTIPO[tipo]} de la navegación (Conallen), tomada del código.')
            e.Update()
            for i in reversed(range(e.Attributes.Count)): e.Attributes.DeleteAt(i, False)
            for i in reversed(range(e.Methods.Count)): e.Methods.DeleteAt(i, False)
            e.Attributes.Refresh(); e.Methods.Refresh()
            for i, a in enumerate(lista(at)):
                x = e.Attributes.AddNew(a.split('=')[0].strip(), ''); x.Visibility = 'Private'; x.Pos = i
                x.IsCollection = True; x.AllowDuplicates = True; x.Update()   # {bag}, como G07
            if nombres_visibles is not None and tipo == 'form':
                op = ''   # Conallen: las funciones de JavaScript pertenecen a la página.
            for i, o in enumerate(lista(op)):
                m = e.Methods.AddNew(o.removesuffix('()'), ''); m.Visibility = 'Public'; m.Pos = i; m.Update()
            e.Update()
        el[k] = e
    vivos = {e.ElementID for e in el.values()}
    for i in reversed(range(pkg.Elements.Count)):
        if pkg.Elements.GetAt(i).ElementID not in vivos: pkg.Elements.DeleteAt(i, True)
    pkg.Elements.Refresh()
    # relaciones: (cliente, proveedor, tipo, estereotipo, nombre)
    deseadas = {}
    for a, b, st, texto in enlaces:
        if st == 'contiene': clave = (el[b].ElementID, el[a].ElementID, 'Aggregation', '', '')
        else:   # el texto en renglones cortos: su rótulo va junto a la caja (franjas_navegacion)
            import franjas_navegacion as F
            entre_paginas = paginas[a][0] in F.PAGINA and paginas[b][0] in F.PAGINA   # pasillo izquierdo: un renglón
            nombre = (texto if entre_paginas else '\r\n'.join(F.renglones(texto))) if nombres_visibles is None else \
                nombres_visibles[(a, b, st, texto)]
            clave = (el[a].ElementID, el[b].ElementID, 'Association', st, nombre)
        deseadas[clave] = (a, b, st, texto)
    conector = {}
    if nombres_visibles is not None:
        assert len(deseadas) == len(enlaces), 'Hay relaciones con los mismos extremos, tipo y nombre'
    for e in el.values():
        for i in reversed(range(e.Connectors.Count)):
            c = e.Connectors.GetAt(i)
            if c.ClientID != e.ElementID or c.SupplierID not in vivos: continue
            clave = (c.ClientID, c.SupplierID, c.Type, c.Stereotype or '', c.Name or '')
            if clave in deseadas and clave not in conector.values(): conector[deseadas[clave]] = c.ConnectorID
            else: e.Connectors.DeleteAt(i, False)
        e.Connectors.Refresh()
    for clave, enlace in deseadas.items():
        if enlace in conector:
            if nombres_visibles is None:
                continue
            c = r.GetConnectorByID(conector[enlace])
        else:
            cliente = next(e for e in el.values() if e.ElementID == clave[0])
            c = cliente.Connectors.AddNew(clave[4], clave[2]); c.SupplierID = clave[1]
            if clave[3]: c.Stereotype = clave[3]
            c.Direction = 'Source -> Destination'
        if nombres_visibles is not None:
            c.Notes = enlace[3]
            if enlace[2] == 'link':
                c.Direction = 'Source -> Destination'
            if enlace[2] == 'contiene' and paginas[enlace[1]][0] == 'form':
                c.SupplierEnd.Aggregation = 2   # composición en el extremo de la página
        c.Update(); conector[enlace] = c.ConnectorID
    return el, conector


DT_NOMBRE, DT_ESTEREOTIPO = 8, 10   # dónde pone EA los rótulos por omisión: nombre arriba, estereotipo abajo del ancla


def geometria(l, cs, ce, horizontal=False):
    """Geometry de t_diagramlinks: extremos (SX/SY/EX/EY, y de EA hacia arriba) y rótulos movidos a su lugar.
    OX/OY desplazan los rótulos desde el ancla que elige EA."""
    pts = l['puntos']
    (sx, sy), (ex, ey) = pts[0], pts[-1]
    lado = lambda px, py, b: 2 if px >= b[2] + b[4] - 1 else 4 if px <= b[2] + 1 else 3 if py >= b[3] + b[5] - 1 else 1
    g = f'SX={round(sx - cs[0])};SY={round(cs[1] - sy)};EX={round(ex - ce[0])};EY={round(ce[1] - ey)};EDGE={lado(sx, sy, cs)};'
    if not l['rotulos']: return g
    if horizontal and len(pts) >= 3 and len(pts) != 4:
        # EA 15 centra el ancla en este tramo en las relaciones personalizadas
        # de varios quiebres. Medido contra los textos del EMF exportado.
        i = len(pts) // 2
        t = (pts[i], pts[i + 1])
    else:
        t = (pts[-3], pts[-2]) if len(pts) > 3 else (pts[0], pts[-1])
    ax, ay = (t[0][0] + t[1][0]) / 2, (t[0][1] + t[1][1]) / 2
    (stx, sty), w_st = l['rotulos']['estereotipo']
    izq, arriba, filas = l['rotulos']['nombre']
    # Medido en el EMF de EA: el bloque del nombre empieza 7 u. arriba del centro pedido; EA ajusta el texto al ancho CX
    # (se le da holgura) y, con varios renglones (ALN=0), su borde izquierdo queda en centro − CX + 128 − 47·renglones.
    n = max(1, len(filas)); largo = max([len(f) for f in filas] + [1])
    w_texto, w_nom = 5.0 * largo, 6.0 * largo + 14
    nx = izq + w_nom - 128 + 47 * n if n > 1 else izq + w_texto / 2
    ny = arriba + 7
    rot = lambda w, h, ox, oy: (f'CX={round(w)}:CY={round(h)}:OX={round(ox)}:OY={round(oy)}:HDN=0:BLD=0:ITA=0:UND=0:'
                                'CLR=-1:ALN={}:DIR=0:ROT=0;')
    lmt = rot(w_nom, 14 * n, nx - ax, ny - (ay - DT_NOMBRE)).format(0 if n > 1 else 1)
    lmb = rot(w_st + 14, 14, stx - ax, sty - (ay + DT_ESTEREOTIPO)).format(1)
    return g + f'$LLB=;LLT=;LMT={lmt}LMB={lmb}LRT=;LRB=;IRHS=;ILHS=;'


def dibujar(r, d, el, conector, paginas, ac, horizontal=False):
    """Rehace el diagrama general del actor con las posiciones calculadas."""
    for i in reversed(range(d.DiagramObjects.Count)): d.DiagramObjects.DeleteAt(i, False)
    d.DiagramObjects.Refresh(); d.Update()
    cajas = {k: (x + DESPLAZA, y + DESPLAZA, w, h) for k, (x, y, w, h) in ac['cajas'].items()}
    for k, (x, y, w, h) in cajas.items():
        x, y, w, h = round(x), round(y), round(w), round(h)
        o = d.DiagramObjects.AddNew(f'l={x};r={x + w};t={-y};b={-(y + h)};', ''); o.ElementID = el[k].ElementID; o.Update()
        o.SetStyleEx('font', 'Calibri'); o.SetStyleEx('fontsz', '100')
        tipo = paginas[k][0]
        if tipo == 'bd': o.BackgroundColor = VERDE_BD
        if tipo == 'externo': o.BackgroundColor = GRIS_EXTERNO
        o.Update()
    d.Update(); r.ReloadDiagram(d.DiagramID); d = r.GetDiagramByID(d.DiagramID)
    centro = {el[k].ElementID: (x + w / 2, y + h / 2, x, y, w, h) for k, (x, y, w, h) in cajas.items()}
    mov = lambda p: (p[0] + DESPLAZA, p[1] + DESPLAZA)
    por_id = {}
    for l in ac['lineas']:
        rot = l['rotulos'] and dict(estereotipo=(mov(l['rotulos']['estereotipo'][0]), l['rotulos']['estereotipo'][1]),
                                    nombre=(l['rotulos']['nombre'][0] + DESPLAZA, l['rotulos']['nombre'][1] + DESPLAZA,
                                            l['rotulos']['nombre'][2]))
        por_id[conector[l['enlace']]] = dict(l, puntos=[mov(p) for p in l['puntos']], rotulos=rot)
    ids = [dl.ConnectorID for dl in d.DiagramLinks]
    faltan = set(por_id) - set(ids)
    assert not faltan, f'EA no mostró {len(faltan)} relaciones en el diagrama'
    rotulos = {}
    for dl in d.DiagramLinks:   # por COM: crea la fila de t_diagramlinks con extremos y quiebres
        l = por_id.get(dl.ConnectorID)
        if l is None: dl.IsHidden = True; dl.Update(); continue
        c = r.GetConnectorByID(dl.ConnectorID)
        g = geometria(l, centro[c.ClientID], centro[c.SupplierID], horizontal)
        camino = ''.join(f'{round(px)}:{-round(py)};' for px, py in l['puntos'][1:-1])
        dl.Geometry = g.split('$')[0]
        if camino or horizontal:
            dl.Style = 'Mode=3;EOID=;SOID=;Color=-1;LWidth=0;'
            dl.Path = camino
        dl.IsHidden = False; dl.Update()
        if '$' in g: rotulos[dl.ConnectorID] = g
    d.Update()
    for cid, g in rotulos.items():   # por SQL: la posición de los rótulos (la API no la expone)
        r.Execute(f"UPDATE t_diagramlinks SET Geometry='{g}' WHERE DiagramID={d.DiagramID} AND ConnectorID={cid}")
    r.ReloadDiagram(d.DiagramID)
    return r.GetDiagramByID(d.DiagramID)


def exportar(r, d, stem):
    """EMF (vectorial, va al documento) y PNG de control. El EMF de un diagrama tan alto ya trae su propio viewport,
    así que va tal cual (compatibilidad_emf.mjs solo hace falta cuando falta el viewport)."""
    pi = r.GetProjectInterface()
    r.ReloadDiagram(d.DiagramID)
    assert pi.PutDiagramImageToFile(d.DiagramGUID, str(DIAGRAMAS / f'{stem}.emf'), 0), f'No exportó {stem}.emf'
    assert pi.PutDiagramImageToFile(d.DiagramGUID, str(DIAGRAMAS / f'{stem}.png'), 1), f'No exportó {stem}.png'
    print('Exportado', stem, flush=True)


def correr(actores, simular):
    import win32com.client
    import sincronizar_documentacion as S
    from ea import navegacion_roles
    ruta_m = DIAGRAMAS / 'nav-franjas.json'
    manifiesto = json.loads(ruta_m.read_text(encoding='utf-8')) if ruta_m.exists() else {}
    planes = {}
    for actor in actores:
        paginas, enlaces = N.vista_rol(actor)
        ac = navegacion_roles.armar(actor, paginas, enlaces)
        planes[actor] = (paginas, enlaces, ac)
        print(f'{actor}: {ac["ancho"]} × {ac["alto"]}, {len(paginas)} cajas y {len(enlaces)} relaciones', flush=True)
    if simular: return
    errores = N.verificar()
    assert not errores, 'navegacion.py no coincide con el código:\n' + '\n'.join(errores)
    clave_reg = r'Software\Sparx Systems\EA400\EA\OPTIONS'
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, clave_reg, 0, winreg.KEY_READ | winreg.KEY_SET_VALUE) as k:
        antes, tipo_reg = winreg.QueryValueEx(k, 'FONTSIZE13')
        winreg.SetValueEx(k, 'FONTSIZE13', 0, tipo_reg, str(FUENTE_ROTULOS) if isinstance(antes, str) else FUENTE_ROTULOS)
    S.OUT.mkdir(parents=True, exist_ok=True)
    r = win32com.client.Dispatch('EA.Repository')
    try:
        assert r.OpenFile(str(EAPX)), 'EA no abrió el EAPX'
        for actor in actores:
            paginas, enlaces, ac = planes[actor]
            nombres_visibles = {l['enlace']: ''.join(l['rotulos']['nombre'][2])
                                for l in ac['lineas'] if l['rotulos']}
            pkg = paquete_actor(r, actor)
            el, conector = sincronizar(r, pkg, paginas, enlaces, nombres_visibles)
            for i in reversed(range(pkg.Packages.Count)):   # versiones anteriores de este script
                if pkg.Packages.GetAt(i).Name == SUBPAQUETE: pkg.Packages.DeleteAt(i, True)
            for i in reversed(range(pkg.Diagrams.Count)):
                if pkg.Diagrams.GetAt(i).Name.startswith(f'Diagrama de Navegacion - {actor} ('): pkg.Diagrams.DeleteAt(i, True)
            pkg.Packages.Refresh(); pkg.Diagrams.Refresh()
            nombre = f'Diagrama de Navegacion - {actor}'
            d = next((x for x in pkg.Diagrams if x.Name == nombre), None)
            if d is None: d = pkg.Diagrams.AddNew(nombre, 'Logical'); d.Update()
            d = dibujar(r, d, el, conector, paginas, ac, horizontal=True)
            for viejo in DIAGRAMAS.glob(f'nav-{actor.lower()}-[0-9][0-9].*'): viejo.unlink()
            stem = f'nav-{actor.lower()}'
            exportar(r, d, stem)
            xs = [x for x, _, _, _ in ac['cajas'].values()] + [p[0] for l in ac['lineas'] for p in l['puntos']]
            nombres = Counter(paginas[k][1] for k in ac['cajas'] if paginas[k][0] in ('cliente', 'ps', 'nota'))
            manifiesto[actor] = dict(stem=stem, cortes=[],
                                     arriba=round(min(y for _, y, _, _ in ac['cajas'].values()) + DESPLAZA, 1),
                                     abajo=round(max(y + h for _, y, _, h in ac['cajas'].values()) + DESPLAZA, 1),
                                     izquierda=round(min(xs) + DESPLAZA, 1), ancho=round(ac['ancho']),
                                     referencias={paginas[k][1]: round(y + DESPLAZA, 1) for k, (_, y, _, _) in ac['cajas'].items()
                                                  if paginas[k][0] in ('cliente', 'ps', 'nota') and nombres[paginas[k][1]] == 1})
            ruta_m.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding='utf-8')
    finally:
        r.CloseFile(); r.Exit()
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, clave_reg, 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, 'FONTSIZE13', 0, tipo_reg, antes)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    correr(args or list(N.DIAGRAMAS), '--simular' in sys.argv)
