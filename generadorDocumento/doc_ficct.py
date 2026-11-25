"""Utilidades comunes para los informes Word de la materia con formato FICCT/APA
(carátula de integrantes, Times New Roman 12, carta, márgenes de 2.5 cm, figuras y tablas numeradas, índices).
Formato FICCT de los informes de la materia, copiado aquí para que el generador sea independiente. Después de guardar, exportar.ps1 actualiza
índices y exporta .doc y .pdf."""
import pathlib, re
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from rutas import LOGO   # escudo FICCT sin el fondo negro de las esquinas
TNR = 'Times New Roman'
INTEGRANTES = (('Lobo Gutierrez Carlos Gabriel', '223043117'), ('Serrate Basma Leonardo', '223044377'),
               ('Vasquez Ardaya Brandon Lider', '223044695'))


def _fuente(style, size=12, bold=False, italic=False, name=TNR):
    style.font.name, style.font.size, style.font.bold, style.font.italic = name, Pt(size), bold, italic
    style.font.color.rgb = RGBColor(0, 0, 0)
    rpr = style.element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.append(rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        rf.set(qn(a), name)
    for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:cstheme', 'w:eastAsiaTheme'):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]


def _campo(par, instr, texto=''):
    r = par.add_run(); f = OxmlElement('w:fldChar'); f.set(qn('w:fldCharType'), 'begin'); r._r.append(f)
    r = par.add_run(); t = OxmlElement('w:instrText'); t.set(qn('xml:space'), 'preserve'); t.text = instr; r._r.append(t)
    r = par.add_run(); f = OxmlElement('w:fldChar'); f.set(qn('w:fldCharType'), 'separate'); r._r.append(f)
    par.add_run(texto)
    r = par.add_run(); f = OxmlElement('w:fldChar'); f.set(qn('w:fldCharType'), 'end'); r._r.append(f)


ABREVIATURAS = {'Ing', 'Sc', 'Lic', 'Dr', 'Dra', 'Av', 'Sr', 'Sra', 'ed', 'Vol', 'No', 'pág', 'págs', 'etc', 'aprox', 'núm', 'Ph', 'p', 'pp'}


def dos_espacios(t):
    """Manual FICCT (Anexo D): dos espacios después del punto final de una oración. No toca abreviaturas ni el
    número inicial de una lista ("1. ")."""
    def rep(m):
        palabra = re.search(r'(\w+)$', t[:m.start()])
        if t[:m.start()].isdigit() or (palabra and palabra.group(1) in ABREVIATURAS): return m.group(0)
        return '.  '
    return re.sub(r'(?<=[\wáéíóúñ)\]»"”%])\. (?=[A-ZÁÉÍÓÚÑ¿¡(«"“])', rep, t)


def _sin_sangria(par, interlineado_simple=True):
    par.paragraph_format.first_line_indent = Cm(0)
    if interlineado_simple: par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    return par


class Informe:
    def __init__(self):
        self.doc = doc = Document()
        self.sec = sec = doc.sections[0]
        sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)
        for m in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'):
            setattr(sec, m, Cm(2.5))
        st = doc.styles
        _fuente(st['Normal'])
        pf = st['Normal'].paragraph_format
        pf.line_spacing_rule, pf.space_after, pf.first_line_indent = WD_LINE_SPACING.DOUBLE, Pt(0), Cm(1.27)
        for nivel, (al, it) in {1: (WD_ALIGN_PARAGRAPH.CENTER, False), 2: (WD_ALIGN_PARAGRAPH.LEFT, False),
                                3: (WD_ALIGN_PARAGRAPH.LEFT, True)}.items():
            hs = st[f'Heading {nivel}']
            _fuente(hs, 12, True, it)
            hs.paragraph_format.alignment = al
            hs.paragraph_format.first_line_indent = Cm(0)
            hs.paragraph_format.space_before, hs.paragraph_format.space_after = Pt(12), Pt(6)
            hs.paragraph_format.keep_with_next = True
        cap = st['Caption']; _fuente(cap, 12, False, True)
        cap.paragraph_format.first_line_indent = Cm(0); cap.paragraph_format.keep_with_next = True
        cap.paragraph_format.space_before = Pt(6); cap.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        codigo = st.add_style('Codigo', 1); _fuente(codigo, 8.5, name='Consolas')
        codigo.paragraph_format.first_line_indent = Cm(0); codigo.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        codigo.paragraph_format.space_after = Pt(0)
        nota = st.add_style('Nota', 1); _fuente(nota, 10)
        nota.paragraph_format.first_line_indent = Cm(0); nota.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        nota.paragraph_format.space_after = Pt(10)
        for s in ('List Bullet', 'List Number'):
            _fuente(st[s]); st[s].paragraph_format.first_line_indent = Cm(0)

    # ---------- texto ----------
    def p(self, texto, estilo=None, sangria=True, alin=None):
        """Párrafo con **negrita** y `código` simples."""
        par = self.doc.add_paragraph(style=estilo)
        if not sangria: par.paragraph_format.first_line_indent = Cm(0)
        if alin is not None: par.alignment = alin
        for i, trozo in enumerate(texto.split('**')):
            for j, t in enumerate(trozo.split('`')):
                if not t: continue
                if j % 2 == 0: t = dos_espacios(t)
                r = par.add_run(t); r.bold = (i % 2 == 1)
                if j % 2 == 1: r.font.name = 'Consolas'; r.font.size = Pt(10.5)
        return par

    def h(self, texto, nivel): return self.doc.add_heading(texto, nivel)

    def orientacion(self, horizontal):
        """Nueva sección (en página nueva) horizontal o vertical, con los mismos márgenes; el encabezado con el número sigue."""
        from docx.enum.section import WD_ORIENT, WD_SECTION
        # Si la sección actual sigue vacía (p. ej. dos figuras apaisadas seguidas), se reorienta en lugar de abrir otra:
        # una sección vacía entre dos saltos de sección es una página en blanco en Word.
        cuerpo = self.doc.element.body
        previo = cuerpo[-2] if len(cuerpo) > 1 else None
        vacia = previo is not None and previo.tag == qn('w:p') and previo.find(qn('w:pPr') + '/' + qn('w:sectPr')) is not None
        s = self.doc.sections[-1] if vacia else self.doc.add_section(WD_SECTION.NEW_PAGE)
        s.orientation = WD_ORIENT.LANDSCAPE if horizontal else WD_ORIENT.PORTRAIT
        s.page_width, s.page_height = (Cm(27.94), Cm(21.59)) if horizontal else (Cm(21.59), Cm(27.94))
        s.different_first_page_header_footer = False   # solo la carátula va sin número
        for m in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'):
            setattr(s, m, Cm(2.5))

    def lista(self, items, numerada=False):
        for n, it in enumerate(items, 1):
            if numerada:
                par = self.p(f'{n}. ' + it, sangria=False)
                par.paragraph_format.left_indent = Cm(1.27); par.paragraph_format.first_line_indent = Cm(-0.63)
            else:
                self.p(it, 'List Bullet', sangria=False)

    def nota(self, texto):
        par = self.doc.add_paragraph(style='Nota'); r = par.add_run('Nota. '); r.italic = True
        for j, t in enumerate(texto.split('`')):
            if t:
                r = par.add_run(t if j % 2 else dos_espacios(t))
                if j % 2 == 1: r.font.name = 'Consolas'

    def salto(self): self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ---------- figuras y tablas ----------
    def rotulo(self, tipo, titulo):
        par = self.doc.add_paragraph(style='Caption')
        par.add_run(f'{tipo} ')
        _campo(par, f' SEQ {tipo} \\* ARABIC ', '1')
        par.add_run(f'. {titulo}')
        return par

    def figura(self, ruta, titulo, nota_txt=None, ancho=16.0):
        self.rotulo('Figura', titulo)
        par = _sin_sangria(self.doc.add_paragraph()); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next = bool(nota_txt)
        img = par.add_run().add_picture(str(ruta), width=Cm(ancho))
        img._inline.docPr.set('descr', str(pathlib.Path(ruta).resolve()))   # exportar.ps1 cambia el PNG por su .emf si existe
        if nota_txt: self.nota(nota_txt)

    def tabla(self, titulo, cab, filas, anchos=None, nota_txt=None, tam=10, centrar_desde=None, partir=False):
        """partir=True: tabla larga que puede continuar en la página siguiente (repite el encabezado y no corta filas)
        en lugar de saltar entera y dejar media página en blanco."""
        self.rotulo('Tabla', titulo)
        t = self.doc.add_table(rows=1, cols=len(cab)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
        b = OxmlElement('w:tblBorders')
        for lado, val in (('top', 'single'), ('bottom', 'single'), ('left', 'nil'), ('right', 'nil'),
                          ('insideH', 'nil'), ('insideV', 'nil')):
            e = OxmlElement(f'w:{lado}'); e.set(qn('w:val'), val); e.set(qn('w:sz'), '8'); e.set(qn('w:color'), '000000'); b.append(e)
        t._tbl.tblPr.append(b)
        for i, c in enumerate(cab):
            cel = t.rows[0].cells[i]; cel.text = ''
            r = cel.paragraphs[0].add_run(c); r.bold = True; r.font.size = Pt(tam)
            bt = OxmlElement('w:tcBorders'); e = OxmlElement('w:bottom'); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '6')
            bt.append(e); cel._tc.get_or_add_tcPr().append(bt)
        for f in filas:
            cells = t.add_row().cells
            for i, v in enumerate(f):
                cells[i].text = ''
                cells[i].paragraphs[0].add_run(str(v)).font.size = Pt(tam)
        for k, row in enumerate(t.rows):
            if partir:
                trpr = row._tr.get_or_add_trPr()
                trpr.append(OxmlElement('w:cantSplit'))
                if k == 0: trpr.append(OxmlElement('w:tblHeader'))
            for i, cel in enumerate(row.cells):
                for par in cel.paragraphs:
                    _sin_sangria(par); par.paragraph_format.space_after = Pt(2)
                    # la tabla no se separa de su título; sin partir, tampoco se corta
                    par.paragraph_format.keep_with_next = k < (1 if partir else len(t.rows) - 1)
                    if centrar_desde is not None and i >= centrar_desde: par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if anchos: cel.width = Cm(anchos[i])
        if nota_txt: self.nota(nota_txt)
        else: self.doc.add_paragraph(style='Nota')
        return t

    def bloque(self, texto, titulo=None):
        """Código o salida de terminal en un recuadro gris."""
        if titulo: self.p(titulo, sangria=False).runs[0].italic = True
        t = self.doc.add_table(rows=1, cols=1); t.alignment = WD_TABLE_ALIGNMENT.CENTER
        cel = t.rows[0].cells[0]
        sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:fill'), 'F3F3F3'); cel._tc.get_or_add_tcPr().append(sh)
        b = OxmlElement('w:tblBorders')
        for lado in ('top', 'bottom', 'left', 'right'):
            e = OxmlElement(f'w:{lado}'); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4'); e.set(qn('w:color'), 'BFBFBF'); b.append(e)
        t._tbl.tblPr.append(b)
        cel.paragraphs[0].style = 'Codigo'
        lineas = texto.rstrip('\n').split('\n')
        cel.paragraphs[0].add_run(lineas[0])
        for l in lineas[1:]:
            cel.add_paragraph(l, style='Codigo')
        self.doc.add_paragraph(style='Nota')

    # ---------- partes fijas ----------
    def caratula(self, titulo, subtitulo, fecha=None, integrantes=INTEGRANTES, grupo=True):
        self.sec.different_first_page_header_footer = True

        def centro(texto, size=12, bold=False, italic=False, antes=0, despues=0):
            par = _sin_sangria(self.doc.add_paragraph()); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.space_before, par.paragraph_format.space_after = Pt(antes), Pt(despues)
            r = par.add_run(texto); r.bold, r.italic, r.font.size = bold, italic, Pt(size)

        def dato(et, val):
            par = _sin_sangria(self.doc.add_paragraph()); par.paragraph_format.space_after = Pt(9)
            par.paragraph_format.left_indent = Cm(1.5)
            par.add_run(f'{et}: ').bold = True; par.add_run(val)

        centro('UNIVERSIDAD AUTÓNOMA GABRIEL RENÉ MORENO', 16, True, despues=10)
        centro('Facultad de Ingeniería en Ciencias de la Computación y Telecomunicaciones', 13, True, despues=14)
        par = _sin_sangria(self.doc.add_paragraph()); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.add_run().add_picture(str(LOGO), width=Cm(4.6))
        centro(titulo, 16, True, antes=14, despues=4)
        centro(subtitulo, 12, False, True, despues=26)
        dato('Materia', 'Tecnología Web (INF513) – SA')
        dato('Docente', 'M.Sc. Ing. Balcázar Veizaga Evans')
        if grupo: dato('Grupo', '05 SA')
        par = _sin_sangria(self.doc.add_paragraph()); par.paragraph_format.left_indent = Cm(1.5)
        par.add_run('Integrantes:' if len(integrantes) > 1 else 'Estudiante:').bold = True
        for nom, reg in integrantes:
            par = _sin_sangria(self.doc.add_paragraph()); par.paragraph_format.left_indent = Cm(2.5)
            par.paragraph_format.space_after = Pt(4)
            par.paragraph_format.tab_stops.add_tab_stop(Cm(11.5)); par.add_run(f'{nom}\t{reg}')
        dato('Gestión', '2-2026')
        centro('Santa Cruz de la Sierra' + (f', {fecha}' if fecha else ''), 12, antes=30)   # sin fecha si no se pasa
        hp = self.sec.header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT; hp.paragraph_format.first_line_indent = Cm(0)
        _campo(hp, ' PAGE ', '1')

    def revision(self, titulo, filas, nota_txt=None):
        """Tabla destacada con URL y cuentas de prueba. filas: (etiqueta, valor, destacar)."""
        self.salto()
        self.h(titulo, 1)
        t = self.doc.add_table(rows=0, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False   # anchos fijos: una URL larga no debe angostar la columna de etiquetas
        lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); t._tbl.tblPr.append(lay)
        b = OxmlElement('w:tblBorders')
        for lado in ('top', 'bottom', 'left', 'right', 'insideH', 'insideV'):
            e = OxmlElement(f'w:{lado}'); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '6'); e.set(qn('w:color'), '7F7F7F'); b.append(e)
        t._tbl.tblPr.append(b)
        for et, val, fuerte in filas:
            c = t.add_row().cells
            for cel, txt, neg in ((c[0], et, True), (c[1], val, fuerte)):
                cel.text = ''
                par = cel.paragraphs[0]
                for i, l in enumerate(txt.split('\n')):
                    if i: par = cel.add_paragraph()
                    r = par.add_run(l); r.bold = neg; r.font.size = Pt(12 if fuerte else 11)
                for par in cel.paragraphs:
                    _sin_sangria(par); par.paragraph_format.space_before = Pt(3); par.paragraph_format.space_after = Pt(3)
            if fuerte:
                for cel in c:
                    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:fill'), 'EAF1FA'); cel._tc.get_or_add_tcPr().append(sh)
            c[0].width, c[1].width = Cm(5.2), Cm(11.3)
        for col, ancho in zip(t.columns, (Cm(5.2), Cm(11.3))): col.width = ancho
        if nota_txt: self.p(nota_txt, 'Nota', sangria=False)

    def indices(self, tablas=True, separar_figuras_tablas=True, niveles='1-3', figuras=True):
        self.salto()
        par = _sin_sangria(self.doc.add_paragraph()); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(12); par.add_run('ÍNDICE GENERAL').bold = True
        par = _sin_sangria(self.doc.add_paragraph(), False)
        _campo(par, f' TOC \\o "{niveles}" \\h \\z \\u ', 'Actualizar campo para generar el índice.')
        self.salto()

        if figuras:   # un informe sin figuras no lleva un índice de figuras vacío
            par = _sin_sangria(self.doc.add_paragraph()); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.space_after = Pt(12); par.add_run('ÍNDICE DE FIGURAS').bold = True
            par = _sin_sangria(self.doc.add_paragraph(), False)
            _campo(par, ' TOC \\h \\z \\c "Figura" ', 'Actualizar campo para generar el índice.')

            if separar_figuras_tablas:
                self.salto()
            else:
                par = _sin_sangria(self.doc.add_paragraph())
                par.paragraph_format.space_before = Pt(18)

        if tablas:
            par = _sin_sangria(self.doc.add_paragraph()); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.space_after = Pt(12); par.add_run('ÍNDICE DE TABLAS').bold = True
            par = _sin_sangria(self.doc.add_paragraph(), False)
            _campo(par, ' TOC \\h \\z \\c "Tabla" ', 'Actualizar campo para generar el índice.')
        self.salto()

    def referencias(self, refs):
        """Lista de referencias según el Anexo D del manual FICCT (APA): orden alfabético, sangría francesa,
        «Recuperado de» antes de la URL, «doi:» para los DOI y sin punto después de la dirección web."""
        import re
        for r in sorted(refs, key=str.lower):
            r = re.sub(r' https://doi\.org/(\S+)$', r' doi: \1', r)
            if 'Recuperado de' not in r: r = re.sub(r' (https?://\S+)$', r' Recuperado de \1', r)
            par = self.doc.add_paragraph(r)
            par.paragraph_format.first_line_indent = Cm(-1.27); par.paragraph_format.left_indent = Cm(1.27)

    def guardar(self, ruta):
        ruta = pathlib.Path(ruta); ruta.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(ruta); print('ok', ruta)
        return ruta
