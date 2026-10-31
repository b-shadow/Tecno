"""Formato del documento aprobado del Grupo 07 (REGLAS_DOCUMENTO_P2.md §1 y §3) sobre doc_ficct.Informe (copia local):
Times New Roman, interlineado 1,5, "Capítulo N" B16 centrado, pie "N | P á g i n a", INDICE, tablas gris / azul de CU /
Mapeo, script físico en negrita y diagramas de navegación cortados en franjas apaisadas."""
import pathlib
import numpy as np
from PIL import Image
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from doc_ficct import Informe, _campo, _fuente, _sin_sangria, LOGO, INTEGRANTES  # noqa: E402

CARTA = (Cm(21.59), Cm(27.94))
MARGEN = dict(left_margin=Cm(3), right_margin=Cm(3), top_margin=Cm(2.5), bottom_margin=Cm(2.5))
MARGEN_NAV = dict(left_margin=Cm(1), right_margin=Cm(1), top_margin=Cm(2), bottom_margin=Cm(2))   # franjas casi a todo el ancho
GRIS, AZUL, AZUL_CLARO, AZUL_MAPEO, AZUL_MAPEO_CLARO = 'C9C9C9', '4F94D9', 'D6E8F5', '5C9CD4', 'DEEBF5'
PENDIENTES = []


def _sombra(celda, color):
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:fill'), color)
    celda._tc.get_or_add_tcPr().append(sh)


def _bordes(tabla, color='000000', sz='4'):
    b = OxmlElement('w:tblBorders')
    for lado in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{lado}'); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), sz); e.set(qn('w:color'), color); b.append(e)
    tabla._tbl.tblPr.append(b)


def _texto_celda(celda, texto, bold=False, italic=False, color=None, tam=12, fuente=None, centro=False):
    celda.text = ''
    par = _sin_sangria(celda.paragraphs[0]); par.paragraph_format.space_after = Pt(0)
    if centro: par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = par.add_run(texto); r.bold, r.italic, r.font.size = bold, italic, Pt(tam)
    if color: r.font.color.rgb = RGBColor.from_string(color)
    if fuente: r.font.name = fuente; r._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:hAnsi'), fuente)
    return par


def renglones(nombre, ancho_cm, tam):
    """Parte un nombre de columna solo después de cada "_" para que entre en ancho_cm (nunca a media palabra)."""
    cabe = max(1, int((ancho_cm - 0.25) / (0.02 * tam)))
    lineas, actual = [], ''
    for trozo in [x + '_' for x in nombre.split('_')[:-1]] + [nombre.split('_')[-1]]:
        if actual and len(actual + trozo) > cabe: lineas.append(actual); actual = trozo
        else: actual += trozo
    return chr(10).join(lineas + [actual])   # python-docx convierte el salto en <w:br/>


class G07(Informe):
    def __init__(self):
        super().__init__()
        s = self.sec
        for k, v in MARGEN.items(): setattr(s, k, v)
        st = self.doc.styles
        pf = st['Normal'].paragraph_format
        pf.line_spacing, pf.first_line_indent, pf.space_after = 1.5, Cm(0), Pt(6)
        for nivel, (tam, centro) in {1: (16, True), 2: (14, False), 3: (13, False), 4: (13, False)}.items():
            hs = st[f'Heading {nivel}']
            _fuente(hs, tam, True, False)
            hs.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if centro else WD_ALIGN_PARAGRAPH.LEFT
            hs.paragraph_format.first_line_indent = Cm(0)
            hs.paragraph_format.space_before, hs.paragraph_format.space_after = Pt(12), Pt(8)
            hs.paragraph_format.keep_with_next = True
        st['Heading 1'].paragraph_format.page_break_before = True   # cada capítulo en página nueva
        from docx.enum.style import WD_STYLE_TYPE
        for nivel in range(1, 5):   # estilos que Word usa al armar el índice
            toc = st.add_style(f'toc {nivel}', WD_STYLE_TYPE.PARAGRAPH); toc.base_style = st['Normal']
            toc.paragraph_format.space_after = Pt(0); toc.paragraph_format.left_indent = Cm(0.42 * (nivel - 1))
        self._pie(s)

    # ---------------------------------------------------------------- partes fijas
    def _pie(self, s):
        """Pie "N | P á g i n a" de Word (barra de acentos): número negro, "Página" gris espaciado, raya gris encima."""
        par = s.footer.paragraphs[0]; par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        _sin_sangria(par)
        bd = OxmlElement('w:pBdr'); top = OxmlElement('w:top')
        for k, v in (('val', 'single'), ('sz', '4'), ('space', '1'), ('color', 'D9D9D9')): top.set(qn(f'w:{k}'), v)
        bd.append(top); par._p.get_or_add_pPr().append(bd)
        _campo(par, ' PAGE ', '1')
        par.add_run(' | ')
        r = par.add_run('Página'); r.font.color.rgb = RGBColor(0x7F, 0x7F, 0x7F)
        esp = OxmlElement('w:spacing'); esp.set(qn('w:val'), '60'); r._r.get_or_add_rPr().append(esp)

    def caratula(self, titulo, grupo='Grupo 05', sigla='INF513-SA', semestre='2/2026', integrantes=INTEGRANTES):
        def linea(texto, tam, bold=True, despues=0):
            par = _sin_sangria(self.doc.add_paragraph()); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.space_after = Pt(despues or (0 if tam > 16 else 8))
            for i, t in enumerate(texto.split('**')):
                if t: r = par.add_run(t); r.font.size = Pt(tam); r.bold = bold if len(texto.split('**')) == 1 else i % 2 == 1
            return par
        linea('UNIVERSIDAD AUTÓNOMA', 24); linea('GABRIEL RENÉ MORENO', 24, despues=10)
        for t in ('FACULTAD DE INGENIERÍA EN CIENCIAS DE', 'LA COMPUTACIÓN Y', 'TELECOMUNICACIONES'): linea(t, 20, False)
        par = _sin_sangria(self.doc.add_paragraph()); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_before = Pt(8); par.paragraph_format.space_after = Pt(8)
        par.add_run().add_picture(str(LOGO), width=Cm(4.4))
        linea(grupo, 16); linea(titulo, 16, despues=10)
        linea('**Materia:** Tecnología Web', 12); linea('**Sigla:** ' + sigla, 12); linea('**Integrantes:**', 12)
        t = self.doc.add_table(rows=0, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER; _bordes(t)
        for nom, reg in integrantes:
            c = t.add_row().cells
            for celda, txt, ancho in ((c[0], nom, 6.5), (c[1], reg, 4.5)):
                _texto_celda(celda, txt, centro=True).paragraph_format.space_before = Pt(4)
                celda.paragraphs[0].paragraph_format.space_after = Pt(4); celda.width = Cm(ancho)
        linea('', 12)
        linea('**Docente:** Ing. Balcázar Veizaga Evans', 12); linea('Semestre: ' + semestre, 12); linea('Santa Cruz Bolivia', 12)

    def indice(self):
        self.salto()
        par = _sin_sangria(self.doc.add_paragraph()); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = par.add_run('INDICE'); r.bold = True; r.font.size = Pt(18)
        _campo(_sin_sangria(self.doc.add_paragraph()), ' TOC \\o "1-4" \\h \\z \\u ', 'Actualizar campo para generar el índice.')

    # ---------------------------------------------------------------- texto
    def p(self, texto, estilo=None, sangria=False, alin=None):
        """Párrafo con **negrita** (G07 no usa los dos espacios del manual APA)."""
        par = self.doc.add_paragraph(style=estilo)
        if alin is not None: par.alignment = alin
        for i, t in enumerate(texto.split('**')):
            if t: par.add_run(t).bold = i % 2 == 1
        return par

    def pendiente(self, que):
        PENDIENTES.append(que)
        r = self.doc.add_paragraph().add_run(f'[PENDIENTE: {que}]'); r.bold = True; r.font.color.rgb = RGBColor(0xC0, 0, 0)

    def texto(self, valor, que):
        """Párrafos de contenido.py; si el dato todavía no existe, marca roja."""
        if not valor: return self.pendiente(que)
        for t in ([valor] if isinstance(valor, str) else valor): self.p(t)

    def vinetas(self, items, sub=False):
        for it in items:
            par = self.p(it, 'List Bullet 2' if sub else 'List Bullet')
            par.paragraph_format.first_line_indent = Cm(0)

    # ---------------------------------------------------------------- tablas
    def tabla_gris(self, cab, filas, negrita_primera=False, anchos=None):
        t = self.doc.add_table(rows=1, cols=len(cab)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; _bordes(t)
        for c, txt in zip(t.rows[0].cells, cab): _texto_celda(c, txt, bold=True); _sombra(c, GRIS)
        for f in filas:
            for i, (c, txt) in enumerate(zip(t.add_row().cells, f)): _texto_celda(c, str(txt), bold=negrita_primera and i == 0)
        if anchos:
            for f in t.rows:
                for c, a in zip(f.cells, anchos): c.width = Cm(a)
        self.doc.add_paragraph()
        return t

    def tabla_cu(self, codigo, nombre, campos):
        """Tabla azul del detalle de CU. campos: [(etiqueta, texto | [pasos])]; una lista va en subfilas numeradas."""
        t = self.doc.add_table(rows=1, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER; _bordes(t, 'FFFFFF', '8')
        for c, txt in zip(t.rows[0].cells, ('Caso de Uso', f'{codigo}. {nombre}')):
            _texto_celda(c, txt, bold=True, color='FFFFFF'); _sombra(c, AZUL)
        for etiqueta, valor in campos:
            filas = valor if isinstance(valor, list) else [valor]
            if not valor:
                filas = ['[PENDIENTE]']; PENDIENTES.append(f'{codigo}: {etiqueta}')
            for i, v in enumerate(filas):
                c = t.add_row().cells
                if i == 0: _texto_celda(c[0], etiqueta)
                _texto_celda(c[1], f'{i + 1}. {v}' if isinstance(valor, list) and etiqueta == 'Proceso' else v,
                             color='C00000' if v == '[PENDIENTE]' else None)
                _sombra(c[0], AZUL); _sombra(c[1], AZUL_CLARO)
            if len(filas) > 1:   # etiqueta combinada a lo alto de sus subfilas
                n = len(t.rows); t.cell(n - len(filas), 0).merge(t.cell(n - 1, 0))
        for f in t.rows: f.cells[0].width, f.cells[1].width = Cm(2.8), Cm(12.8)
        self.doc.add_paragraph()

    def tabla_mapeo(self, nombre, columnas, ancho=15.6):
        """columnas: [(columna, 'pk' | 'fk' | 'pk fk' | '')]. Una tabla por tabla de la BD, como G07: fila de nombre, fila
        de marcas y fila de atributos (sin las dos filas vacías de G07, a pedido del usuario). Los nombres se parten en
        renglones después de cada "_"; la letra baja de 11 a 8 pt solo en las tablas que no entran a 11."""
        largo = lambda c: max(len(x) for x in [y + '_' for y in c.split('_')[:-1]] + [c.split('_')[-1], 'pk fk'])   # renglón más largo, con su _
        mide = lambda c, m, tam: largo(c) * 0.02 * tam * (1.1 if 'pk' in m else 1) + 0.25   # la PK va en negrita
        cm = lambda cols, tam: sum(mide(c, m, tam) for c, m in cols)
        tam = next((t for t in (11, 10.5, 10, 9.5, 9, 8.5, 8) if cm(columnas, t) <= ancho), 8)
        n = len(columnas)
        t = self.doc.add_table(rows=3, cols=n); t.alignment = WD_TABLE_ALIGNMENT.CENTER; _bordes(t, '9CC2E5')
        t.autofit = False
        mar = OxmlElement('w:tblCellMar')   # márgenes de celda de 0,1 cm: más espacio para los nombres
        for lado in ('left', 'right'):
            e = OxmlElement(f'w:{lado}'); e.set(qn('w:w'), '57'); e.set(qn('w:type'), 'dxa'); mar.append(e)
        t._tbl.tblPr.append(mar)
        lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); t._tbl.tblPr.append(lay)
        anchos = [mide(c, m, tam) for c, m in columnas]
        anchos = [a * ancho / sum(anchos) for a in anchos]   # repartir el sobrante: la tabla ocupa todo el ancho
        cab = t.cell(0, 0).merge(t.cell(0, n - 1))
        _texto_celda(cab, nombre, bold=True, tam=16, fuente='Calibri', centro=True); _sombra(cab, AZUL_MAPEO)
        for i, (col, marca) in enumerate(columnas):
            _texto_celda(t.cell(1, i), marca, bold=bool(marca), italic='fk' in marca and 'pk' not in marca, tam=tam, fuente='Calibri')
            _texto_celda(t.cell(2, i), renglones(col, anchos[i], tam * (1.1 if 'pk' in marca else 1)), bold='pk' in marca,
                         tam=tam, fuente='Calibri')
            _sombra(t.cell(1, i), AZUL_MAPEO_CLARO)
        for col, a in zip(t.columns, anchos): col.width = Cm(a)
        for f in t.rows:
            f._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            for c, a in zip(f.cells, anchos if len(f.cells) == n else [ancho]):
                c.width = Cm(a)
                for par in c.paragraphs: par.paragraph_format.keep_with_next = True
        self.doc.add_paragraph()

    def fisico(self, nombre, columnas):
        """CREATE TABLE en TNR Bold 12 con columnas alineadas por tabulaciones (G07 7.3)."""
        def linea(texto, tabs=False):
            par = _sin_sangria(self.doc.add_paragraph(), False); par.paragraph_format.space_after = Pt(0)
            if tabs:
                par.paragraph_format.left_indent = Cm(0.6)
                for x in (5.0, 9.6, 12.3): par.paragraph_format.tab_stops.add_tab_stop(Cm(x))
            par.add_run(texto).bold = True
            return par
        linea(f'CREATE TABLE {nombre} (')
        for i, (col, tipo, nn, defecto) in enumerate(columnas):
            fin = ',' if i < len(columnas) - 1 else ''
            linea(f'{col}\t{tipo}\t{"NOT NULL" if nn else "NULL"}' + (f'\tDEFAULT {defecto}' if defecto else '') + fin, True)
        linea(');')
        self.doc.add_paragraph()

    # ---------------------------------------------------------------- figuras
    def imagen(self, ruta, rotulo=None, ancho=15.5, negrita=False, pie=None, alto_max=21.0):
        """Rótulo de texto encima (G07). pie: "Ilustración N Texto" debajo, solo donde G07 lo pone."""
        ruta = pathlib.Path(ruta)
        if rotulo: par = self.p(rotulo); par.runs[0].bold = negrita; par.paragraph_format.keep_with_next = True
        if not ruta.exists(): return self.pendiente(f'diagrama {ruta.name}')
        w, h = Image.open(ruta).size
        ancho = min(ancho, alto_max * w / h)
        par = _sin_sangria(self.doc.add_paragraph()); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img = par.add_run().add_picture(str(ruta), width=Cm(ancho))
        img._inline.docPr.set('descr', str(ruta.resolve()))   # el exportador cambia el PNG por su .emf
        if pie:
            par = self.p('Ilustración '); _campo(par, ' SEQ Ilustración \\* ARABIC ', '1'); par.add_run(' ' + pie)

    def seccion(self, horizontal, margenes=None):
        s = self.doc.add_section(WD_SECTION.NEW_PAGE)
        s.orientation = WD_ORIENT.LANDSCAPE if horizontal else WD_ORIENT.PORTRAIT
        s.page_width, s.page_height = (CARTA[1], CARTA[0]) if horizontal else CARTA
        for k, v in (margenes or (MARGEN_NAV if horizontal else MARGEN)).items(): setattr(s, k, v)
        return s

    def franjas(self, ruta, titulos, carpeta, primero=True):
        """Diagrama de navegación de G07: una imagen alta cortada en franjas horizontales, una por página apaisada; los
        títulos solo en la primera. Corta en la fila con menos tinta para no partir cajas. primero=False: sigue en la misma
        sección apaisada (salto de página), para no dejar páginas verticales en blanco entre actores; el llamador vuelve a
        la sección vertical al terminar."""
        ruta = pathlib.Path(ruta)
        if primero: self.seccion(True)
        for i, (t, nivel) in enumerate(titulos):   # "salto antes" en el párrafo: un salto suelto deja páginas vacías
            self.h(t, nivel).paragraph_format.page_break_before = not primero and i == 0
        if not ruta.exists():
            self.pendiente(f'diagrama {ruta.name}'); return
        img = Image.open(ruta)
        W, H = img.size
        ancho_cm, alto_cm = 25.9, 16.9
        tinta = (np.asarray(img.convert('L')) < 200).sum(axis=1)
        y, n, primera = 0, 1, True
        while y < H:
            util = alto_cm - (1.25 * len(titulos) if primera else 0)
            meta = y + int(W * util / ancho_cm)
            if meta >= H: corte = H
            else:
                desde = y + int((meta - y) * 0.88)   # llenar la página; dentro de ese margen, la fila más vacía
                corte = desde + int(np.argmin(tinta[desde:meta]))
            archivo = carpeta / f'{ruta.stem}-{n}.png'
            img.crop((0, y, W, corte)).save(archivo)
            par = _sin_sangria(self.doc.add_paragraph()); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.space_after = Pt(0); par.paragraph_format.page_break_before = not primera
            par.add_run().add_picture(str(archivo), width=Cm(ancho_cm))
            y, n, primera = corte, n + 1, False
