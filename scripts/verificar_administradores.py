"""Regla «siempre queda al menos un administrador activo», también con dos bajas simultáneas.
Solo contra una base QA local: crea un administrador temporal y lo deja inactivo al terminar.
"""
import concurrent.futures

from qa_comun import api, caso, fin, login, unico

ADMIN = 'admin@crm-educativo.local'
admin = login('admin')
otro = f'admin.qa.{unico()}@example.invalid'
s, r = api('POST', '/usuarios', {'nombre': 'Administrador', 'apellido': 'Temporal', 'correo': otro, 'password': 'QaAdmin12345',
                                 'rol': 'administrador', 'estado': 'activo', 'fecha_inicio': '2026-01-01', 'fecha_fin': '2030-12-31'}, admin)
caso('se crea un segundo administrador activo', s == 201, (s, r))
otro_tok = login(otro, 'QaAdmin12345')

# Cada administrador da de baja al otro al mismo tiempo: solo una baja puede prosperar.
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    a = pool.submit(api, 'PATCH', f'/usuarios/{otro}/estado', {'estado': 'inactivo'}, admin)
    b = pool.submit(api, 'PATCH', f'/usuarios/{ADMIN}/estado', {'estado': 'inactivo'}, otro_tok)
    (sa, ra), (sb, rb) = a.result(), b.result()
# La que pierde responde 422 (último administrador) o 401 (la otra baja ya le revocó la sesión).
caso('dos bajas simultáneas: solo una prospera', sorted([sa, sb]) in ([200, 401], [200, 422]), (sa, ra, sb, rb))

quedo = admin if sa == 200 else otro_tok
_, r = api('GET', '/usuarios', token=quedo)
activos = [u['correo'] for u in r['usuarios'] if u['rol'] == 'administrador' and u['estado'] == 'activo']
caso('queda exactamente un administrador activo', len(activos) == 1, activos)

# Restaurar: el original activo y el temporal inactivo.
if ADMIN not in activos:
    s, _ = api('PATCH', f'/usuarios/{ADMIN}/estado', {'estado': 'activo'}, quedo)
    caso('el administrador que quedó reactiva al original', s == 200, s)
admin = login('admin')
s, _ = api('PATCH', f'/usuarios/{otro}/estado', {'estado': 'inactivo'}, admin)
caso('el temporal queda inactivo', s in (200, 422) and otro not in [u['correo'] for u in api('GET', '/usuarios', token=admin)[1]['usuarios']
                                                                     if u['rol'] == 'administrador' and u['estado'] == 'activo'], s)
s, r = api('PATCH', f'/usuarios/{ADMIN}/estado', {'estado': 'inactivo'}, admin)
caso('el último administrador no puede darse de baja (422 en español)', s == 422 and 'administrador' in str(r), (s, r))

fin('ADMINISTRADORES')
