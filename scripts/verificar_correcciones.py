"""Prueba de punta a punta de las correcciones de la clienta (catalogo por programa, asignacion,
reasignacion con historial, agenda, comision configurable y reportes por vendedor).

ATENCION: crea usuarios, interesados, pagos y comisiones. Correr SOLO contra una base de prueba
recien migrada con el seeder (php artisan migrate:fresh --seed), nunca contra la base de la demo.

Uso: python scripts/verificar_correcciones.py URL_API   (ej. http://localhost:18001/api, entorno de prueba)
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta

if len(sys.argv) < 2:
    sys.exit(__doc__)
BASE = sys.argv[1].rstrip('/')


def call(method, path, token=None, body=None):
    req = urllib.request.Request(BASE + path, method=method, data=json.dumps(body).encode() if body is not None else None)
    req.add_header('Accept', 'application/json')
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {'raw': raw[:200]}


def ok(cond, label):
    print(('OK   ' if cond else 'FAIL ') + label)
    if not cond:
        ok.failed += 1


ok.failed = 0


def login(correo, password):
    st, d = call('POST', '/login', body={'correo': correo, 'password': password})
    assert st == 200, (st, d)
    return d['token']


admin = login('admin@crm-educativo.local', 'Admin12345')
vend_a = login('vendedor.demo@crm-educativo.local', 'Vendedor12345')
for correo, rol in [('vendedor.b@test.local', 'vendedor'), ('coord@test.local', 'coordinador')]:
    call('POST', '/usuarios', admin, {'nombre': rol.title(), 'apellido': 'B' if rol == 'vendedor' else 'Coord', 'correo': correo,
                                      'password': 'Clave12345', 'rol': rol, 'estado': 'activo'})
vend_b = login('vendedor.b@test.local', 'Clave12345')
coord = login('coord@test.local', 'Clave12345')

# 1. Catalogo por programa: interes en programa completo crea un interes por modulo
persona = {'apellido': 'Prueba', 'telefono': '70000001', 'profesion': 'Ing', 'ubicacion': 'SCZ'}
st, d = call('POST', '/registro-interes', body={**persona, 'nombre': 'Ana', 'documento': '111', 'correo': 'ana@x.bo', 'programa_id': 'datos-bi'})
ok(st == 201, f'registro por programa completo -> {st}')
st, d = call('POST', '/registro-interes', body={**persona, 'nombre': 'Beto', 'documento': '222', 'correo': 'beto@x.bo', 'modulo_id': 'ia-aplicada-m1'})
ok(st == 201, f'registro por modulo suelto -> {st}')
call('POST', '/registro-interes', body={**persona, 'nombre': 'Caro', 'documento': '333', 'correo': 'caro@x.bo', 'modulo_id': 'ciberseguridad-m2'})
st, d = call('POST', '/registro-interes', body={**persona, 'nombre': 'X', 'documento': '444', 'correo': 'x@x.bo'})
ok(st == 422, f'registro sin modulo ni programa -> 422 ({st})')
st, d = call('GET', '/intereses', admin)
ana = [i for i in d['intereses'] if i['prospecto']['nombre'] == 'Ana']
ok(len(ana) == 5, f'Ana tiene 5 intereses (uno por modulo de datos-bi): {len(ana)}')

# 2. Sin autoasignacion
st, d = call('GET', '/intereses', vend_a)
ok(st == 200 and len(d['intereses']) == 0, f'vendedor no ve intereses sin asignar ({len(d.get("intereses", []))})')
st, _ = call('PATCH', f'/intereses/{ana[0]["id"]}/tomar', vend_a)
ok(st in (404, 405), f'ruta tomar eliminada -> {st}')
st, _ = call('POST', '/intereses/distribuir', vend_a)
ok(st == 403, f'vendedor no puede distribuir -> {st}')
st, d = call('GET', '/usuarios?rol=vendedor&estado=activo', coord)
ok(st == 200 and len(d['usuarios']) == 2, f'coordinador lista vendedores -> {st}')
st, d = call('GET', '/usuarios', coord)
ok(st == 403, f'coordinador no lista todos los usuarios -> {st}')

st, d = call('POST', '/intereses/distribuir', coord)
ok(st == 200 and d['asignados'] == 7, f'distribuir asigna 7 -> {st} {d}')
st, d = call('GET', '/intereses', admin)
todos = d['intereses']
ok(all(i['vendedor_id'] for i in todos), 'todos quedaron asignados')
ok(len({i['vendedor_id'] for i in todos if i['prospecto']['nombre'] == 'Ana'}) == 1, 'los 5 intereses de Ana con el mismo vendedor')
otros = {i['prospecto']['nombre']: i['vendedor_id'] for i in todos if i['prospecto']['nombre'] != 'Ana'}
ana_v = next(i['vendedor_id'] for i in todos if i['prospecto']['nombre'] == 'Ana')
ok(otros['Beto'] != ana_v and otros['Caro'] != ana_v, f'reparto equitativo: Beto y Caro al otro vendedor ({otros}, Ana={ana_v})')

# 3. Historial y reasignacion
beto = next(i for i in todos if i['prospecto']['nombre'] == 'Beto')
st, me_a = call('GET', '/me', vend_a)
id_a = me_a['usuario']['id']
token_de = lambda vid: vend_a if vid == id_a else vend_b
dueno = token_de(beto['vendedor_id'])
otro_id = next(i['vendedor_id'] for i in todos if i['vendedor_id'] != beto['vendedor_id'])
st, d = call('POST', '/interacciones', dueno, {'interes_id': beto['id'], 'tipo': 'WhatsApp', 'descripcion': 'Primer contacto',
                                              'resultado': 'Espera autorizacion del jefe', 'fecha': '2020-01-01T10:00:00'})
ok(st == 201 and d['interaccion']['fecha'][:4] != '2020', f'fecha del contacto la pone el servidor ({d["interaccion"]["fecha"][:16]})')
futuro = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%dT10:00')
st, d = call('POST', '/recordatorios', dueno, {'interes_id': beto['id'], 'fecha_programada': futuro, 'descripcion': 'Llamar por pago de empresa'})
rec1 = d['recordatorio']['id']
st, d = call('POST', '/recordatorios', dueno, {'interes_id': beto['id'], 'fecha_programada': futuro, 'descripcion': 'Segundo seguimiento'})
rec2 = d['recordatorio']['id']
st, _ = call('PATCH', f'/recordatorios/{rec1}/completar', dueno, {})
ok(st == 422, f'completar sin nota -> 422 ({st})')
st, _ = call('PATCH', f'/recordatorios/{rec1}/completar', dueno, {'resultado': 'Dice que la empresa aprobo'})
ok(st == 200, f'completar con nota -> {st}')

st, _ = call('PATCH', f'/intereses/{beto["id"]}/asignar', dueno, {'vendedor_id': otro_id})
ok(st == 403, f'vendedor no puede reasignar -> {st}')
st, d = call('PATCH', f'/intereses/{beto["id"]}/asignar', coord, {'vendedor_id': otro_id})
ok(st == 200 and d['interes']['vendedor_id'] == otro_id, f'coordinador reasigna -> {st}')
nuevo = token_de(otro_id)
st, d = call('GET', f'/intereses/{beto["id"]}', nuevo)
ok(st == 200, f'nuevo vendedor abre el interes -> {st}')
inter = d['interes']['interacciones']
tipos = [(i['tipo'], i['usuario']['id']) for i in inter]
ok(any(t == 'WhatsApp' and u == beto['vendedor_id'] for t, u in tipos), 'nuevo vendedor ve el contacto del vendedor anterior con su nombre')
ok(any('Actividad agendada' in i['descripcion'] for i in inter), 'la actividad realizada quedo en el historial con su nota')
ok(any('Reasignado de' in i['descripcion'] for i in inter), 'queda constancia de la reasignacion')
st, d = call('GET', '/recordatorios', nuevo)
ok(any(r['id'] == rec2 for r in d['recordatorios']), 'la actividad pendiente pasa al calendario del nuevo vendedor')
st, d = call('GET', f'/intereses/{beto["id"]}', dueno)
ok(st == 403, f'vendedor anterior ya no lo ve -> {st}')

# 4. Comision configurable
st, _ = call('PUT', '/configuracion/comision', nuevo, {'porcentaje': 9})
ok(st == 403, f'vendedor no cambia la comision -> {st}')
st, d = call('PUT', '/configuracion/comision', coord, {'porcentaje': 5})
ok(st == 200 and d['porcentaje'] == 5, f'coordinador fija 5% -> {d}')
st, d = call('POST', f'/intereses/{beto["id"]}/ordenes-pago', nuevo, {'modulos': ['ia-aplicada-m1'], 'descuentos': []})
orden = d.get('orden') or d.get('orden_pago') or {}
ok(st == 201 and orden.get('id'), f'orden creada -> {st}')
st, d = call('POST', '/pagos/generar', nuevo, {'orden_pago_id': orden['id']})
pago = d['pago']
call('POST', '/comprobantes', nuevo, {'pago_id': pago['id'], 'archivo': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a01cAAAAASUVORK5CYII=', 'nombre_archivo': 'c.png', 'mime': 'image/png'})
st, d = call('PATCH', f'/pagos/{pago["id"]}/aprobar', coord, {})
ok(st == 200, f'pago aprobado -> {st}')
st, d = call('GET', '/comisiones', admin)
com = d['comisiones'][0]
ok(float(com['porcentaje']) == 5 and float(com['monto']) == round(600 * 0.05, 2), f'comision al 5%: {com["porcentaje"]}% = {com["monto"]} Bs')

# 5. Reporte por vendedor
st, d = call('GET', '/reportes/listado?tipo=vendedores', coord)
cols = [c['label'] for c in d['columns']]
ok(all(c in cols for c in ['Asignados', 'Contactados', 'Concretados']), f'columnas por vendedor: {cols}')
fila = next(r for r in d['rows'] if r['vendedor_id'] == otro_id)
ok(fila['concretados'] == 1 and fila['contactados'] >= 1, f'vendedor actual de Beto: {fila}')
st, d = call('GET', f'/reportes/listado?tipo=intereses&vendedor_id={otro_id}&estado=Convertido', coord)
ok(d['total'] == 1 and d['rows'][0]['contactos'] >= 3, f'listado de concretados del vendedor con contactos: {d["rows"]}')

# 6. Contratos usados por Alumnos, Validacion de pagos y Agenda tras normalizar ventas.
st, d = call('GET', '/inscripciones', coord)
inscrita = d['inscripciones'][0]
venta = inscrita['solicitud_compra']
ok(st == 200 and venta['orden_pago']['prospecto']['id'] == beto['prospecto']['id'],
   'alumnos obtiene el prospecto por venta -> orden -> interes')
ok(venta['orden_pago']['pago']['estado'] == 'Pago aprobado', 'alumnos obtiene el pago de la orden')
st, d = call('GET', '/pagos?estado=Pago%20aprobado', coord)
validado = next(p for p in d['pagos'] if p['id'] == pago['id'])
ok(st == 200 and validado['orden_pago']['items'][0]['id'] == venta['id'],
   'validacion usa la misma venta como detalle de orden')
ok(float(validado['orden_pago']['items'][0]['precio_acordado']) == 600,
   'agenda recibe precio_acordado en el detalle')
st, d = call('GET', '/exportaciones/preparar', coord)
ok(st == 200 and d['total'] == 1, 'preparacion academica encuentra la inscripcion normalizada')
st, d = call('POST', '/exportaciones/academico', coord, {})
ok(st == 200 and d['filas'][0]['correo'] == beto['prospecto']['correo'],
   'exportacion CSV conserva alumno, modulo y pago')
st, d = call('GET', '/exportaciones/preparar', coord)
ok(st == 200 and d['total'] == 0, 'el alumno exportado deja de aparecer como pendiente')
st, d = call('POST', '/exportaciones/academico', coord, {})
ok(st == 200 and len(d['exportaciones']) == 0, 'repetir la exportacion no duplica envios')

print('\nFALLAS:', ok.failed)
sys.exit(1 if ok.failed else 0)
