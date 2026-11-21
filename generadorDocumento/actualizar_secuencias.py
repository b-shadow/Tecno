"""Actualiza solo las ocho figuras de secuencia en el Word ya editado.

Se usa después de ea/ea_faltantes.py --secuencias. Conserva tablas y textos manuales. Deja 7.4 en su propia sección
con 1 cm de margen lateral (como documento_p2.py) y cada sd lo más grande que entra entero en su hoja carta;
exportar.ps1 actualiza a continuación las versiones .doc y .pdf.
"""
import pathlib
import re
import shutil
import tempfile
import uuid

import win32com.client
import pywintypes


from formato_g07 import ALTO_SD
from rutas import DIAGRAMAS, DOCUMENTO

CM = 28.3464567   # puntos por centímetro
TITULO_74 = '7.4. Diseño de casos de uso (Diagrama de secuencia)'


def seccion_74(doc):
    """El título 7.4 del capítulo (no el del índice) abre su propia sección, con 1 cm de margen a los lados."""
    rango, titulo = doc.Content, None
    rango.Find.ClearFormatting()
    while rango.Find.Execute(TITULO_74):
        if rango.Paragraphs.Item(1).OutlineLevel < 10: titulo = rango.Paragraphs.Item(1).Range   # encabezado real
        rango.Collapse(0)
    if titulo is None: raise RuntimeError(f'No encontré el encabezado «{TITULO_74}».')
    if titulo.Sections.Item(1).Range.Start != titulo.Start:
        antes = doc.Range(titulo.Start, titulo.Start)
        antes.InsertBreak(2)   # wdSectionBreakNextPage
        titulo = doc.Range(antes.End, antes.End).Paragraphs.Item(1).Range
    ps = titulo.Sections.Item(1).PageSetup
    ps.LeftMargin = ps.RightMargin = 1 * CM
    return titulo.Start


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
        inicio = seccion_74(doc)
        for i, n in elegidos[1:]:   # cada CU abre página con «salto antes» en su título, sin el renglón del salto manual
            titulo = doc.InlineShapes.Item(i).Range.Paragraphs.Item(1).Previous()
            previo = titulo.Previous()
            texto = previo.Range.Text if previo is not None else ''
            if chr(12) in texto and not texto.strip(chr(12) + chr(13) + ' '):   # párrafo con solo el salto de página
                previo.Range.Delete()
            titulo.Format.PageBreakBefore = True
        if doc.InlineShapes.Item(elegidos[0][0]).Range.Start < inicio:
            raise RuntimeError('La primera secuencia quedó antes del título 7.4.')
        for i, n in elegidos:
            figura = doc.InlineShapes.Item(i)
            ruta = DIAGRAMAS / f'sd-cu{n}.emf'
            if not ruta.is_file(): raise FileNotFoundError(ruta)
            rango = figura.Range
            figura.Delete()
            nueva = doc.InlineShapes.AddPicture(str(ruta), False, True, rango)
            nueva.LockAspectRatio = -1
            alto = (ALTO_SD[0] if n == 1 else ALTO_SD[1]) * CM
            nueva.Width = 19.5 * CM
            if nueva.Height > alto: nueva.Height = alto   # entero en su hoja (con la proporción que Word da al EMF)
            nueva.AlternativeText = str(ruta.resolve())
        doc.Save()
        print(f'Actualizadas {len(elegidos)} secuencias en {DOCUMENTO}')
        print(f'Respaldo previo: {respaldo}')
    finally:
        if doc is not None: doc.Close(0)
        word.Quit()


if __name__ == '__main__': main()
