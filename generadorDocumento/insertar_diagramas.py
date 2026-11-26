"""Sustituye solo los marcadores de diagramas existentes en el DOCX de P2.

No reconstruye el documento: conserva textos, tablas y cambios manuales.
Ejecutar después de ea/ea_faltantes.py, con el documento cerrado en Word.
"""
import os
import pathlib
import re
import shutil
import tempfile
import uuid

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm
from PIL import Image

from rutas import DIAGRAMAS, DOCUMENTO


def main():
    try:
        import win32com.client
        word = win32com.client.GetActiveObject('Word.Application')
        if any(pathlib.Path(d.FullName).resolve() == DOCUMENTO.resolve() for d in word.Documents):
            raise RuntimeError('Cierre el documento de P2 en Word antes de insertar los diagramas.')
    except (ImportError, OSError):
        pass
    doc = Document(DOCUMENTO)
    patron = re.compile(r'^\[PENDIENTE: diagrama ([\w.-]+\.png)\]$')
    insertados = []
    for parrafo in doc.paragraphs:
        m = patron.fullmatch(parrafo.text.strip())
        if not m: continue
        ruta = DIAGRAMAS / m.group(1)
        if not ruta.is_file(): raise FileNotFoundError(ruta)
        w, h = Image.open(ruta).size
        ancho = min(15.5, 19 * w / h)
        parrafo.clear()
        parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        forma = parrafo.add_run().add_picture(str(ruta), width=Cm(ancho))
        forma._inline.docPr.set('descr', str(ruta.resolve()))
        insertados.append(ruta.name)
    if not insertados:
        print('No hay marcadores de diagramas para reemplazar.')
        return
    # Copia de seguridad fuera del repositorio por si Word tenía algún cambio
    # que todavía no hubiera sido guardado.
    respaldo = pathlib.Path(tempfile.gettempdir()) / ('p2-antes-diagramas-' + uuid.uuid4().hex + '.docx')
    shutil.copy2(DOCUMENTO, respaldo)
    temporal = DOCUMENTO.with_name(DOCUMENTO.stem + '.diagramas.tmp.docx')
    try:
        doc.save(temporal)
        os.replace(temporal, DOCUMENTO)
    finally:
        if temporal.exists(): temporal.unlink()
    print(f'Reemplazados {len(insertados)} marcadores en {DOCUMENTO}')
    print(f'Respaldo previo: {respaldo}')


if __name__ == '__main__': main()
