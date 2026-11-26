import sys,json,re,collections,subprocess,hashlib,difflib
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent.parent;E=R/'auditoria_documental/evidencias'
def l(n):return json.loads((E/n).read_text(encoding='utf-8-sig'))
def s(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf8')
sys.path.insert(0,str(R/'generadorDocumento'));import esquema,codigo,contenido
save=lambda n,x:s(n,x)
save('diferencias_migraciones.json',esquema.diferencias_migraciones())
# Listado de rutas: no invoca sus acciones. Providers inspeccionados antes de ejecutar.
p=subprocess.run(['php','artisan','route:list','--path=api','--json'],cwd=R/'negocio',capture_output=True,text=True,encoding='utf8')
try:s('rutas_laravel.json',json.loads(p.stdout))
except Exception:s('rutas_laravel_error.json',{'exit':p.returncode,'error':p.stderr[:1000]})
history={}
for commit in ['c0c64d1','480a051','5bf47b2']:
 p=subprocess.run(['git','show','--format=fuller','--numstat',commit],cwd=R,capture_output=True,text=True,encoding='utf8',errors='replace');history[commit]=p.stdout
s('historial_git.json',history)
files=l('archivos.json'); tests=[]
for f in files:
 if not f['ruta'].startswith('scripts/') or not re.search(r'(verificar|qa_)',f['ruta']):continue
 p=R/f['ruta'];txt=p.read_text(encoding='utf-8-sig',errors='replace')
 tests.append({'archivo':f['ruta'],'sha256':f['sha256'],'modifica_datos':bool(re.search(r"['\"](?:POST|PATCH|PUT|DELETE)['\"]|\.post\(|\.click\(|\.fill\(",txt)),'casos_detectados':re.findall(r"(?:caso|check|test)\(['\"]([^'\"]+)",txt),'ejecutado_en_auditoria':False})
s('pruebas_inventario.json',tests)
# Firmas PHP contra operaciones EA, incluso parámetros, orden y retorno.
ops=l('comparacion_metodos_ea.json');cg=codigo.clases_php()
for row in ops:
 actual=cg.get(row['clase'],{}).get('metodos',{}).get(row['metodo_documental'])
 if not actual:continue
 raw=actual['params'];exp=[]
 for p in codigo._args(raw+')') if raw else []:
  m=re.search(r'(?:(\??[\\\w|]+)\s+)?\$(\w+)(?:\s*=\s*(.+))?',p)
  if m:exp.append((m.group(1) or '',m.group(2),m.group(3)))
 got=[(x[0],x[1],None if x[2] in ['','<none>'] else x[2]) for x in row['parametros_documentales']]
 row['parametros_reales']=exp
 row['diferencias_firma']=[]
 if [(x[0],x[1]) for x in got]!=[(x[0],x[1]) for x in exp]:row['diferencias_firma'].append('Parámetros o tipos')
 firma=actual['firma'];ret=firma.rsplit('): ',1)[-1] if '): ' in firma else ''
 if (row['retorno_documental'] or '')!=ret:row['diferencias_firma'].append('Retorno')
 vis={'+':'Public','-':'Private','#':'Protected'}.get(actual['vis'])
 if row['visibilidad_documental']!=vis:row['diferencias_firma'].append('Visibilidad')
 row['estado']='DIFERENCIA DE FIRMA' if row['diferencias_firma'] else 'COINCIDE FIRMA (defaults no certificados)'
s('comparacion_metodos_ea.json',ops)
# Catálogo único de FK con cardinalidad y correspondencia conceptual. Los mínimos del padre no se infieren de los datos.
cons=l('pg_restricciones.json');cc=l('pg_columnas.json');concep=[x for x in l('relaciones_ea.json') if x['diagrama']==133];cards=[]
for fk in l('pg_fk_columnas.json'):
 if fk['esquema']!='public':continue
 cols=fk['columnas'];table=fk['tabla'];p=fk['destino']
 unique=False
 for c in cons:
  if c['esquema']!='public' or c['tabla']!=table or c['tipo'] not in ['u','p']:continue
  m=re.search(r'\(([^)]+)\)',c['definicion'])
  if m and set(x.strip().strip('"') for x in m.group(1).split(','))<=set(cols):unique=True
 nullable=any(c['is_nullable']=='YES' for c in cc if c['table_schema']=='public' and c['table_name']==table and c['column_name'] in cols)
 expectedchild='0..1' if unique else '0..*';expectedparent='0..1' if nullable else '1'
 matches=[c for c in concep if c['tipo']=='Association' and c['origen']==table and c['destino']==p]
 status='COINCIDE' if any(c['multiplicidad_origen']==expectedchild and c['multiplicidad_destino']==expectedparent for c in matches) else 'DIFERENTE O ABSTRACCIÓN N:N'
 fk.update({'hijos_por_padre':expectedchild,'padres_por_hijo':expectedparent,'nullable':nullable,'fk_unica':unique,'conectores_ea':[c['conector'] for c in matches],'estado':status,'on_delete_texto':{'a':'NO ACTION','r':'RESTRICT','c':'CASCADE','n':'SET NULL','d':'SET DEFAULT'}.get(fk['on_delete']),'on_update_texto':{'a':'NO ACTION','r':'RESTRICT','c':'CASCADE','n':'SET NULL','d':'SET DEFAULT'}.get(fk['on_update'])});cards.append(fk)
s('cardinalidades.json',cards)
# Restricciones del volcado: tipos y nombres, definiciones completas preservadas.
sql=(R/'generadorDocumento/fuentes/esquema.sql').read_text(encoding='utf8')
dc=[]
for m in re.finditer(r'ALTER TABLE ONLY public\.(\w+)\s+ADD CONSTRAINT (\w+) (.*?);',sql,re.S):dc.append({'tabla':m.group(1),'nombre':m.group(2),'definicion':re.sub(r'\s+',' ',m.group(3))})
for m in re.finditer(r'CREATE TABLE public\.(\w+) \((.*?)\n\);',sql,re.S):
 for a in re.finditer(r'CONSTRAINT (\w+) (CHECK .*?)(?=,?\n|$)',m.group(2)):dc.append({'tabla':m.group(1),'nombre':a.group(1),'definicion':a.group(2).rstrip(',')})
s('restricciones_documentales.json',dc)
index={(c['tabla'],c['nombre']):c for c in dc};result=[]
for c in cons:
 if c['esquema']!='public':continue
 d=index.get((c['tabla'],c['nombre']));result.append({**c,'definicion_documental':d['definicion'] if d else None,'estado':'NOMBRE PRESENTE; definición a comparar' if d else 'NO DOCUMENTADA EN VOLCADO'})
s('comparacion_restricciones.json',result)
# Equivalencia textual de entregables. PDF contiene texto vectorial adicional de diagramas.
a=(E/'word_doc.txt').read_text(encoding='utf-8-sig');b=(E/'word_docx.txt').read_text(encoding='utf-8-sig');pdf=' '.join(p['texto'] for p in l('paginas_pdf.json'))
paragraphs=l('parrafos_docx.json');normal=lambda t:re.sub(r'\s+','',t).casefold();np=normal(pdf)
missing=[{'indice':p['indice'],'texto':p['texto']} for p in paragraphs if p['indice']>=124 and len(p['texto'])>30 and normal(p['texto']) not in np]
s('equivalencia_formatos.json',{'doc_docx_texto_identico':a==b,'paginas_doc':l('word_doc_info.json')['paginas'],'paginas_docx':l('word_docx_info.json')['paginas'],'paginas_pdf':len(l('paginas_pdf.json')),'parrafos_no_coincidentes_pdf':missing,'criterio':'Comparación sin espacios. DDL partido y glifos pueden impedir coincidencia literal; no equivale por sí mismo a diferencia semántica.'})
print('Rutas Laravel:',len(l('rutas_laravel.json')) if (E/'rutas_laravel.json').exists() else 'falló');print('Diferencias firmas:',collections.Counter(';'.join(x.get('diferencias_firma',[])) for x in ops));print('Cardinalidades:',collections.Counter(x['estado'] for x in cards));print('Constraints:',collections.Counter(x['estado'] for x in result));print('Parrafos PDF sin coincidencia literal:',len(missing))
