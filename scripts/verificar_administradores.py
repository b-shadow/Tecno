"""Regresion de concurrencia del ultimo administrador. Solo BD QA local."""
import concurrent.futures
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

base = sys.argv[1].rstrip('/')
assert urllib.parse.urlparse(base).hostname in ('localhost', '127.0.0.1'), 'Solo QA local'

def call(method, path, body=None, token=None):
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    if token: headers['Authorization'] = 'Bearer '+token
    request = urllib.request.Request(base+path, method=method, headers=headers,
        data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())

def login(email, password):
    code, data = call('POST', '/login', {'correo': email, 'password': password})
    assert code == 200
    return data

admin = login('admin@crm-educativo.local', 'Admin12345')
token = admin['token']
code, extra = call('POST', '/usuarios', {'nombre': 'Admin', 'apellido': 'Concurrencia QA',
    'correo': 'admin.race.'+str(time.time_ns())+'@example.invalid', 'rol': 'administrador',
    'estado': 'activo', 'password': 'QaAdmin12345'}, token)
assert code == 201
other = login(extra['usuario']['correo'], 'QaAdmin12345')
pairs = [(admin['usuario']['id'], token), (other['usuario']['id'], other['token'])]
with concurrent.futures.ThreadPoolExecutor(2) as pool:
    codes = list(pool.map(lambda pair: call('PATCH', f'/usuarios/{pair[0]}/estado', {'estado':'inactivo'}, pair[1])[0], pairs))
assert sorted(codes) == [200, 422], codes
print('OK dos bajas concurrentes conservan un administrador activo')
remaining = next(t for _, t in pairs if call('GET', '/me', token=t)[0] == 200)
code, data = call('GET', '/usuarios', token=remaining)
assert code == 200
assert sum(u['rol']=='administrador' and u['estado']=='activo' for u in data['usuarios']) == 1
assert call('PATCH', f'/usuarios/{admin["usuario"]["id"]}/estado', {'estado':'activo'}, remaining)[0] == 200
restored = login('admin@crm-educativo.local', 'Admin12345')['token']
assert call('PATCH', f'/usuarios/{other["usuario"]["id"]}/estado', {'estado':'inactivo'}, restored)[0] == 200
assert call('PATCH', f'/usuarios/{admin["usuario"]["id"]}/estado', {'estado':'inactivo'}, restored)[0] == 422
print('OK administrador inicial restaurado y ultima baja individual impedida')
