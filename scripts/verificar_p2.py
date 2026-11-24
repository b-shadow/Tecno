"""Prueba de la API del P2 contra una base de DESARROLLO sembrada (php artisan db:seed). Nunca contra producción.

Recorre los requisitos del enunciado y los CU: bitácora de login, menú dinámico por rol, matriz de acceso,
RF1.2/RF1.3, Kanban (motivo obligatorio, conversión con validación), métodos de pago, plan de cuotas,
pasarela simulada, contador de visitas, búsqueda y validación en español.

Uso: python scripts/verificar_p2.py [http://localhost:8001]
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8001').rstrip('/') + '/api'
assert any(h in BASE for h in ('localhost', '127.0.0.1')), 'Solo contra una base local de prueba'
fallas = []


def api(metodo, ruta, cuerpo=None, token=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(BASE + ruta, data=datos, method=metodo, headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


def caso(nombre, condicion, detalle=''):
    print(('OK   ' if condicion else 'FALLA') + ' ' + nombre + ('' if condicion else f'  -> {detalle}'))
    if not condicion:
        fallas.append(nombre)


def login(correo, clave):
    s, r = api('POST', '/login', {'correo': correo, 'password': clave})
    return r.get('token'), r


# --- Enunciado 4: bitácora de login fallido / exitoso
s, r = api('POST', '/login', {'correo': 'admin@crm-educativo.local', 'password': 'mala-clave-1'})
caso('login fallido rechazado con mensaje en español', s == 422 and 'incorrectos' in r.get('mensaje', ''), r)
s, r = api('POST', '/login', {'correo': 'no-es-correo', 'password': ''})
caso('validación en español', s == 422 and 'obligatorio' in json.dumps(r, ensure_ascii=False), r)

admin, ra = login('admin@crm-educativo.local', 'Admin12345')
coord, rc = login('coord@test.local', 'Clave12345')
vend, rv = login('vendedor.demo@crm-educativo.local', 'Vendedor12345')
caso('login de los tres roles', all([admin, coord, vend]))

# --- Enunciado 1/2: menú dinámico desde la BD, distinto por rol
menu = lambda r: [m['codigo'] for m in r.get('menu', [])]
caso('menú admin incluye matriz y bitácora', {'matriz', 'bitacora', 'usuarios'} <= set(menu(ra)), menu(ra))
caso('menú vendedor sin usuarios ni validación', not ({'usuarios', 'validacion-pagos', 'interesados'} & set(menu(rv))) and 'embudo' in menu(rv), menu(rv))
caso('menú coordinador con asignación y sin matriz', 'interesados' in menu(rc) and 'matriz' not in menu(rc), menu(rc))

# --- Enunciado 4: matriz aplicada en el servidor
s, _ = api('GET', '/usuarios', token=vend)
caso('vendedor no puede listar usuarios (403)', s == 403, s)
s, r = api('GET', '/bitacora?evento=acceso_denegado', token=admin)
caso('el acceso denegado queda en la bitácora', s == 200 and r['registros']['total'] >= 1, r.get('registros', {}).get('total'))
s, r = api('GET', '/bitacora?evento=login_fallido', token=admin)
caso('el login fallido queda en la bitácora con IP', s == 200 and r['registros']['data'] and r['registros']['data'][0]['ip'], s)

# Cambiar la matriz cambia el menú
api('PUT', '/matriz', {'rol': 'vendedor', 'recurso_codigo': 'motivos', 'acceso': 'lectura'}, admin)
s, r = api('GET', '/me', token=vend)
caso('al dar un permiso aparece en el menú del rol', 'motivos' in menu(r), menu(r))
api('PUT', '/matriz', {'rol': 'vendedor', 'recurso_codigo': 'motivos', 'acceso': None}, admin)
s, r = api('PUT', '/matriz', {'rol': 'administrador', 'recurso_codigo': 'matriz', 'acceso': 'lectura'}, admin)
caso('el admin no puede quitarse la matriz', s == 422, s)

# --- RF1.2 / RF1.3: alcance por rol
s, r = api('GET', '/intereses', token=vend)
caso('RF1.2 vendedor ve solo su cartera', s == 200 and r['intereses'] and all(i['vendedor_correo'] == 'vendedor.demo@crm-educativo.local' for i in r['intereses']), s)
s, r = api('GET', '/intereses', token=coord)
programas = {'Desarrollo de Aplicaciones Web', 'Inteligencia Artificial Aplicada', 'Análisis de Datos y Business Intelligence'}
caso('RF1.3 coordinador ve solo sus programas', s == 200 and all(i['programa_nombre'] in programas for i in r['intereses']), {i['programa_nombre'] for i in r.get('intereses', [])})
caso('RF3.2 columnas del Kanban', r.get('estados') == ['Nuevo', 'En Contacto', 'Seguimiento', 'Promesa de Pago', 'Convertido', 'Perdido'], r.get('estados'))

s, r = api('GET', '/intereses', token=vend)
tarjetas = r['intereses']
abierta = next(t for t in tarjetas if t['estado'] in ('Nuevo', 'En Contacto', 'Seguimiento'))

# --- CU5 / RF3.3: perder exige motivo
s, r = api('PATCH', f"/intereses/{abierta['nro_tarjeta']}/estado", {'estado': 'Perdido'}, vend)
caso('Perdido sin motivo se rechaza', s == 422 and 'motivo' in json.dumps(r, ensure_ascii=False).lower(), r)

# --- CU6 / RF3.4: convertir sin pago se rechaza con lo que falta
s, r = api('PATCH', f"/intereses/{abierta['nro_tarjeta']}/estado", {'estado': 'Convertido'}, vend)
caso('Convertido sin pago aprobado se rechaza', s == 422 and r.get('faltantes'), r)

# Datos completos del prospecto (RF3.4) para que la conversión dependa solo del pago: así el script se puede repetir.
p = abierta['prospecto']
s, r = api('PUT', f"/prospectos/{p['documento']}", {k: p.get(k) for k in ('nombre', 'apellido', 'correo', 'telefono', 'origen')}
           | {'profesion': p.get('profesion') or 'Contador', 'ubicacion': p.get('ubicacion') or 'Santa Cruz'}, vend)
caso('el vendedor completa los datos del prospecto', s == 200, r)

# --- Enunciado 10: métodos de pago, plan de cuotas y pasarela simulada
doc = abierta['documento']
s, r = api('POST', f'/prospectos/{doc}/metodos-pago', {'tipo': 'Tarjeta', 'titular': 'Prueba Demo', 'numero': '4111 1111 1111 1112', 'vencimiento': '12/30'}, vend)
caso('tarjeta con número inválido rechazada', s == 422, r)
s, r = api('POST', f'/prospectos/{doc}/metodos-pago', {'tipo': 'Tarjeta', 'titular': 'Prueba Demo', 'numero': '4111 1111 1111 1111', 'vencimiento': '12/30'}, vend)
metodo = r.get('metodo', {})
caso('tarjeta registrada guarda solo marca y últimos 4', s == 201 and metodo.get('ultimos_digitos') == '1111' and metodo.get('marca') == 'Visa' and 'numero' not in metodo, r)

s, r = api('POST', f"/intereses/{abierta['nro_tarjeta']}/ordenes-pago", {'modulos': [abierta['modulo_codigo']], 'cuotas': 3, 'primer_vencimiento': '2030-01-10'}, vend)
orden = r.get('orden', {})
caso('orden con plan de 3 cuotas', s == 201 and len(orden.get('cuotas', [])) == 3 and abs(sum(float(c['monto']) for c in orden['cuotas']) - float(orden['total'])) < 0.01, r)

s, r = api('POST', f"/intereses/{abierta['nro_tarjeta']}/ordenes-pago", {'modulos': [abierta['modulo_codigo']], 'cuotas': 1, 'primer_vencimiento': '2030-01-10'}, vend)
caso('segunda orden con otra abierta se rechaza (venta duplicada)', s == 422, r)

nro = orden.get('nro_orden')
s, r = api('POST', f"/ordenes-pago/{nro}/cuotas/1/pagar", {'nro_metodo': metodo.get('nro_metodo')}, vend)
caso('pasarela simulada cobra la 1.ª cuota', s == 200 and r.get('transaccion', '').startswith('SIM-'), r)
s, r = api('GET', f"/intereses/{abierta['nro_tarjeta']}", token=vend)
caso('el cobro con tarjeta queda En revisión (no se autoaprueba)', r.get('interes', {}).get('estado') == 'Promesa de Pago', r.get('interes', {}).get('estado'))
s, r = api('PATCH', f"/ordenes-pago/{nro}/cuotas/1/aprobar", {}, vend)
caso('el vendedor no aprueba su propio pago', s == 403, (s, r))
s, r = api('PATCH', f"/ordenes-pago/{nro}/cuotas/1/aprobar", {}, admin)
caso('administración aprueba la cuota en revisión', s == 200, r)
s, r = api('GET', f"/intereses/{abierta['nro_tarjeta']}", token=vend)
caso('1.ª cuota aprobada + datos completos = Convertido', r.get('interes', {}).get('estado') == 'Convertido', r.get('interes', {}).get('estado'))
s, r = api('GET', '/cuotas?estado=Pendiente de pago'.replace(' ', '%20'), token=coord)
caso('coordinación ve las cuotas pendientes', s == 200, s)

# --- Enunciado 7: contador de visitas persistente (trigger)
s1, r1 = api('POST', '/visitas', {'ruta': '/anuncios'})
s2, r2 = api('POST', '/visitas', {'ruta': '/anuncios'})
caso('el contador de visitas sube en 1', s2 == 200 and r2['visitas'] == r1['visitas'] + 1, (r1, r2))

# --- Enunciado 9: búsqueda global
s, r = api('GET', '/buscar?q=python')
caso('búsqueda pública encuentra módulos', s == 200 and any(x['tipo'] == 'Módulo' for x in r['resultados']), r)
s, r = api('GET', '/buscar?q=' + urllib.parse.quote(abierta['prospecto']['nombre'][:4]), token=vend)
caso('búsqueda interna encuentra prospectos de la cartera', s == 200 and any(x['tipo'] == 'Prospecto' for x in r['resultados']), r)

# --- RF2.1 importación CSV con origen
ci_csv = str(int(time.time()))[-8:]  # único en cada corrida: el script se puede repetir sobre la misma base
csv = f'documento,nombre,apellido,telefono,correo,origen\n{ci_csv},Elena,Prueba Csv,71234567,elena.{ci_csv}@correo-demo.bo,Feria\n'
s, r = api('POST', '/prospectos/importar', {'csv': csv}, coord)
caso('importación CSV', s == 200 and r.get('creados') == 1, r)
s, r = api('POST', '/prospectos/importar', {'csv': csv}, coord)
caso('CSV duplicado se rechaza sin cargar nada', s == 422, r)
s, r = api('POST', '/prospectos/importar', {'csv': csv}, vend)
caso('el vendedor no importa prospectos', s == 403, s)

# CSV con la columna opcional modulo_codigo: el prospecto entra al Kanban sin vendedor, listo para el Round-Robin
s, r = api('GET', '/intereses', token=coord)
modulo_coord = r['intereses'][0]['modulo_codigo'] if s == 200 and r.get('intereses') else abierta['modulo_codigo']
ci_csv2 = str(int(ci_csv) + 1)
csv2 = f'documento,nombre,apellido,telefono,correo,origen,modulo_codigo\n{ci_csv2},Rosa,Prueba Kanban,71234568,rosa.{ci_csv2}@correo-demo.bo,Feria,{modulo_coord}\n'
s, r = api('POST', '/prospectos/importar', {'csv': csv2}, coord)
caso('CSV con módulo crea el interés', s == 200 and r.get('creados') == 1, r)
s, r = api('GET', f'/intereses?buscar={ci_csv2}', token=coord)
nueva = (r.get('intereses') or [{}])[0]
caso('el prospecto del CSV aparece en el embudo como Nuevo sin vendedor', nueva.get('estado') == 'Nuevo' and not nueva.get('vendedor_correo'), r)
s, r = api('POST', '/prospectos/importar', {'csv': csv2.replace(ci_csv2, str(int(ci_csv2) + 1)).replace(modulo_coord, 'NO-EXISTE')}, coord)
caso('CSV con módulo inexistente se rechaza', s == 422 and any(e.get('columna') == 'modulo_codigo' for e in r.get('errores', [])), r)

# --- RF2.3 Round-Robin
s, r = api('POST', '/intereses/distribuir', {}, coord)
caso('reparto Round-Robin', s == 200, r)

# --- Enunciado 8: dashboard con negocio y accesos
s, r = api('GET', '/dashboard', token=admin)
caso('dashboard con negocio y accesos (admin)', s == 200 and 'embudo' in r and 'accesos' in r, list(r))
s, r = api('GET', '/dashboard', token=coord)
caso('dashboard del coordinador sin logins', s == 200 and 'accesos' not in r, list(r))
s, r = api('GET', '/reportes/estadisticas', token=coord)
caso('estadísticas porcentuales', s == 200 and abs(sum(x['porcentaje'] for x in r['embudo']) - 100) < 1, r.get('embudo'))

print('\n' + ('TODO OK' if not fallas else f'{len(fallas)} FALLA(S): ' + ', '.join(fallas)))
sys.exit(1 if fallas else 0)
