"""7.5 del maestro: cada diagrama de navegación partido en hojas apaisadas, una imagen EMF entera por página (las de
ea/navegacion_hojas.py, listadas en diagramas/nav-hojas.json). Conserva los títulos 7.5 y 7.5.n y la sección apaisada
de 1 cm de margen lateral; reemplaza solo las imágenes. Lo demás (capítulo IV incluido) no se toca. Luego: exportar.ps1.
"""
import copy
import json
import zipfile
from PIL import Image
from lxml import etree as E
import actualizar_documento as D
import navegacion as N

V, R, O = 'urn:schemas-microsoft-com:vml', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships', 'urn:schemas-microsoft-com:office:office'
PR, CT = 'http://schemas.openxmlformats.org/package/2006/relationships', 'http://schemas.openxmlformats.org/package/2006/content-types'
CM_PT = 28.3465
ANCHO_CM = 25.9                                  # carta apaisada con 1 cm de margen lateral
ALTO_CM = {0: 17.2, 1: 15.8, 2: 14.6}            # alto útil según los títulos que van encima (ninguno, 7.5.n, 7.5 + 7.5.n)


def salto_antes(p):
    pr = p.find('w:pPr', D.NS)
    if pr is None: pr = E.Element(D.q('pPr')); p.insert(0, pr)
    if pr.find('w:pageBreakBefore', D.NS) is not None: return
    estilo = pr.find('w:pStyle', D.NS)
    pr.insert(0 if estilo is None else list(pr).index(estilo) + 1, E.Element(D.q('pageBreakBefore')))


def main():
    path, root, body = D.doc_read()
    guardia = D.protected(body)
    with zipfile.ZipFile(path) as z: partes = {n: z.read(n) for n in z.namelist()}
    rels, tipos = E.fromstring(partes['word/_rels/document.xml.rels']), E.fromstring(partes['[Content_Types].xml'])
    hojas = json.loads((D.DOC / 'diagramas' / 'nav-hojas.json').read_text(encoding='utf-8'))
    items = list(body)
    estilo = lambda e: (e.find('.//w:pStyle', D.NS).get(D.q('val')) if e.find('.//w:pStyle', D.NS) is not None else '')
    titulo = lambda e, t: D.txt(e).startswith(t) and not estilo(e).startswith('TDC')
    a = next(i for i, e in enumerate(items) if titulo(e, '7.5. Diseño de Navegación'))
    b = next(i for i in range(a, len(items)) if titulo(items[i], '7.6.'))
    viejo = items[a + 1:b - 1]
    cierre = items[b - 1]
    assert cierre.find('.//w:sectPr', D.NS) is not None, '7.5 ya no termina en su sección apaisada'
    plantilla = next(e for e in viejo if e.find(f'.//{{{V}}}imagedata') is not None)
    encabezados = {}
    for n, actor in enumerate(N.DIAGRAMAS, 1):
        texto = f'7.5.{n}. Diagrama de Navegación del {actor}'
        encabezados[actor] = next(e for e in viejo if D.txt(e).startswith(texto))
    for rel in rels.findall(f'{{{PR}}}Relationship'):   # imágenes de una corrida anterior de este script
        if rel.get('Id', '').startswith('rIdNav'): rels.remove(rel)

    def figura(stem, ancho, alto, n):
        rid = f'rIdNav{n}'
        E.SubElement(rels, f'{{{PR}}}Relationship', Id=rid, Type=R + '/image', Target=f'media/nav-{stem}.emf')
        partes[f'word/media/nav-{stem}.emf'] = (D.DOC / 'diagramas' / f'{stem}.emf').read_bytes()
        p = copy.deepcopy(plantilla)
        for s in p.findall('.//w:sectPr', D.NS): s.getparent().remove(s)
        forma = p.find(f'.//{{{V}}}shape')
        forma.set('id', f'_x0000_i{9500 + n}')
        forma.set('style', f'width:{ancho * CM_PT:.2f}pt;height:{alto * CM_PT:.2f}pt')
        im = forma.find(f'{{{V}}}imagedata'); im.set(f'{{{R}}}id', rid); im.set(f'{{{O}}}title', stem)
        return p

    nuevo, n = [], 0
    for i, actor in enumerate(N.DIAGRAMAS):
        enc = copy.deepcopy(encabezados[actor])
        if i: salto_antes(enc)
        nuevo.append(enc)
        for j, hoja in enumerate(hojas[actor]):
            w, h = Image.open(D.DOC / 'diagramas' / f'{hoja["stem"]}.png').size
            limite = ALTO_CM[0 if j else (2 if i == 0 else 1)]
            ancho = min(ANCHO_CM, limite * w / h)
            n += 1
            img = figura(hoja['stem'], ancho, ancho * h / w, n)
            if j: salto_antes(img)
            nuevo.append(img)
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
    print(f'7.5: {n} hojas de navegación, una por página')


if __name__ == '__main__': main()
