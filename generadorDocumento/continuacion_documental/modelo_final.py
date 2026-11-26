"""Control secuencial y reanudable del EAPX, sin escritores simultáneos."""
from pathlib import Path
import os,sys,json,subprocess,time,hashlib
ROOT=Path.cwd();OUT=ROOT/'tmp/actualizacion_documental'
STATE=OUT/'modelo_final_progreso.json'
env={**os.environ,'PYTHONIOENCODING':'utf-8','CODEX_DOCUMENT_NODE':r'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1123-915-0_26.1123.915.0_x64__3k8sg7r9htsxt\dependencies\node\bin\node.exe'}
python=sys.executable
state=json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {'completed':[]}

def save():STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
def run(key,script,*args):
    if key in state['completed']:return
    print('INICIO',key,flush=True);state['active']=key;save();begin=time.time()
    with (OUT/(key+'.log')).open('w',encoding='utf-8') as log:
        result=subprocess.run([python,script,*args],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise RuntimeError(f'{key}: salida {result.returncode}; revisar el log antes de continuar')
    state['completed'].append(key);state['active']=None;save();print('COMPLETO',key,round(time.time()-begin,1),'s',flush=True)

S='generadorDocumento/ea/sincronizar_documentacion.py'
run('final-01-catalogo',S,'catalogo')
run('final-02-integrar-clases',S,'integrar-clases')
run('final-03-organizar-clases',S,'organizar-clases')
run('final-04-presentacion-clases',S,'presentacion-clases')
run('final-05-capas',S,'capas')
run('final-06-relaciones',S,'relaciones-clases')
run('final-07-asociaciones','generadorDocumento/ea/asociaciones_fuente.py')
run('final-08-algoritmos','generadorDocumento/ea/algoritmos_documentados.py')
if 'final-09-interacciones' not in state['completed']:
    complete=False
    for batch in range(1,61):
        key='final-09-lote-'+str(batch).zfill(2)
        run(key,'generadorDocumento/ea/actualizar_interacciones.py','reanudar','80')
        if 'INTERACCIONES_COMPLETAS' in (OUT/(key+'.log')).read_text(encoding='utf-8'):
            complete=True;break
    assert complete,'No se agotará el control dando por completas vistas pendientes'
    state['completed'].append('final-09-interacciones');save()
run('final-10-presentacion-interacciones','generadorDocumento/ea/actualizar_interacciones.py','presentacion')
run('final-11-conceptual','generadorDocumento/ea/actualizar_datos_despliegue.py','conceptual')
run('final-12-despliegue','generadorDocumento/ea/actualizar_datos_despliegue.py','despliegue')
run('final-13-navegacion','generadorDocumento/ea/actualizar_navegacion.py','navegacion')
run('final-14-base','generadorDocumento/ea/actualizar_navegacion.py','base')
run('final-15-exportar-relaciones',S,'exportar-relaciones')
print('MODELO_FINAL_GENERADO_PENDIENTE_VALIDACION_Y_LIMPIEZA',flush=True)
