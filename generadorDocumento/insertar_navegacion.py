"""Inserta vistas vectoriales de navegación en la sección apaisada 7.5 del maestro."""
import argparse
import copy
import json
import struct
import zipfile
from itertools import count, pairwise
from pathlib import Path
from lxml import etree as E
import actualizar_documento as D
import navegacion as N
from rutas import DOCUMENTO

V, R, O = 'urn:schemas-microsoft-com:vml', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships', 'urn:schemas-microsoft-com:office:office'
PR, CT = 'http://schemas.openxmlformats.org/package/2006/relationships', 'http://schemas.openxmlformats.org/package/2006/content-types'
CM_PT = 28.3465
ANCHO_CM = 25.9                 # carta apaisada con 1 cm de margen lateral
ALTO_PRIMERA_PT = 418           # deja sitio para los encabezados de 7.5 y 7.5.1
ALTO_SIGUIENTES_PT = 485        # caja útil apaisada de Word, con holgura para el párrafo


def salto_antes(p):
    pr = p.find('w:pPr', D.NS)
    if pr is None: pr = E.Element(D.q('pPr')); p.insert(0, pr)
    if pr.find('w:pageBreakBefore', D.NS) is not None: return
    estilo = pr.find('w:pStyle', D.NS)
    pr.insert(0 if estilo is None else list(pr).index(estilo) + 1, E.Element(D.q('pageBreakBefore')))


def leer_emf(ruta):
    """Límites exportados y rectángulos de texto con sus orígenes lógicos de EA."""
    b = ruta.read_bytes()
    limites = struct.unpack_from('<4i', b, 8)
    textos, pos = [], 0
    while pos + 8 <= len(b):
        tipo, largo = struct.unpack_from('<II', b, pos)
        if tipo == 84:   # EMR_EXTTEXTOUTW
            caja = struct.unpack_from('<4i', b, pos + 8)
            x, y = struct.unpack_from('<2i', b, pos + 36)
            n, off = struct.unpack_from('<II', b, pos + 44)
            texto = b[pos + off: pos + off + 2 * n].decode('utf-16le', 'replace')
            textos.append((texto, caja, (x, -y)))
        pos += largo
    return limites, textos


def franjas_actor(ruta, actor):
    from ea.navegacion_administrador import ALTURAS_DE_CORTE
    from ea.navegacion_hojas import DESPLAZA
    from ea.navegacion_roles import armar

    limites, textos = leer_emf(ruta)
    origenes = {(x - caja[0], y - caja[1]) for _, caja, (x, y) in textos}
    assert len(origenes) == 1, f'{ruta.name}: no se pudo identificar el origen de coordenadas'
    ox, oy = origenes.pop()
    dx, dy = DESPLAZA - ox, DESPLAZA - oy
    paginas, enlaces = N.vista_rol(actor)
    plano = armar(actor, paginas, enlaces)
    protegidos = [caja for _, caja, _ in textos]
    for clave, (x, y, w, h) in plano['cajas'].items():
        caja = (x + dx, y + dy, x + dx + w, y + dy + h)
        titulo = paginas[clave][1]
        assert any(t == titulo and caja[0] <= (r[0] + r[2]) / 2 <= caja[2] + 4
                   and caja[1] <= r[1] <= caja[3] + 16 for t, r, _ in textos), (
                       f'{ruta.name}: la posición de {titulo} no coincide con el generador de EA')
        protegidos.append(caja)

    izq, arriba, der, abajo = limites
    escala = ANCHO_CM * CM_PT / (der - izq)
    aprobados = [arriba, *(y + dy for y in ALTURAS_DE_CORTE), abajo]
    if actor == 'Administrador' and all(all(not r[1] - 9 < y < r[3] + 9 for r in protegidos) for y in aprobados[1:-1]) and all(
        0 < (fin - inicio) * escala <= (ALTO_PRIMERA_PT if inicio == arriba else ALTO_SIGUIENTES_PT)
        for inicio, fin in pairwise(aprobados)
    ):
        return limites, [(izq, inicio, der, fin) for inicio, fin in pairwise(aprobados)]
    candidatos = [y for y in range(arriba + 8, abajo, 8)
                  if all(not r[1] - 9 < y < r[3] + 9 for r in protegidos)]
    trazos = [(min(y0, y1) + dy, max(y0, y1) + dy) for linea in plano['lineas']
              for (_, y0), (_, y1) in pairwise(linea['puntos'])]
    # Entre los planes que requieren menos páginas, favorece franjas de tamaño
    # parecido y cortes que interrumpan menos tramos.
    costos = {arriba: (0, 0)}
    anterior = {}
    for fin in [*candidatos, abajo]:
        cruces = sum(a < fin < b for a, b in trazos) if fin != abajo else 0
        for inicio, (n, costo) in costos.items():
            limite = ALTO_PRIMERA_PT if inicio == arriba else ALTO_SIGUIENTES_PT
            alto = (fin - inicio) * escala
            if alto > limite:
                continue
            alternativa = (n + 1, costo + (limite - alto) ** 2 + 30 * cruces)
            if fin not in anterior or alternativa < mejor:
                mejor = alternativa
                anterior[fin] = inicio
        if fin in anterior:
            costos[fin] = mejor
    if abajo not in anterior:
        raise ValueError(f'{ruta.name}: no se encontraron franjas que entren en la página sin partir cajas o textos')
    cortes = [abajo]
    while cortes[-1] != arriba:
        cortes.append(anterior[cortes[-1]])
    cortes.reverse()
    return limites, [(izq, a, der, b) for a, b in pairwise(cortes)]


def figura(plantilla, rid, forma_id, titulo, limites, recorte, escala, salto=False):
    _, arriba, _, abajo = limites
    x0, y0, x1, y1 = recorte
    p = copy.deepcopy(plantilla)
    for s in p.findall('.//w:sectPr', D.NS):
        s.getparent().remove(s)
    forma = p.find(f'.//{{{V}}}shape')
    forma.set('id', forma_id)
    forma.set('style', f'width:{(x1 - x0) * escala:.2f}pt;height:{(y1 - y0) * escala:.2f}pt')
    im = forma.find(f'{{{V}}}imagedata')
    for k in list(im.attrib):
        if k.startswith('crop'):
            del im.attrib[k]
    im.set(f'{{{R}}}id', rid)
    im.set(f'{{{O}}}title', titulo)
    for lado, fraccion in {'top': (y0 - arriba) / (abajo - arriba),
                           'bottom': (abajo - y1) / (abajo - arriba)}.items():
        if fraccion > 0:
            im.set('crop' + lado, f'{round(fraccion * 65536)}f')
    if salto:
        salto_antes(p)
    return p


def main(path, actores):
    with zipfile.ZipFile(path) as z:
        partes = {n: z.read(n) for n in z.namelist()}
    root = E.fromstring(partes['word/document.xml'])
    body = root.find('w:body', D.NS)
    guardia = D.protected(body)
    rels, tipos = E.fromstring(partes['word/_rels/document.xml.rels']), E.fromstring(partes['[Content_Types].xml'])
    franjas = json.loads((D.DOC / 'diagramas' / 'nav-franjas.json').read_text(encoding='utf-8'))
    items = list(body)
    estilo = lambda e: (e.find('.//w:pStyle', D.NS).get(D.q('val')) if e.find('.//w:pStyle', D.NS) is not None else '')
    titulo = lambda e, t: D.txt(e).startswith(t) and not estilo(e).startswith('TDC')
    a = next(i for i, e in enumerate(items) if titulo(e, '7.5. Diseño de Navegación'))
    b = next(i for i in range(a, len(items)) if titulo(items[i], '7.6.'))
    assert items[b - 1].find('.//w:sectPr', D.NS) is not None, '7.5 ya no termina en su sección apaisada'
    encabezados = {actor: next(i for i in range(a + 1, b) if titulo(items[i], f'7.5.{n}. Diagrama de Navegación del {actor}'))
                   for n, actor in enumerate(N.DIAGRAMAS, 1)}
    plantilla = next(e for e in items[a + 1:b] if e.find(f'.//{{{V}}}imagedata') is not None)
    ids_actuales = {forma.get('id') for forma in body.iter(f'{{{V}}}shape')}
    ids_libres = (forma_id for numero in count(9501)
                  if (forma_id := f'_x0000_i{numero}') not in ids_actuales)
    n = 0
    for actor in actores:
        i = list(N.DIAGRAMAS).index(actor)
        inicio = encabezados[actor] + 1
        fin = encabezados[list(N.DIAGRAMAS)[i + 1]] if i + 1 < len(N.DIAGRAMAS) else b - 1
        viejo = items[inicio:fin]
        f = franjas[actor]
        emf = D.DOC / 'diagramas' / f'{f["stem"]}.emf'
        rid = f'rIdNav{i + 1}'
        for rel in rels.findall(f'{{{PR}}}Relationship'):
            if rel.get('Id') == rid:
                rels.remove(rel)
        E.SubElement(rels, f'{{{PR}}}Relationship', Id=rid, Type=R + '/image', Target=f'media/{f["stem"]}.emf')
        partes[f'word/media/{f["stem"]}.emf'] = emf.read_bytes()
        nuevo = []
        if actor != 'Administrador':
            salto_antes(items[encabezados[actor]])
        limites, recortes = franjas_actor(emf, actor)
        escala = ANCHO_CM * CM_PT / (limites[2] - limites[0])
        for j, recorte in enumerate(recortes, 1):
            n += 1
            nuevo.append(figura(plantilla, rid, next(ids_libres), f'{f["stem"]} ({j} de {len(recortes)})',
                                 limites, recorte, escala, salto=(j > 1)))
        for e in viejo:
            body.remove(e)
        pos = list(body).index(items[encabezados[actor]]) + 1
        for k, e in enumerate(nuevo):
            body.insert(pos + k, e)

    assert D.protected(body) == guardia, 'Capítulo IV modificado'
    if not any(x.get('Extension') == 'emf' for x in tipos):
        E.SubElement(tipos, f'{{{CT}}}Default', Extension='emf', ContentType='image/x-emf')
    xml = lambda x: E.tostring(x, xml_declaration=True, encoding='UTF-8', standalone=True)
    partes.update({'word/document.xml': xml(root), 'word/_rels/document.xml.rels': xml(rels), '[Content_Types].xml': xml(tipos)})
    tmp = path.with_name(path.stem + '.nav.tmp.docx')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for nombre, datos in partes.items(): z.writestr(nombre, datos)
    tmp.replace(path)
    print(f'7.5: {len(actores)} diagramas actualizados, {n} vistas')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument('--administrador', action='store_true', help='actualiza únicamente la sección 7.5.1')
    grupo.add_argument('--actor', action='append', choices=N.DIAGRAMAS, help='actor a actualizar, se puede repetir')
    parser.add_argument('--docx', type=Path, default=DOCUMENTO, help='documento maestro o copia de revisión')
    args = parser.parse_args()
    actores = ['Administrador'] if args.administrador else args.actor or list(N.DIAGRAMAS)
    main(args.docx, actores)
