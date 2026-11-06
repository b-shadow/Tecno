"""Pruebas de regresión Fase A (API, seguridad, A04 intereses, A05 fotos, A07 búsquedas ILIKE).
Solo contra base local de prueba. Uso: python scripts/verificar_fase_a.py [http://127.0.0.1:8001]
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8001').rstrip('/') + '/api'
assert any(h in BASE for h in ('localhost', '127.0.0.1')), 'Solo contra base local'

PNG_1PX = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a01cAAAAASUVORK5CYII='
fallas = []
total = 0


def api(metodo, ruta, cuerpo=None, token=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(
        BASE + ruta,
        data=datos,
        method=metodo,
        headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
    )
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


def caso(nombre, cond, detalle=''):
    global total
    total += 1
    print(('OK   ' if cond else 'FALLA') + ' ' + nombre + ('' if cond else f' -> {detalle}'))
    if not cond:
        fallas.append(nombre)


def login(correo, clave):
    s, r = api('POST', '/login', {'correo': correo, 'password': clave})
    assert s == 200 and r.get('token'), f'Login fallo para {correo}: {s} {r}'
    return r['token']


adm = login('admin@crm-educativo.local', 'Admin12345')
crd = login('coord@test.local', 'Clave12345')
vnd1 = login('vendedor.demo@crm-educativo.local', 'Vendedor12345')
vnd2 = login('vendedor2@crm-educativo.local', 'Vendedor12345')

# --- A04: crearInteres (POST /prospectos/{p}/intereses) ---
stamp = str(int(time.time()))[-7:]
ci = 'FA' + stamp
p_datos = {
    'documento': ci,
    'nombre': 'Luciano',
    'apellido': 'Fase A',
    'telefono': '71234567',
    'correo': f'luciano.{stamp}@correo-demo.bo',
    'origen': 'Web',
    'profesion': 'Analista',
    'ubicacion': 'Santa Cruz',
}
s, r = api('POST', '/prospectos', p_datos, adm)
caso('A04 alta prospecto sin interes', s == 201 and r['prospecto']['documento'] == ci, (s, r))

# Agregar interes valido (como admin)
s, r = api('POST', f'/prospectos/{ci}/intereses', {'modulo_codigo': 'ia-aplicada-m1'}, adm)
caso('A04 agregar interes valido -> 201', s == 201 and len(r.get('intereses', [])) == 1, (s, r))

# Duplicado debe rechazarse en espanol (422)
s, r = api('POST', f'/prospectos/{ci}/intereses', {'modulo_codigo': 'ia-aplicada-m1'}, adm)
caso('A04 interes duplicado rechazado -> 422', s == 422 and 'ya tiene' in json.dumps(r, ensure_ascii=False).lower(), (s, r))

# Modulo inexistente -> 422
s, r = api('POST', f'/prospectos/{ci}/intereses', {'modulo_codigo': 'NO-EXISTE-99'}, adm)
caso('A04 modulo inexistente rechazado -> 422', s == 422, (s, r))

# Sin modulo ni programa -> 422 en espanol
s, r = api('POST', f'/prospectos/{ci}/intereses', {}, adm)
caso('A04 datos vacios rechazados en espanol -> 422', s == 422 and 'errores' in r, (s, r))

# Prospecto inexistente -> 404
s, _ = api('POST', '/prospectos/NOEXISTECI999/intereses', {'modulo_codigo': 'ia-aplicada-m1'}, adm)
caso('A04 prospecto inexistente -> 404', s == 404, s)

# Sin sesion -> 401
s, _ = api('POST', f'/prospectos/{ci}/intereses', {'modulo_codigo': 'ia-aplicada-m2'})
caso('A04 sin sesion -> 401', s == 401, s)

# Vendedor fuera de cartera -> 403
s, _ = api('POST', f'/prospectos/{ci}/intereses', {'modulo_codigo': 'ia-aplicada-m2'}, vnd1)
caso('A04 vendedor fuera de cartera -> 403', s == 403, s)

# Asignar tarjeta de ci a vnd1 y verificar que vnd1 SI puede agregar otro modulo, pero vnd2 NO
nro_t = api('GET', f'/intereses?buscar={ci}', token=adm)[1]['intereses'][0]['nro_tarjeta']
api('PATCH', f'/intereses/{nro_t}/asignar', {'vendedor_correo': 'vendedor.demo@crm-educativo.local'}, token=crd)
s, r = api('POST', f'/prospectos/{ci}/intereses', {'modulo_codigo': 'ia-aplicada-m2'}, token=vnd1)
caso('A04 vendedor autorizado agrega interes en su cartera -> 201', s == 201, (s, r))
s, _ = api('POST', f'/prospectos/{ci}/intereses', {'modulo_codigo': 'ia-aplicada-m3'}, token=vnd2)
caso('A04 otro vendedor (IDOR) -> 403', s == 403, s)

# --- A05: eliminacion de fotografia (DELETE /usuarios/{u}/foto) ---
u_correo = f'foto.{stamp}@crm-educativo.local'
u_payload = {
    'nombre': 'Elena',
    'apellido': 'FotoTest',
    'correo': u_correo,
    'telefono': '71112233',
    'password': 'Clave12345',
    'rol': 'vendedor',
    'estado': 'activo',
    'fecha_inicio': '2026-01-01',
    'fecha_fin': '2027-12-31',
    'foto': PNG_1PX,
}
s, r = api('POST', '/usuarios', u_payload, adm)
caso('A05 crear usuario con foto', s == 201 and bool(r['usuario']['foto_url']), (s, r))

# Vendedor y coordinador no pueden eliminar foto -> 403
s, _ = api('DELETE', f'/usuarios/{urllib.parse.quote(u_correo)}/foto', token=vnd1)
caso('A05 vendedor no elimina foto -> 403', s == 403, s)
s, _ = api('DELETE', f'/usuarios/{urllib.parse.quote(u_correo)}/foto', token=crd)
caso('A05 coordinador no elimina foto -> 403', s == 403, s)
s, _ = api('DELETE', f'/usuarios/{urllib.parse.quote(u_correo)}/foto')
caso('A05 sin sesion no elimina foto -> 401', s == 401, s)

# Administrador elimina foto -> 200 y foto_url queda null
s, r = api('DELETE', f'/usuarios/{urllib.parse.quote(u_correo)}/foto', token=adm)
caso('A05 admin elimina foto -> 200', s == 200, (s, r))
s, r = api('GET', f'/usuarios?buscar={urllib.parse.quote(u_correo)}', token=adm)
u_leido = (r.get('usuarios') or [{}])[0]
caso('A05 foto queda null en BD tras eliminar', u_leido.get('foto_url') is None and u_leido.get('foto') is None, u_leido)

# Re-cargar foto nueva tras eliminar
s, r = api('PUT', f'/usuarios/{urllib.parse.quote(u_correo)}', {**u_payload, 'password': ''}, adm)
caso('A05 recargar nueva foto tras eliminar', s == 200 and bool(r['usuario']['foto_url']), (s, r))
# Dejar usuario temporal inactivo
api('PATCH', f'/usuarios/{urllib.parse.quote(u_correo)}/estado', {'estado': 'inactivo'}, adm)

# --- A07: filtros ILIKE con caracteres especiales (%, _, \, ', acentos, largo, SQLi) ---
ci_pct = 'PCT' + stamp
s, r_pct = api('POST', '/prospectos', {
    'documento': ci_pct,
    'nombre': 'Prueba Literal',
    'apellido': "O'Connor Test",
    'telefono': '79998877',
    'correo': f'pct_{stamp}@correo-demo.bo',
    'origen': 'Feria',
    'modulo_codigo': 'ciberseguridad-m1',
}, adm)
caso('A07 crear prospecto con _ y apostrofo para prueba ILIKE', s == 201, (s, r_pct))

# Buscar "%" literal: NO debe devolver los 20 prospectos, solo [] porque ninguno contiene "%"
s, r = api('GET', '/prospectos?buscar=' + urllib.parse.quote('%'), token=adm)
docs_pct = [x['documento'] for x in r.get('prospectos', [])]
caso('A07 buscar "%" en prospectos es literal (no coincide con todos)', len(docs_pct) == 0, docs_pct)

# Buscar "_" literal en prospectos e intereses: solo debe devolver el prospecto con "_" en su correo (no todos)
s, r = api('GET', '/prospectos?buscar=' + urllib.parse.quote(f'pct_{stamp}'), token=adm)
docs_under = [x['documento'] for x in r.get('prospectos', [])]
caso('A07 buscar "pct_<id>" literal con "_" devuelve solo ese prospecto', docs_under == [ci_pct], docs_under)

s, r = api('GET', '/intereses?buscar=' + urllib.parse.quote("O'Connor"), token=adm)
docs_apo = [x['documento'] for x in r.get('intereses', [])]
caso('A07 buscar "O\'Connor" literal en intereses funciona', ci_pct in docs_apo and len(docs_apo) < 10, docs_apo)

# Buscar "_" solo en usuarios: solo debe coincidir si un usuario tiene "_" literal (en este caso ninguno o solo los de prueba)
s, r = api('GET', '/usuarios?buscar=_', token=adm)
caso('A07 buscar "_" en usuarios no coincide con todos', len(r.get('usuarios', [])) == 0, len(r.get('usuarios', [])))

# Buscar "\" y SQLi inofensiva y cadena larga en busqueda global y modulos
for label, term in [
    ('barra invertida', '\\'),
    ('acentos', 'Análisis'),
    ('vacio', ''),
    ('largo 200 chars', 'x' * 200),
    ('SQLi', "' OR 1=1 --"),
]:
    q = urllib.parse.quote(term)
    s1, _ = api('GET', f'/buscar?q={q}', token=adm)
    s2, _ = api('GET', f'/prospectos?buscar={q}', token=adm)
    s3, _ = api('GET', f'/intereses?buscar={q}', token=adm)
    s4, _ = api('GET', f'/bitacora?usuario={q}', token=adm)
    ok_largo = (s4 in (200, 422)) if label == 'largo 200 chars' else (s4 == 200)
    caso(f'A07 entrada "{label}" no genera 500', all(code == 200 for code in (s1, s2, s3)) and ok_largo, (s1, s2, s3, s4))

# Vendedor1 no ve el prospecto de ciberseguridad-m1 (sin asignar) al buscar "_" o "O'Connor"
s, r = api('GET', '/prospectos?buscar=' + urllib.parse.quote(f'pct_{stamp}'), token=vnd1)
caso('A07 vendedor1 no ve prospecto ajeno al buscar "_"', len(r.get('prospectos', [])) == 0, r.get('prospectos'))

# --- Seguridad negativa adicional (18 comprobaciones base) ---
seg_tests = [
    ('SEG sin token /usuarios -> 401', api('GET', '/usuarios')[0] == 401),
    ('SEG token invalido /me -> 401', api('GET', '/me', token='invalido')[0] == 401),
    ('SEG vnd PUT /matriz -> 403', api('PUT', '/matriz', {'rol': 'vendedor', 'recurso_codigo': 'usuarios', 'acceso': 'lectura'}, vnd1)[0] == 403),
    ('SEG vnd GET /bitacora -> 403', api('GET', '/bitacora', token=vnd1)[0] == 403),
    ('SEG crd GET /bitacora -> 403', api('GET', '/bitacora', token=crd)[0] == 403),
    ('SEG crd GET /usuarios -> 403', api('GET', '/usuarios', token=crd)[0] == 403),
    ('SEG crd PUT /configuracion/comision -> 403', api('PUT', '/configuracion/comision', {'porcentaje': 5}, crd)[0] == 403),
    ('SEG adm comision negativa -> 422', api('PUT', '/configuracion/comision', {'porcentaje': -5}, adm)[0] == 422),
    ('SEG vnd2 GET /intereses/1 (IDOR) -> 403', api('GET', '/intereses/1', token=vnd2)[0] == 403),
    ('SEG vnd2 GET metodos prospecto ajeno -> 403', api('GET', '/prospectos/6100000/metodos-pago', token=vnd2)[0] == 403),
    ('SEG interes inexistente -> 404', api('GET', '/intereses/999999', token=adm)[0] == 404),
    ('SEG cuotas -1 -> 422', api('POST', '/intereses/1/ordenes-pago', {'modulos': ['ciberseguridad-m1'], 'cuotas': -1, 'primer_vencimiento': '2030-01-01'}, vnd1)[0] == 422),
    ('SEG vencimiento pasado -> 422', api('POST', '/intereses/1/ordenes-pago', {'modulos': ['ciberseguridad-m1'], 'cuotas': 1, 'primer_vencimiento': '2020-01-01'}, vnd1)[0] == 422),
    ('SEG modulo inexistente orden -> 422', api('POST', '/intereses/1/ordenes-pago', {'modulos': ['fake'], 'cuotas': 1, 'primer_vencimiento': '2030-01-01'}, vnd1)[0] == 422),
    ('SEG tarjeta vencida -> 422', api('POST', '/prospectos/6100000/metodos-pago', {'tipo': 'Tarjeta', 'titular': 'Test', 'numero': '4111 1111 1111 1111', 'vencimiento': '01/20'}, vnd1)[0] == 422),
    ('SEG tipo reporte invalido -> 422', api('GET', '/reportes/listado?tipo=invalido', token=adm)[0] == 422),
    ('SEG buscar publico no filtra prospectos', not any(x['tipo'] == 'Prospecto' for x in api('GET', '/buscar?q=Camila')[1].get('resultados', []))),
]
for nombre, ok in seg_tests:
    caso(nombre, ok)

print(f'\nFASE A API: {total - len(fallas)}/{total} aprobadas; {len(fallas)} fallas.')
sys.exit(1 if fallas else 0)
