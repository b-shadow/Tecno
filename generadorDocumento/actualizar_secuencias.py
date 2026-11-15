"""Actualiza solo las ocho figuras de secuencia en el Word ya editado.

Se usa después de ea/ea_faltantes.py. Conserva tablas y textos manuales;
exportar.ps1 actualiza a continuación las versiones .doc y .pdf.
"""
import pathlib
import re
import shutil
import tempfile
import uuid

import win32com.client
import pywintypes

from rutas import DIAGRAMAS, DOCUMENTO


def main():
    try:
        activa = win32com.client.GetActiveObject('Word.Application')
        if any(pathlib.Path(doc.FullName).resolve() == DOCUMENTO.resolve() for doc in activa.Documents):
            raise RuntimeError('Cierre el documento P2 en Word antes de actualizar sus diagramas.')
    except (OSError, pywintypes.com_error):
        pass

    respaldo = pathlib.Path(tempfile.gettempdir()) / f'p2-antes-secuencias-{uuid.uuid4().hex}.docx'
    shutil.copy2(DOCUMENTO, respaldo)
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(str(DOCUMENTO))
        candidatos = []
        for i in range(1, doc.InlineShapes.Count + 1):
            figura = doc.InlineShapes.Item(i)
            anterior = figura.Range.Paragraphs.Item(1).Previous()
            titulo = anterior.Range.Text.strip() if anterior else ''
            match = re.match(r'^CU([1-8])\.', titulo)
            if match: candidatos.append((i, int(match.group(1))))
        # En el documento hay otros diagramas con rótulo CU. Solo son secuencias
        # los últimos ocho CU consecutivos antes de la sección de navegación.
        elegidos = candidatos[-8:]
        if [n for _, n in elegidos] != list(range(1, 9)):
            raise RuntimeError(f'No se localizaron inequívocamente las ocho secuencias: {elegidos}')
        for i, n in elegidos:
            figura = doc.InlineShapes.Item(i)
            ruta = DIAGRAMAS / f'sd-cu{n}.emf'
            if not ruta.is_file(): raise FileNotFoundError(ruta)
            an, al = figura.Width, figura.Height
            rango = figura.Range
            figura.Delete()
            nueva = doc.InlineShapes.AddPicture(str(ruta), False, True, rango)
            nueva.LockAspectRatio = -1
            nueva.Width = an
            if nueva.Height > 19 * 28.3464567: nueva.Height = 19 * 28.3464567
            nueva.AlternativeText = str(ruta.resolve())
        doc.Save()
        print(f'Actualizadas {len(elegidos)} secuencias en {DOCUMENTO}')
        print(f'Respaldo previo: {respaldo}')
    finally:
        if doc is not None: doc.Close(0)
        word.Quit()


if __name__ == '__main__': main()
