"""Flujo de punta a punta de las correcciones de la clienta que no recorren verificar_p2.py ni verificar_fase_a.py:
registro por programa (una tarjeta por módulo), reparto que mantiene juntas las tarjetas de un prospecto, reasignación
con historial y actividades, comisión configurable, reporte por vendedor, matrícula y exportación sin duplicados.
Solo contra una base QA local: crea prospectos, pagos y comisiones ficticios (restaura el porcentaje de comisión).
"""
from qa_comun import PNG, V1, V2, api, caso, fin, login, unico

admin, coord, v1, v2 = login('admin'), login('coord'), login('v1'), login('v2')

# Un programa a cargo del coordinador, para que también él vea todo el recorrido.
_, r = api('GET', '/intereses', token=coord)
suyos = {i['programa_nombre'] for i in r['intereses']}
_, cat = api('GET', '/catalogo')
programa = next(p for p in cat['programas'] if p['nombre'] in suyos)

# --- Registro público: por programa completo, por módulo suelto y sin ninguno
u = unico()
persona = {'documento': f'CO{u}', 'nombre': 'Ana', 'apellido': 'Correcciones', 'correo': f'ana.{u}@example.invalid', 'telefono': '71234567'}
s, r = api('POST', '/registro-interes', {**persona, 'programa_codigo': programa['codigo']})
caso('registro por programa completo -> 201', s == 201, (s, r))
_, r = api('GET', f'/intereses?buscar=CO{u}', token=admin)
tarjetas = r['intereses']
caso(f'el programa crea una tarjeta por módulo ({len(programa["modulos"])})', len(tarjetas) == len(programa['modulos']), len(tarjetas))
caso('las tarjetas nuevas llegan sin vendedor', all(t['vendedor_correo'] is None for t in tarjetas), [t['vendedor_correo'] for t in tarjetas])
u2 = unico()
s, r = api('POST', '/registro-interes', {**persona, 'documento': f'CO{u2}', 'correo': f'beto.{u2}@example.invalid', 'nombre': 'Beto',
                                         'modulo_codigo': programa['modulos'][0]['codigo']})
caso('registro por módulo suelto -> 201', s == 201, (s, r))
s, r = api('POST', '/registro-interes', {**persona, 'documento': f'CO{unico()}', 'correo': f'caro.{unico()}@example.invalid'})
caso('registro sin módulo ni programa -> 422 en español', s == 422 and 'modulo_codigo' in r.get('errores', {}), (s, r))

_, r = api('GET', f'/intereses?buscar=CO{u}', token=v1)
caso('el vendedor no ve tarjetas sin asignar', r.get('intereses') == [], r)

# --- Reparto (Round-Robin): solo coordinación; las tarjetas de un mismo prospecto van al mismo vendedor
s, _ = api('POST', '/intereses/distribuir', {}, v1)
caso('el vendedor no reparte (403)', s == 403, s)
s, r = api('GET', '/vendedores', token=coord)
caso('coordinación lista los vendedores', s == 200 and {V1, V2} <= {x['correo'] for x in r['vendedores']}, (s, r))
s, _ = api('GET', '/usuarios', token=coord)
caso('coordinación no lista todos los usuarios (403)', s == 403, s)
s, r = api('POST', '/intereses/distribuir', {}, coord)
caso('coordinación reparte las tarjetas sin vendedor', s == 200 and r.get('asignados', 0) >= len(tarjetas), (s, r))
_, r = api('GET', f'/intereses?buscar=CO{u}', token=admin)
duenos = {t['vendedor_correo'] for t in r['intereses']}
caso('las tarjetas de un mismo prospecto quedan con un solo vendedor', len(duenos) == 1 and None not in duenos, duenos)

# --- Reasignación con historial y actividades
tarjeta = r['intereses'][0]['nro_tarjeta']
dueno = duenos.pop()
otro = V2 if dueno == V1 else V1
t_dueno, t_otro = (v1, v2) if dueno == V1 else (v2, v1)
s, r = api('POST', f'/intereses/{tarjeta}/interacciones', {'tipo': 'WhatsApp', 'descripcion': 'Primer contacto', 'fecha': '2020-01-01 10:00'}, t_dueno)
caso('la fecha del contacto la pone el servidor (ignora la enviada)', s == 201 and not r['interaccion']['fecha'].startswith('2020'), (s, r))
_, r = api('POST', f'/intereses/{tarjeta}/recordatorios', {'fecha_programada': '2030-01-10T10:00', 'descripcion': 'Llamar para cerrar'}, t_dueno)
hecha = r['recordatorio']['nro_recordatorio']
s, r = api('PATCH', f'/recordatorios/{hecha}/completar', {}, t_dueno)
caso('completar una actividad sin nota -> 422', s == 422, (s, r))
s, r = api('PATCH', f'/recordatorios/{hecha}/completar', {'resultado': 'Pidió la malla curricular'}, t_dueno)
caso('completar con nota -> 200', s == 200, (s, r))
_, r = api('POST', f'/intereses/{tarjeta}/recordatorios', {'fecha_programada': '2030-01-11T09:30', 'descripcion': 'Enviar la cotización'}, coord)
pendiente = r['recordatorio']['nro_recordatorio']
caso('una actividad creada por coordinación queda a nombre del vendedor de la tarjeta', r['recordatorio']['usuario_correo'] == dueno, r)

s, _ = api('PATCH', f'/intereses/{tarjeta}/asignar', {'vendedor_correo': otro}, t_dueno)
caso('el vendedor no reasigna (403)', s == 403, s)
s, r = api('PATCH', f'/intereses/{tarjeta}/asignar', {'vendedor_correo': otro}, coord)
caso('coordinación reasigna', s == 200 and r['interes']['vendedor_correo'] == otro, (s, r))
s, r = api('GET', f'/intereses/{tarjeta}', token=t_otro)
historial = r.get('interes', {}).get('interacciones', [])
caso('el vendedor nuevo abre la tarjeta', s == 200, s)
caso('ve el contacto del vendedor anterior', any(i['tipo'] == 'WhatsApp' and i['usuario_correo'] == dueno for i in historial), historial)
caso('la actividad realizada quedó en el historial con su nota', any('Pidió la malla curricular' in (i['descripcion'] + (i['resultado'] or '')) for i in historial), historial)
caso('queda constancia de la reasignación', any('Reasignado de' in i['descripcion'] for i in historial), historial)
_, r = api('GET', '/recordatorios', token=t_otro)
caso('la actividad pendiente pasa al calendario del vendedor nuevo', any(x['nro_recordatorio'] == pendiente for x in r['recordatorios']), r)
s, _ = api('GET', f'/intereses/{tarjeta}', token=t_dueno)
caso('el vendedor anterior ya no ve la tarjeta (403)', s == 403, s)

# --- Comisión configurable (solo administración), venta y reporte por vendedor
_, conf = api('GET', '/configuracion/comision', token=admin)
original = conf['porcentaje']
s, _ = api('PUT', '/configuracion/comision', {'porcentaje': 9}, t_otro)
caso('el vendedor no cambia la comisión (403)', s == 403, s)
s, _ = api('PUT', '/configuracion/comision', {'porcentaje': 9}, coord)
caso('coordinación no cambia la comisión (403)', s == 403, s)
s, r = api('PUT', '/configuracion/comision', {'porcentaje': 2.75}, admin)
caso('administración fija 2,75 %', s == 200, (s, r))

_, r = api('GET', f'/intereses/{tarjeta}', token=t_otro)
p = r['interes']['prospecto']
api('PUT', f"/prospectos/{p['documento']}", {k: p[k] for k in ('nombre', 'apellido', 'correo', 'telefono', 'origen')}
    | {'profesion': 'Contadora', 'ubicacion': 'Santa Cruz'}, t_otro)
_, r = api('POST', f"/prospectos/{p['documento']}/metodos-pago", {'tipo': 'QR', 'titular': 'Ana Correcciones'}, t_otro)
metodo = r['metodo']['nro_metodo']
modulo = next(t['modulo_codigo'] for t in tarjetas if t['nro_tarjeta'] == tarjeta)
s, r = api('POST', f'/intereses/{tarjeta}/ordenes-pago', {'modulos': [modulo], 'cuotas': 1, 'primer_vencimiento': '2030-01-10'}, t_otro)
caso('el vendedor nuevo genera la orden', s == 201, (s, r))
orden, total = r['orden']['nro_orden'], float(r['orden']['total'])
api('POST', f'/ordenes-pago/{orden}/cuotas/1/comprobante', {'nro_metodo': metodo, 'archivo': PNG}, t_otro)
s, r = api('PATCH', f'/ordenes-pago/{orden}/cuotas/1/aprobar', {}, admin)
caso('se aprueba el pago', s == 200, (s, r))
_, r = api('GET', '/comisiones', token=admin)
com = next((c for c in r['comisiones'] if c['vendedor_correo'] == otro and float(c['porcentaje']) == 2.75
            and abs(float(c['monto']) - round(total * 0.0275, 2)) < 0.01), None)
caso(f'la comisión del vendedor que cerró usa 2,75 % (Bs {round(total * 0.0275, 2)})', com is not None, r['comisiones'][:3])
api('PUT', '/configuracion/comision', {'porcentaje': original}, admin)

s, r = api('GET', '/reportes/listado?tipo=vendedores', token=coord)
caso('reporte por vendedor con columnas de cartera', s == 200 and {'Tarjetas', 'Abiertas', 'Concretadas', 'Perdidas'} <= {c['label'] for c in r['columnas']}, r.get('columnas'))
s, r = api('GET', '/inscripciones', token=coord)
caso('la matrícula aparece en Alumnos', s == 200 and any(i['solicitud_compra']['nro_orden'] == orden for i in r['inscripciones']), s)

# --- Exportación al sistema académico sin duplicados
s, r = api('POST', '/exportaciones', {}, admin)
caso('la exportación incluye al alumno nuevo', s == 200 and any(f['correo'] == p['correo'] for f in r['filas']), (s, r.get('mensaje')))
s, r = api('POST', '/exportaciones', {}, admin)
caso('repetir la exportación no duplica alumnos', s == 200 and r['filas'] == [], (s, r.get('mensaje')))

fin('CORRECCIONES')
