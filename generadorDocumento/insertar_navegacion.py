"""7.5 del maestro, como G07: un diagrama de navegación grande por actor (ea/navegacion_hojas.py) cortado en franjas
apaisadas, una por página, con el título 7.5.n solo en la primera. Cada franja es el mismo EMF vectorial recortado
(croptop / cropbottom de VML) en las alturas de diagramas/nav-franjas.json, que caen en huecos sin cajas: las
relaciones siguen de una página a la siguiente. Conserva la sección apaisada de 1 cm de margen lateral; lo demás del
maestro (capítulo IV incluido) no se toca. Luego: limpiar_medios_docx.py y exportar.ps1.
"""
import copy
import json
import struct
import zipfile
from lxml import etree as E
import actualizar_documento as D
import navegacion as N

V, R, O = 'urn:schemas-microsoft-com:vml', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships', 'urn:schemas-microsoft-com:office:office'
PR, CT = 'http://schemas.openxmlformats.org/package/2006/relationships', 'http://schemas.openxmlformats.org/package/2006/content-types'
CM_PT = 28.3465
ANCHO_CM = 25.9                 # carta apaisada con 1 cm de margen lateral
TITULO_EMF = 9.5                # el texto del título de una caja empieza 9,5 u. bajo su borde (EA, Calibri 10)


def salto_antes(p):
    pr = p.find('w:pPr', D.NS)
    if pr is None: pr = E.Element(D.q('pPr')); p.insert(0, pr)
    if pr.find('w:pageBreakBefore', D.NS) is not None: return
    estilo = pr.find('w:pStyle', D.NS)
    pr.insert(0 if estilo is None else list(pr).index(estilo) + 1, E.Element(D.q('pageBreakBefore')))


def mapa_emf(ruta, referencias):
    """(arriba, abajo, ancho, desfase) del EMF: y del EMF = y del diagrama − desfase. El desfase se mide con los textos
    de los títulos de las cajas (registros EMR_EXTTEXTOUTW) contra su posición conocida en el diagrama."""
    b = ruta.read_bytes()
    izq, arriba, der, abajo = struct.unpack_from('<4i', b, 8)
    medidas, pos = [], 0
    while pos + 8 <= len(b):
        tipo, largo = struct.unpack_from('<II', b, pos)
        if tipo == 84:   # EMR_EXTTEXTOUTW
            sup = struct.unpack_from('<4i', b, pos + 8)[1]
            n, off = struct.unpack_from('<II', b, pos + 44)
            texto = b[pos + off: pos + off + 2 * n].decode('utf-16le', 'replace')
            if texto in referencias: medidas.append(referencias[texto] + TITULO_EMF - sup)
        pos += largo
    assert len(medidas) >= 3 and max(medidas) - min(medidas) < 4, f'{ruta.name}: no se pudo ubicar el diagrama en el EMF'
    return arriba, abajo, der - izq, sum(medidas) / len(medidas)


def main():
    path, root, body = D.doc_read()
    guardia = D.protected(body)
    with zipfile.ZipFile(path) as z: partes = {n: z.read(n) for n in z.namelist()}
    rels, tipos = E.fromstring(partes['word/_rels/document.xml.rels']), E.fromstring(partes['[Content_Types].xml'])
    franjas = json.loads((D.DOC / 'diagramas' / 'nav-franjas.json').read_text(encoding='utf-8'))
    items = list(body)
    estilo = lambda e: (e.find('.//w:pStyle', D.NS).get(D.q('val')) if e.find('.//w:pStyle', D.NS) is not None else '')
    titulo = lambda e, t: D.txt(e).startswith(t) and not estilo(e).startswith('TDC')
    a = next(i for i, e in enumerate(items) if titulo(e, '7.5. Diseño de Navegación'))
    b = next(i for i in range(a, len(items)) if titulo(items[i], '7.6.'))
    viejo = items[a + 1:b - 1]
    assert items[b - 1].find('.//w:sectPr', D.NS) is not None, '7.5 ya no termina en su sección apaisada'
    plantilla = next(e for e in viejo if e.find(f'.//{{{V}}}imagedata') is not None)
    encabezados = {actor: next(e for e in viejo if D.txt(e).startswith(f'7.5.{n}. Diagrama de Navegación del {actor}'))
                   for n, actor in enumerate(N.DIAGRAMAS, 1)}
    for rel in rels.findall(f'{{{PR}}}Relationship'):   # imágenes de corridas anteriores de este script
        if rel.get('Id', '').startswith('rIdNav'): rels.remove(rel)

    nuevo, n = [], 0
    for i, actor in enumerate(N.DIAGRAMAS):
        enc = copy.deepcopy(encabezados[actor])
        if i: salto_antes(enc)
        nuevo.append(enc)
        f = franjas[actor]
        emf = D.DOC / 'diagramas' / f'{f["stem"]}.emf'
        rid = f'rIdNav{i + 1}'
        E.SubElement(rels, f'{{{PR}}}Relationship', Id=rid, Type=R + '/image', Target=f'media/{f["stem"]}.emf')
        partes[f'word/media/{f["stem"]}.emf'] = emf.read_bytes()
        arriba, abajo, ancho, desfase = mapa_emf(emf, f['referencias'])
        alto = abajo - arriba
        cortes = f['cortes']
        for j, (y0, y1) in enumerate(zip(cortes, cortes[1:])):
            e0 = arriba if j == 0 else y0 - desfase                       # la primera franja lleva el marco «class …»
            e1 = abajo if j == len(cortes) - 2 else y1 - desfase
            sup, inf = (e0 - arriba) / alto, (abajo - e1) / alto
            n += 1
            p = copy.deepcopy(plantilla)
            for s in p.findall('.//w:sectPr', D.NS): s.getparent().remove(s)
            forma = p.find(f'.//{{{V}}}shape')
            forma.set('id', f'_x0000_i{9500 + n}')
            forma.set('style', f'width:{ANCHO_CM * CM_PT:.2f}pt;height:{ANCHO_CM * (e1 - e0) / ancho * CM_PT:.2f}pt')
            im = forma.find(f'{{{V}}}imagedata')
            for k in list(im.attrib):
                if k.startswith('crop'): del im.attrib[k]
            im.set(f'{{{R}}}id', rid); im.set(f'{{{O}}}title', f'{f["stem"]} ({j + 1} de {len(cortes) - 1})')
            if sup > 0: im.set('croptop', f'{round(sup * 65536)}f')
            if inf > 0: im.set('cropbottom', f'{round(inf * 65536)}f')
            if j: salto_antes(p)
            nuevo.append(p)
    for e in viejo: body.remove(e)
    pos = list(body).index(items[a]) + 1
    for k, e in enumerate(nuevo): body.insert(pos + k, e)

    assert D.protected(body) == guardia, 'Capítulo IV modificado'
    if not any(x.get('Extension') == 'emf' for x in tipos):
        E.SubElement(tipos, f'{{{CT}}}Default', Extension='emf', ContentType='image/x-emf')
    xml = lambda x: E.tostring(x, xml_declaration=True, encoding='UTF-8', standalone=True)
    partes.update({'word/document.xml': xml(root), 'word/_rels/document.xml.rels': xml(rels), '[Content_Types].xml': xml(tipos)})
    tmp = path.with_name(path.stem + '.nav.tmp.docx')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for nombre, datos in partes.items(): z.writestr(nombre, datos)
    tmp.replace(path)
    print(f'7.5: {len(franjas)} diagramas en {n} franjas, una por página')


if __name__ == '__main__': main()
