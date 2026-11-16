"""Seguridad de la API que no cubren verificar_p2.py ni verificar_fase_a.py: barrido de rutas por rol, comprobante
ajeno, doble aprobación, cuota aprobada que no se rechaza, porcentaje fuera de rango y cierre de sesión.
Solo contra una base QA local: crea un prospecto, una orden y un comprobante ficticios.
"""
from qa_comun import api, caso, fin, login, nuevo_interes, orden_con_comprobante, orden

admin, v1, v2 = login('admin'), login('v1'), login('v2')

# Rutas solo de administración: sin sesión 401, vendedor 403, administrador 200
for ruta in ['/usuarios', '/matriz', '/bitacora', '/bitacora/resumen', '/exportaciones']:
    s0, _ = api('GET', ruta)
    s1, _ = api('GET', ruta, token=v1)
    s2, _ = api('GET', ruta, token=admin)
    caso(f'{ruta}: sin sesión 401, vendedor 403, administrador 200', (s0, s1, s2) == (401, 403, 200), (s0, s1, s2))

doc, nro_tarjeta, modulo = nuevo_interes(admin)
nro = orden_con_comprobante(v1, doc, nro_tarjeta, modulo)
comprobante = orden(admin, nro_tarjeta, nro)['pago']['comprobantes'][0]['nro_comprobante']
s1, _ = api('GET', f'/comprobantes/{comprobante}', token=v1)
s2, _ = api('GET', f'/comprobantes/{comprobante}', token=v2)
caso('el comprobante lo ve su vendedor (200) y no otro vendedor (403)', (s1, s2) == (200, 403), (s1, s2))

s, r = api('PATCH', f'/ordenes-pago/{nro}/cuotas/1/aprobar', {}, admin)
caso('administración aprueba la cuota en revisión', s == 200, r)
s, r = api('PATCH', f'/ordenes-pago/{nro}/cuotas/1/aprobar', {}, admin)
caso('aprobar dos veces la misma cuota se rechaza (422)', s == 422, (s, r))
s, r = api('PATCH', f'/ordenes-pago/{nro}/cuotas/1/rechazar', {'observacion': 'Intento tardío'}, admin)
caso('una cuota aprobada no se puede rechazar (422)', s == 422, (s, r))

for valor in [51, 'abc', None]:
    s, r = api('PUT', '/configuracion/comision', {'porcentaje': valor}, admin)
    caso(f'porcentaje de comisión inválido ({valor!r}) -> 422 en español', s == 422 and 'porcentaje' in r.get('errores', {}), (s, r))

sesion = login('v1')
s1, _ = api('POST', '/logout', {}, sesion)
s2, _ = api('GET', '/me', token=sesion)
caso('cerrar sesión revoca el token', (s1, s2) == (200, 401), (s1, s2))

fin('SEGURIDAD')
