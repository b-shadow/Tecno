"""Utilidades de los scripts de verificación de la API. Solo contra una base QA local, nunca contra la demo ni producción.

Uso de cada script: python scripts/<script>.py [http://localhost:18001]   (con o sin /api al final)
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:18001').rstrip('/')
API = BASE if BASE.endswith('/api') else BASE + '/api'
assert urllib.parse.urlparse(API).hostname in ('localhost', '127.0.0.1'), 'Solo contra una base QA local'

CUENTAS = {
    'admin': ('admin@crm-educativo.local', 'Admin12345'),
    'coord': ('coord@test.local', 'Clave12345'),
    'v1': ('vendedor.demo@crm-educativo.local', 'Vendedor12345'),
    'v2': ('vendedor2@crm-educativo.local', 'Vendedor12345'),
}
V1, V2 = CUENTAS['v1'][0], CUENTAS['v2'][0]
PNG = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
fallas = []
total = 0


def api(metodo, ruta, cuerpo=None, token=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(API + ruta, data=datos, method=metodo,
                                 headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        texto = e.read()
        try:
            return e.code, json.loads(texto or b'{}')
        except ValueError:
            return e.code, {'raw': texto[:200].decode(errors='replace')}


def caso(nombre, cond, detalle=''):
    global total
    total += 1
    print(('OK   ' if cond else 'FALLA') + ' ' + nombre + ('' if cond else f'  -> {str(detalle)[:300]}'), flush=True)
    if not cond:
        fallas.append(nombre)


def login(cuenta, clave=None):
    correo, clave = CUENTAS[cuenta] if clave is None else (cuenta, clave)
    s, r = api('POST', '/login', {'correo': correo, 'password': clave})
    if s == 429:  # límite de intentos de login (10/min por cuenta e IP): esperar la ventana y reintentar una vez
        time.sleep(61)
        s, r = api('POST', '/login', {'correo': correo, 'password': clave})
    assert s == 200, f'login {correo}: {s} {r}'
    return r['token']


def unico():
    return str(time.time_ns())[-9:]


def modulos_abiertos():
    _, cat = api('GET', '/catalogo')
    return [m['codigo'] for p in cat['programas'] for m in p['modulos']]


def nuevo_interes(admin, vendedor=V1, modulo=None):
    """Prospecto nuevo con datos completos y una tarjeta asignada a `vendedor`. Devuelve (documento, nro_tarjeta, módulo)."""
    u = unico()
    modulo = modulo or modulos_abiertos()[0]
    s, r = api('POST', '/prospectos', {'documento': f'QA{u}', 'nombre': 'Prueba', 'apellido': 'Automatica', 'correo': f'qa.{u}@example.invalid',
                                        'telefono': '71234567', 'profesion': 'Ingeniero', 'ubicacion': 'Santa Cruz', 'origen': 'Web',
                                        'modulo_codigo': modulo}, admin)
    assert s == 201, f'alta de prospecto: {s} {r}'
    nro = r['prospecto']['intereses'][0]['nro_tarjeta']
    if vendedor:
        s, r = api('PATCH', f'/intereses/{nro}/asignar', {'vendedor_correo': vendedor}, admin)
        assert s == 200, f'asignación: {s} {r}'
    return f'QA{u}', nro, modulo


def orden_con_comprobante(vendedor, documento, nro_tarjeta, modulo):
    """Método QR, orden de 1 cuota y comprobante enviado a revisión. Devuelve nro_orden."""
    s, r = api('POST', f'/prospectos/{documento}/metodos-pago', {'tipo': 'QR', 'titular': 'Prueba Automatica'}, vendedor)
    assert s == 201, f'método QR: {s} {r}'
    metodo = r['metodo']['nro_metodo']
    s, r = api('POST', f'/intereses/{nro_tarjeta}/ordenes-pago', {'modulos': [modulo], 'cuotas': 1, 'primer_vencimiento': '2030-01-10'}, vendedor)
    assert s == 201, f'orden: {s} {r}'
    nro = r['orden']['nro_orden']
    s, r = api('POST', f'/ordenes-pago/{nro}/cuotas/1/comprobante', {'nro_metodo': metodo, 'archivo': PNG, 'remitente': 'Prueba'}, vendedor)
    assert s == 201, f'comprobante: {s} {r}'
    return nro


def orden(admin, nro_tarjeta, nro_orden):
    _, r = api('GET', f'/intereses/{nro_tarjeta}', token=admin)
    return next(o for o in r['interes']['ordenes_pago'] if o['nro_orden'] == nro_orden)


def fin(titulo):
    print(f'\n{titulo}: {total - len(fallas)}/{total} aprobadas' + (f'; FALLAN: {", ".join(fallas)}' if fallas else '; TODO OK'))
    sys.exit(1 if fallas else 0)
