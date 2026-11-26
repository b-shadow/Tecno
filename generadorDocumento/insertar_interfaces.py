"""Actualiza las capturas de 7.6 y la carta en el DOCX maestro."""
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from PIL import Image

from actualizar_documento import protected
from contenido import CU
from doc_ficct import _sin_sangria
from rutas import AQUI, DOCUMENTO

RECURSOS = AQUI / 'recursos'
CAPTURAS = RECURSOS / 'interfaces'
CARTA = RECURSOS / 'carta-proyecto.jpg'
TITULO_INTERFACES = '7.6. Diagrama de interfaces'
TITULO_CARTA = '13.1. Anexo # 1: Carta de solicitud de desarrollo del proyecto'


def imagen(doc, ruta, descripcion, ancho, alto_max, antes_de=None):
    with Image.open(ruta) as foto:
        ancho_px, alto_px = foto.size
    parrafo = antes_de.insert_paragraph_before() if antes_de else doc.add_paragraph()
    _sin_sangria(parrafo)
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    parrafo.paragraph_format.space_after = Pt(8)
    figura = parrafo.add_run().add_picture(
        str(ruta), width=Cm(min(ancho, alto_max * ancho_px / alto_px))
    )
    figura._inline.docPr.set('descr', descripcion)


def insertar_capturas(doc, antes_de=None):
    for i, (cu, nombre) in enumerate(CU.items()):
        titulo = f'Diagrama de Interfaz {cu}. {nombre}'
        rotulo = antes_de.insert_paragraph_before() if antes_de else doc.add_paragraph()
        formato = _sin_sangria(rotulo).paragraph_format
        formato.keep_with_next = True
        formato.keep_together = True
        formato.space_after = Pt(6)
        formato.page_break_before = i > 0 and i % 2 == 0
        rotulo.add_run(titulo)
        imagen(doc, CAPTURAS / f'{cu.lower()}.png', titulo, 15.5, 8.4, antes_de)


def insertar_carta(doc, antes_de=None):
    if antes_de:
        titulo = antes_de.insert_paragraph_before(TITULO_CARTA, style='Heading 2')
    else:
        titulo = doc.add_paragraph(TITULO_CARTA, style='Heading 2')
    titulo.paragraph_format.keep_with_next = True
    imagen(doc, CARTA, 'Oficio ING. SIS. OF. N.° 485/2026 de la Dirección de Carrera',
           15.5, 17.4, antes_de)


def buscar(doc, estilo, prefijo):
    encontrados = [p for p in doc.paragraphs if p.style.name == estilo and p.text.startswith(prefijo)]
    if len(encontrados) != 1:
        raise ValueError(f'Se esperaba un párrafo «{prefijo}» de estilo {estilo}')
    return encontrados[0]


def retirar_imagenes(doc, nodos):
    cuerpo = doc._element.body
    relaciones = {blip.get(qn('r:embed')) for nodo in nodos for blip in nodo.iter(qn('a:blip'))}
    for nodo in nodos:
        cuerpo.remove(nodo)
    usadas = set(doc._element.xpath('//@r:embed | //@r:id | //@r:link'))
    for rid in relaciones - usadas - {None}:
        doc.part.rels.pop(rid, None)


def actualizar(origen, salida):
    doc = Document(origen)
    cuerpo = doc._element.body
    capitulo_iv = protected(cuerpo)
    interfaces = buscar(doc, 'Heading 3', TITULO_INTERFACES)
    implementacion = buscar(doc, 'Heading 1', 'Capítulo VIII: Implementación')
    anexo = buscar(doc, 'Heading 1', '13. Anexo')
    github = buscar(doc, 'Normal', 'URL Proyecto GitHub:')

    intervalo = list(cuerpo)[cuerpo.index(interfaces._p) + 1:cuerpo.index(implementacion._p)]
    retirar_imagenes(doc, intervalo)
    insertar_capturas(doc, implementacion)

    existentes = list(cuerpo)[cuerpo.index(anexo._p) + 1:cuerpo.index(github._p)]
    for nodo in existentes:
        if ''.join(nodo.xpath('.//w:t/text()')) == TITULO_CARTA:
            siguiente = nodo.getnext()
            if siguiente not in existentes or not siguiente.xpath('./w:r/w:drawing'):
                raise ValueError('La carta existente no tiene la imagen esperada')
            retirar_imagenes(doc, [nodo, siguiente])
            break
    insertar_carta(doc, github)

    if protected(cuerpo) != capitulo_iv:
        raise ValueError('El capítulo IV fue modificado')
    with TemporaryDirectory(dir=salida.parent) as temporal:
        intermedio = Path(temporal) / salida.name
        doc.save(intermedio)
        intermedio.replace(salida)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origen', type=Path, default=DOCUMENTO)
    parser.add_argument('--salida', type=Path, default=DOCUMENTO)
    args = parser.parse_args()
    actualizar(args.origen, args.salida)
