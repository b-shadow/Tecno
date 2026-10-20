"""Auditoria de navegadores en Linux aislado; no controla las ventanas del usuario.
Uso: python scripts/qa_browsers.py [chromium|firefox|webkit]
Requiere scripts/qa_local.py start y la imagen oficial Playwright indicada abajo.
Los resultados se guardan en qa-artifacts/ (ignorado por Git).
"""
import pathlib
import subprocess
import sys
import io
import tarfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
NAME='crm-qa-browsers'
IMAGE='mcr.microsoft.com/playwright:v1.64.1-noble'
engines=sys.argv[1:] or ['chromium','firefox','webkit']
assert all(e in ['chromium','firefox','webkit'] for e in engines)

def run(*args,check=True,data=None):
    return subprocess.run(['docker',*args],cwd=ROOT,check=check,capture_output=True,input=data)

existing=run('ps','-a','--filter','name=^/'+NAME+'$','--format','{{.Names}}').stdout.strip()
if existing: raise RuntimeError('Ya existe un ejecutor de navegadores. No se reemplaza automaticamente.')
run('create','--name',NAME,'--label','tecnotarea.qa=true','--network','crm-web_default','--init','--ipc=host',
    '-e','QA_BASE=http://crm-qa-audit:18002','-e','QA_ENGINES='+','.join(engines),'-w','/work',IMAGE,
    'sh','-c','npm ci --prefix backend --ignore-scripts --no-audit && node scripts/verificar_navegadores.mjs')
try:
    archive=io.BytesIO()
    with tarfile.open(fileobj=archive,mode='w') as tar:
        for name in ['backend/package.json','backend/package-lock.json','scripts/verificar_navegadores.mjs']:
            tar.add(ROOT/name,arcname=name)
    run('cp','-',NAME+':/work',data=archive.getvalue())
    completed=subprocess.run(['docker','start','-a',NAME],cwd=ROOT)
    (ROOT/'qa-artifacts').mkdir(exist_ok=True)
    run('cp',NAME+':/work/qa-artifacts/.',str(ROOT/'qa-artifacts'),check=False)
    if completed.returncode: raise RuntimeError('Fallo la auditoria de navegadores; revisar qa-artifacts/summary.json.')
finally:
    run('rm','-f',NAME,check=False)
