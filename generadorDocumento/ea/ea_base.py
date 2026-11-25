"""Base genérica de Enterprise Architect 15 Trial (COM, EA.Repository) para los diagramas del documento P2:
clase EA (paquetes, elementos, conectores, exportación PNG + EMF) y acomodo automático de cajas.
Adaptada del generador del P1 (carpeta del curso); aquí no depende de nada fuera de esta carpeta. ea_p2.py fija EAPX y SALIDA."""
import math, pathlib, random, shutil
import win32com.client

SALIDA = None   # carpeta de PNG/EMF; la fija ea_p2.py
EAPX = None     # repositorio .eapx; lo fija ea_p2.py
from rutas import EA_BASE as BASE  # noqa: E402  (plantilla vacía de EA: su ruta está en rutas.py)

# Visibilidad de miembros en un diagrama (t_diagramobjects.ObjectStyle): oculta atributos y operaciones.
OCULTO = 'AttPub=0;AttPri=0;AttPro=0;AttPkg=0;AttCustom=0;OpCustom=0;OpPub=0;OpPri=0;OpPro=0;OpPkg=0;'


def efectivo(w, h):
    """Letra impresa (pt) de un diagrama de w×h unidades de EA: el PNG sale al doble y el texto de EA mide ~20 px.
    Se toma la mejor orientación: carta apaisada (650×428 pt útiles bajo el rótulo) o vertical (468×588 pt)."""
    w, h = 2 * w + 80, 2 * h + 80
    return 20 * max(min(650 / w, 428 / h), min(468 / w, 588 / h))


def _cruzan(p1, p2, p3, p4):
    o = lambda a, b, c: (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return o(p3, p4, p1) * o(p3, p4, p2) < 0 and o(p1, p2, p3) * o(p1, p2, p4) < 0


def _atraviesa(p1, p2, r):
    """¿El segmento p1-p2 pasa por el rectángulo r = (x0, y0, x1, y1)? (recorte de Liang-Barsky)"""
    t0, t1, dx, dy = 0.0, 1.0, p2[0] - p1[0], p2[1] - p1[1]
    for p, q in ((-dx, p1[0] - r[0]), (dx, r[2] - p1[0]), (-dy, p1[1] - r[1]), (dy, r[3] - p1[1])):
        if p == 0:
            if q < 0: return False
        else:
            t = q / p
            if p < 0: t0 = max(t0, t)
            else: t1 = min(t1, t)
            if t0 > t1: return False
    return True


def _grilla(asig, medidas, cols, gx, gy):
    """Posiciones de una asignación {nodo: (fila, col)}: cada columna y fila mide lo que su caja más grande;
    las filas y columnas vacías no ocupan lugar."""
    anchos, altos = {}, {}
    for n, (f, c) in asig.items():
        anchos[c] = max(anchos.get(c, 0), medidas[n][0]); altos[f] = max(altos.get(f, 0), medidas[n][1])
    xs, x = {}, 30
    for c in sorted(anchos): xs[c] = x; x += anchos[c] + gx
    ys, y = {}, 30
    for f in sorted(altos): ys[f] = y; y += altos[f] + gy
    pos = {n: (xs[c] + (anchos[c] - medidas[n][0]) // 2, ys[f], *medidas[n]) for n, (f, c) in asig.items()}
    return pos, x - gx - 30, y - gy - 30


def _costo(pos, aristas):
    cen = {n: (x + w / 2, y + h / 2) for n, (x, y, w, h) in pos.items()}
    cajas = {n: (x - 8, y - 8, x + w + 8, y + h + 8) for n, (x, y, w, h) in pos.items()}
    atraviesan = cruces = largo = 0
    for i, (a, b) in enumerate(aristas):
        largo += abs(cen[a][0] - cen[b][0]) + abs(cen[a][1] - cen[b][1])
        for n, r in cajas.items():
            if n not in (a, b) and _atraviesa(cen[a], cen[b], r): atraviesan += 1
        for c, d in aristas[i + 1:]:
            if len({a, b, c, d}) == 4 and _cruzan(cen[a], cen[b], cen[c], cen[d]): cruces += 1
    return atraviesan, cruces, largo


def acomodar(medidas, aristas, gx=60, gy=70, semilla=5, sin_atravesar=False):
    """Ubica las cajas en una grilla para que ninguna línea atraviese una caja, se crucen lo menos posible y queden
    cortas (recocido simulado), y elige el número de columnas que da la letra impresa más grande.
    medidas: {nodo: (w, h)}; aristas: [(a, b)]. Devuelve ({nodo: (x, y, w, h)}, ancho, alto)."""
    nodos = list(medidas)
    aristas = list(dict.fromkeys(tuple(sorted(e)) for e in aristas if e[0] != e[1] and e[0] in medidas and e[1] in medidas))
    mejor_r, mejor_puntaje = None, None
    for cols in range(2, min(7, len(nodos)) + 1):
        filas = -(-len(nodos) // cols) + 1   # una fila de holgura para separar lo que se cruza
        celdas = [(f, c) for f in range(filas) for c in range(cols)]
        rnd = random.Random(semilla)
        asig = dict(zip(nodos, celdas))
        libres = celdas[len(nodos):]

        def puntaje(a):
            pos, w, h = _grilla(a, medidas, cols, gx, gy)
            at, cr, lg = _costo(pos, aristas)
            return (50000 if sin_atravesar else 4000) * at + 700 * cr + 0.5 * lg + 2.0 * (w + h), (pos, w, h, at, cr)

        actual, info = puntaje(asig)
        mejor_c, mejor_a = actual, dict(asig)
        T = 3000.0
        for _ in range(2500):
            a = dict(asig); n = rnd.choice(nodos)
            if libres and rnd.random() < 0.35:
                k = rnd.randrange(len(libres)); a[n], nuevo_libre = libres[k], a[n]
            else:
                m = rnd.choice(nodos); a[n], a[m] = a[m], a[n]; nuevo_libre = None
            c_, _ = puntaje(a)
            if c_ < actual or rnd.random() < math.exp((actual - c_) / T):
                asig, actual = a, c_
                if nuevo_libre is not None: libres[k] = nuevo_libre
                if c_ < mejor_c: mejor_c, mejor_a = c_, dict(a)
            T *= 0.996
        _, (pos, w, h, at, cr) = puntaje(mejor_a)
        p = (-at, efectivo(w, h) - 0.4 * cr) if sin_atravesar else efectivo(w, h) - 3 * at - 0.4 * cr
        if mejor_puntaje is None or p > mejor_puntaje:
            mejor_puntaje, mejor_r = p, (pos, w, h, at, cr)
    pos, w, h, at, cr = mejor_r
    return pos, w, h, at, cr


def despejar_cajas(pos, aristas):
    """Desplaza cajas a huecos libres para que las relaciones no pasen por los atributos de otra clase."""
    pos = dict(pos)
    aristas = list(dict.fromkeys(tuple(sorted(e)) for e in aristas if e[0] != e[1]))
    def dimensiones(p):
        return max(x + w for x, y, w, h in p.values()), max(y + h for x, y, w, h in p.values())
    def puntuacion(p):
        at, cr, lg = _costo(p, aristas)
        w, h = dimensiones(p)
        return at, cr, w * h, lg
    for _ in range(12):
        actual = puntuacion(pos)
        if actual[0] == 0: break
        mejor, mejor_pos = actual, None
        xs = {x for x, _, _, _ in pos.values()}
        ys = {y for _, y, _, _ in pos.values()}
        xs |= {min(xs) - max(w for _, _, w, _ in pos.values()) - 35,
               max(x + w for x, _, w, _ in pos.values()) + 35}
        ys |= {min(ys) - max(h for _, _, _, h in pos.values()) - 35,
               max(y + h for _, y, _, h in pos.values()) + 35}
        for n, (x, y, w, h) in pos.items():
            candidatos = {(xx, y) for xx in xs | {x - w - 35, x + w + 35}}
            candidatos |= {(x, yy) for yy in ys | {y - h - 35, y + h + 35}}
            candidatos |= {(xx, yy) for xx in xs for yy in ys}
            for xx, yy in candidatos:
                if (xx, yy) == (x, y): continue
                if any(xx < ox + ow + 25 and xx + w + 25 > ox and yy < oy + oh + 25 and yy + h + 25 > oy
                       for k, (ox, oy, ow, oh) in pos.items() if k != n): continue
                propuesta = {**pos, n: (xx, yy, w, h)}
                nota = puntuacion(propuesta)
                if nota < mejor: mejor, mejor_pos = nota, propuesta
        if mejor_pos is None: break
        pos = mejor_pos
    dx, dy = 30 - min(x for x, _, _, _ in pos.values()), 30 - min(y for _, y, _, _ in pos.values())
    pos = {n: (x + dx, y + dy, w, h) for n, (x, y, w, h) in pos.items()}
    w, h = dimensiones(pos)
    at, cr, _ = _costo(pos, aristas)
    return pos, w, h, at, cr


class EA:
    def __init__(self, nombre_modelo):
        shutil.copy(BASE, EAPX)
        self.r = win32com.client.Dispatch('EA.Repository')
        if not self.r.OpenFile(str(EAPX)): raise SystemExit('EA no abrió ' + str(EAPX))
        self.pi = self.r.GetProjectInterface()
        self.modelo = self.r.Models.AddNew(nombre_modelo, ''); self.modelo.Update()
        self.exportados = []

    @classmethod
    def abrir_existente(cls):
        """Amplía el proyecto P2 sin copiar EABase ni borrar los diagramas editados a mano."""
        self = cls.__new__(cls)
        self.r = win32com.client.Dispatch('EA.Repository')
        if not self.r.OpenFile(str(EAPX)): raise SystemExit('EA no abrió ' + str(EAPX))
        self.pi = self.r.GetProjectInterface()
        self.modelo = next((m for m in self.r.Models if len(m.Packages)), self.r.Models.GetAt(0))
        self.exportados = []
        return self

    def cerrar(self):
        self.r.CloseFile(); self.r.Exit()

    def paquete(self, padre, nombre):
        p = padre.Packages.AddNew(nombre, ''); p.Update(); return p

    def elemento(self, pkg, nombre, tipo, st='', padre=None, notas=''):
        e = pkg.Elements.AddNew(nombre, tipo)
        if st: e.Stereotype = st
        if notas: e.Notes = notas
        e.Update()
        if padre is not None: e.ParentID = padre.ElementID; e.Update()
        return e

    def diagrama(self, pkg, nombre, tipo):
        d = pkg.Diagrams.AddNew(nombre, tipo); d.Update(); return d

    def poner(self, d, el, x, y, w, h, seq=None, plegado=False):
        """plegado: la clase se muestra solo con su nombre en este diagrama (sus miembros están en otra figura)."""
        o = d.DiagramObjects.AddNew(f'l={x};r={x + w};t={y};b={y + h};', '')
        o.ElementID = el.ElementID if hasattr(el, 'ElementID') else el.Element.ElementID
        if seq is not None: o.Sequence = seq
        o.Update()
        if plegado:
            self.r.Execute(f"UPDATE t_diagramobjects SET ObjectStyle='{OCULTO}' WHERE Diagram_ID={d.DiagramID} "
                           f"AND Object_ID={o.ElementID}")
        return o

    def conector(self, a, b, tipo, nombre='', st='', dirigido=False, card=None):
        a = a if hasattr(a, 'Connectors') and not hasattr(a, 'Packages') else a.Element
        b = b if hasattr(b, 'ElementID') else b.Element
        c = a.Connectors.AddNew(nombre, tipo); c.SupplierID = b.ElementID
        if st: c.Stereotype = st
        if dirigido: c.Direction = 'Source -> Destination'
        c.Update()
        if card:
            c.ClientEnd.Cardinality, c.SupplierEnd.Cardinality = card
            c.ClientEnd.Update(); c.SupplierEnd.Update(); c.Update()
        return c

    def mensaje_seq(self, d, a, b, texto, n, tipo='call', args=''):
        """Mensajes UML de secuencia, con la misma notación que el generador del P1."""
        c = a.Connectors.AddNew(texto, 'Sequence'); c.SupplierID = b.ElementID
        c.DiagramID = d.DiagramID; c.SequenceNo = n; c.Update()
        p1, p3 = ('Asynchronous', 'Signal') if tipo == 'signal' else ('Synchronous', 'Call')
        p2 = f'retval=void;params={args};paramsDlg={args};' if args else ''
        self.r.Execute(f"UPDATE t_connector SET PDATA1='{p1}', PDATA2='{p2}', PDATA3='{p3}', "
                       f"PDATA4='{int(tipo == 'return')}', StateFlags='IsReturn={str(tipo == 'return').lower()};' "
                       f'WHERE Connector_ID={c.ConnectorID}')
        return c

    def mensaje_com(self, d, enlace, a, b, texto, numero, n, apilado, color=0x446688):
        """Mensaje numerado unido a su enlace de comunicación, como en el P1."""
        c = a.Connectors.AddNew(texto, 'Collaboration'); c.SupplierID = b.ElementID
        c.DiagramID = d.DiagramID; c.SequenceNo = n
        c.Direction = 'Source -> Destination'; c.Color = color; c.Update()
        sy = 18 + 30 * apilado
        self.r.Execute(f"UPDATE t_connector SET PDATA1='Synchronous', PDATA3='Call', PDATA4='{numero}', "
                       f"PDATA5='SX=-15;SY={sy};EX=15;EY={sy};EDGE=2;', "
                       f"SourceIsAggregate={enlace.ConnectorID}, RouteStyle=1, DestIsNavigable=TRUE, "
                       f"StateFlags='IsReturn=false;', SourceTS='instance', DestTS='instance' "
                       f'WHERE Connector_ID={c.ConnectorID}')
        return c

    def exportar(self, d, archivo):
        d.Update(); self.r.ReloadDiagram(d.DiagramID)
        ruta = SALIDA / archivo
        if not self.pi.PutDiagramImageToFile(d.DiagramGUID, str(ruta), 1): raise SystemExit('no se exportó ' + archivo)
        # EMF (vectorial): word_export.ps1 lo pone en lugar del PNG para que el PDF y la impresión salgan nítidos
        if not self.pi.PutDiagramImageToFile(d.DiagramGUID, str(ruta.with_suffix('.emf')), 0): raise SystemExit('no se exportó EMF ' + archivo)
        self.exportados.append(archivo); print('  ', archivo)

