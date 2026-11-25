"""Rechazo y reenvío de un comprobante manual (lo que verificar_p2.py no recorre): la cuota y el Pago quedan
"Pago rechazado", el vendedor reenvía, vuelve a "En revision" con los dos comprobantes y al aprobar queda pagada.
Solo contra una base QA local: crea un prospecto, una orden y dos comprobantes ficticios.
"""
from qa_comun import PNG, api, caso, fin, login, nuevo_interes, orden_con_comprobante, orden

admin, v1 = login('admin'), login('v1')
doc, nro_tarjeta, modulo = nuevo_interes(admin)
nro = orden_con_comprobante(v1, doc, nro_tarjeta, modulo)

s, r = api('PATCH', f'/ordenes-pago/{nro}/cuotas/1/rechazar', {}, admin)
caso('rechazar exige observación (422 en español)', s == 422 and 'observacion' in r.get('errores', {}), (s, r))
s, r = api('PATCH', f'/ordenes-pago/{nro}/cuotas/1/rechazar', {'observacion': 'El monto no coincide'}, admin)
caso('administración rechaza el comprobante', s == 200, (s, r))
o = orden(admin, nro_tarjeta, nro)
caso('la 1.ª cuota y el Pago de la orden quedan "Pago rechazado"', o['cuotas'][0]['estado'] == 'Pago rechazado' and o['pago']['estado'] == 'Pago rechazado',
     (o['cuotas'][0]['estado'], o['pago']['estado']))
caso('la observación del rechazo queda en el Pago', o['pago']['observacion_validacion'] == 'El monto no coincide', o['pago'])

s, r = api('POST', f'/ordenes-pago/{nro}/cuotas/1/comprobante', {'archivo': PNG, 'remitente': 'Segundo intento'}, v1)
caso('el vendedor reenvía un comprobante nuevo', s == 201, (s, r))
o = orden(admin, nro_tarjeta, nro)
comprobantes = o['pago']['comprobantes']
caso('la cuota vuelve a "En revision" y conserva los dos comprobantes', o['cuotas'][0]['estado'] == 'En revision' and len(comprobantes) == 2,
     (o['cuotas'][0]['estado'], len(comprobantes)))
caso('el comprobante anterior queda rechazado y el nuevo en revisión',
     sorted(c['estado_revision'] for c in comprobantes) == ['En revision', 'Pago rechazado'], [c['estado_revision'] for c in comprobantes])
caso('el archivo nuevo tiene nombre legible ligado al dato', all(f'orden{nro}_cuota1' in c['nombre_archivo'] for c in comprobantes),
     [c['nombre_archivo'] for c in comprobantes])

s, r = api('PATCH', f'/ordenes-pago/{nro}/cuotas/1/aprobar', {}, admin)
o = orden(admin, nro_tarjeta, nro)
caso('al aprobar el reenvío la cuota y el Pago quedan "Pago aprobado"', s == 200 and o['cuotas'][0]['estado'] == o['pago']['estado'] == 'Pago aprobado',
     (s, o['cuotas'][0]['estado'], o['pago']['estado']))

fin('REENVÍO DE COMPROBANTE')
