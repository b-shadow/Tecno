"""Entorno QA retenido: sin crear bases, migrar ni tocar datos comerciales."""
from pathlib import Path
import os,sys,json,re,subprocess,time,socket
import psycopg
ROOT=Path.cwd();OUT=ROOT/'tmp/actualizacion_documental/qa';OUT.mkdir(exist_ok=True)
QA='crm_qa_manual_email_20261126'
cfg={}
for line in (ROOT/'negocio/.env').read_text(encoding='utf-8-sig').splitlines():
 if '=' in line and not line.lstrip().startswith('#'):
  k,v=line.split('=',1);cfg[k]=v.strip().strip('"').strip("'")
env={**os.environ,**cfg,'DB_DATABASE':QA,'APP_ENV':'testing','APP_DEBUG':'false','APP_URL':'http://127.0.0.1:18001','FRONTEND_URL':'http://localhost:18003','VITE_BASE':'/','QA_BASE':'http://localhost:18003','QA_API':'http://127.0.0.1:18001/api','MAIL_HOST':'127.0.0.1','MAIL_PORT':'1026','MAIL_USERNAME':'(null)','MAIL_PASSWORD':'(null)','MAIL_URL':'(null)','MAIL_SCHEME':'smtp','MAIL_MAILER':'smtp','CACHE_PREFIX':'qa_doc_20261126_','PGPASSWORD':cfg.get('DB_PASSWORD',''),'PGHOST':cfg['DB_HOST'],'PGPORT':cfg.get('DB_PORT','5432')}
assert env['DB_DATABASE']==QA and QA!=cfg['DB_DATABASE']
assert env.get('STRIPE_SECRET','').startswith('sk_test_'),'Se requiere Stripe Sandbox'
NODE=r'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1123-915-0_26.1123.915.0_x64__3k8sg7r9htsxt\dependencies\node\bin\node.exe'

def spawn(name,args,cwd=ROOT):
 p=subprocess.Popen(args,cwd=cwd,env=env,stdout=(OUT/(name+'.log')).open('w',encoding='utf-8'),stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 (OUT/(name+'.pid')).write_text(str(p.pid));return p

def listen_secret():
 path=OUT/'stripe.log'
 if path.exists():
  m=re.search(r'whsec_[A-Za-z0-9]+',path.read_text(errors='replace'))
  if m:env['STRIPE_WEBHOOK_SECRET']=m[0];return True
 return False

def start():
 probe=json.loads(subprocess.check_output(['php','tmp/actualizacion_documental/configuracion.php'],env=env,text=True))
 assert probe['cache'] is False and probe['conexion']['database']==QA,'La configuración efectiva no corresponde a QA sin caché'
 for port in [18001,18003,1026]:
  with socket.socket() as sock:assert sock.connect_ex(('127.0.0.1',port))!=0,f'Puerto QA {port} ocupado'
 with psycopg.connect(host=cfg['DB_HOST'],port=cfg.get('DB_PORT',5432),dbname=QA,user=cfg['DB_USERNAME'],password=cfg.get('DB_PASSWORD','')) as c:
  assert c.execute('select current_database()').fetchone()[0]==QA
  counts=c.execute("select count(*) from information_schema.tables where table_schema='public' and table_type='BASE TABLE'").fetchone()[0]
  assert counts==31,'Usar únicamente la base QA ya existente; no ejecutar migraciones'
  seqs=c.execute("select schemaname,sequencename,last_value from pg_sequences where schemaname='public'").fetchall()
  for schema,name,last in seqs:
   # Solo datos QA: evita colisiones de metadatos con el listener Sandbox comercial.
   c.execute('select setval(%s::regclass,%s,true)',(schema+'.'+name,max(last or 1,1000000)))
 env['STRIPE_API_KEY']=env['STRIPE_SECRET']
 spawn('stripe',['stripe','listen','--skip-update','--all-snapshot','--forward-to','http://127.0.0.1:18001/api/stripe/webhook'])
 for _ in range(30):
  if listen_secret():break
  time.sleep(1)
 assert listen_secret(),'No se obtuvo el secreto del listener QA'
 spawn('api',['php','artisan','serve','--host=127.0.0.1','--port=18001'],ROOT/'negocio')
 spawn('smtp',[sys.executable,'tmp/manual-email/smtp_sink.py'])
 env['VITE_API_PROXY']='http://127.0.0.1:18001'
 spawn('vite',[NODE,'node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','18003'],ROOT/'presentacion')
 (OUT/'entorno.json').write_text(json.dumps({'db':QA,'api':'http://127.0.0.1:18001','frontend':'http://localhost:18003','smtp':'127.0.0.1:1026','stripe':'Sandbox','secuencias_qa_minimo':1000000,'sin_migraciones':True},indent=2))
 print('QA existente aislado preparado; puertos 18001/18003/1026; Stripe Sandbox y SMTP local. No se guardó el entorno con credenciales.')

def run():
 listen_secret();args=sys.argv[2:];name=Path(args[1] if len(args)>1 else args[0]).stem
 log=OUT/(name+'-resultado.log')
 with log.open('w',encoding='utf-8') as stream:
  result=subprocess.run(args,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
 data={'script':args,'exit_code':result.returncode,'log':str(log.relative_to(ROOT)),'db':QA,'commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'fecha':'2026-11-26'}
 (OUT/(name+'-resultado.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(data,ensure_ascii=False));sys.exit(result.returncode)

if __name__=='__main__':
 if sys.argv[1]=='start':start()
 elif sys.argv[1]=='run':run()
 else:raise ValueError(sys.argv[1])
