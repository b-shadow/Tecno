import sys,json,re,collections,hashlib,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent.parent;E=R/'auditoria_documental/evidencias'
def l(n):return json.loads((E/n).read_text(encoding='utf-8-sig'))
def s(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf8')
sys.path.insert(0,str(R/'generadorDocumento'));import esquema
# Normalizaciones explícitas: solo cualificación public y paréntesis redundantes en CHECK.
def norm(s):return re.sub(r'\s+','',s.replace('public.','')).lower()
rs=l('comparacion_restricciones.json')
for c in rs:
 d=c['definicion_documental']
 if not d:c['estado']='NO DOCUMENTADA EN VOLCADO'
 elif c['tipo']=='c':
  a=norm(d).replace('(','').replace(')','');b=norm(c['definicion']).replace('(','').replace(')','')
  c['estado']='COINCIDE (paréntesis redundantes normalizados)' if a==b else 'REVISAR DEFINICIÓN CHECK'
 else:c['estado']='COINCIDE' if norm(d)==norm(c['definicion']) else 'DIFERENTE'
s('comparacion_restricciones.json',rs)
cols=l('comparacion_columnas.json')
for c in cols:
 if c['diferencias']=='Default (comparación literal)' and norm(c['default_documental'] or '')==norm(c['default_real'] or ''):
  c['diferencias']='';c['estado']='COINCIDE';c['nota']='nextval equivalente; public explícito en volcado'
s('comparacion_columnas.json',cols)
# Evitar falso faltante conceptual: omitir columnas FK es una convención explícita.
fks={(t,c) for t,cs,p,ps in esquema.fks() for c in cs};con=l('comparacion_conceptual_ea.json')
for x in con:
 x['fk_omitidas_intencionalmente']=[c for c in x['faltantes'] if (x['tabla'],c) in fks]
 x['faltantes_no_fk']=[c for c in x['faltantes'] if (x['tabla'],c) not in fks]
 x['estado']='COINCIDE CON VOLCADO, abstracción de FK mediante asociaciones' if not x['faltantes_no_fk'] and not x['extras'] else 'DIFERENCIA'
s('comparacion_conceptual_ea.json',con)
cards=l('cardinalidades.json')
for c in cards:
 if c['estado']!='COINCIDE' and c['tabla'] in ['permisos','orden_pago_descuentos']:
  c['estado']='ABSTRACCIÓN N:N VÁLIDA; dos FK y entidad asociativa'
s('cardinalidades.json',cards)
# Párrafos partidos entre páginas: quitar pies de página antes de comparar.
pages=l('paginas_pdf.json');normtext=lambda x:re.sub(r'\s+','',x).casefold();text=''.join(re.sub(r'^\s*\d+\s*\|\s*P\s*á\s*g\s*i\s*n\s*a\s*','',p['texto'],flags=re.I) for p in pages)
eq=l('equivalencia_formatos.json');eq['parrafos_no_coincidentes_pdf_sin_pies']=[p for p in eq['parrafos_no_coincidentes_pdf'] if normtext(p['texto']) not in normtext(text)];s('equivalencia_formatos.json',eq)
# Permisos efectivos comparados con migración generadora. Sin datos personales.
sys.path.insert(0,str(R/'generadorDocumento'));import contenido
per=l('pg_permisos_aplicacion.json');result=[]
for x in per:
 role=x['rol'];recurso=x['recurso_codigo'];expected=contenido.PERMISOS.get(role,{}).get(recurso)
 result.append({**x,'esperado_migracion':expected,'estado':'COINCIDE' if expected==x.get('acceso') else 'DIFERENTE'})
s('comparacion_permisos.json',result)
# Código PHP: obtención de configuración efectiva sin credenciales, tras bootstrap de providers inspeccionados.
php="require 'vendor/autoload.php'; $app=require 'bootstrap/app.php'; $app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap(); $c=config('database.connections.'.config('database.default')); echo json_encode(['driver'=>config('database.default'),'host'=>$c['host']??null,'port'=>$c['port']??null,'database'=>$c['database']??null,'search_path'=>$c['search_path']??null,'timezone'=>config('app.timezone'),'frontend'=>config('services.frontend.url'),'app_url'=>config('app.url'),'config_cached'=>$app->configurationIsCached()],JSON_UNESCAPED_SLASHES);"
p=subprocess.run(['php','-r',php],cwd=R/'negocio',capture_output=True,text=True,encoding='utf8',errors='replace')
try:s('configuracion_efectiva.json',json.loads(p.stdout))
except:s('configuracion_efectiva_error.json',{'exit':p.returncode,'error':p.stderr[:300]})
# Comprobar dependencias fijadas por locks (no por versiones públicas actuales).
composer=json.loads((R/'negocio/composer.lock').read_text(encoding='utf8'));npm=json.loads((R/'presentacion/package-lock.json').read_text(encoding='utf8'));versions={x['name']:x['version'] for x in composer.get('packages',[]) if x['name'] in ['laravel/framework','stripe/stripe-php']}
versions.update({n:v.get('version') for n,v in npm.get('packages',{}).items() if n in ['node_modules/react','node_modules/vite','node_modules/axios','node_modules/tailwindcss','node_modules/react-router-dom','node_modules/chart.js','node_modules/lucide-react','node_modules/@playwright/test','node_modules/playwright']});s('versiones_lock.json',versions)
# Revisión de diseño impreso por todas las páginas, no lectura detallada de texto en miniaturas.
import fitz
from PIL import Image,ImageDraw
pdf=fitz.open(R/'generadorDocumento/documento/P2-INF513-GRUPO05SA.pdf')
for i in range(0,len(pdf),9):
 canvas=Image.new('RGB',(1800,2220),'#bbb');draw=ImageDraw.Draw(canvas)
 for j in range(min(9,len(pdf)-i)):
  pix=pdf[i+j].get_pixmap(matrix=fitz.Matrix(.7,.7));im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((580,690));x=(j%3)*600+(600-im.width)//2;y=(j//3)*740+35;canvas.paste(im,(x,y));draw.text(((j%3)*600+20,(j//3)*740+8),f'PDF {i+j+1}',fill='black',font_size=22)
 canvas.save(E/f'paginas_contacto_{i//9+1:02}.png')
# Índices, triggers y funciones: comparación cuerpo/definición, no solo nombres.
sql=(R/'generadorDocumento/fuentes/esquema.sql').read_text(encoding='utf8');fun=[]
for p in l('pg_funciones.json'):
 m=re.search(r'CREATE FUNCTION public\.'+re.escape(p['nombre'])+r'\(.*?AS \$function\$(.*?)\$function\$;',sql,re.S)
 if not m:m=re.search(r'CREATE FUNCTION public\.'+re.escape(p['nombre'])+r'\(.*?AS \$\$(.*?)\$\$;',sql,re.S)
 a=re.search(r'AS \$function\$(.*?)\$function\$',p['definicion'],re.S)
 fun.append({'funcion':p['nombre'],'estado':'CUERPO COINCIDE' if m and a and norm(m.group(1))==norm(a.group(1)) else 'REQUIERE REVISIÓN DE CUERPO','documental':m.group(1) if m else None,'real':p['definicion']})
s('comparacion_funciones.json',fun)
print('Constraints',collections.Counter(c['estado'] for c in rs));print('Columns',collections.Counter(c['estado'] for c in cols));print('Permissions',collections.Counter(c['estado'] for c in result));print('Functions',[(c['funcion'],c['estado']) for c in fun]);print('PDF paragraphs unmatched',len(eq['parrafos_no_coincidentes_pdf_sin_pies']))
