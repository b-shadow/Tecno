"""Sustituye solo la imagen conceptual del DOCX actual, conservando sus ediciones manuales."""
from pathlib import Path
import os
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


def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').lower()


def localizar_imagen(z):
    document = ET.fromstring(z.read('word/document.xml'))
    rels = ET.fromstring(z.read('word/_rels/document.xml.rels'))
    destinos = {rel.get('Id'): rel.get('Target') for rel in rels}
    parrafos = document.findall(f'.//{W}body/{W}p')
    candidatos = [i for i, p in enumerate(parrafos)
                  if '7.1. diseno conceptual de base de datos' in
                  normalizar(''.join(t.text or '' for t in p.iter(f'{W}t')))]
    if not candidatos:
        raise RuntimeError('No encontré el encabezado 7.1 del diagrama conceptual.')
    inicio = candidatos[-1]  # saltar el índice y tomar el encabezado del capítulo
    for p in parrafos[inicio + 1:]:
        texto = normalizar(''.join(t.text or '' for t in p.iter(f'{W}t')))
        if texto.startswith('7.2. diseno logico'):
            break
        refs = [el.get(R + 'embed') or el.get(R + 'id')
                for el in list(p.iter(A + 'blip')) + list(p.iter(V + 'imagedata'))]
        refs = [ref for ref in refs if ref]
        if refs:
            destino = destinos.get(refs[0])
            if not destino:
                raise RuntimeError(f'La relación {refs[0]} de la figura no existe.')
            return 'word/' + destino.lstrip('/'), refs[0]
    raise RuntimeError('No encontré la imagen del diagrama conceptual bajo el encabezado 7.1.')


def main():
    figura = DIAGRAMAS / 'conceptual.emf'
    if not figura.is_file():
        raise FileNotFoundError(figura)
    temporal = DOCUMENTO.with_name(DOCUMENTO.stem + '.conceptual.tmp.docx')
    respaldo = Path(tempfile.gettempdir()) / f'p2-antes-conceptual-{uuid.uuid4().hex}.docx'
    shutil.copy2(DOCUMENTO, respaldo)
    try:
        with ZipFile(DOCUMENTO, 'r') as origen:
            nombre, rid = localizar_imagen(origen)
            if nombre not in origen.namelist():
                raise RuntimeError(f'No existe la imagen asociada {nombre} en el DOCX.')
            with ZipFile(temporal, 'w', ZIP_DEFLATED) as salida:
                salida.comment = origen.comment
                for item in origen.infolist():
                    contenido = figura.read_bytes() if item.filename == nombre else origen.read(item.filename)
                    salida.writestr(item, contenido)
        os.replace(temporal, DOCUMENTO)
    finally:
        if temporal.exists(): temporal.unlink()
    print(f'Actualizada solo la imagen {rid} ({nombre}) en {DOCUMENTO}')
    print(f'Respaldo previo: {respaldo}')


if __name__ == '__main__':
    main()
