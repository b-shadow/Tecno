"""Entorno desechable para auditar el CRM sin tocar la base de trabajo.
Uso: python scripts/qa_local.py start|test|stop
Requiere el Compose local en marcha. Solo usa la base crm_qa_audit y el puerto 18002.
"""
import base64
import io
import json
import pathlib
import secrets
import subprocess
import sys
import tarfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
NAME = 'crm-qa-audit'
DB = 'crm_qa_audit'
URL = 'http://127.0.0.1:18002/api'

def docker(*args, data=None):
    r = subprocess.run(['docker', *args], cwd=ROOT, input=data, capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode(errors='replace')+r.stdout.decode(errors='replace'))
    return r.stdout

def start():
    existing = docker('ps','-a','--filter','name=^/'+NAME+'$','--format','{{.Names}}').decode().strip()
    if existing: raise RuntimeError('El entorno QA ya existe; detenerlo con stop antes de recrearlo.')
    docker('compose','exec','-T','postgres','createdb','-U','crm_user',DB)
    mounts = json.loads(docker('inspect','crm-web-app-1','--format','{{json .Mounts}}'))
    vendor = next(m['Name'] for m in mounts if m['Destination']=='/app/vendor')
    network = next(iter(json.loads(docker('inspect','crm-web-app-1','--format','{{json .NetworkSettings.Networks}}'))))
    image = docker('inspect','crm-web-app-1','--format','{{.Config.Image}}').decode().strip()
    docker('create','--name',NAME,'--label','tecnotarea.qa=true','--network',network,'-p','127.0.0.1:18002:18002',
        '-v',vendor+':/app/vendor:ro','-e','APP_ENV=testing','-e','APP_DEBUG=false',
        '-e','APP_KEY=base64:'+base64.b64encode(secrets.token_bytes(32)).decode(),
        '-e','APP_URL=http://localhost:18002','-e','APP_TIMEZONE=America/La_Paz',
        '-e','DB_CONNECTION=pgsql','-e','DB_HOST=postgres','-e','DB_DATABASE='+DB,
        '-e','DB_USERNAME=crm_user','-e','DB_PASSWORD=crm_password','-e','SESSION_DRIVER=file',
        '-e','CACHE_STORE=file','-e','MAIL_MAILER=log','-e','PHP_CLI_SERVER_WORKERS=4',image,
        'sh','-c','cd /app && mkdir -p bootstrap/cache storage/framework/cache/data storage/framework/sessions storage/framework/views storage/logs && php artisan migrate --seed --force && cd public && php -S 0.0.0.0:18002 ../vendor/laravel/framework/src/Illuminate/Foundation/resources/server.php')
    archive = io.BytesIO()
    backend = ROOT/'backend'
    with tarfile.open(fileobj=archive, mode='w') as tar:
        for path in backend.rglob('*'):
            rel = path.relative_to(backend)
            if any(p in ['vendor','node_modules','storage','.git'] for p in rel.parts): continue
            if rel.as_posix().startswith('bootstrap/cache/'): continue
            if path.name.startswith('.env') or path.name=='hot' or not path.is_file(): continue
            tar.add(path, arcname=rel.as_posix())
    docker('cp','-',NAME+':/app',data=archive.getvalue())
    docker('start',NAME)
    for _ in range(30):
        try:
            with urllib.request.urlopen(URL+'/health', timeout=2) as r:
                if r.status==200: print('QA aislado listo:',URL); return
        except Exception: time.sleep(1)
    raise RuntimeError(docker('logs','--tail','20',NAME).decode())

def test():
    for script in ['verificar_correcciones.py','verificar_seguridad.py','verificar_reenvio_comprobante.py','verificar_auditoria.py','verificar_administradores.py']:
        path=ROOT/'scripts'/script
        if path.exists(): subprocess.run([sys.executable,'-u',str(path),URL],cwd=ROOT,check=True)
    subprocess.run(['node','scripts/verificar_sesion.mjs'],cwd=ROOT,check=True)
    sql=(ROOT/'scripts/verificar_integridad.sql').read_bytes()
    print(docker('compose','exec','-T','postgres','psql','-U','crm_user','-d',DB,'-v','ON_ERROR_STOP=1',data=sql).decode())

def stop():
    existing=docker('ps','-a','--filter','name=^/'+NAME+'$','--format','{{.Names}}').decode().strip()
    if existing:
        label=docker('inspect',NAME,'--format','{{index .Config.Labels "tecnotarea.qa"}}').decode().strip()
        if label!='true': raise RuntimeError('No se elimina un contenedor que no tenga la etiqueta QA.')
        docker('rm','-f',NAME)
    docker('compose','exec','-T','postgres','dropdb','-U','crm_user','--if-exists',DB)
    print('Contenedor y base QA eliminados; la base de trabajo se conserva.')

if __name__=='__main__': {'start':start,'test':test,'stop':stop}[sys.argv[1]]()
