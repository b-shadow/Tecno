import sys,json,re,hashlib,collections,textwrap,math,csv
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent.parent;O=R/'auditoria_documental';E=O/'evidencias'
def l(n):return json.loads((E/n).read_text(encoding='utf-8-sig'))
def s(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf8')
# Inventario React/JS independiente, incluidas páginas y componentes no presentes en las figuras.
react=[]
for p in sorted((R/'presentacion/src').rglob('*')):
 if p.suffix not in ['.jsx','.js']:continue
 text=p.read_text(encoding='utf8');definitions=[]
 for m in re.finditer(r'(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)\s*\((.*?)\)',text,re.S):
  definitions.append({'nombre':m.group(1),'parametros':re.sub(r'\s+',' ',m.group(2)),'linea':text[:m.start()].count('\n')+1})
 exports=re.findall(r'export\s+const\s+(\w+)',text)
 react.append({'archivo':p.relative_to(R).as_posix(),'tipo':'Página' if p.parent.name=='paginas' else 'Módulo API' if p.parent.name=='api' else 'Componente/servicio','funciones':definitions,'constantes_exportadas':exports,'imports':re.findall(r"from\s+['\"]([^'\"]+)['\"]",text)})
s('componentes_react.json',react)
# Historial del catálogo sin repetir consultas que podrían tocar información comercial.
import subprocess
githead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
gitstatus=subprocess.check_output(['git','status','--porcelain=v1'],cwd=R,text=True)
(E/'git_final.txt').write_text('HEAD '+githead+'\n'+gitstatus,encoding='utf8')
assert githead==l('git_inicial.json')['head']
assert all('auditoria_documental' in line for line in gitstatus.splitlines() if line.strip()),gitstatus
# Inventario comparado de PK/FK impresas, no solo nombres de columnas.
schema=l('esquema_documental.json');compare=[]
for t in l('tablas_docx.json')[12:]:
 name=t['filas'][0][0];cols=[re.sub(r'\s+','',v) for v in t['filas'][-1]];marks=t['filas'][1]
 pk=[c for c,m in zip(cols,marks) if 'pk' in m.lower()];fk=[c for c,m in zip(cols,marks) if 'fk' in m.lower()];expfk=sorted(set(c for a,cs,b,bs in schema['fks'] if a==name for c in cs))
 compare.append({'tabla':name,'pk_impresa':pk,'pk_volcado':schema['pks'][name],'fk_impresas':fk,'fk_volcado':expfk,'pk_coincide':set(pk)==set(schema['pks'][name]),'fk_coincide':set(fk)==set(expfk)})
s('verificacion_claves_impresas.json',compare)
# Índices/secuencias/triggers cotejados contra DDL de origen. Se preservan faltantes, no se generan originales.
sql=(R/'generadorDocumento/fuentes/esquema.sql').read_text(encoding='utf8')
tr=[]
normal=lambda x:re.sub(r'\s+','',x.replace('public.','')).lower()
for t in l('pg_triggers.json'):
 m=re.search(r'CREATE TRIGGER '+re.escape(t['nombre'])+r'\b.*?;',sql,re.S)
 tr.append({'nombre':t['nombre'],'definicion_real':t['definicion'],'definicion_documental':m.group(0).rstrip(';') if m else None,'estado':'COINCIDE NORMALIZADA' if m and normal(m.group(0).rstrip(';')).replace('(','').replace(')','')==normal(t['definicion']).replace('(','').replace(')','') else 'PRESENTE; NOTACIÓN SQL REQUIERE REVISIÓN' if m else 'AUSENTE'})
s('comparacion_triggers.json',tr)
seqdocs=set(re.findall(r'CREATE SEQUENCE public\.(\w+)',sql));seqreal={x['sequencename'] for x in l('pg_secuencias.json')};s('comparacion_secuencias.json',{'documentales':sorted(seqdocs),'reales':sorted(seqreal),'faltantes':sorted(seqreal-seqdocs),'sobrantes':sorted(seqdocs-seqreal)})
indexes=[]
for i in l('pg_indices.json'):
 if i['schemaname']!='public':continue
 m=re.search(r'CREATE (?:UNIQUE )?INDEX '+re.escape(i['indexname'])+r'\b.*?;',sql,re.S)
 constraint=next((c for c in l('comparacion_restricciones.json') if c['nombre']==i['indexname']),None)
 status='COINCIDE POR CONSTRAINT' if constraint and constraint['estado'].startswith('COINCIDE') else 'FALTA EN VOLCADO' if not m else 'COINCIDE DEFINICIÓN' if normal(m.group(0).rstrip(';'))==normal(i['indexdef']) else 'REVISAR NOTACIÓN'
 indexes.append({**i,'estado_documental':status,'definicion_documental':m.group(0) if m else constraint.get('definicion_documental') if constraint else None})
s('comparacion_indices.json',indexes)
# Inventarios CSV equivalentes para filtros fuera de Excel y reproducibilidad.
for src in ['hallazgos.json','comparacion_columnas.json','cardinalidades.json','diagramas_auditados.json','trazabilidad_integral.json','documentacion_inventario.json']:
 rows=l(src);headers=list(dict.fromkeys(k for x in rows for k in x));p=E/(Path(src).stem+'.csv')
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=headers);w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False,default=str) if isinstance(v,(list,dict)) else v for k,v in r.items()})
# QA estructural y revisión visual reproducible de la primera zona de cada hoja.
from openpyxl import load_workbook
from PIL import Image,ImageDraw,ImageFont
fontpath=Path('C:/Windows/Fonts/arial.ttf');font=ImageFont.truetype(str(fontpath),15);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',15)
qa={};previews=[]
for fn in ['08_MATRIZ_TRAZABILIDAD.xlsx','09_HALLAZGOS_PRIORIZADOS.xlsx']:
 w=load_workbook(O/fn);infos=[]
 for sh in w:
  assert sh.freeze_panes=='A2' and sh.auto_filter.ref
  assert sh.max_row>=2
  assert all(c.font.name=='Arial' for row in sh for c in row)
  errors=[c.coordinate for row in sh for c in row if c.data_type=='e'];assert not errors
  # Vista de seis columnas. El contenido adicional sigue en el libro, con scroll horizontal.
  widths=[int(min(sh.column_dimensions[sh.cell(1,c).column_letter].width*7,420)) for c in range(1,min(sh.max_column,6)+1)];heights=[58]+[min(210,int(sh.row_dimensions[r].height*1.33)) for r in range(2,min(6,sh.max_row)+1)];canvas=Image.new('RGB',(sum(widths)+1,sum(heights)+40),'white');d=ImageDraw.Draw(canvas);d.text((8,6),fn[:2]+' / '+sh.title,fill='#17365D',font=bold);y=35
  for ir,height in enumerate(heights,1):
   x=0
   for ic,width in enumerate(widths,1):
    val=str(sh.cell(ir,ic).value or '');fill='#17365D' if ir==1 else '#F2F5F9' if ir%2==0 else 'white';d.rectangle((x,y,x+width,y+height),fill=fill,outline='#d0d5dc');limit=max(10,int(width/8));lines=[]
    for line in val.splitlines() or ['']:lines.extend(textwrap.wrap(line,limit,break_long_words=True) or [''])
    maxlines=max(1,(height-10)//18)
    if len(lines)>maxlines:lines=lines[:maxlines];lines[-1]=lines[-1][:-3]+'…'
    d.multiline_text((x+5,y+5),'\n'.join(lines),font=bold if ir==1 else font,fill='white' if ir==1 else '#20252a',spacing=2)
    x+=width
   y+=height
  out=E/(fn[:2]+'_hoja_'+re.sub(r'[^\w]+','_',sh.title)+'.png');canvas.save(out);previews.append(out)
  infos.append({'hoja':sh.title,'filas_datos':sh.max_row-1,'columnas':sh.max_column,'filtro':sh.auto_filter.ref,'freeze':sh.freeze_panes,'errores_excel':errors,'formulas':sum(c.data_type=='f' for row in sh for c in row),'preview':out.name})
 qa[fn]=infos
s('qa_libros.json',qa)
for start in range(0,len(previews),4):
 canvas=Image.new('RGB',(2400,2000),'#ccc');d=ImageDraw.Draw(canvas)
 for j,p in enumerate(previews[start:start+4]):
  im=Image.open(p);im.thumbnail((1180,920));x=(j%2)*1200;y=(j//2)*1000+30;canvas.paste(im,(x,y));d.text((x+5,y-22),p.name,font=bold,fill='black')
 canvas.save(E/f'libros_contacto_{start//4+1:02}.png')
# SQL adicional: cardinalidades derivables sin consultar registros personales.
p=O/'10_CONSULTAS_VERIFICACION.sql';text=p.read_text(encoding='utf8');marker='-- cardinalidades_garantizadas'
if marker not in text:
 q="""
-- cardinalidades_garantizadas: hijo->padre según NULL; padre->hijos según UNIQUE/PK.
-- 0..* no significa que haya hijos: la FK nunca exige una fila hija al padre.
SELECT n.nspname AS esquema,t.relname AS hija,c.conname AS fk,
       pt.relname AS padre, pg_get_constraintdef(c.oid,true) AS definicion,
       CASE WHEN EXISTS (SELECT 1 FROM unnest(c.conkey) k(attnum)
                         JOIN pg_attribute a ON a.attrelid=t.oid AND a.attnum=k.attnum
                         WHERE NOT a.attnotnull) THEN '0..1' ELSE '1' END AS padres_por_hijo,
       CASE WHEN EXISTS (SELECT 1 FROM pg_constraint u WHERE u.conrelid=t.oid
                          AND u.contype IN ('p','u') AND u.conkey <@ c.conkey)
            THEN '0..1' ELSE '0..*' END AS hijos_por_padre
FROM pg_constraint c JOIN pg_class t ON t.oid=c.conrelid
JOIN pg_namespace n ON n.oid=t.relnamespace JOIN pg_class pt ON pt.oid=c.confrelid
WHERE c.contype='f' AND n.nspname='public' ORDER BY hija,fk;
"""
 text=text.replace('\nROLLBACK;',q+'\nROLLBACK;');p.write_text(text,encoding='utf8')
# Preservación de cada archivo inventariado previo: hashes de DOC/DOCX/PDF/EAPX, fuentes y diagramas incluidos.
originals=l('archivos.json');changes=[];missing=[]
for x in originals:
 p=R/x['ruta']
 if not p.exists():missing.append(x['ruta'])
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:changes.append(x['ruta'])
s('integridad_originales.json',{'head_inicial':l('git_inicial.json')['head'],'archivos_comprobados':len(originals),'archivos_modificados':changes,'archivos_ausentes':missing,'credenciales':'No copiadas ni publicadas; .env excluido del inventario de contenido','base_datos':'Las consultas de catálogo se ejecutaron con transaction_read_only=on y ROLLBACK. No se ejecutaron endpoints ni comandos de escritura; no se extrajeron registros comerciales para comparar valores.'})
assert not changes and not missing,(changes,missing)
needed=['00_CONTROL_AVANCE.md','01_INFORME_AUDITORIA_COMPLETA.md','02_INVENTARIO_DOCUMENTACION.md','03_INVENTARIO_DIAGRAMAS.md','04_AUDITORIA_CASOS_USO.md','05_AUDITORIA_CLASES_METODOS.md','06_AUDITORIA_SECUENCIAS.md','07_AUDITORIA_BASE_DATOS.md','08_MATRIZ_TRAZABILIDAD.xlsx','09_HALLAZGOS_PRIORIZADOS.xlsx','10_CONSULTAS_VERIFICACION.sql','11_CHECKLIST_REVISION_MANUAL.md','12_PLAN_CORRECCION_DOCUMENTAL.md','13_RESUMEN_EJECUTIVO.md']
assert all((O/n).is_file() and (O/n).stat().st_size>100 for n in needed)
assert all(x['pk_coincide'] and x['fk_coincide'] for x in compare)
f=l('hallazgos.json');assert len({x['id'] for x in f})==len(f)
assert len(l('comparacion_columnas.json'))==292
assert len(l('casos_uso_auditados.json'))==8
assert len(l('diagramas_auditados.json'))==49
assert len(qa['08_MATRIZ_TRAZABILIDAD.xlsx'])>=16
assert not re.search(r'^\s*(INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE)\b',text,re.M|re.I)
assert len(l('equivalencia_formatos.json')['parrafos_no_coincidentes_pdf_sin_pies'])==0
metrics=l('metricas_finales.json')
assert len(f)==metrics['hallazgos']
assert len(qa['09_HALLAZGOS_PRIORIZADOS.xlsx'])==1 and qa['09_HALLAZGOS_PRIORIZADOS.xlsx'][0]['filas_datos']==len(f)
for fn in ['01_INFORME_AUDITORIA_COMPLETA.md','02_INVENTARIO_DOCUMENTACION.md','03_INVENTARIO_DIAGRAMAS.md','04_AUDITORIA_CASOS_USO.md','05_AUDITORIA_CLASES_METODOS.md','06_AUDITORIA_SECUENCIAS.md','07_AUDITORIA_BASE_DATOS.md','11_CHECKLIST_REVISION_MANUAL.md','12_PLAN_CORRECCION_DOCUMENTAL.md','13_RESUMEN_EJECUTIVO.md']:
 p=O/fn;tx=p.read_text(encoding='utf8')
 # Espacios en prosa, preservando identificadores y rutas.
 for a,b in {'las108':'las 108','las49':'las 49','las31':'las 31','los8':'los 8','Los8':'Los 8','las46':'las 46','Las31':'Las 31','Los34':'Los 34','los34':'los 34','Las10':'Las 10','Los14':'Los 14','las19':'las 19','Los13':'Los 13','a09:00':'a las 09:00','tras24h':'tras 24 h','después de24h':'después de 24 h','en104':'en 104'}.items():tx=tx.replace(a,b)
 p.write_text(tx,encoding='utf8')
# Número de páginas de PDFs de apoyo, sin volver a extraerlos completamente.
import fitz
docs=l('documentacion_inventario.json')
for d in docs:
 if d['formato']=='.pdf':
  with fitz.open(R/d['ruta']) as pdf:d['paginas']=len(pdf)
s('documentacion_inventario.json',docs)
with (O/'02_INVENTARIO_DOCUMENTACION.md').open('a',encoding='utf8') as out:
 out.write('\n## Páginas y alcance de PDFs de referencia\n\n'+'\n'.join('- `'+d['ruta']+'`: '+str(d['paginas'])+' páginas.' for d in docs if d['formato']=='.pdf')+'\n\nEl referente G07 se inventaría como ejemplo ajeno; no constituye el enunciado oficial del grupo.\n')
s('validacion_entrega.json',{'entregables':len(needed),'hallazgos_unicos':len(f),'PK_FK_impresas_comparadas':len(compare),'columnas_comparadas':292,'diagrams_inventariados':49,'casos_uso':8,'originales_sin_cambios':True,'libros_comprobados':2,'limitacion_visual_excel':'Previews de lectura derivadas de openpyxl/PIL, no render nativo Excel. Hoja completa verificable con filtros/scroll; no contiene fórmulas.'})
with (O/'00_CONTROL_AVANCE.md').open('a',encoding='utf8') as out:
 out.write('\n## Cierre de integridad y entrega\n\nLos14 entregables existen y están poblados. Se reabrieron ambos XLSX:19 hojas de trazabilidad y1 de hallazgos, filtros y A2 congelado, sin fórmulas ni errores de celda. Comparadas PK/FK impresas de31 tablas. Ver validacion_entrega.json y qa_libros.json. Las vistas PIL revisan lectura de primeras filas/columnas; no se certifica render nativo Excel.\n\nRecalculados SHA256 de los1028 originales inventariados:0 cambios,0 ausentes. La BD se consultó solo mediante transacciones de lectura; no se dispararon acciones comerciales. Estado Git final se registra por separado en git_final.txt. EtapaK: Revisado con observaciones por las limitaciones declaradas, sin pendientes ocultos.\n')
print(json.dumps({'integridad':{'originales':len(originals),'cambios':changes,'ausentes':missing},'claves_impresas':len(compare),'indices':dict(collections.Counter(x['estado_documental'] for x in indexes)),'triggers':dict(collections.Counter(x['estado'] for x in tr)),'entregables':len(needed)},ensure_ascii=True))
