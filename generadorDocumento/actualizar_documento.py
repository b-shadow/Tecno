"""Ediciones puntuales sobre el DOCX maestro; nunca regenera capítulos no autorizados."""
from pathlib import Path
import copy,json,re,sys,zipfile,hashlib
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

def section_range(body,start_text,end_text):
    items=list(body);starts=[i for i,p in enumerate(items) if txt(p).startswith(start_text)]
    assert starts,start_text
    a=starts[-1];b=next(i for i in range(a+1,len(items)) if txt(items[i]).startswith(end_text))
    return a,b

def replace_range(body,start,end,nodes):
    old=list(body)[start:end]
    # Se conservan los saltos de sección originales: sus propiedades pueden
    # gobernar páginas anteriores al segmento sustituido.
    section_paras=[copy.deepcopy(p) for p in old if p.tag==q('p') and p.find('w:pPr/w:sectPr',NS) is not None]
    for p in old:body.remove(p)
    for i,p in enumerate(nodes+section_paras):body.insert(start+i,p)

def phase1_word():
    path,root,body=doc_read();guard=protected(body)
    data=json.loads((OUT/'postgres_actual.json').read_text(encoding='utf-8'));types={(x['tabla'],x['columna']):x['tipo'] for x in data['tipos'] if x['esquema']=='public'}
    fks=foreign_keys(data);columns={table:[x for x in data['columnas'] if x['table_schema']=='public' and x['table_name']==table] for table in TABLAS}
    mapping=[heading('7.2. Diseño Lógico',2),heading('7.2.1. Mapeo',3),paragraph('Se representan las 31 tablas del dominio y sus 287 columnas verificadas en PostgreSQL local. La tabla auxiliar laravel.migrations contiene tres columnas y se diferencia del dominio comercial. Las claves compuestas, nulabilidad y valores predeterminados se conservan; las relaciones no se rediseñan.')]
    dictionary=[heading('7.3.1. Diccionario de datos y finalidad de las columnas',3)]
    for table,cols in columns.items():
        mapping.append(heading(table,4));mapping.append(paragraph(TABLAS[table]))
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
            drows.append([name,types[table,name],purpose,nullable+'; '+default+('; '+', '.join(restr) if restr else '')+('; referencia '+ '; '.join(related) if related else '')])
        mapping.append(data_table(['Columna','Tipo exacto','Clave','Nulabilidad','Predeterminado'],mrows,[2600,2700,1000,1500,2900]))
        dictionary.append(heading(table,4));dictionary.append(data_table(['Columna','Tipo','Descripción y finalidad en UNEXO','Restricciones / relación'],drows,[2200,2500,3600,2400]))
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
    assert protected(body)==guard,'El capítulo IV cambió'
    replace_zip(path,{'word/document.xml':E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)})
    dump={'tablas':len(columns),'columnas':sum(map(len,columns.values())),'restricciones':len(data['restricciones']),'triggers':len(data['triggers']),'capitulo_IV_intacto':True}
    (OUT/'fase1_word.json').write_text(json.dumps(dump,indent=2),encoding='utf-8');print(dump)
if __name__=='__main__':
    if sys.argv[1]=='cu':phase2()
    elif sys.argv[1]=='bd':phase1_word()
    elif sys.argv[1]=='arquitectura':phase7()
    else:raise ValueError(sys.argv[1])
