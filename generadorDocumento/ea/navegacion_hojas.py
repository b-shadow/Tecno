"""7.5 en Enterprise Architect, como G07: un diagrama de navegación grande por actor («Diagrama de Navegacion -
<Actor>», en su paquete «Navegacion <Actor>») que el documento corta en franjas apaisadas.

  python ea/navegacion_hojas.py                 # los cuatro actores
  python ea/navegacion_hojas.py Vendedor        # solo uno
  python ea/navegacion_hojas.py --simular       # sin EA: tamaño, franjas y letra impresa de cada actor

Sincroniza los elementos del paquete con navegacion.py (el modelo es el del código: crea, actualiza y borra lo que
sobra), los ubica con ea/franjas_navegacion.py y escribe cada relación con sus quiebres por COM; la posición de sus
rótulos («estereotipo» arriba, texto abajo, junto a la caja) va directo en t_diagramlinks.Geometry porque la API no
la expone. Salida: diagramas/nav-<actor>.emf/.png y diagramas/nav-franjas.json (alturas de corte y referencias para
ubicar el diagrama dentro del EMF; lo lee insertar_navegacion.py). Cerrar EA antes de correrlo; respaldar el EAPX.
"""
import json
import sys
import winreg
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


def sincronizar(r, pkg, actor, paginas, enlaces):
    """Elementos y relaciones del paquete del actor = navegacion.py (crea, actualiza y borra lo que sobra)."""
    nombres = [v[1] for v in paginas.values()]
    assert len(nombres) == len(set(nombres)), f'{actor}: nombres repetidos en navegacion.py'
    existentes = {e.Name: e for e in pkg.Elements}
    el = {}
    for k, (tipo, nombre, at, op) in paginas.items():
        e = existentes.get(nombre)
        if e is not None and (e.Type == 'Actor') != (tipo == 'actor'): e = None
        if e is None:
            e = pkg.Elements.AddNew(nombre, 'Actor' if tipo == 'actor' else 'Class'); e.Update()
        if tipo != 'actor':
            e.Stereotype = ESTEREOTIPO[tipo]
            e.Notes = ('Server page: ' + (N.API.get(k) or N.INCLUIDAS.get(k, ('',))[0] + ' (parte compartida, «include»)')
                       if tipo == 'ps' else f'{ESTEREOTIPO[tipo]} de la navegación (Conallen), tomada del código.')
            e.Update()
            for i in reversed(range(e.Attributes.Count)): e.Attributes.DeleteAt(i, False)
            for i in reversed(range(e.Methods.Count)): e.Methods.DeleteAt(i, False)
            e.Attributes.Refresh(); e.Methods.Refresh()
            for i, a in enumerate(lista(at)):
                x = e.Attributes.AddNew(a.split('=')[0].strip(), ''); x.Visibility = 'Private'; x.Pos = i
                x.IsCollection = True; x.AllowDuplicates = True; x.Update()   # {bag}, como G07
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
            clave = (el[a].ElementID, el[b].ElementID, 'Association', st, texto if entre_paginas else '\r\n'.join(F.renglones(texto)))
        deseadas[clave] = (a, b, st, texto)
    conector = {}
    for e in el.values():
        for i in reversed(range(e.Connectors.Count)):
            c = e.Connectors.GetAt(i)
            if c.ClientID != e.ElementID or c.SupplierID not in vivos: continue
            clave = (c.ClientID, c.SupplierID, c.Type, c.Stereotype or '', c.Name or '')
            if clave in deseadas and clave not in conector.values(): conector[deseadas[clave]] = c.ConnectorID
            else: e.Connectors.DeleteAt(i, False)
        e.Connectors.Refresh()
    for clave, enlace in deseadas.items():
        if enlace in conector: continue
        cliente = next(e for e in el.values() if e.ElementID == clave[0])
        c = cliente.Connectors.AddNew(clave[4], clave[2]); c.SupplierID = clave[1]
        if clave[3]: c.Stereotype = clave[3]
        c.Direction = 'Source -> Destination' if clave[2] == 'Association' else 'Unspecified'
        c.Update(); conector[enlace] = c.ConnectorID
    return el, conector


DT_NOMBRE, DT_ESTEREOTIPO = 8, 10   # dónde pone EA los rótulos por omisión: nombre arriba, estereotipo abajo del ancla


def geometria(l, cs, ce):
    """Geometry de t_diagramlinks: extremos (SX/SY/EX/EY, y de EA hacia arriba) y rótulos movidos a su lugar.
    EA ancla los rótulos en el medio del tramo entre los dos últimos quiebres (o de la recta); OX/OY los corren desde ahí."""
    pts = l['puntos']
    (sx, sy), (ex, ey) = pts[0], pts[-1]
    lado = lambda px, py, b: 2 if px >= b[2] + b[4] - 1 else 4 if px <= b[2] + 1 else 3 if py >= b[3] + b[5] - 1 else 1
    g = f'SX={round(sx - cs[0])};SY={round(cs[1] - sy)};EX={round(ex - ce[0])};EY={round(ce[1] - ey)};EDGE={lado(sx, sy, cs)};'
    if not l['rotulos']: return g
    t = (pts[-3], pts[-2]) if len(pts) > 3 else (pts[0], pts[-1])   # EA: tramo entre los dos últimos quiebres
    ax, ay = (t[0][0] + t[1][0]) / 2, (t[0][1] + t[1][1]) / 2
    (stx, sty), w_st = l['rotulos']['estereotipo']
    x0, y_linea, hacia_der, filas = l['rotulos']['nombre']
    # bloque del texto debajo de la línea, alineado a la caja. Medido en el EMF de EA: el bloque empieza 7 u. arriba
    # del centro pedido; con varios renglones (ALN=0) su borde izquierdo queda en centro − CX + 128 − 47·renglones.
    # EA ajusta el texto al ancho CX: se le da holgura para que respete solo los saltos de renglón propios.
    n = max(1, len(filas)); largo = max([len(f) for f in filas] + [1])
    w_texto, w_nom = 5.0 * largo, 6.0 * largo + 14
    izq = x0 if hacia_der else x0 - w_texto
    nx = izq + w_nom - 128 + 47 * n if n > 1 else izq + w_texto / 2   # medido en el EMF para 2 y 3 renglones
    ny = y_linea + 3 + 7
    rot = lambda w, h, ox, oy: (f'CX={round(w)}:CY={round(h)}:OX={round(ox)}:OY={round(oy)}:HDN=0:BLD=0:ITA=0:UND=0:'
                                'CLR=-1:ALN={}:DIR=0:ROT=0;')
    lmt = rot(w_nom, 14 * n, nx - ax, ny - (ay - DT_NOMBRE)).format(0 if n > 1 else 1)
    lmb = rot(w_st + 14, 14, stx - ax, sty - (ay + DT_ESTEREOTIPO)).format(1)
    return g + f'$LLB=;LLT=;LMT={lmt}LMB={lmb}LRT=;LRB=;IRHS=;ILHS=;'


def dibujar(r, d, el, conector, paginas, ac):
    """Rehace el diagrama general del actor con el acomodo de franjas_navegacion."""
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
                                            *l['rotulos']['nombre'][2:]))
        por_id[conector[l['enlace']]] = dict(l, puntos=[mov(p) for p in l['puntos']], rotulos=rot)
    ids = [dl.ConnectorID for dl in d.DiagramLinks]
    faltan = set(por_id) - set(ids)
    assert not faltan, f'EA no mostró {len(faltan)} relaciones en el diagrama'
    rotulos = {}
    for dl in d.DiagramLinks:   # por COM: crea la fila de t_diagramlinks con extremos y quiebres
        l = por_id.get(dl.ConnectorID)
        if l is None: dl.IsHidden = True; dl.Update(); continue
        c = r.GetConnectorByID(dl.ConnectorID)
        g = geometria(l, centro[c.ClientID], centro[c.SupplierID])
        camino = ''.join(f'{round(px)}:{-round(py)};' for px, py in l['puntos'][1:-1])
        dl.Geometry = g.split('$')[0]
        if camino: dl.Style = 'Mode=3;EOID=;SOID=;Color=-1;LWidth=0;'; dl.Path = camino
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
    pi.PutDiagramImageToFile(d.DiagramGUID, str(DIAGRAMAS / f'{stem}.png'), 1)
    print('Exportado', stem, flush=True)


def correr(actores, simular):
    import win32com.client
    import sincronizar_documentacion as S
    import franjas_navegacion as F
    ruta_m = DIAGRAMAS / 'nav-franjas.json'
    manifiesto = json.loads(ruta_m.read_text(encoding='utf-8')) if ruta_m.exists() else {}
    planes = {}
    for actor in actores:
        paginas, enlaces, secciones = N.hojas(actor)
        ac, cortes, escala = F.armar_en_franjas(paginas, enlaces, secciones, con_titulo_75=(actor == list(N.DIAGRAMAS)[0]))
        planes[actor] = (paginas, enlaces, ac, cortes, escala)
        print(f'{actor}: {round(ac["ancho"])} x {round(ac["alto"])}, {len(cortes) - 1} franjas, letra impresa {10 * escala:.1f} pt')
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
            paginas, enlaces, ac, cortes, escala = planes[actor]
            pkg = paquete_actor(r, actor)
            el, conector = sincronizar(r, pkg, actor, paginas, enlaces)
            for i in reversed(range(pkg.Packages.Count)):   # versiones anteriores de este script
                if pkg.Packages.GetAt(i).Name == SUBPAQUETE: pkg.Packages.DeleteAt(i, True)
            for i in reversed(range(pkg.Diagrams.Count)):
                if pkg.Diagrams.GetAt(i).Name.startswith(f'Diagrama de Navegacion - {actor} ('): pkg.Diagrams.DeleteAt(i, True)
            pkg.Packages.Refresh(); pkg.Diagrams.Refresh()
            nombre = f'Diagrama de Navegacion - {actor}'
            d = next((x for x in pkg.Diagrams if x.Name == nombre), None)
            if d is None: d = pkg.Diagrams.AddNew(nombre, 'Logical'); d.Update()
            d = dibujar(r, d, el, conector, paginas, ac)
            for viejo in DIAGRAMAS.glob(f'nav-{actor.lower()}-[0-9][0-9].*'): viejo.unlink()
            stem = f'nav-{actor.lower()}'
            exportar(r, d, stem)
            xs = [x for x, _, _, _ in ac['cajas'].values()] + [p[0] for l in ac['lineas'] for p in l['puntos']]
            manifiesto[actor] = dict(stem=stem, cortes=[round(c + DESPLAZA, 1) for c in cortes],
                                     arriba=round(min(y for _, y, _, _ in ac['cajas'].values()) + DESPLAZA, 1),
                                     abajo=round(max(y + h for _, y, _, h in ac['cajas'].values()) + DESPLAZA, 1),
                                     izquierda=round(min(xs) + DESPLAZA, 1), ancho=round(ac['ancho']), letra_pt=round(10 * escala, 1),
                                     referencias={paginas[k][1]: round(y + DESPLAZA, 1) for k, (_, y, _, _) in ac['cajas'].items()
                                                  if paginas[k][0] in ('cliente', 'ps')})
            ruta_m.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding='utf-8')
    finally:
        r.CloseFile(); r.Exit()
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, clave_reg, 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, 'FONTSIZE13', 0, tipo_reg, antes)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    correr(args or list(N.DIAGRAMAS), '--simular' in sys.argv)
