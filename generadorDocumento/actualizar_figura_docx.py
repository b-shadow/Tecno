"""Sustituye solo una figura del DOCX actual (conceptual 7.1 o despliegue 6.1), conservando sus ediciones manuales.
Uso: python actualizar_figura_docx.py [conceptual|despliegue]   (por defecto: conceptual)"""
from pathlib import Path
import os
import re
import struct
import sys
import shutil
import tempfile
import unicodedata
import uuid
from zipfile import ZIP_DEFLATED, ZipFile
from xml.etree import ElementTree as ET

from rutas import DIAGRAMAS, DOCUMENTO

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
V = '{urn:schemas-microsoft-com:vml}'
# figura: (archivo en diagramas/, encabezado donde está, encabezado siguiente, caja máxima en cm o None)
# Encabezados sin tildes y en minúsculas. Con caja, la figura ocupa lo más que entra en ella (6.1: página apaisada
# bajo los tres títulos, como documento_p2.py); sin caja, conserva su ancho.
FIGURAS = {
    'conceptual': ('conceptual', '7.1. diseno conceptual de base de datos', '7.2. diseno logico', (19.5, 21.0)),
    'despliegue': ('despliegue', '6.1. diseno fisico de la arquitectura', '7. diseno de datos', (25.9, 13.2)),
}


def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').lower()


def localizar_imagen(z, encabezado, fin):
    document = ET.fromstring(z.read('word/document.xml'))
    rels = ET.fromstring(z.read('word/_rels/document.xml.rels'))
    destinos = {rel.get('Id'): rel.get('Target') for rel in rels}
    parrafos = document.findall(f'.//{W}body/{W}p')
    candidatos = [i for i, p in enumerate(parrafos)
                  if encabezado in
                  normalizar(''.join(t.text or '' for t in p.iter(f'{W}t')))]
    if not candidatos:
        raise RuntimeError(f'No encontré el encabezado «{encabezado}».')
    inicio = candidatos[-1]  # saltar el índice y tomar el encabezado del capítulo
    for p in parrafos[inicio + 1:]:
        texto = normalizar(''.join(t.text or '' for t in p.iter(f'{W}t')))
        if texto.startswith(fin):
            break
        refs = [el.get(R + 'embed') or el.get(R + 'id')
                for el in list(p.iter(A + 'blip')) + list(p.iter(V + 'imagedata'))]
        refs = [ref for ref in refs if ref]
        if refs:
            destino = destinos.get(refs[0])
            if not destino:
                raise RuntimeError(f'La relación {refs[0]} de la figura no existe.')
            return 'word/' + destino.lstrip('/'), refs[0]
    raise RuntimeError(f'No encontré la imagen bajo «{encabezado}».')


def proporcion(xml, rid, png, caja=None):
    """Ajusta el tamaño de la figura al nuevo PNG para que no salga estirada: sin caja conserva el ancho;
    con caja (ancho, alto en cm) toma lo más grande que entra en ella."""
    ancho, alto = struct.unpack('>II', png.read_bytes()[16:24])
    patron = re.compile(r'(<v:shape [^>]*?style="width:)([\d.]+)(pt;height:)[^;"]+(;?[^"]*"[^>]*>\s*<v:imagedata r:id="%s")' % rid)

    def medida(m):
        w = float(m.group(2))
        if caja: w = min(caja[0], caja[1] * ancho / alto) / 2.54 * 72
        return f'{m.group(1)}{w:.1f}{m.group(3)}{w * alto / ancho:.1f}pt{m.group(4)}'
    xml, n = patron.subn(medida, xml)
    if n != 1: raise RuntimeError(f'No pude ajustar el tamaño de la figura {rid} ({n} coincidencias).')
    return xml


def main():
    clave = sys.argv[1] if len(sys.argv) > 1 else 'conceptual'
    archivo, encabezado, fin, caja = FIGURAS[clave]
    figura = DIAGRAMAS / f'{archivo}.emf'
    if not figura.is_file():
        raise FileNotFoundError(figura)
    temporal = DOCUMENTO.with_name(DOCUMENTO.stem + f'.{clave}.tmp.docx')
    respaldo = Path(tempfile.gettempdir()) / f'p2-antes-{clave}-{uuid.uuid4().hex}.docx'
    shutil.copy2(DOCUMENTO, respaldo)
    try:
        with ZipFile(DOCUMENTO, 'r') as origen:
            nombre, rid = localizar_imagen(origen, encabezado, fin)
            if nombre not in origen.namelist():
                raise RuntimeError(f'No existe la imagen asociada {nombre} en el DOCX.')
            with ZipFile(temporal, 'w', ZIP_DEFLATED) as salida:
                salida.comment = origen.comment
                for item in origen.infolist():
                    contenido = figura.read_bytes() if item.filename == nombre else origen.read(item.filename)
                    if item.filename == 'word/document.xml':
                        contenido = proporcion(contenido.decode('utf-8'), rid, figura.with_suffix('.png'), caja).encode('utf-8')
                    salida.writestr(item, contenido)
        os.replace(temporal, DOCUMENTO)
    finally:
        if temporal.exists(): temporal.unlink()
    print(f'Actualizada solo la imagen {rid} ({nombre}) en {DOCUMENTO}')
    print(f'Respaldo previo: {respaldo}')


if __name__ == '__main__':
    main()
