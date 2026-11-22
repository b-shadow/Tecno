"""Auditoría independiente. No importa Laravel ni ejecuta generadores."""
import os,sys,json,re,hashlib,subprocess,zipfile,datetime,collections,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'auditoria_documental'; E=OUT/'evidencias'
sys.dont_write_bytecode=True
def save(name,obj):
 (E/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str),encoding='utf8')
def read(p): return p.read_text(encoding='utf-8-sig',errors='replace')
def rel(p): return p.relative_to(ROOT).as_posix()
EX={'node_modules','vendor','.git','auditoria_documental','dist','build','__pycache__','.cache'}
files=[]
for base,ds,fs in os.walk(ROOT):
 ds[:]=[d for d in ds if d not in EX]
 for n in fs: files.append(Path(base)/n)
inv=[]
for p in files:
 if p.name.startswith('.env') or p.suffix.lower() in {'.log'}: continue
 s=p.stat(); inv.append(dict(ruta=rel(p),formato=p.suffix.lower(),bytes=s.st_size,fecha=datetime.datetime.fromtimestamp(s.st_mtime).isoformat(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
save('archivos.json',inv)
save('git_inicial.json',{'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'status':subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT,text=True)})
import fitz
pdf=fitz.open(ROOT/'generadorDocumento/documento/P2-INF513-GRUPO05SA.pdf')
pages=[{'pagina_pdf':i+1,'texto':p.get_text(),'ancho':p.rect.width,'alto':p.rect.height} for i,p in enumerate(pdf)]
save('paginas_pdf.json',pages)
(E/'pdf_texto.txt').write_text('\n\n'.join(f'=== PDF {p["pagina_pdf"]} ===\n{p["texto"]}' for p in pages),encoding='utf8')
from docx import Document
d=Document(ROOT/'generadorDocumento/documento/P2-INF513-GRUPO05SA.docx')
paras=[{'indice':i,'estilo':p.style.name,'texto':p.text} for i,p in enumerate(d.paragraphs) if p.text.strip()]
tables=[{'indice':i,'filas':[[c.text for c in r.cells] for r in t.rows]} for i,t in enumerate(d.tables)]
save('parrafos_docx.json',paras); save('tablas_docx.json',tables)
heads=[p for p in paras if 'heading' in p['estilo'].lower() or re.match(r'^\d+(?:\.\d+)*\.?\s',p['texto'])]
for h in heads:
 needle=re.sub(r'\s+',' ',h['texto']).strip()
 h['paginas_pdf']=[p['pagina_pdf'] for p in pages if needle in re.sub(r'\s+',' ',p['texto'])]
save('estructura.json',heads)
z=zipfile.ZipFile(ROOT/'generadorDocumento/documento/P2-INF513-GRUPO05SA.docx')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
x=ET.fromstring(z.read('word/document.xml'))
save('imagenes_docx.json',[dict(n.attrib) for n in x.findall('.//wp:docPr',ns)])
classes=[]; methods=[]
for p in files:
 if p.suffix!='.php' or not any(rel(p).startswith(k) for k in ['negocio/app/','datos/src/']): continue
 t=read(p); cm=re.search(r'\b(?:abstract\s+|final\s+)?class\s+(\w+)(?:\s+extends\s+([\\\w]+))?',t)
 if not cm: continue
 name,parent=cm.groups(); layer='D' if rel(p).startswith('datos/') else 'N'
 attrs=[{'nombre':m.group(1),'linea':t[:m.start()].count('\n')+1} for m in re.finditer(r'(?:public|protected|private)\s+(?:static\s+)?(?:\??[\\\w|]+\s+)?\$(\w+)',t)]
 ms=[]
 for m in re.finditer(r'(public|protected|private)?\s*(static\s+)?function\s+(\w+)\s*\((.*?)\)\s*(?::\s*([^\s{]+))?',t,re.S):
  row=dict(clase=name,metodo=m.group(3),parametros=re.sub(r'\s+',' ',m.group(4)),retorno=m.group(5),visibilidad=m.group(1) or 'public',archivo=rel(p),linea=t[:m.start()].count('\n')+1,capa=layer); methods.append(row); ms.append(row)
 classes.append(dict(clase=name,padre=parent,archivo=rel(p),capa=layer,atributos=attrs,metodos=ms,imports=re.findall(r'^use ([^;]+);',t,re.M)))
save('clases.json',classes);save('metodos.json',methods)
sys.path.insert(0,str(ROOT/'generadorDocumento'))
import codigo,contenido,esquema
save('rutas_estaticas.json',codigo.rutas_api());save('funciones_api.json',codigo.funciones_api());save('clases_generador.json',codigo.clases_php())
save('chequeo_generador.json',{'errores':codigo.errores_codigo(),'sin_pantalla':codigo.rutas_sin_pantalla()})
for name in ['ACTORES','CASOS_USO','CU','REQUERIMIENTOS','REQUISITOS','PAQUETES','PRUEBAS','EVIDENCIA','BIBLIOGRAFIA','PERMISOS','RECURSOS']:
 if hasattr(contenido,name): save('contenido_'+name+'.json',getattr(contenido,name))
save('variables_contenido.json',{k:type(v).__name__ for k,v in vars(contenido).items() if k.isupper()})
diagrams=[]
from PIL import Image
for p in sorted((ROOT/'generadorDocumento/diagramas').glob('*.png')):
 im=Image.open(p);diagrams.append(dict(id=p.stem,archivo=rel(p),ancho=im.width,alto=im.height,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),editable='generadorDocumento/ea/crm-p2.eapx',estado='Pendiente de inspección visual'))
save('diagramas.json',diagrams)
save('metricas_extraccion.json',dict(archivos=len(inv),paginas_pdf=len(pages),parrafos_docx=len(paras),tablas_docx=len(tables),imagenes_docx=len(x.findall('.//wp:docPr',ns)),clases=len(classes),metodos=len(methods),diagramas_png=len(diagrams)))
print(json.dumps(json.loads((E/'metricas_extraccion.json').read_text(encoding='utf8'))));print('Variables contenido:',[k for k in vars(contenido) if k.isupper()])
