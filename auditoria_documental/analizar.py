import sys,json,re,collections,subprocess,hashlib,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent.parent;O=R/'auditoria_documental';E=O/'evidencias'
def load(n):return json.loads((E/n).read_text(encoding='utf-8-sig'))
def save(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf8')
sys.path.insert(0,str(R/'generadorDocumento'));import esquema,codigo,contenido
pg=load('pg_columnas.json');tab=esquema.tablas(); cp={(c['table_name'],c['column_name']):c for c in pg if c['table_schema']=='public'}
exact={(c['tabla'],c['columna']):c['tipo'] for c in load('pg_tipos_exactos.json') if c['esquema']=='public'}
def normtype(x):
 return x.replace('character varying','varchar').replace('timestamp without time zone','timestamp').replace('numeric','decimal').replace('boolean','bool').replace('integer','int4').replace('bigint','int8').replace('smallint','int2')
def pgtype(c):
 if (c['table_name'],c['column_name']) in exact:return exact[c['table_name'],c['column_name']]
 t=c['data_type']
 if t=='character varying' and c['character_maximum_length']: t+='('+str(c['character_maximum_length'])+')'
 if t=='numeric':t+=f'({c["numeric_precision"]},{c["numeric_scale"]})'
 return t
rows=[]
for t in sorted(set(tab)|{t for t,c in cp}):
 dc={c[0]:c for c in tab.get(t,[])}
 for c in sorted(set(dc)|{c for tt,c in cp if tt==t}):
  d=dc.get(c);p=cp.get((t,c));diff=[]
  if not d:diff.append('Falta en volcado documental')
  elif not p:diff.append('No existe en PostgreSQL')
  else:
   if normtype(d[1])!=normtype(pgtype(p)):diff.append('Tipo')
   if d[2]!=(p['is_nullable']=='NO'):diff.append('Nulabilidad')
   if re.sub(r'\s+',' ',d[3] or '')!=re.sub(r'\s+',' ',p['column_default'] or ''):diff.append('Default (comparación literal)')
  rows.append({'tabla':t,'columna':c,'tipo_documental':d[1] if d else None,'tipo_real':pgtype(p) if p else None,'nullable_documental':not d[2] if d else None,'nullable_real':p['is_nullable'] if p else None,'default_documental':d[3] if d else None,'default_real':p['column_default'] if p else None,'diferencias':'; '.join(diff),'estado':'DIFERENTE' if diff else 'COINCIDE'})
save('comparacion_columnas.json',rows)
paras=load('parrafos_docx.json');pages=load('paginas_pdf.json');tables=load('tablas_docx.json')
def compact(s):return re.sub(r'\s+','',s).lower()
maprows=[]
for table in tables[12:]:
 fs=table['filas'];t=fs[0][0];cols=[compact(x) for x in fs[-1]]
 expected=[c[0] for c in tab.get(t,[])];maprows.append({'tabla':t,'indice_tabla_docx':table['indice'],'columnas_documento':cols,'faltan':sorted(set(expected)-set(cols)),'sobran':sorted(set(cols)-set(expected)),'pk_fk_documento':fs[1]})
save('comparacion_mapeo_docx.json',maprows)
heads=[p.copy() for p in paras if p['estilo'].startswith('Heading')]
for i,h in enumerate(heads):
 a=h['indice'];b=heads[i+1]['indice'] if i+1<len(heads) else 99999
 h['contenido']=[p['texto'] for p in paras if a<p['indice']<b]
 h['paginas_pdf']=[p['pagina_pdf'] for p in pages if compact(h['texto']) in compact(p['texto']) and p['pagina_pdf']>=7]
save('secciones_reales.json',heads)
objects={x['Object_ID']:x for x in load('ea_t_object.json')};diags=load('ea_t_diagram.json');dos=load('ea_t_diagramobjects.json');links=load('ea_t_diagramlinks.json');conns=load('ea_t_connector.json');ops=load('ea_t_operation.json');params=load('ea_t_operationparams.json');attrs=load('ea_t_attribute.json')
actual={x['clase']:x for x in load('clases.json')};gcl=codigo.clases_php()
compar=[];opcomp=[];attrcomp=[]
for d in diags:
 ids={x['Object_ID'] for x in dos if x['Diagram_ID']==d['Diagram_ID']}
 for oid in ids:
  ob=objects.get(oid,{});name=ob.get('Name','');st=ob.get('Stereotype','');found=actual.get(name)
  if st in ['negocio','datos','model']:
   compar.append({'diagrama':d['Diagram_ID'],'objeto':oid,'clase_documentada':name,'estereotipo':st,'archivo':found['archivo'] if found else None,'estado':'EXISTE' if found else 'NO LOCALIZADA'})
   for op in [x for x in ops if x['Object_ID']==oid]:
    met=next((m for m in found['metodos'] if m['metodo']==op['Name']),None) if found else None
    ps=sorted([x for x in params if x['OperationID']==op['OperationID']],key=lambda x:x['Pos'])
    opcomp.append({'diagrama':d['Diagram_ID'],'clase':name,'metodo_documental':op['Name'],'parametros_documentales':[(p.get('Type',''),p.get('Name',''),p.get('Default','')) for p in ps],'retorno_documental':op.get('Type'),'visibilidad_documental':op.get('Scope'),'firma_real':met,'estado':'MÉTODO EXISTE; firma por contrastar' if met else 'NO LOCALIZADO'})
   for at in [x for x in attrs if x['Object_ID']==oid]:
    attrcomp.append({'diagrama':d['Diagram_ID'],'clase':name,'atributo':at.get('Name'),'tipo':at.get('Type'),'visibilidad':at.get('Scope'),'estado':'Abstracción de columna' if st=='model' else 'Contrastar con propiedad PHP','archivo':found['archivo'] if found else None})
save('comparacion_clases_ea.json',compar);save('comparacion_metodos_ea.json',opcomp);save('comparacion_atributos_ea.json',attrcomp)
msgs=[];relations=[]
for d in diags:
 ids={x['Object_ID'] for x in dos if x['Diagram_ID']==d['Diagram_ID']};lids={x['ConnectorID'] for x in links if x['DiagramID']==d['Diagram_ID']}
 for c in conns:
  if not (c.get('DiagramID')==d['Diagram_ID'] or c['Connector_ID'] in lids or (c.get('DiagramID',0)==0 and c['Start_Object_ID'] in ids and c['End_Object_ID'] in ids)):continue
  source=objects.get(c['Start_Object_ID'],{}).get('Name','');target=objects.get(c['End_Object_ID'],{}).get('Name','');message=c.get('Name','')
  row={'diagrama':d['Diagram_ID'],'nombre_diagrama':d['Name'],'conector':c['Connector_ID'],'tipo':c['Connector_Type'],'orden':c.get('SeqNo'),'origen':source,'destino':target,'mensaje':message,'multiplicidad_origen':c.get('SourceCard'),'multiplicidad_destino':c.get('DestCard'),'direccion':c.get('Direction')}
  if c['Connector_Type'] in ['Sequence','Collaboration']:
   m=re.search(r'\b([ND]\w+)::(\w+)\(',message)
   if m:
    clas,met=m.groups();found=next((x for x in actual.get(clas,{}).get('metodos',[]) if x['metodo']==met),None)
    row['metodo_real']=found;row['estado']='EXISTE; orden y flujo requieren revisión semántica' if found else 'NO LOCALIZADO'
   else:row['estado']='Mensaje de interfaz, HTTP, retorno o infraestructura'
   msgs.append(row)
  else:relations.append(row)
save('mensajes_ea.json',msgs);save('relaciones_ea.json',relations)
concept=next(x for x in diags if x['Diagram_ID']==133);ids={x['Object_ID'] for x in dos if x['Diagram_ID']==133}
conceptrows=[]
for oid in ids:
 ob=objects[oid];t=ob.get('Name','');aa=[a for a in attrs if a['Object_ID']==oid];names=[re.sub(r'\s+PK$','',a['Name']) for a in aa]
 if t in tab:conceptrows.append({'objeto':oid,'tabla':t,'columnas_ea':names,'faltantes':sorted(set(c[0] for c in tab[t])-set(names)),'extras':sorted(set(names)-set(c[0] for c in tab[t]))})
save('comparacion_conceptual_ea.json',conceptrows)
from PIL import Image,ImageOps,ImageDraw
pngs=sorted((R/'generadorDocumento/diagramas').glob('*.png'))
for k in range(0,len(pngs),4):
 canvas=Image.new('RGB',(2800,2000),'#ddd');draw=ImageDraw.Draw(canvas)
 for j,p in enumerate(pngs[k:k+4]):
  im=Image.open(p).convert('RGB');im.thumbnail((1380,930));x=(j%2)*1400+(1400-im.width)//2;y=(j//2)*1000+50;canvas.paste(im,(x,y));draw.text(((j%2)*1400+20,(j//2)*1000+10),p.name,fill='black',font_size=26)
 canvas.save(E/f'contacto_{k//4+1:02}.png')
import fitz
pdf=fitz.open(R/'generadorDocumento/documento/P2-INF513-GRUPO05SA.pdf')
for num in [1,22,24,25,30,39,40,45,48,49,50,51,65,66,67,68,73,74,75,76,86,95,96,97,100,104,105,108]:
 pdf[num-1].get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(E/f'pagina_{num:03}.png')
# VML et DrawingML: tous les formats, sans supposer wp:docPr.
z=zipfile.ZipFile(R/'generadorDocumento/documento/P2-INF513-GRUPO05SA.docx');root=ET.fromstring(z.read('word/document.xml'))
save('imagenes_docx_vml.json',[dict(x.attrib) for x in root.iter() if x.tag.endswith('}shape') or x.tag.endswith('}imagedata') or x.tag.endswith('}docPr')])
summary={'diferencias_columnas':collections.Counter(r['diferencias'] for r in rows),'mapeos_con_diferencias':[r for r in maprows if r['faltan'] or r['sobran']],'conceptual_diferencias':[r for r in conceptrows if r['faltantes'] or r['extras']],'clases_no_localizadas':[r for r in compar if r['estado']=='NO LOCALIZADA'],'metodos_no_localizados':[r for r in opcomp if r['estado']=='NO LOCALIZADO'],'mensajes_no_localizados':[r for r in msgs if r['estado']=='NO LOCALIZADO'],'tipos_diagramas':collections.Counter(d['Diagram_Type'] for d in diags)}
save('resumen_comparaciones.json',summary)
print(json.dumps(summary,ensure_ascii=True)[:9000])
