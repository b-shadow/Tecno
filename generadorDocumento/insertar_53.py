"""5.3.1 y 5.3.2 del maestro: cada CU entero en su hoja carta, con 1 cm de margen lateral, en la orientación que lo
deja más grande (formato_g07.hoja_53). Figuras: com-cuN / cls-cuN.emf de `ea_faltantes.py --analisis`.
Reemplaza solo esas dos secciones del DOCX maestro; lo demás (capítulo IV incluido) no se toca. Luego: exportar.ps1."""
import copy
import re
import zipfile
from PIL import Image
from lxml import etree as E
import actualizar_documento as D
import contenido as C
from formato_g07 import hoja_53, MARGEN_NAV

V, R, O = 'urn:schemas-microsoft-com:vml', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships', 'urn:schemas-microsoft-com:office:office'
PR, CT = 'http://schemas.openxmlformats.org/package/2006/relationships', 'http://schemas.openxmlformats.org/package/2006/content-types'
CM_PT, CM_TW = 28.3465, 567


def main():
    path, root, body = D.doc_read()
    guardia = D.protected(body)
    with zipfile.ZipFile(path) as z: partes = {n: z.read(n) for n in z.namelist()}
    rels, tipos = E.fromstring(partes['word/_rels/document.xml.rels']), E.fromstring(partes['[Content_Types].xml'])
    items = list(body)
    estilo = lambda e: (e.find('.//w:pStyle', D.NS).get(D.q('val')) if e.find('.//w:pStyle', D.NS) is not None else '')
    titulo = lambda e, t: D.txt(e).startswith(t) and not estilo(e).startswith('TDC')   # el título, no su línea del índice
    a = next(i for i, e in enumerate(items) if titulo(e, '5.3. Análisis de Caso de Uso'))
    b = next(i for i in range(a, len(items)) if titulo(items[i], 'Capítulo VII'))
    viejo = items[a:b]
    base = items[a - 1].find('.//w:sectPr', D.NS)   # ya aplicado antes: 5.2 cierra su propia sección
    if base is None: base = viejo[-1].find('.//w:sectPr', D.NS)
    assert base is not None, 'la sección de 5.3 ya no termina antes del capítulo VII'
    h532 = next(e for e in viejo if D.txt(e).startswith('5.3.2.'))
    rotulo = next(e for e in viejo if re.match(r'CU1\. ', D.txt(e)))
    plantilla = next(e for e in viejo if e.find(f'.//{{{V}}}imagedata') is not None)

    def seccion(parrafo, apaisada=None):
        """El párrafo cierra una sección: la de 5.3 tal cual (apaisada None) o una hoja carta con MARGEN_NAV."""
        s = copy.deepcopy(base)
        if apaisada is not None:
            pg, mar = s.find('w:pgSz', D.NS), s.find('w:pgMar', D.NS)
            pg.attrib.clear(); pg.set(D.q('w'), '15840' if apaisada else '12240'); pg.set(D.q('h'), '12240' if apaisada else '15840')
            if apaisada: pg.set(D.q('orient'), 'landscape')
            for lado in ('left', 'right', 'top', 'bottom'): mar.set(D.q(lado), str(round(MARGEN_NAV[f'{lado}_margin'].cm * CM_TW)))
        pr = parrafo.find('w:pPr', D.NS)
        if pr is None: pr = E.Element(D.q('pPr')); parrafo.insert(0, pr)
        for viejo_s in pr.findall('w:sectPr', D.NS): pr.remove(viejo_s)
        pr.append(s)

    def figura(emf, ancho, alto, n):
        rid = f'rIdP53n{n}'
        for x in rels.findall(f'{{{PR}}}Relationship[@Id="{rid}"]'): rels.remove(x)   # de una corrida anterior
        E.SubElement(rels, f'{{{PR}}}Relationship', Id=rid, Type=R + '/image', Target=f'media/p53-{emf.stem}.emf')
        partes[f'word/media/p53-{emf.stem}.emf'] = emf.read_bytes()
        p = copy.deepcopy(plantilla)
        for s in p.findall('.//w:sectPr', D.NS): s.getparent().remove(s)
        forma = p.find(f'.//{{{V}}}shape')
        forma.set('id', f'_x0000_i{9000 + n}')
        forma.set('style', f'width:{ancho * CM_PT:.2f}pt;height:{alto * CM_PT:.2f}pt')
        im = forma.find(f'{{{V}}}imagedata'); im.set(f'{{{R}}}id', rid); im.set(f'{{{O}}}title', emf.stem)
        return p

    seccion(items[a - 1])   # cierra la sección de 5.2 con el formato que tenía
    nuevo, n = [], 0
    for prefijo, titulos in (('com', viejo[:2]), ('cls', [h532])):
        for i, (cu, nombre) in enumerate(C.CU.items()):
            png = D.DOC / 'diagramas' / f'{prefijo}-{cu.lower()}.png'
            apaisada, ancho, alto = hoja_53(png, i == 0)
            w, h = Image.open(png).size
            ancho = min(ancho, alto * w / h)
            if i == 0: nuevo += [copy.deepcopy(t) for t in titulos]
            r = copy.deepcopy(rotulo)
            ts = r.findall('.//w:t', D.NS); ts[0].text = f'{cu}. {nombre}'
            for t in ts[1:]: t.getparent().remove(t)
            n += 1
            img = figura(png.with_suffix('.emf'), ancho, ancho * h / w, n)
            seccion(img, apaisada)
            nuevo += [r, img]
    for e in viejo: body.remove(e)
    for k, e in enumerate(nuevo): body.insert(a + k, e)

    assert D.protected(body) == guardia, 'Capítulo IV modificado'
    if not any(x.get('Extension') == 'emf' for x in tipos):
        E.SubElement(tipos, f'{{{CT}}}Default', Extension='emf', ContentType='image/x-emf')
    xml = lambda x: E.tostring(x, xml_declaration=True, encoding='UTF-8', standalone=True)
    partes.update({'word/document.xml': xml(root), 'word/_rels/document.xml.rels': xml(rels), '[Content_Types].xml': xml(tipos)})
    tmp = path.with_name(path.stem + '.53.tmp.docx')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for nombre, datos in partes.items(): z.writestr(nombre, datos)
    tmp.replace(path)
    print(f'5.3.1 y 5.3.2: {n} figuras, una por hoja')


if __name__ == '__main__': main()
