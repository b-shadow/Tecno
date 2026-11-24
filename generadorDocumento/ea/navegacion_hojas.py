"""7.5 en Enterprise Architect: sincroniza los elementos de navegación de cada actor con navegacion.py (el modelo es el
del código) y dibuja cada hoja del documento como un diagrama propio, con el acomodo de acomodo_navegacion.py.

  python ea/navegacion_hojas.py                 # los cuatro actores
  python ea/navegacion_hojas.py Vendedor        # solo uno
  python ea/navegacion_hojas.py --simular       # sin EA: tamaños y letra impresa de cada hoja

En el EAPX, cada actor conserva su paquete «Navegacion <Actor>» con un solo elemento por página, formulario, server
page y tabla (los que ya no existen en el código se borran); las hojas son los diagramas «Diagrama de Navegacion -
<Actor> (n de N)» de ese paquete, que se rehacen en cada corrida (el diagrama general del actor se conserva). Una hoja muestra solo las relaciones de sus secciones: las demás quedan ocultas en ese
diagrama (siguen en el modelo). Salida: diagramas/nav-<actor>-NN.png/.emf y diagramas/nav-hojas.json (lo lee
insertar_navegacion.py). Cerrar EA antes de correrlo; respaldar el EAPX.
"""
import json
import sys
import winreg
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI)); sys.path.insert(0, str(AQUI.parent))
import acomodo_navegacion as A  # noqa: E402
import navegacion as N  # noqa: E402
from rutas import DIAGRAMAS  # noqa: E402

EAPX = AQUI / 'crm-p2.eapx'
ESTEREOTIPO = {'cliente': 'client page', 'externo': 'client page', 'form': 'Formulario', 'ps': 'server page', 'bd': 'database'}
VERDE_BD, GRIS_EXTERNO = 0xE0ECCF, 0xEEEEEE   # COLORREF 0xBBGGRR, como G07
SUBPAQUETE = 'Hojas 7.5'
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
        else:   # rótulo en dos renglones: un salto final deja ambos sobre la línea (EA centra el bloque del nombre)
            partes = A.partir(texto)
            clave = (el[a].ElementID, el[b].ElementID, 'Association', st, '\r\n'.join(partes) + ('\r\n' if len(partes) > 1 else ''))
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


def dibujar(r, pkg_hojas, nombre, el, conector, paginas, relaciones, ac):
    d = pkg_hojas.Diagrams.AddNew(nombre, 'Logical'); d.Update()
    ac = dict(ac, cajas={k: (x + DESPLAZA, y + DESPLAZA, w, h) for k, (x, y, w, h) in ac['cajas'].items()},
              lineas=[dict(l, puntos=[(px + DESPLAZA, py + DESPLAZA) for px, py in l['puntos']]) for l in ac['lineas']])
    for k, (x, y, w, h) in ac['cajas'].items():
        x, y, w, h = round(x), round(y), round(w), round(h)
        o = d.DiagramObjects.AddNew(f'l={x};r={x + w};t={-y};b={-(y + h)};', ''); o.ElementID = el[k].ElementID; o.Update()
        o.SetStyleEx('font', 'Calibri'); o.SetStyleEx('fontsz', '100')
        tipo = paginas[k][0]
        if tipo == 'bd': o.BackgroundColor = VERDE_BD
        if tipo == 'externo': o.BackgroundColor = GRIS_EXTERNO
        o.Update()
    d.Update(); r.ReloadDiagram(d.DiagramID); d = r.GetDiagramByID(d.DiagramID)
    por_id = {conector[l['enlace']]: l for l in ac['lineas']}
    centro = {el[k].ElementID: (x + w / 2, y + h / 2, x, y, w, h) for k, (x, y, w, h) in ac['cajas'].items()}
    for dl in d.DiagramLinks:
        l = por_id.get(dl.ConnectorID)
        if l is None: dl.IsHidden = True; dl.Update(); continue
        c = r.GetConnectorByID(dl.ConnectorID)
        pts = l['puntos']
        (sx, sy), (ex, ey) = pts[0], pts[-1]
        cs, ce = centro[c.ClientID], centro[c.SupplierID]
        lado = lambda px, py, b: 2 if px >= b[2] + b[4] - 1 else 4 if px <= b[2] + 1 else 3 if py >= b[3] + b[5] - 1 else 1
        dl.Geometry = (f'SX={round(sx - cs[0])};SY={round(cs[1] - sy)};EX={round(ex - ce[0])};EY={round(ce[1] - ey)};'   # y de EA hacia arriba
                       f'EDGE={lado(sx, sy, cs)};')
        if len(pts) > 2:
            dl.Style = 'Mode=3;EOID=;SOID=;Color=-1;LWidth=0;'
            dl.Path = ''.join(f'{round(px)}:{-round(py)};' for px, py in pts[1:-1])
        dl.Update()
    d.Update()
    return d


def correr(actores, simular):
    import win32com.client
    import sincronizar_documentacion as S
    manifiesto = json.loads((DIAGRAMAS / 'nav-hojas.json').read_text(encoding='utf-8')) if (DIAGRAMAS / 'nav-hojas.json').exists() else {}
    planes = {}
    for actor in actores:
        paginas, enlaces, secciones = N.hojas(actor)
        planes[actor] = (paginas, enlaces, A.paginar(paginas, enlaces, secciones))
        for n, (titulos, claves, rel, ac) in enumerate(planes[actor][2], 1):
            print(f'{actor} {n:2}: {10 * A.escala(ac["ancho"], ac["alto"]):4.1f} pt, {len(claves):2} cajas — {" + ".join(titulos)}')
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
            paginas, enlaces, hojas = planes[actor]
            pkg = paquete_actor(r, actor)
            el, conector = sincronizar(r, pkg, actor, paginas, enlaces)
            for i in reversed(range(pkg.Packages.Count)):   # versión anterior de este script
                if pkg.Packages.GetAt(i).Name == SUBPAQUETE: pkg.Packages.DeleteAt(i, True)
            for i in reversed(range(pkg.Diagrams.Count)):   # hojas de la corrida anterior (el diagrama general se conserva)
                if pkg.Diagrams.GetAt(i).Name.startswith(f'Diagrama de Navegacion - {actor} ('): pkg.Diagrams.DeleteAt(i, True)
            pkg.Packages.Refresh(); pkg.Diagrams.Refresh()
            sub = pkg   # mismo paquete que los elementos: EA no antepone «Navegacion <Actor>::» a los nombres
            for viejo in DIAGRAMAS.glob(f'nav-{actor.lower()}-[0-9][0-9].*'): viejo.unlink()
            registro, salida = [], []
            for n, (titulos, claves, rel, ac) in enumerate(hojas, 1):
                nombre = f'Diagrama de Navegacion - {actor} ({n} de {len(hojas)})'
                d = dibujar(r, sub, nombre, el, conector, paginas, rel, ac)
                stem = f'nav-{actor.lower()}-{n:02d}'
                S.export(r, d, stem, registro, 'navegacion-hojas')
                salida.append({'stem': stem, 'secciones': titulos, 'ancho': round(ac['ancho']), 'alto': round(ac['alto']),
                               'letra_pt': round(10 * A.escala(ac['ancho'], ac['alto']), 1)})
            manifiesto[actor] = salida
            (DIAGRAMAS / 'nav-hojas.json').write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding='utf-8')
    finally:
        r.CloseFile(); r.Exit()
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, clave_reg, 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, 'FONTSIZE13', 0, tipo_reg, antes)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    correr(args or list(N.DIAGRAMAS), '--simular' in sys.argv)
