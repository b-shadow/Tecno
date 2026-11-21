"""Pone al día el Mapeo (7.2.1) y el Diseño Físico (7.3) del DOCX actual con fuentes/esquema.sql, conservando el resto
de las ediciones manuales: reemplaza solo la tabla de mapeo y el CREATE TABLE de las tablas que difieren, generados con
las mismas funciones que documento_p2.py. Uso (con el documento cerrado en Word):
    python actualizar_datos_docx.py            # y después exportar.ps1 para el .doc y el .pdf"""
import copy, os, shutil, tempfile, uuid
from docx import Document

import esquema
from formato_g07 import G07
from rutas import DOCUMENTO

T, PK, FKC = esquema.tablas(), esquema.pks(), esquema.columnas_fk()
plano = lambda s: ''.join(s.split())


def columnas_mapeo(t):
    """Igual que documento_p2.py: PK, luego atributos propios, luego FK."""
    marca = lambda c: ' '.join(m for m, si in (('pk', c in PK[t]), ('fk', (t, c) in FKC)) if si)
    cols = [c for c, *_ in T[t]]
    orden = [c for c in cols if c in PK[t]] + [c for c in cols if c not in PK[t] and (t, c) not in FKC] + \
            [c for c in cols if c not in PK[t] and (t, c) in FKC]
    return [(c, marca(c)) for c in orden]


def generar(t):
    """Bloques nuevos de la tabla t en un documento G07 vacío: (tabla de mapeo, párrafos del CREATE TABLE)."""
    g = G07(); body = g.doc.element.body
    # lo nuevo entra antes del sectPr final: empieza en len(body) - 1
    n = len(body) - 1; g.tabla_mapeo(t, columnas_mapeo(t), ancho=19.5); mapeo = body[n]   # sin el párrafo vacío de después
    n = len(body) - 1; g.fisico(t, T[t]); fisico = list(body)[n:-2]                       # sin el párrafo vacío ni sectPr
    return mapeo, fisico


def texto(el):
    return ''.join(x.text or '' for x in el.iter() if x.tag.endswith('}t'))


def main():
    doc = Document(DOCUMENTO)
    hijos = list(doc.element.body)
    i72 = next(i for i, e in enumerate(hijos) if texto(e).strip().startswith('7.2.1. Mapeo') and e.tag.endswith('}p')
               and i > len(hijos) // 4)   # el del capítulo, no el del índice
    i73 = next(i for i, e in enumerate(hijos) if i > i72 and texto(e).strip().startswith('7.3. Diseño Físico'))
    i74 = next(i for i, e in enumerate(hijos) if i > i73 and texto(e).strip().startswith('7.4.'))
    cambios = []
    for t in T:
        nuevo_mapeo, nuevo_fisico = generar(t)
        viejo = [e for e in hijos[i72:i73] if e.tag.endswith('}tbl') and plano(texto(e)).startswith(t)
                 and plano(texto(e))[len(t):len(t) + 2] in ('pk', 'fk')]
        if len(viejo) != 1: raise RuntimeError(f'Mapeo: encontré {len(viejo)} tablas «{t}» en 7.2.1')
        if plano(texto(viejo[0])) != plano(texto(nuevo_mapeo)):
            viejo[0].addprevious(copy.deepcopy(nuevo_mapeo)); viejo[0].getparent().remove(viejo[0]); cambios.append(f'mapeo {t}')
        ini = [i for i in range(i73, i74) if texto(hijos[i]).strip() == f'CREATE TABLE {t} (']
        if len(ini) != 1: raise RuntimeError(f'Físico: encontré {len(ini)} «CREATE TABLE {t} (» en 7.3')
        fin = next(i for i in range(ini[0], i74) if texto(hijos[i]).strip() == ');')
        viejos = hijos[ini[0]:fin + 1]
        if [plano(texto(e)) for e in viejos] != [plano(texto(e)) for e in nuevo_fisico]:
            for e in nuevo_fisico: viejos[0].addprevious(copy.deepcopy(e))
            for e in viejos: e.getparent().remove(e)
            cambios.append(f'físico {t}')
    if not cambios: return print('Mapeo y físico ya coinciden con fuentes/esquema.sql: nada que cambiar.')
    respaldo = os.path.join(tempfile.gettempdir(), f'p2-antes-datos-{uuid.uuid4().hex}.docx')
    shutil.copy2(DOCUMENTO, respaldo)
    doc.save(DOCUMENTO)
    print('Actualizado:', ', '.join(cambios)); print('Respaldo previo:', respaldo)


if __name__ == '__main__':
    main()
