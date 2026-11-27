"""Ediciones puntuales sobre el DOCX maestro; nunca regenera capítulos no autorizados."""
from pathlib import Path
import copy,json,re,sys,zipfile,hashlib,shutil,tempfile,uuid
from lxml import etree as E
ROOT=Path(__file__).resolve().parent.parent; DOC=ROOT/'generadorDocumento';OUT=ROOT/'tmp/actualizacion_documental'
sys.path.insert(0,str(DOC))
from actualizacion_contenido import ESPECIFICACIONES
from diccionario_actual import TABLAS,TRIGGERS,descripcion,foreign_keys
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';NS={'w':W}
def q(name):return '{'+W+'}'+name
def txt(e):return ''.join(e.itertext()) if False else ''.join(t.text or '' for t in e.findall('.//w:t',NS))
def paragraph(text='',bold=False,size=24,style=None):
    p=E.Element(q('p'));pr=E.SubElement(p,q('pPr'));E.SubElement(pr,q('spacing'),{q('after'):'100'})
    if style:E.SubElement(pr,q('pStyle'),{q('val'):style})
    r=E.SubElement(p,q('r'));rp=E.SubElement(r,q('rPr'));E.SubElement(rp,q('rFonts'),{q('ascii'):'Times New Roman',q('hAnsi'):'Times New Roman'})
    E.SubElement(rp,q('sz'),{q('val'):str(size)})
    if bold:E.SubElement(rp,q('b'))
    E.SubElement(r,q('t'),{'{http://www.w3.org/XML/1998/namespace}space':'preserve'}).text=text
    return p
def set_cell(cell,lines):
    for child in list(cell):
        if child.tag!=q('tcPr'):cell.remove(child)
    for line in lines if isinstance(lines,list) else [lines]:cell.append(paragraph(line))
def replace_zip(path,parts):
    temp=path.with_name(path.stem+'.incremental.tmp.docx')
    with zipfile.ZipFile(path) as z,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as target:
        for item in z.infolist():target.writestr(item,parts.get(item.filename,z.read(item.filename)))
    temp.replace(path)
def doc_read():
    path=DOC/'documento/P2-INF513-GRUPO05SA.docx'
    with zipfile.ZipFile(path) as z:root=E.fromstring(z.read('word/document.xml'))
    return path,root,root.find('w:body',NS)
def protected(body):
    items=list(body); starts=[i for i,b in enumerate(items) if txt(b).startswith('Capítulo IV:')]
    a=starts[-1];b=next(i for i in range(a+1,len(items)) if txt(items[i]).startswith('Capítulo V:'))
    return [E.tostring(x,method='c14n') for x in items[a:b]]
def phase2():
    path,root,body=doc_read();guard=protected(body);done=[]
    cat=json.loads((OUT/'catalogo_fuente.json').read_text(encoding='utf-8'))
    for cu,spec in ESPECIFICACIONES.items():
        table=next(t for t in body.findall('w:tbl',NS) if re.match(r'Caso de UsoCU0?'+cu[2]+r'\.',txt(t)))
        rows=table.findall('w:tr',NS);template=copy.deepcopy(rows[1]);header=copy.deepcopy(rows[0])
        for row in rows:table.remove(row)
        table.append(header)
        fields=[('Propósito',spec['Objetivo']),('Descripción',spec['Descripción']),('Actores',spec['Actores']),('Actor Iniciador','Vendedor' if cu in ('CU4','CU5','CU6','CU7') else 'Visitante' if cu=='CU2' else 'Administrador o Coordinador' if cu=='CU3' else 'Usuario autenticado con el rol y permiso existentes'),('Precondición',spec['Precondición'])]
        fields += [('Proceso',f'{i}. {step}') for i,step in enumerate(spec['Proceso'],1)]
        fields += [('Flujos Alternativos',[f'A{i}. {step}' for i,step in enumerate(spec['Flujos Alternativos'],1)]),('Excepciones',spec['Excepciones']),('Postcondición',spec['Postcondición']),('Reglas de negocio',spec['Reglas de negocio']),('Interfaces',spec['Interfaces']),('Operaciones',spec['Operaciones']),('Clases relacionadas',', '.join(cat[cu]['nodes'])),('Diagramas','Se conservan los diagramas originales de este CU en crm-p2.eapx; clases, secuencia y comunicación se presentan con sus vistas complementarias legibles. Los identificadores de los CU y los cuatro actores originales se mantienen.')]
        for label,value in fields:
            row=copy.deepcopy(template);cells=row.findall('w:tc',NS)
            for c in cells:
                vm=c.find('w:tcPr/w:vMerge',NS)
                if vm is not None:vm.getparent().remove(vm)
            set_cell(cells[0],label);set_cell(cells[1],value);table.append(row)
        done.append(cu)
    assert protected(body)==guard,'El capítulo IV cambió'
    replace_zip(path,{'word/document.xml':E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)})
    (OUT/'fase2_word.json').write_text(json.dumps({'cu_actualizados':done,'capitulo_IV_intacto':True},indent=2),encoding='utf-8')
    print('Ocho especificaciones actualizadas; capítulo IV y encabezados originales conservados.')

def heading(text,level=3):
    return paragraph(text,bold=True,size=26,style='Ttulo'+str(level+1))

def phase7():
    from actualizacion_contenido import ARQUITECTURA
    import contenido
    path,root,body=doc_read();guard=protected(body);chapter='';changes=[]
    for p in body:
        text=txt(p)
        if text.startswith('Capítulo'):chapter=text
        if not chapter.startswith('Capítulo IV:'):
            for node in p.findall('.//w:t',NS):
                if node.text and (node.text[0].isspace() or node.text[-1].isspace()):node.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        if p.tag==q('p'):
            ps=p.find('w:pPr/w:pStyle',NS)
            if ps is not None and re.fullmatch(r'Heading[1-4]',ps.get(q('val'),'') or ''):
                ps.set(q('val'),'Ttulo'+str(int(ps.get(q('val'))[-1])+1))
        replacement=None
        if chapter.startswith('Capítulo I:') and text.startswith('CU6. '+contenido.CU['CU6']+':'):
            replacement='CU6. '+contenido.CU['CU6']+': '+contenido.ALCANCE['CU6']
        if chapter.startswith('Capítulo VI:') and 'los comprobantes manuales' in text:
            replacement=text.replace('los comprobantes manuales','la consulta/revisión de comprobantes históricos y el envío manual de enlaces')
        if chapter.startswith('Capítulo VIII:'):
            if text.startswith('PHP 8.4:'):
                replacement='PHP 8.4.24: versión CLI comprobada en el entorno local de trabajo. El código de negocio y datos se ejecuta en PHP; no se acredita la versión del servidor institucional previsto sin medición remota.'
            elif text.startswith('PostgreSQL 18:'):
                replacement='PostgreSQL 17.4: versión local verificada en crm_educativo, esquema public, puerto 5432. El servidor db.tecnoweb.org.bo y db_grupo05sa corresponden al destino institucional previsto; su versión y disponibilidad no fueron comprobadas.'
            elif text.startswith('Enterprise Architect 15 Trial:'):
                replacement='Enterprise Architect 15: herramienta UML instalada, con automatización COM oficial sobre el proyecto original generadorDocumento/ea/crm-p2.eapx. El modelo conserva diagramas y elementos editables; las exportaciones EMF mantienen los trazos vectoriales en Word.'
        if replacement is not None:
            oldpr=copy.deepcopy(p.find('w:pPr',NS));new=paragraph(replacement)
            if oldpr is not None:new.remove(new.find('w:pPr',NS));new.insert(0,oldpr)
            body.replace(p,new);changes.append(replacement.split(':')[0])
    marker='Responsabilidades verificadas de las tres capas'
    if not any(txt(p)==marker for p in body):
        ix=next(i for i,p in enumerate(body) if txt(p)=='5. Análisis de la Arquitectura')+1
        additions=[paragraph(marker,bold=True)]
        for title,text in ARQUITECTURA:additions.append(paragraph(title+': '+text))
        for p in reversed(additions):body.insert(ix,p)
    assert protected(body)==guard,'El capítulo IV cambió'
    replace_zip(path,{'word/document.xml':E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)})
    (OUT/'fase7_word.json').write_text(json.dumps({'cambios':changes,'capitulo_IV_intacto':True},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Arquitectura y herramientas actualizadas puntualmente; capítulo IV intacto.')

def data_table(headers,rows,widths):
    table=E.Element(q('tbl'));pr=E.SubElement(table,q('tblPr'))
    E.SubElement(pr,q('tblW'),{q('w'):str(sum(widths)),q('type'):'dxa'})
    E.SubElement(pr,q('tblLayout'),{q('type'):'fixed'})
    borders=E.SubElement(pr,q('tblBorders'))
    for side in ('top','left','bottom','right','insideH','insideV'):E.SubElement(borders,q(side),{q('val'):'single',q('sz'):'4',q('color'):'B7C9D8'})
    grid=E.SubElement(table,q('tblGrid'))
    for width in widths:E.SubElement(grid,q('gridCol'),{q('w'):str(width)})
    for index,row in enumerate([headers]+list(rows)):
        tr=E.SubElement(table,q('tr'));trpr=E.SubElement(tr,q('trPr'))
        if index==0:E.SubElement(trpr,q('tblHeader'))
        for value,width in zip(row,widths):
            cell=E.SubElement(tr,q('tc'));cp=E.SubElement(cell,q('tcPr'));E.SubElement(cp,q('tcW'),{q('w'):str(width),q('type'):'dxa'})
            if index==0:E.SubElement(cp,q('shd'),{q('fill'):'D6E8F5'})
            for line in str(value).splitlines() or ['']:cell.append(paragraph(line,bold=index==0))
    return table

ANCHO_DICCIONARIO = [2000, 1750, 3600, 900, 850, 1600]
ANCHO_MAXIMO_MAPEO = 10700
ATRIBUTOS_POR_BLOQUE = 8

def tabla_mapeo(nombre, columnas):
    """Modelo horizontal con nombre en la franja azul, claves y dos filas vacías."""
    cantidad = len(columnas)
    ancho = min(ANCHO_MAXIMO_MAPEO, max(6000, cantidad * 1450))
    anchos = [ancho // cantidad] * cantidad
    anchos[-1] += ancho - sum(anchos)
    tabla = E.Element(q('tbl')); propiedades = E.SubElement(tabla, q('tblPr'))
    E.SubElement(propiedades, q('tblW'), {q('w'):str(ancho), q('type'):'dxa'})
    E.SubElement(propiedades, q('tblInd'), {q('w'):'80', q('type'):'dxa'})
    E.SubElement(propiedades, q('tblLayout'), {q('type'):'fixed'})
    margen = E.SubElement(propiedades, q('tblCellMar'))
    for lado in ('top','bottom'):E.SubElement(margen, q(lado), {q('w'):'55', q('type'):'dxa'})
    for lado in ('left','right'):E.SubElement(margen, q(lado), {q('w'):'60', q('type'):'dxa'})
    bordes = E.SubElement(propiedades, q('tblBorders'))
    for lado in ('top','left','bottom','right','insideH','insideV'):
        E.SubElement(bordes, q(lado), {q('val'):'single', q('sz'):'4', q('color'):'9DBED9'})
    grilla = E.SubElement(tabla, q('tblGrid'))
    for medida in anchos:E.SubElement(grilla, q('gridCol'), {q('w'):str(medida)})

    for indice in range(5):
        fila = E.SubElement(tabla, q('tr'))
        reglas_fila = E.SubElement(fila, q('trPr'))
        E.SubElement(reglas_fila, q('cantSplit'))
        if indice == 0:E.SubElement(reglas_fila, q('tblHeader'))
        valores = ([nombre] if indice == 0 else
                   [', '.join(m.lower() for m in ('PK','FK') if m in clave.split(', '))
                    for _, clave in columnas] if indice == 1 else
                   [atributo for atributo, _ in columnas] if indice == 2 else
                   [''] * cantidad)
        for posicion, valor in enumerate(valores):
            celda = E.SubElement(fila, q('tc'))
            reglas_celda = E.SubElement(celda, q('tcPr'))
            E.SubElement(reglas_celda, q('tcW'), {q('w'):str(ancho if indice == 0 else anchos[posicion]), q('type'):'dxa'})
            if indice == 0:E.SubElement(reglas_celda, q('gridSpan'), {q('val'):str(cantidad)})
            if indice in (0, 1, 3):
                E.SubElement(reglas_celda, q('shd'), {q('fill'):'5B9BD5' if indice == 0 else 'DCEAF6'})
            parrafo = paragraph(valor, bold=(indice in (0, 1) or
                                              indice == 2 and 'PK' in columnas[posicion][1]),
                                size=23 if indice == 0 else 17)
            espaciado = parrafo.find('w:pPr/w:spacing', NS)
            espaciado.set(q('after'), '0')
            if indice < 4:E.SubElement(parrafo.find('w:pPr', NS), q('keepNext'))
            if indice == 0:
                E.SubElement(parrafo.find('w:pPr', NS), q('jc'), {q('val'):'center'})
            if indice == 2 and len(valor) > 14 and '_' in valor:
                # Saltos visibles en los guiones bajos; el nombre extraído sigue siendo idéntico.
                segmentos = valor.split('_'); lineas = []; linea = ''
                for i, segmento in enumerate(segmentos):
                    pieza = segmento + ('_' if i < len(segmentos)-1 else '')
                    if linea and len(linea)+len(pieza) > 14:
                        lineas.append(linea); linea = pieza
                    else:linea += pieza
                lineas.append(linea)
                if len(lineas) > 1:
                    run = parrafo.find('w:r', NS)
                    run.find('w:t', NS).text = lineas[0]
                    for linea in lineas[1:]:
                        E.SubElement(run, q('br'))
                        E.SubElement(run, q('t')).text = linea
            celda.append(parrafo)
    return tabla

def bloques_mapeo(nombre, columnas):
    grupos = [columnas[i:i+ATRIBUTOS_POR_BLOQUE]
              for i in range(0, len(columnas), ATRIBUTOS_POR_BLOQUE)]
    return [tabla_mapeo(nombre, grupo) for grupo in grupos]

def titulo_mapeo(nombre):
    titulo = paragraph(nombre, bold=True, size=22)
    titulo.find('w:pPr/w:spacing', NS).set(q('after'), '60')
    E.SubElement(titulo.find('w:pPr', NS), q('keepNext'))
    return titulo

def separador_mapeo():
    espacio = paragraph('\u00a0', size=12)
    espacio.find('w:pPr/w:spacing', NS).set(q('after'), '120')
    return espacio

def actualizar_mapeo_actual():
    """Sustituye el mapeo detallado o actualiza el horizontal sin cambiar sus datos."""
    path, root, body = doc_read()
    inicio, fin = section_range(body, '7.2.1. Mapeo', '7.3. Diseño Físico')
    seccion = list(body)[inicio:fin]
    tablas = [x for x in seccion if x.tag == q('tbl')]
    horizontal = (len(tablas) > len(TABLAS) or
                  len(tablas[0].findall('w:tr', NS)) == 4 or
                  len(tablas[0].find('w:tblGrid', NS)) != 5)
    if horizontal:
        grupos = {}
        nombre_actual = None
        for elemento in seccion:
            if elemento.tag == q('p') and txt(elemento) in TABLAS:
                nombre_actual = txt(elemento)
            if elemento.tag != q('tbl'):continue
            filas = elemento.findall('w:tr', NS)
            primera = filas[0].find('w:tc/w:tcPr/w:gridSpan', NS)
            tamano_bloque = 5 if primera is not None else 4
            assert len(filas) % tamano_bloque == 0
            for inicio_bloque in range(0, len(filas), tamano_bloque):
                if tamano_bloque == 5:
                    nombre = re.sub(r' \(parte \d+ de \d+\)$', '', txt(filas[inicio_bloque]))
                    indice_marcas, indice_atributos = inicio_bloque+1, inicio_bloque+2
                else:
                    nombre = nombre_actual
                    indice_marcas, indice_atributos = inicio_bloque, inicio_bloque+1
                assert nombre in TABLAS, nombre
                marcas = [txt(c).upper() for c in filas[indice_marcas].findall('w:tc', NS)]
                atributos = [txt(c) for c in filas[indice_atributos].findall('w:tc', NS)]
                assert len(marcas) == len(atributos)
                grupos.setdefault(nombre, []).extend(zip(atributos, marcas))
    else:
        parrafos = [txt(x) for x in seccion if x.tag == q('p')]
        nombres = [nombre for nombre in parrafos if nombre in TABLAS]
        assert len(tablas) == len(nombres) == len(TABLAS)
        grupos = {}
        for nombre, tabla in zip(nombres, tablas):
            filas = [[txt(c) for c in fila.findall('w:tc', NS)]
                     for fila in tabla.findall('w:tr', NS)[1:]]
            grupos[nombre] = [(fila[0], fila[2]) for fila in filas]
    assert len(grupos) == len(TABLAS)
    nuevos = [copy.deepcopy(seccion[0])]
    total = bloques = 0
    for nombre, columnas in grupos.items():
        partes = bloques_mapeo(nombre, columnas)
        nuevos.append(titulo_mapeo(nombre))
        for parte in partes:nuevos.extend([parte, separador_mapeo()])
        total += len(columnas)
        bloques += len(partes)
    assert total == 287, total
    replace_range(body, inicio, fin, nuevos)
    continuar_tras_mapeo(body)
    OUT.mkdir(parents=True, exist_ok=True)
    respaldo = OUT / ('respaldo_antes_mapeo_' + uuid.uuid4().hex + '.docx')
    shutil.copy2(path, respaldo)
    replace_zip(path, {'word/document.xml':E.tostring(root, xml_declaration=True,
                                                       encoding='UTF-8', standalone=True)})
    print(f'Mapeo actualizado: {len(grupos)} tablas, {total} atributos, '
          f'{bloques} bloques. Respaldo: {respaldo}')

def fila_diccionario(nombre, tipo_exacto, descripcion, clave, nulabilidad):
    """Presenta metadatos existentes sin alterar el tipo ni la condición de la columna."""
    tipo = tipo_exacto.lower().strip()
    if tipo.startswith('character varying('):
        dato, tamano = 'VARCHAR', tipo[tipo.index('(')+1:tipo.index(')')]
    elif tipo.startswith('numeric('):
        dato, tamano = 'NUMERIC', tipo[tipo.index('(')+1:tipo.index(')')]
    elif tipo.startswith('timestamp('):
        dato, tamano = 'TIMESTAMP', '—'
    else:
        dato = {'integer':'INT', 'bigint':'BIGINT', 'smallint':'SMALLINT'}.get(tipo, tipo.upper())
        tamano = '—'
    marcas = [x.strip() for x in clave.split(',') if x.strip() in ('PK', 'FK', 'UNIQUE')]
    return [nombre, dato, descripcion, tamano,
            'Sí' if nulabilidad == 'NULL' else 'No', ', '.join(marcas) or '—']

def tabla_diccionario(filas):
    """Tabla de seis columnas con ancho fijo menor que el área útil de 7.3."""
    anchos = ANCHO_DICCIONARIO
    tabla = E.Element(q('tbl')); propiedades = E.SubElement(tabla, q('tblPr'))
    E.SubElement(propiedades, q('tblW'), {q('w'):str(sum(anchos)), q('type'):'dxa'})
    E.SubElement(propiedades, q('tblInd'), {q('w'):'80', q('type'):'dxa'})
    E.SubElement(propiedades, q('tblLayout'), {q('type'):'fixed'})
    margenes = E.SubElement(propiedades, q('tblCellMar'))
    for lado in ('top', 'bottom'):
        E.SubElement(margenes, q(lado), {q('w'):'65', q('type'):'dxa'})
    for lado in ('left', 'right'):
        E.SubElement(margenes, q(lado), {q('w'):'75', q('type'):'dxa'})
    bordes = E.SubElement(propiedades, q('tblBorders'))
    for lado in ('top','left','bottom','right','insideH','insideV'):
        E.SubElement(bordes, q(lado), {q('val'):'single', q('sz'):'4', q('color'):'B7C9D8'})
    grilla = E.SubElement(tabla, q('tblGrid'))
    for ancho in anchos:E.SubElement(grilla, q('gridCol'), {q('w'):str(ancho)})
    encabezado = ['Atributo', 'Tipo de dato', 'Descripción', 'Tamaño', 'Nulo', 'Llave']
    for indice, valores in enumerate([encabezado] + list(filas)):
        fila = E.SubElement(tabla, q('tr'))
        propiedades_fila = E.SubElement(fila, q('trPr'))
        E.SubElement(propiedades_fila, q('cantSplit'))
        if indice == 0:E.SubElement(propiedades_fila, q('tblHeader'))
        for valor, ancho in zip(valores, anchos):
            celda = E.SubElement(fila, q('tc'))
            propiedades_celda = E.SubElement(celda, q('tcPr'))
            E.SubElement(propiedades_celda, q('tcW'), {q('w'):str(ancho), q('type'):'dxa'})
            if indice == 0:E.SubElement(propiedades_celda, q('shd'), {q('fill'):'16324F'})
            parrafo = paragraph(str(valor), bold=indice == 0, size=18)
            parrafo.find('w:pPr/w:spacing', NS).set(q('after'), '0')
            if indice == 0:
                E.SubElement(parrafo.find('w:pPr', NS), q('keepNext'))
                color = E.SubElement(parrafo.find('w:r/w:rPr', NS), q('color'))
                color.set(q('val'), 'FFFFFF')
            celda.append(parrafo)
    return tabla

def actualizar_diccionario_actual():
    """Rehace solamente 7.3.1; admite el mapeo antiguo y el horizontal."""
    path, root, body = doc_read()
    inicio_mapeo, fin_mapeo = section_range(body, '7.2.1. Mapeo', '7.3. Diseño Físico')
    inicio, fin = section_range(body, '7.3.1. Diccionario', '7.3.2.')
    mapeo = [x for x in list(body)[inicio_mapeo:fin_mapeo] if x.tag == q('tbl')]
    seccion = list(body)[inicio:fin]
    actuales = [x for x in seccion if x.tag == q('tbl')]
    nombres = [txt(x) for x in seccion if x.tag == q('p')][1:]
    assert len(actuales) == len(nombres) == len(TABLAS)
    nuevos = [copy.deepcopy(seccion[0])]
    total = 0
    mapeo_antiguo = len(mapeo) == len(TABLAS) and txt(mapeo[0].find('w:tr', NS)).startswith('Columna')
    for indice, (nombre, tabla_actual) in enumerate(zip(nombres, actuales)):
        assert nombre in TABLAS, nombre
        filas_actuales = [[txt(c) for c in fila.findall('w:tc', NS)]
                          for fila in tabla_actual.findall('w:tr', NS)[1:]]
        if mapeo_antiguo:
            filas_mapeo = [[txt(c) for c in fila.findall('w:tc', NS)]
                           for fila in mapeo[indice].findall('w:tr', NS)[1:]]
            assert len(filas_mapeo) == len(filas_actuales), nombre
            filas = []
            for m, d in zip(filas_mapeo, filas_actuales):
                assert m[0] == d[0], (nombre, m[0], d[0])
                filas.append(fila_diccionario(m[0], m[1], d[2], m[2], m[3]))
        else:
            assert len(filas_actuales[0]) == 6, nombre
            filas = filas_actuales
        titulo = copy.deepcopy(next(x for x in seccion if x.tag == q('p') and txt(x) == nombre))
        propiedades_titulo = titulo.find('w:pPr', NS)
        if propiedades_titulo is None:propiedades_titulo = E.Element(q('pPr'));titulo.insert(0, propiedades_titulo)
        if propiedades_titulo.find('w:keepNext', NS) is None:E.SubElement(propiedades_titulo, q('keepNext'))
        nuevos.extend([titulo, tabla_diccionario(filas)])
        total += len(filas)
    assert total == 287, total
    replace_range(body, inicio, fin, nuevos)
    respaldo = OUT / ('respaldo_antes_diccionario_' + uuid.uuid4().hex + '.docx')
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, respaldo)
    replace_zip(path, {'word/document.xml':E.tostring(root, xml_declaration=True,
                                                       encoding='UTF-8', standalone=True)})
    print(f'Diccionario actualizado: {len(actuales)} tablas, {total} atributos. Respaldo: {respaldo}')

def section_range(body,start_text,end_text):
    items=list(body);starts=[i for i,p in enumerate(items) if txt(p).startswith(start_text)]
    assert starts,start_text
    a=starts[-1];b=next(i for i in range(a+1,len(items)) if txt(items[i]).startswith(end_text))
    return a,b

def continuar_tras_mapeo(body):
    """Inicia 7.3 en la misma página cuando queda espacio tras el mapeo."""
    inicio_anterior, fin_anterior = section_range(body, '7.2.1. Mapeo', '7.3. Diseño Físico')
    anterior = [p.find('w:pPr/w:sectPr', NS) for p in list(body)[inicio_anterior:fin_anterior]
                if p.tag == q('p') and p.find('w:pPr/w:sectPr', NS) is not None]
    assert len(anterior) == 1, len(anterior)
    # Word guarda el tipo de inicio en la sección que viene después. El corte
    # al final de 7.2 describe 7.2; se revierte el ajuste anterior si existe.
    previo = anterior[0].find('w:type', NS)
    if previo is not None and previo.get(q('val')) == 'continuous':anterior[0].remove(previo)
    inicio, fin = section_range(body, '7.3. Diseño Físico', '7.4.')
    cortes = [p.find('w:pPr/w:sectPr', NS) for p in list(body)[inicio:fin]
              if p.tag == q('p') and p.find('w:pPr/w:sectPr', NS) is not None]
    assert len(cortes) == 1, len(cortes)
    tipo = cortes[0].find('w:type', NS)
    if tipo is None:
        tipo = E.Element(q('type'))
        cortes[0].insert(0, tipo)
    tipo.set(q('val'), 'continuous')

def continuar_mapeo_actual():
    path, root, body = doc_read()
    continuar_tras_mapeo(body)
    OUT.mkdir(parents=True, exist_ok=True)
    respaldo = OUT / ('respaldo_antes_continuidad_' + uuid.uuid4().hex + '.docx')
    shutil.copy2(path, respaldo)
    replace_zip(path, {'word/document.xml':E.tostring(root, xml_declaration=True,
                                                       encoding='UTF-8', standalone=True)})
    print(f'El apartado 7.3 continúa después del mapeo. Respaldo: {respaldo}')

def replace_range(body,start,end,nodes):
    old=list(body)[start:end]
    # Se conservan los saltos de sección originales: sus propiedades pueden
    # gobernar páginas anteriores al segmento sustituido.
    section_paras=[copy.deepcopy(p) for p in old if p.tag==q('p') and p.find('w:pPr/w:sectPr',NS) is not None]
    for p in old:body.remove(p)
    for i,p in enumerate(nodes+section_paras):body.insert(start+i,p)

def fijar_ancho_tabla(table,widths):
    """Impide que Word expanda la tabla más allá de los márgenes al abrirla."""
    pr=table.find('w:tblPr',NS);grid=table.find('w:tblGrid',NS)
    assert pr is not None and grid is not None
    cols=grid.findall('w:gridCol',NS)
    assert len(cols)==len(widths),(len(cols),len(widths))
    width=pr.find('w:tblW',NS)
    if width is None:width=E.SubElement(pr,q('tblW'))
    width.set(q('w'),str(sum(widths)));width.set(q('type'),'dxa')
    layout=pr.find('w:tblLayout',NS)
    if layout is None:layout=E.SubElement(pr,q('tblLayout'))
    layout.set(q('type'),'fixed')
    for col,value in zip(cols,widths):col.set(q('w'),str(value))
    for row in table.findall('w:tr',NS):
        cells=row.findall('w:tc',NS)
        cursor=0
        for cell in cells:
            cp=cell.find('w:tcPr',NS)
            if cp is None:cp=E.SubElement(cell,q('tcPr'))
            span=cp.find('w:gridSpan',NS)
            n=int(span.get(q('val'))) if span is not None else 1
            value=sum(widths[cursor:cursor+n]);cursor+=n
            cw=cp.find('w:tcW',NS)
            if cw is None:cw=E.SubElement(cp,q('tcW'))
            cw.set(q('w'),str(value));cw.set(q('type'),'dxa')
        assert cursor==len(widths),(cursor,len(widths))

def ajustar_tablas_datos(body):
    """Acomoda solo el mapeo y el físico; conserva sus textos y el resto del DOCX."""
    items=list(body)
    i72=next(i for i,x in enumerate(items) if txt(x).startswith('7.2.1. Mapeo') and i>len(items)//4)
    i73=next(i for i in range(i72+1,len(items)) if txt(items[i]).startswith('7.3. Diseño Físico'))
    i74=next(i for i in range(i73+1,len(items)) if txt(items[i]).startswith('7.4.'))
    mapping=[x for x in items[i72:i73] if x.tag==q('tbl')]
    physical=[x for x in items[i73:i74] if x.tag==q('tbl')]
    assert len(mapping)>=len(TABLAS) and len(physical)==len(TABLAS)+len(TRIGGERS),(len(mapping),len(physical))
    for table in mapping:
        grid=table.find('w:tblGrid',NS)
        anchos=[int(col.get(q('w'))) for col in grid.findall('w:gridCol',NS)]
        if len(anchos)==5 and len(mapping)==len(TABLAS):anchos=[2600,2700,1000,1500,2900]
        assert sum(anchos)<=ANCHO_MAXIMO_MAPEO
        fijar_ancho_tabla(table,anchos)
    for table in physical:
        columns=len(table.find('w:tblGrid',NS))
        if columns==4:fijar_ancho_tabla(table,[2100,2200,3100,3300])
        elif columns==6:fijar_ancho_tabla(table,ANCHO_DICCIONARIO)
        elif columns==2:fijar_ancho_tabla(table,[2500,8200])
        else:raise RuntimeError(f'Tabla física con {columns} columnas inesperadas')
    breaks=[x.find('.//w:sectPr',NS) for x in items[i73:i74]]
    breaks=[x for x in breaks if x is not None]
    assert len(breaks)==1,'No se encontró el salto de sección entre 7.3 y 7.4'
    margins=breaks[0].find('w:pgMar',NS)
    assert margins is not None
    margins.set(q('left'),'567');margins.set(q('right'),'567')
    return len(mapping),len(physical)

def ajustar_margenes_actual():
    path,root,body=doc_read()
    counts=ajustar_tablas_datos(body)
    backup=Path(tempfile.gettempdir())/f'p2-antes-margenes-{uuid.uuid4().hex}.docx'
    shutil.copy2(path,backup)
    replace_zip(path,{'word/document.xml':E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)})
    print(f'Anchos y márgenes corregidos: {counts[0]} tablas de mapeo y {counts[1]} del físico. Respaldo: {backup}')

def phase1_word():
    path,root,body=doc_read();guard=protected(body)
    data=json.loads((OUT/'postgres_actual.json').read_text(encoding='utf-8'));types={(x['tabla'],x['columna']):x['tipo'] for x in data['tipos'] if x['esquema']=='public'}
    fks=foreign_keys(data);columns={table:[x for x in data['columnas'] if x['table_schema']=='public' and x['table_name']==table] for table in TABLAS}
    mapping=[heading('7.2. Diseño Lógico',2),heading('7.2.1. Mapeo',3)]
    dictionary=[heading('7.3.1. Diccionario de datos y finalidad de las columnas',3)]
    for table,cols in columns.items():
        mrows=[];drows=[]
        for c in cols:
            name=c['column_name']; related=[];marks=[];restr=[]
            for k in data['restricciones']:
                if k['esquema']!='public' or k['tabla']!=table:continue
                if k['tipo'] in ('p','u'):
                    names=re.search(r'\(([^)]+)\)',k['definicion'])
                    if names and name in [x.strip() for x in names[1].split(',')]:marks.append('PK' if k['tipo']=='p' else 'UNIQUE');restr.append(k['nombre'])
                elif k['tipo']=='c' and re.search(r'\b'+re.escape(name)+r'\b',k['definicion']):restr.append(k['nombre'])
            for fk in fks:
                if fk['tabla']==table and name in fk['columnas']:
                    related.append(fk['destino']+'('+', '.join(fk['destino_columnas'])+')');marks.append('FK');restr.append(fk['nombre'])
            nullable='NULL' if c['is_nullable']=='YES' else 'NOT NULL';default=c['column_default'] if c['column_default'] is not None else 'Sin DEFAULT'
            mrows.append([name,types[table,name],', '.join(dict.fromkeys(marks)) or '—',nullable,default])
            purpose=descripcion(table,name,'; '.join(related) if related else None)
            drows.append(fila_diccionario(name,types[table,name],purpose,', '.join(dict.fromkeys(marks)),nullable))
        mapping.append(titulo_mapeo(table))
        for bloque in bloques_mapeo(table,[(row[0],row[2]) for row in mrows]):
            mapping.extend([bloque,separador_mapeo()])
        dictionary.append(heading(table,4));dictionary.append(tabla_diccionario(drows))
    physical=[heading('7.3. Diseño Físico',2),paragraph('El esquema SQL documental es un volcado de solo estructura de public, verificado contra la conexión efectiva de Laravel en PostgreSQL 17.4. No incluye datos comerciales, propietarios ni credenciales. El archivo conserva su protección original para impedir aplicarlo sobre un esquema existente; no se ejecutó durante esta actualización.')]
    sql=(DOC/'fuentes/esquema.sql').read_text(encoding='utf-8')
    for table,definition in re.findall(r'CREATE TABLE public\.(\w+) \((.*?)^\);',sql,re.M|re.S):
        physical.append(heading(table,4))
        physical.extend(paragraph(line) for line in ('CREATE TABLE public.'+table+' ('+definition+');').splitlines())
    physical+=dictionary
    physical.append(heading('7.3.2. Claves, restricciones y cardinalidades verificadas',3))
    physical.append(paragraph('Se conservan 31 PK, 46 FK, siete UNIQUE y 28 CHECK en public. La PK de laravel.migrations se documenta por separado como estructura interna de Laravel. Una FK no exige que exista un hijo para cada padre: el extremo de hijos inicia en cero; la nulabilidad y unicidad determinan el otro extremo. Las dos relaciones muchos a muchos existentes conservan sus tablas intermedias y asociaciones del modelo conceptual.'))
    for k in data['restricciones']:
        physical.append(paragraph(f"{k['esquema']}.{k['tabla']} — {k['nombre']}: {k['definicion']}"))
    physical.append(paragraph('cuotas_token_pago_unique garantiza que un token no nulo identifique una sola cuota. transacciones_stripe_token_publico_unique garantiza que un token público no nulo no se repita entre sesiones. Ambas columnas admiten NULL; PostgreSQL permite múltiples NULL con estas restricciones UNIQUE. Estos tokens se conservan para seguridad de enlaces e idempotencia del flujo público.'))
    physical.append(heading('7.3.3. Índices reales',3))
    for index in data['indices']:
        physical.append(paragraph(index['indexname']+' — '+index['indexdef']))
    physical.append(heading('7.3.4. Triggers y funciones reales',3))
    for trigger in data['triggers']:
        table,event,function,operation,affected,rule=TRIGGERS[trigger['nombre']]
        physical.append(heading(trigger['nombre'],4))
        physical.append(data_table(['Propiedad','Definición comprobada'],[['Tabla',table],['Evento y momento',event+'; FOR EACH ROW'],['Función',function],['Operaciones y condiciones',operation],['Tablas afectadas',affected],['Regla y resultado',rule],['Definición del trigger',trigger['definicion']]],[2500,8200]))
        definition=next(f['definicion'] for f in data['funciones'] if f['nombre']==function).replace('\r','')
        physical.extend(paragraph(line) for line in definition.splitlines() if line.strip())
    a,b=section_range(body,'7.2. Diseño Lógico','7.3. Diseño Físico');replace_range(body,a,b,mapping)
    a,b=section_range(body,'7.3. Diseño Físico','7.4.');replace_range(body,a,b,physical)
    continuar_tras_mapeo(body)
    assert protected(body)==guard,'El capítulo IV cambió'
    ajustar_tablas_datos(body)
    replace_zip(path,{'word/document.xml':E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)})
    dump={'tablas':len(columns),'columnas':sum(map(len,columns.values())),'restricciones':len(data['restricciones']),'triggers':len(data['triggers']),'capitulo_IV_intacto':True}
    (OUT/'fase1_word.json').write_text(json.dumps(dump,indent=2),encoding='utf-8');print(dump)
if __name__=='__main__':
    if sys.argv[1]=='cu':phase2()
    elif sys.argv[1]=='bd':phase1_word()
    elif sys.argv[1]=='arquitectura':phase7()
    elif sys.argv[1]=='margenes':ajustar_margenes_actual()
    elif sys.argv[1]=='diccionario':actualizar_diccionario_actual()
    elif sys.argv[1]=='mapeo':actualizar_mapeo_actual()
    elif sys.argv[1]=='continuidad-mapeo':continuar_mapeo_actual()
    else:raise ValueError(sys.argv[1])
