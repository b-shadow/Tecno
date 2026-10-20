"""Regresion del rechazo y reenvio de comprobantes. SOLO instancia local de QA,
previamente poblada por verificar_correcciones.py. Crea datos ficticios.
Uso: python scripts/verificar_reenvio_comprobante.py http://localhost:18001/api
"""
import base64
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = sys.argv[1].rstrip('/')
assert urllib.parse.urlparse(BASE).hostname in ('localhost', '127.0.0.1'), 'Solo QA local'
checks = 0

def call(method, path, body=None, token=None, expected=200):
    global checks
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    if token: headers['Authorization'] = 'Bearer '+token
    req = urllib.request.Request(BASE+path, method=method, headers=headers,
                                 data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req, timeout=30) as response:
        assert response.status == expected, path
        data = json.loads(response.read())
    checks += 1
    return data

def login(correo, password):
    return call('POST', '/login', {'correo': correo, 'password': password})

admin = login('admin@crm-educativo.local', 'Admin12345')['token']
suffix = str(int(time.time()))
email = 'reenvio.'+suffix+'@example.invalid'
call('POST', '/registro-interes', {'nombre': 'Reenvio', 'apellido': 'Comprobante QA', 'documento': 'QA-'+suffix,
    'correo': email, 'telefono': '00008888', 'profesion': 'Pruebas', 'ubicacion': 'QA aislado', 'modulo_id': 'ia-aplicada-m1'}, expected=201)
call('POST', '/intereses/distribuir', {}, admin)
interest = next(i for i in call('GET', '/intereses', token=admin)['intereses'] if i['prospecto']['correo'] == email)
seller = None
for correo, clave in [('vendedor.demo@crm-educativo.local','Vendedor12345'), ('vendedor.b@test.local','Clave12345')]:
    account = login(correo, clave)
    if account['usuario']['id'] == interest['vendedor_id']: seller = account['token']
assert seller
order = call('POST', '/intereses/'+str(interest['id'])+'/ordenes-pago', {'modulos': ['ia-aplicada-m1'], 'descuentos': []}, seller, 201)['orden']
payment = order['pago']['id']
for n in [1,2]:
    image = '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"><rect width="400" height="200" fill="#e0f2fe"/><text x="20" y="80" font-size="22">COMPROBANTE QA '+str(n)+'</text><text x="20" y="120">Sin validez bancaria</text></svg>'
    call('POST', '/comprobantes', {'pago_id': payment, 'archivo': 'data:image/svg+xml;base64,'+base64.b64encode(image.encode()).decode(),
         'nombre_archivo': f'qa-intento-{n}.svg', 'mime':'image/svg+xml', 'remitente': 'QA ficticio', 'observacion': 'Intento '+str(n)}, seller, 201)
    call('PATCH', '/pagos/'+str(payment)+'/rechazar', {'observacion': 'QA: enviar comprobante corregido, intento '+str(n)}, admin)
data = call('GET', '/pagos/'+str(payment), token=admin)['pago']
assert data['estado'] == 'Pago rechazado'
assert len(data['comprobantes']) == 2
assert max(data['comprobantes'], key=lambda c:c['id'])['nombre_archivo'] == 'qa-intento-2.svg'
print(checks+3, 'comprobaciones de reenvio aprobadas; interes QA:',interest['id'],'pago:',payment)
print('Abrir agenda?interes='+str(interest['id'])+' para verificar carga habilitada y ultimo comprobante.')
