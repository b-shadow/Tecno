"""Auditoría funcional de lo que no cubren verificar_p2.py ni verificar_fase_a.py: registro público, actividades
(permisos, doble cierre, concurrencia y hora de Bolivia), seguimiento cerrado, CSV con formato difícil, sesiones al
cambiar o restablecer la clave, notificaciones, órdenes simultáneas y límite de intentos de login.
Solo contra una base QA local: crea datos ficticios. Deja el límite de login de esa IP lleno durante un minuto.
"""
import concurrent.futures

from qa_comun import V1, api, caso, fin, login, nuevo_interes, unico

admin, coord, v1, v2 = login('admin'), login('coord'), login('v1'), login('v2')

# --- Registro público
u = unico()
persona = {'documento': f'AU{u}', 'nombre': 'Auditoria', 'apellido': 'Publica', 'correo': f'au.{u}@example.invalid', 'telefono': '71234567'}
modulo = api('GET', '/catalogo')[1]['programas'][0]['modulos'][0]['codigo']
s, r = api('POST', '/registro-interes', {**persona, 'modulo_codigo': modulo})
caso('el registro público no expone datos internos', s == 201 and set(r) <= {'mensaje', 'detalle', 'nuevo_prospecto'}, r)
api('POST', '/registro-interes', {**persona, 'nombre': 'Sobrescrito', 'modulo_codigo': modulo})
_, r = api('GET', f'/intereses?buscar=AU{u}', token=admin)
caso('un registro repetido no sobrescribe el contacto existente', r['intereses'] and r['intereses'][0]['prospecto']['nombre'] == 'Auditoria', r['intereses'][:1])
s, r = api('POST', '/registro-interes', {**persona, 'correo': f'otro.{u}@example.invalid', 'modulo_codigo': modulo})
caso('el mismo carnet con otro correo se rechaza (422)', s == 422, (s, r))
for _ in range(25):  # cada página vista suma una visita: no debe gastar el límite propio del registro (20/min)
    api('POST', '/visitas', {'ruta': '/anuncios'})
v = unico()
s, r = api('POST', '/registro-interes', {**persona, 'documento': f'AU{v}', 'correo': f'au.{v}@example.invalid', 'modulo_codigo': modulo})
caso('navegar muchas páginas no bloquea el registro público (límites separados)', s == 201, (s, r))

# --- Actividades: dueño, hora de Bolivia, permisos, doble cierre y concurrencia
doc, tarjeta, _ = nuevo_interes(admin, V1)
s, r = api('POST', f'/intereses/{tarjeta}/recordatorios', {'fecha_programada': '2026-12-20T10:00', 'descripcion': 'Llamada de seguimiento'}, coord)
rec = r['recordatorio']
caso('10:00 de Bolivia se guarda como 14:00 UTC', rec['fecha_programada'].startswith('2026-12-20T14:00'), rec['fecha_programada'])
caso('la actividad que crea coordinación es del vendedor de la tarjeta', rec['usuario_correo'] == V1, rec)
s, _ = api('POST', f'/intereses/{tarjeta}/recordatorios', {'fecha_programada': '2026-12-21T10:00', 'descripcion': 'Ajena'}, v2)
caso('otro vendedor no agenda sobre una tarjeta ajena (403)', s == 403, s)
n = rec['nro_recordatorio']
codigos = [api('PATCH', f'/recordatorios/{n}/completar', {'resultado': 'No autorizado'}, v2)[0], api('PATCH', f'/recordatorios/{n}/cancelar', {}, v2)[0]]
caso('otro vendedor no completa ni cancela la actividad (403)', codigos == [403, 403], codigos)
s, _ = api('PATCH', f'/recordatorios/{n}/completar', {'resultado': 'Realizada'}, v1)
caso('el dueño la completa', s == 200, s)
codigos = [api('PATCH', f'/recordatorios/{n}/completar', {'resultado': 'Otra vez'}, v1)[0], api('PATCH', f'/recordatorios/{n}/cancelar', {}, v1)[0]]
caso('una actividad realizada no se completa ni cancela de nuevo (422)', codigos == [422, 422], codigos)
n2 = api('POST', f'/intereses/{tarjeta}/recordatorios', {'fecha_programada': '2026-12-22T10:00', 'descripcion': 'Para cancelar'}, v1)[1]['recordatorio']['nro_recordatorio']
api('PATCH', f'/recordatorios/{n2}/cancelar', {}, v1)
s, _ = api('PATCH', f'/recordatorios/{n2}/completar', {'resultado': 'Reactivar'}, v1)
caso('una actividad cancelada no se reactiva (422)', s == 422, s)
n3 = api('POST', f'/intereses/{tarjeta}/recordatorios', {'fecha_programada': '2026-12-23T10:00', 'descripcion': 'Doble clic'}, v1)[1]['recordatorio']['nro_recordatorio']
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    codigos = sorted(f.result()[0] for f in [pool.submit(api, 'PATCH', f'/recordatorios/{n3}/completar', {'resultado': 'Doble'}, v1) for _ in range(2)])
caso('completar dos veces a la vez produce un solo cumplimiento', codigos == [200, 422], codigos)

# --- Seguimiento cerrado: un registro repetido no lo reabre
motivo = next(m['nombre'] for m in api('GET', '/motivos', token=admin)[1]['motivos'] if m['nombre'] != 'Sin clasificar (web)')
_, r = api('GET', f'/intereses/{tarjeta}', token=v1)
p = r['interes']['prospecto']
s, r = api('PATCH', f'/intereses/{tarjeta}/estado', {'estado': 'Perdido', 'motivo_perdida': motivo}, v1)
caso('la tarjeta pasa a Perdido con motivo', s == 200, (s, r))
api('POST', '/registro-interes', {'documento': p['documento'], 'nombre': p['nombre'], 'apellido': p['apellido'], 'correo': p['correo'],
                                  'telefono': p['telefono'], 'modulo_codigo': r['interes']['modulo_codigo'] if 'interes' in r else modulo})
caso('un registro repetido no reabre una tarjeta perdida', api('GET', f'/intereses/{tarjeta}', token=admin)[1]['interes']['estado'] == 'Perdido', tarjeta)

# --- CSV exportado desde Excel: BOM, campos entre comillas con tildes y fin de línea CRLF
c = unico()
CRLF = chr(13) + chr(10)
csv = chr(0xFEFF) + 'documento,nombre,apellido,telefono,correo,origen' + CRLF + f'CSV{c},"María José","Pérez Rojas",71234567,csv.{c}@example.invalid,Feria' + CRLF
s, r = api('POST', '/prospectos/importar', {'csv': csv}, coord)
caso('CSV con BOM, comillas, tildes y CRLF', s == 200 and r.get('creados') == 1, (s, r))
_, r = api('GET', f'/prospectos?buscar=CSV{c}', token=admin)
filas = r['prospectos']['data'] if isinstance(r.get('prospectos'), dict) else r.get('prospectos', [])
caso('el CSV conserva las tildes y quita las comillas', any(x['nombre'] == 'María José' and x['apellido'] == 'Pérez Rojas' for x in filas), filas[:1])

# --- Sesiones: cambiar, restablecer y desactivar revocan los tokens
correo = f'sesion.{unico()}@example.invalid'
usuario = {'nombre': 'Temporal', 'apellido': 'Sesion', 'correo': correo, 'password': 'QaClave12345', 'rol': 'vendedor', 'estado': 'activo',
           'fecha_inicio': '2026-01-01', 'fecha_fin': '2030-12-31'}
api('POST', '/usuarios', usuario, admin)
t1, t2 = login(correo, 'QaClave12345'), login(correo, 'QaClave12345')
s, _ = api('PUT', '/perfil/password', {'password_actual': 'mala', 'password': 'OtraClave123', 'password_confirmation': 'OtraClave123'}, t1)
caso('cambiar la clave con la actual errada -> 422', s == 422, s)
s, _ = api('PUT', '/perfil/password', {'password_actual': 'QaClave12345', 'password': 'sololetras', 'password_confirmation': 'sololetras'}, t1)
caso('clave nueva sin números -> 422', s == 422, s)
s, _ = api('PUT', '/perfil/password', {'password_actual': 'QaClave12345', 'password': 'OtraClave123', 'password_confirmation': 'OtraClave123'}, t1)
caso('cambiar la clave cierra las otras sesiones y conserva la actual', (s, api('GET', '/me', token=t1)[0], api('GET', '/me', token=t2)[0]) == (200, 200, 401))
s, _ = api('PUT', f'/usuarios/{correo}', {**usuario, 'password': 'ResetAdmin123'}, admin)
caso('si administración restablece la clave, la sesión se cierra', s == 200 and api('GET', '/me', token=t1)[0] == 401, s)
t3 = login(correo, 'ResetAdmin123')
api('PATCH', f'/usuarios/{correo}/estado', {'estado': 'inactivo'}, admin)
caso('desactivar la cuenta cierra la sesión y bloquea el login (403)',
     (api('GET', '/me', token=t3)[0], api('POST', '/login', {'correo': correo, 'password': 'ResetAdmin123'})[0]) == (401, 403))

# --- Notificaciones
s, _ = api('POST', '/notificaciones', {'destinatario': p['correo'], 'tipo': 'Seguimiento', 'mensaje': 'Mensaje de prueba'}, v2)
caso('un vendedor no escribe a un prospecto ajeno (403)', s == 403, s)
s, _ = api('POST', '/notificaciones', {'destinatario': p['correo'], 'tipo': 'Seguimiento', 'mensaje': 'Mensaje de prueba'}, v1)
caso('el vendedor escribe a un prospecto de su cartera (201)', s == 201, s)
s, r = api('POST', '/notificaciones', {'tipo': 'Sin destino', 'mensaje': 'Prueba'}, coord)
caso('notificación sin destinatario -> 422 en español', s == 422 and 'destinatario' in r.get('errores', {}), (s, r))

# --- Dos órdenes a la vez sobre la misma tarjeta: solo una
doc2, tarjeta2, modulo2 = nuevo_interes(admin, V1)
cuerpo = {'modulos': [modulo2], 'cuotas': 1, 'primer_vencimiento': '2030-01-10'}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    codigos = sorted(f.result()[0] for f in [pool.submit(api, 'POST', f'/intereses/{tarjeta2}/ordenes-pago', cuerpo, v1) for _ in range(2)])
caso('dos órdenes simultáneas no duplican la venta', codigos == [201, 422], codigos)

# --- Límite de intentos de login (al final: deja la ventana de esta IP ocupada un minuto)
falso = f'limite.{unico()}@example.invalid'
codigos = [api('POST', '/login', {'correo': falso, 'password': 'incorrecta'})[0] for _ in range(11)]
caso('tras 10 intentos fallidos el login responde 429', codigos[:10] == [422] * 10 and codigos[10] == 429, codigos)

fin('AUDITORÍA')
