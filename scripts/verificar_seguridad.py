"""Regresion sobre la base AISLADA poblada por verificar_correcciones.py. Nunca usar en la demo."""
import json
import sys
import urllib.request
import urllib.error

BASE = sys.argv[1].rstrip('/')
failures = 0
checks = 0

def call(method, path, token=None, body=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Accept': 'application/json', 'Content-Type': 'application/json',
                 **({'Authorization': 'Bearer ' + token} if token else {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or '{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or '{}')

def check(condition, label):
    global failures, checks
    checks += 1
    failures += not condition
    print(('OK   ' if condition else 'FAIL ') + label)

def login(email, password):
    status, data = call('POST', '/login', body={'correo': email, 'password': password})
    assert status == 200
    return data['token']

admin = login('admin@crm-educativo.local', 'Admin12345')
coord = login('coord@test.local', 'Clave12345')
seller = login('vendedor.demo@crm-educativo.local', 'Vendedor12345')
outsider = login('vendedor.b@test.local', 'Clave12345')
check(call('POST', '/login', body={'correo': 'admin@crm-educativo.local', 'password': 'incorrecta'})[0] in (401, 422), 'login incorrecto rechazado')
for path in ['/me', '/usuarios', '/prospectos', '/intereses', '/pagos', '/recordatorios', '/inscripciones', '/comisiones', '/reportes/administrativos', '/exportaciones']:
    check(call('GET', path)[0] == 401, 'sin sesion: ' + path)
for path in ['/usuarios', '/pagos', '/inscripciones', '/comisiones/resumen', '/reportes/administrativos', '/exportaciones/preparar']:
    check(call('GET', path, seller)[0] == 403, 'vendedor restringido: ' + path)
for path in ['/me', '/usuarios', '/prospectos', '/intereses', '/pagos', '/recordatorios', '/inscripciones', '/comisiones', '/comisiones/resumen', '/configuracion/comision', '/descuentos', '/ordenes-pago', '/dashboard/metricas', '/reportes/administrativos', '/reportes/comerciales', '/reportes/listado?tipo=alumnos', '/notificaciones', '/exportaciones/preparar', '/exportaciones']:
    check(call('GET', path, admin)[0] == 200, 'administrador: ' + path)

_, data = call('GET', '/pagos', coord)
payment = next(p for p in data['pagos'] if p['estado'] == 'Pago aprobado')
pid, oid = payment['id'], payment['orden_pago_id']
check(call('GET', f'/pagos/{pid}', outsider)[0] == 403, 'pago ajeno no visible')
check(call('GET', f'/comprobantes/{pid}', outsider)[0] == 403, 'comprobante ajeno no visible')
check(call('POST', '/pagos/generar', outsider, {'orden_pago_id': oid})[0] == 403, 'no generar pago sobre orden ajena')
check(call('PATCH', f'/pagos/{pid}/aprobar', seller, {})[0] == 403, 'vendedor no aprueba pagos')
check(call('PATCH', f'/pagos/{pid}/aprobar', coord, {})[0] == 422, 'doble aprobacion no duplica historial')
check(call('PATCH', f'/pagos/{pid}/rechazar', coord, {'observacion':'Intento QA'})[0] == 422, 'pago aprobado no se rechaza dejando matricula vigente')
for value in [-1, 101, 'texto']:
    check(call('PUT', '/configuracion/comision', coord, {'porcentaje':value})[0] == 422, f'porcentaje invalido: {value}')
check(call('GET', '/pagos/999999', admin)[0] == 404, 'recurso inexistente devuelve 404')
check(call('GET', '/me', 'token-invalido')[0] == 401, 'token invalido rechazado')
session = login('coord@test.local', 'Clave12345')
check(call('POST', '/logout', session, {})[0] == 200 and call('GET', '/me', session)[0] == 401, 'logout revoca sesion')
print(f'\n{checks} comprobaciones; FALLAS: {failures}')
sys.exit(bool(failures))
