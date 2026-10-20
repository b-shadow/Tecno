"""Auditoria funcional adicional. SOLO QA local poblado por las verificaciones anteriores.
Crea datos ficticios y prueba permisos, archivos, CSV, sesiones, concurrencia y conversion.
Uso: python scripts/verificar_auditoria.py http://localhost:18002/api
"""
import base64
import concurrent.futures
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE=sys.argv[1].rstrip('/')
assert urllib.parse.urlparse(BASE).hostname in ('localhost','127.0.0.1'), 'Solo QA local'
checks=0
stamp=str(time.time_ns())
PNG='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a01cAAAAASUVORK5CYII='

def request(method,path,token=None,body=None):
    headers={'Accept':'application/json','Content-Type':'application/json'}
    if token: headers['Authorization']='Bearer '+token
    req=urllib.request.Request(BASE+path,method=method,headers=headers,data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req,timeout=30) as r: return r.status,json.loads(r.read() or '{}')
    except urllib.error.HTTPError as e: return e.code,json.loads(e.read() or '{}')

def call(method,path,token=None,body=None,status=200):
    code,data=request(method,path,token,body)
    check(code==status,f'{method} {path} -> {status} (recibido {code})')
    return data

def check(condition,label):
    global checks
    if not condition: raise AssertionError(label)
    checks+=1
    print('OK',label,flush=True)

def login(email,password): return call('POST','/login',body={'correo':email,'password':password})

admin=login('admin@crm-educativo.local','Admin12345')['token']
coord=login('coord@test.local','Clave12345')['token']
a=login('vendedor.demo@crm-educativo.local','Vendedor12345')
b=login('vendedor.b@test.local','Clave12345')
ta,tb=a['token'],b['token']
aid,bid=a['usuario']['id'],b['usuario']['id']
person={'nombre':'Auditoria','apellido':'Compartida '+stamp,'documento':'AUD-'+stamp,'correo':'audit.'+stamp+'@example.invalid',
        'telefono':'00009999','profesion':'QA','ubicacion':'Base aislada','modulo_id':'ia-aplicada-m1'}
public=call('POST','/registro-interes',body=person,status=201)
check(not any(k in public for k in ['prospecto','interes','usuario','vendedor']),'registro publico no expone entidades internas')
interests=call('GET','/intereses',admin)['intereses']
i=next(i for i in interests if i['prospecto']['correo']==person['correo'])
pid=i['prospecto_id']
call('PATCH',f'/intereses/{i["id"]}/asignar',coord,{'vendedor_id':aid})
j=call('POST','/intereses',admin,{'prospecto_id':pid,'modulo_id':'ia-aplicada-m2'},201)['interes']
call('PATCH',f'/intereses/{j["id"]}/asignar',coord,{'vendedor_id':bid})
call('POST','/registro-interes',body={**person,'nombre':'NO SOBRESCRIBIR'})
saved=next(p for p in call('GET','/prospectos',admin)['prospectos'] if p['id']==pid)
check(saved['nombre']=='Auditoria','registro anonimo no sobrescribe un contacto existente')
call('POST','/registro-interes',body={**person,'correo':'otro.'+stamp+'@example.invalid'},status=422)
owned=next(p for p in call('GET','/prospectos',ta)['prospectos'] if p['id']==pid)
check([x['id'] for x in owned['intereses']]==[i['id']],'cartera no incluye intereses del otro vendedor')
edited=call('PUT',f'/prospectos/{pid}',ta,{k:saved[k] for k in ['nombre','apellido','documento','correo','telefono','profesion','ubicacion','estado']})['prospecto']
check([x['id'] for x in edited['intereses']]==[i['id']],'editar prospecto compartido no revela intereses ajenos')
check([x['id'] for x in call('GET',f'/prospectos/{pid}/intereses',ta)['intereses']]==[i['id']],'detalle de prospecto mantiene el alcance por interes')
allowed_docs={p['documento'] for p in call('GET','/prospectos',ta)['prospectos']}
report=call('GET','/reportes/listado?tipo=prospectos',ta)
check(all(row['ci'] in allowed_docs for row in report['rows']),'reporte de prospectos no revela otras carteras')
check(next(row for row in report['rows'] if row['ci']==person['documento'])['intereses']==1,'reporte cuenta solo intereses autorizados del prospecto compartido')
contact={'interes_id':j['id'],'tipo':'Nota comercial','descripcion':'Nota privada de cartera B'}
call('POST','/interacciones',tb,contact,201)
call('POST','/interacciones',ta,contact,403)
history=call('GET',f'/prospectos/{pid}/interacciones',ta)['interacciones']
check(not any(x['interes_id']==j['id'] for x in history),'historial compartido no filtra cartera ajena')
reminder={'interes_id':j['id'],'fecha_programada':'2026-12-20T10:00','descripcion':'Agenda de cartera B'}
r=call('POST','/recordatorios',coord,reminder,201)['recordatorio']
check(r['fecha_programada'].startswith('2026-12-20T14:00'),'10:00 Bolivia se serializa como 14:00 UTC')
check(r['usuario_id']==bid,'actividad creada por coordinacion pertenece al vendedor asignado')
check(any(x['id']==r['id'] for x in call('GET','/recordatorios',tb)['recordatorios']),'vendedor recibe su actividad creada por coordinacion')
call('POST','/recordatorios',ta,reminder,403)
call('PATCH',f'/recordatorios/{r["id"]}/completar',ta,{'resultado':'No autorizado'},403)
call('PATCH',f'/recordatorios/{r["id"]}/cancelar',ta,{},403)
call('PATCH',f'/recordatorios/{r["id"]}/completar',tb,{'resultado':'Realizada QA'})
call('PATCH',f'/recordatorios/{r["id"]}/completar',tb,{'resultado':'No duplicar'},422)
call('PATCH',f'/recordatorios/{r["id"]}/cancelar',tb,{},422)
r2=call('POST','/recordatorios',tb,reminder,201)['recordatorio']
call('PATCH',f'/recordatorios/{r2["id"]}/cancelar',tb,{})
call('PATCH',f'/recordatorios/{r2["id"]}/completar',tb,{'resultado':'No reactivar'},422)
r3=call('POST','/recordatorios',tb,reminder,201)['recordatorio']
with concurrent.futures.ThreadPoolExecutor(2) as pool:
    codes=list(pool.map(lambda _:request('PATCH',f'/recordatorios/{r3["id"]}/completar',tb,{'resultado':'Carrera QA'})[0],range(2)))
check(sorted(codes)==[200,422],'completar concurrentemente produce un solo cumplimiento')
call('PATCH',f'/intereses/{i["id"]}/estado',ta,{'estado':'Convertido'},422)
call('PATCH',f'/prospectos/{pid}/estado',ta,{'estado':'Convertido'},422)
call('PATCH',f'/intereses/{i["id"]}/estado',ta,{'estado':'Perdido'},422)
call('PATCH',f'/intereses/{i["id"]}/estado',ta,{'estado':'Perdido','observacion':'QA: horario incompatible'})
call('POST','/registro-interes',body=person)
check(call('GET',f'/intereses/{i["id"]}',admin)['interes']['estado']=='Perdido','registro repetido no reabre un seguimiento cerrado')
call('PATCH',f'/intereses/{i["id"]}/estado',ta,{'estado':'Interesado'})

header='nombres,apellidos,ci,telefono,profesion,ubicacion,correo'
csv='\ufeff'+header+'\r\n"Ana, QA",Auditoria,CSV-'+stamp+',00000000,"Docencia\nSuperior",Santa Cruz,csv.'+stamp+'@example.invalid'
check(call('POST','/prospectos/importar',coord,{'csv':csv})['creados']==1,'CSV con BOM, comas y salto de linea entre comillas')
for bad in [header, 'nombres,nombres\na,b', header+'\na,b,c,0,p,l,no-es-correo',
            header+'\n'+('A'*121)+',b,c,0,p,l,qa@example.invalid',csv]:
    call('POST','/prospectos/importar',coord,{'csv':bad},422)
call('POST','/prospectos/importar',ta,{'csv':csv},403)

admin_id=call('GET','/me',admin)['usuario']['id']
call('PATCH',f'/usuarios/{admin_id}/estado',admin,{'estado':'inactivo'},422)
call('PUT',f'/usuarios/{admin_id}',admin,{'nombre':'Administrador','apellido':'General','correo':'admin@crm-educativo.local','rol':'vendedor','estado':'activo'},422)
user={'nombre':'Temporal','apellido':'QA','correo':'cuenta.'+stamp+'@example.invalid','rol':'vendedor','estado':'activo','password':'QaClave12345'}
u=call('POST','/usuarios',admin,user,201)['usuario']
first=login(user['correo'].upper(),user['password'])['token']
second=login(user['correo'],user['password'])['token']
call('PUT','/perfil/password',first,{'password_actual':'mal','password':'OtraClave123','password_confirmation':'OtraClave123'},422)
call('PUT','/perfil/password',first,{'password_actual':user['password'],'password':'sololetras','password_confirmation':'sololetras'},422)
call('PUT','/perfil/password',first,{'password_actual':user['password'],'password':'OtraClave123','password_confirmation':'OtraClave123'})
call('GET','/me',first)
call('GET','/me',second,status=401)
call('PUT',f'/usuarios/{u["id"]}',admin,{**user,'password':'ResetAdmin123'})
call('GET','/me',first,status=401)
third=login(user['correo'],'ResetAdmin123')['token']
call('PUT',f'/usuarios/{u["id"]}',admin,{**user,'password':'','estado':'inactivo'})
call('GET','/me',third,status=401)
call('POST','/login',body={'correo':user['correo'],'password':'ResetAdmin123'},status=403)

note={'usuario_id':bid,'tipo':'Auditoria','mensaje':'Notificacion ficticia, correo log'}
call('POST','/notificaciones/enviar',ta,note,403)
n=call('POST','/notificaciones/enviar',tb,note,201)['notificacion']
call('PATCH',f'/notificaciones/{n["id"]}/leida',ta,{},403)
call('PATCH',f'/notificaciones/{n["id"]}/leida',tb,{})
call('POST','/notificaciones/enviar',ta,{'destinatario':person['correo'],'tipo':'Seguimiento QA','mensaje':'Ficticio, modo log'},201)
call('POST','/notificaciones/enviar',coord,{'tipo':'Sin destino','mensaje':'QA'},422)

call('PUT','/configuracion/comision',coord,{'porcentaje':2.75})
orders=[]
for _ in range(2):
    o=call('POST',f'/intereses/{i["id"]}/ordenes-pago',ta,{'modulos':['ia-aplicada-m1'],'descuentos':[]},201)['orden']
    payment=o['pago']['id']; orders.append(payment)
    call('POST','/comprobantes',ta,{'pago_id':payment,'archivo':'data:text/html;base64,'+base64.b64encode(b'<script>alert(1)</script>').decode()},422)
    call('POST','/comprobantes',ta,{'pago_id':payment,'archivo':'data:image/png;base64,iVBORw0KGgo='},422)
    call('POST','/comprobantes',ta,{'pago_id':payment,'archivo':PNG,'nombre_archivo':'QA-valido.png'},201)
    call('POST','/comprobantes',ta,{'pago_id':payment,'archivo':PNG},422)
with concurrent.futures.ThreadPoolExecutor(2) as pool:
    codes=list(pool.map(lambda p:request('PATCH',f'/pagos/{p}/aprobar',coord,{})[0],orders))
check(sorted(codes)==[200,422],'dos ordenes simultaneas no duplican la misma matricula')
commission=next(c for c in call('GET','/comisiones',admin)['comisiones'] if c['venta']['orden_pago']['prospecto']['id']==pid)
check(float(commission['porcentaje'])==2.75 and float(commission['monto'])==16.5,'comision fraccionaria conserva porcentaje y monto')
call('POST','/registro-interes',body=person)
check(call('GET',f'/intereses/{i["id"]}',admin)['interes']['estado']=='Convertido','registro repetido no reinicia una matricula confirmada')
call('PATCH',f'/comisiones/vendedores/{aid}/pagar',coord,{})
check(all(c['estado']=='Pagada' for c in call('GET','/comisiones',ta)['comisiones']),'marcar comisiones recibidas actualiza la cartera correcta')
for role,token in [('admin',admin),('coordinador',coord),('vendedor',ta)]:
    for report in ['prospectos','intereses','pagos','alumnos','comisiones','vendedores']:
        call('GET','/reportes/listado?tipo='+report,token)
    call('GET','/dashboard/metricas',token)
ready=call('GET','/exportaciones/preparar',coord)['total']
export=call('POST','/exportaciones/academico',coord,{})
check(len(export['filas'])==ready,'exportacion conserva la cantidad de inscripciones pendientes')
check(call('POST','/exportaciones/academico',coord,{})['filas']==[],'exportacion repetida no duplica alumnos')
for _ in range(10): call('POST','/login',body={'correo':'limite.'+stamp+'@example.invalid','password':'incorrecta'},status=422)
call('POST','/login',body={'correo':'limite.'+stamp+'@example.invalid','password':'incorrecta'},status=429)
print('TOTAL AUDITORIA:',checks,'comprobaciones aprobadas.')
