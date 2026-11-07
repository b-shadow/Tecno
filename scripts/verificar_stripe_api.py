"""Pruebas funcionales y de seguridad de Stripe Checkout Sandbox contra la API Laravel + PostgreSQL local."""
import concurrent.futures
import hmac
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8001').rstrip('/')
API = f'{BASE}/api'
PSQL = r'C:\Program Files\PostgreSQL\17\bin\psql.exe'


def leer_env(clave):
    with open('negocio/.env', encoding='utf-8') as f:
        for line in f:
            if line.startswith(f'{clave}='):
                return line.split('=', 1)[1].strip()
    return ''


def req(path, method='GET', body=None, token=None, headers=None):
    hdr = {'Accept': 'application/json'}
    raw = None
    if body is not None:
        if isinstance(body, (bytes, str)):
            raw = body.encode('utf-8') if isinstance(body, str) else body
        else:
            raw = json.dumps(body).encode('utf-8')
            hdr['Content-Type'] = 'application/json'
    if token:
        hdr['Authorization'] = f'Bearer {token}'
    if headers:
        hdr.update(headers)
    r = urllib.request.Request(f'{API}{path}', data=raw, headers=hdr, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        txt = e.read().decode('utf-8', errors='replace')
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, {'raw': txt}


def login(correo, password):
    st, data = req('/login', 'POST', {'correo': correo, 'password': password})
    assert st == 200 and 'token' in data, f'Login fallo {correo}: {st} {data}'
    return data['token']


def ok(msg):
    print(f'OK    {msg}')


adm = login('admin@crm-educativo.local', 'Admin12345')
vnd = login('vendedor.demo@crm-educativo.local', 'Vendedor12345')
vnd2 = login('vendedor2@crm-educativo.local', 'Vendedor12345')
crd = login('coord@test.local', 'Clave12345')

# 1. Buscar módulos del catálogo y crear prospecto completo + interés + orden de prueba
_, cat = req('/catalogo')
mods = [m for p in cat['programas'] for m in p['modulos']]
assert len(mods) >= 2, 'Se requieren modulos abiertos'
mod1 = mods[0]

uid = str(int(time.time()))[-6:]
doc = f'STR{uid}'
st, pr = req('/prospectos', 'POST', {
    'documento': doc, 'nombre': 'Carlos', 'apellido': 'StripeTest',
    'correo': f'stripe.{uid}@example.invalid', 'telefono': '71234567',
    'profesion': 'Ingeniero', 'ubicacion': 'Santa Cruz', 'origen': 'Web',
    'modulo_codigo': mod1['codigo'],
}, adm)
assert st == 201, f'Alta prospecto fallo: {st} {pr}'
nro_tarjeta = pr['prospecto']['intereses'][0]['nro_tarjeta']

st, asg = req(f'/intereses/{nro_tarjeta}/asignar', 'PATCH', {'vendedor_correo': 'vendedor.demo@crm-educativo.local'}, adm)
assert st == 200, f'Asignacion fallo: {st} {asg}'

st, ord_res = req(f'/intereses/{nro_tarjeta}/ordenes-pago', 'POST', {
    'modulos': [mod1['codigo']],
    'cuotas': 2,
    'primer_vencimiento': '2030-05-01',
}, vnd)
assert st == 201, f'Crear orden fallo: {st} {ord_res}'
nro_orden = ord_res['orden']['nro_orden']
monto_c1 = float(ord_res['orden']['cuotas'][0]['monto'])
ok(f'Orden #{nro_orden} creada con 2 cuotas (cuota 1 = {monto_c1} BOB)')

# P12: sin token
st, _ = req(f'/ordenes-pago/{nro_orden}/cuotas/1/checkout', 'POST', {})
assert st == 401, f'P12 esperaba 401, recibido {st}'
ok('P12 checkout sin token rechazado (401)')

# P14: vendedor ajeno (IDOR)
st, _ = req(f'/ordenes-pago/{nro_orden}/cuotas/1/checkout', 'POST', {}, vnd2)
assert st == 403, f'P14 esperaba 403, recibido {st}'
ok('P14 vendedor ajeno no puede iniciar checkout (403)')

# P11: manipulacion de monto/moneda
for payload_bad in [{'monto': 1}, {'amount': 100}, {'total': 5}, {'moneda': 'usd'}, {'currency': 'usd'}]:
    st, r = req(f'/ordenes-pago/{nro_orden}/cuotas/1/checkout', 'POST', payload_bad, vnd)
    assert st == 422, f'P11 esperaba 422 para {payload_bad}, recibido {st} {r}'
ok('P11 manipulacion de monto o moneda rechazada por backend (422)')

# Validar rechazo de tarjeta manual (sin pasar por Stripe Setup)
st, r_man = req(f'/prospectos/{doc}/metodos-pago', 'POST', {'tipo': 'Tarjeta', 'titular': 'Carlos StripeTest'}, vnd)
assert st == 422, f'Registro manual de tarjeta debio rechazarse: {st} {r_man}'
ok('Metodo manual rechaza tipo Tarjeta (exige Stripe Setup)')

# Registro de Setup Session real en Stripe
st, setup_res = req(f'/prospectos/{doc}/metodos-pago/stripe-setup', 'POST', {'nro_tarjeta': nro_tarjeta}, vnd)
assert st == 201 and setup_res['url'].startswith('https://checkout.stripe.com/'), f'Setup fallo: {st} {setup_res}'
ok(f'Stripe Setup Session real creada ({setup_res["session_id"][:20]}...)')

# P06 & P07: doble clic / concurrencia sobre misma cuota devuelve misma Checkout Session
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    f1 = pool.submit(req, f'/ordenes-pago/{nro_orden}/cuotas/1/checkout', 'POST', {}, vnd)
    f2 = pool.submit(req, f'/ordenes-pago/{nro_orden}/cuotas/1/checkout', 'POST', {}, vnd)
    (st1, c1), (st2, c2) = f1.result(), f2.result()
assert st1 == 201 and st2 == 201, f'P06 fallo: {st1} {c1} | {st2} {c2}'
assert c1['session_id'] == c2['session_id'], f'Se generaron 2 sesiones distintas: {c1["session_id"]} vs {c2["session_id"]}'
assert c1['moneda'] == 'BOB' and float(c1['monto']) == monto_c1
assert c1['url'].startswith('https://checkout.stripe.com/')
ok(f'P06/P07 idempotencia y doble clic devuelven una sola sesion BOB ({c1["session_id"][:20]}...)')

# P14 sobre consulta/cancelacion ajena
st, _ = req(f'/pagos/stripe/sesiones/{c1["session_id"]}', 'GET', token=vnd2)
assert st == 403, f'P14 consulta ajena debio ser 403: {st}'
st, _ = req(f'/pagos/stripe/sesiones/{c1["session_id"]}/cancelar', 'POST', {}, vnd2)
assert st == 403, f'P14 cancelacion ajena debio ser 403: {st}'
ok('P14 consulta y cancelacion de sesion ajena bloqueadas (403)')

# P10: webhook con firma invalida rechazado
st, w_bad = req('/stripe/webhook', 'POST', '{"id":"evt_fake","type":"checkout.session.completed"}', headers={'Stripe-Signature': 't=123,v1=bad', 'Content-Type': 'application/json'})
assert st == 400, f'P10 esperaba 400, recibido {st} {w_bad}'
ok('P10 webhook con firma invalida rechazado (400)')

# P21: anulación controlada de orden pendiente (expira sesión Stripe abierta y permite nueva orden)
st, anu_bad = req(f'/ordenes-pago/{nro_orden}/anular', 'PATCH', {'motivo': 'abc'}, vnd)
assert st == 422, f'Anulacion con motivo corto debio fallar: {st}'
st, anu_ok = req(f'/ordenes-pago/{nro_orden}/anular', 'PATCH', {'motivo': 'Cambio de modulo acordado con el prospecto'}, vnd)
assert st == 200 and anu_ok['orden']['estado'] == 'Anulada', f'Anulacion fallo: {st} {anu_ok}'
st, pay_anu = req(f'/ordenes-pago/{nro_orden}/cuotas/1/checkout', 'POST', {}, vnd)
assert st == 422, f'Cobro de orden anulada debio fallar: {st}'
ok(f'P21 orden #{nro_orden} anulada correctamente y bloquea cobros posteriores')

# P25: nueva orden sobre la misma tarjeta tras anular, con descuento aplicado
_, d_res = req('/descuentos', token=vnd)
dctos = [d_res['descuentos'][0]['codigo']] if d_res['descuentos'] else []
st, ord2 = req(f'/intereses/{nro_tarjeta}/ordenes-pago', 'POST', {
    'modulos': [mod1['codigo']],
    'descuentos': dctos,
    'cuotas': 1,
    'primer_vencimiento': '2030-06-01',
}, vnd)
assert st == 201, f'Nueva orden tras anular fallo: {st} {ord2}'
nro_orden2 = ord2['orden']['nro_orden']
monto2 = float(ord2['orden']['total'])
st, chk2 = req(f'/ordenes-pago/{nro_orden2}/cuotas/1/checkout', 'POST', {}, vnd)
assert st == 201 and abs(float(chk2['monto']) - monto2) < 0.01
ok(f'P25 nueva orden #{nro_orden2} con descuento tras anular -> Checkout por Bs {monto2:.2f} BOB')

# Verificar conversión BOB 499.99 -> 49999 centavos vía PHP unit test sobre NStripe::aCentavos
out_php = subprocess.check_output([
    'php', '-r',
    "require 'negocio/vendor/autoload.php'; $app=require 'negocio/bootstrap/app.php'; $app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap(); "
    "$r=new ReflectionMethod(App\\Negocio\\NStripe::class,'aCentavos'); $r->setAccessible(true); $s=$app->make(App\\Negocio\\NStripe::class); "
    "echo json_encode(['499.99'=>$r->invoke($s,'499.99'),'350.00'=>$r->invoke($s,350.00),'1200.00'=>$r->invoke($s,1200)]);"
]).decode().strip()
cent_check = json.loads(out_php)
assert cent_check == {'499.99': 49999, '350.00': 35000, '1200.00': 120000}, f'Centavos mismatch: {cent_check}'
ok(f'P23 conversion exacta BOB a centavos verificada: {cent_check}')

# Verificar P09 webhook duplicado usando firma HMAC auténtica con el secreto real del entorno sobre evento checkout.session.expired de prueba (sin inventar pagos exitosos)
whsec = leer_env('STRIPE_WEBHOOK_SECRET')
assert whsec.startswith('whsec_'), 'STRIPE_WEBHOOK_SECRET no configurado'
ts = str(int(time.time()))
evt_payload = json.dumps({
    'id': f'evt_test_idemp_{uid}',
    'object': 'event',
    'api_version': '2026-04-22.dahlia',
    'created': int(ts),
    'livemode': False,
    'type': 'checkout.session.expired',
    'data': {'object': {'id': c1['session_id'], 'object': 'checkout.session', 'status': 'expired'}},
})
sig = hmac.new(whsec.encode('utf-8'), f'{ts}.{evt_payload}'.encode('utf-8'), hashlib.sha256).hexdigest()
hdr_sig = {'Stripe-Signature': f't={ts},v1={sig}', 'Content-Type': 'application/json'}
st_w1, w1 = req('/stripe/webhook', 'POST', evt_payload, headers=hdr_sig)
st_w2, w2 = req('/stripe/webhook', 'POST', evt_payload, headers=hdr_sig)
assert st_w1 == 200 and w1.get('duplicado') is False, f'Webhook 1 fallo: {st_w1} {w1}'
assert st_w2 == 200 and w2.get('duplicado') is True, f'Webhook 2 (duplicado) fallo: {st_w2} {w2}'
ok('P09 webhook firmado valido procesado e idempotente ante reenvio duplicado')

print('\nSTRIPE API & SEGURIDAD: TODO OK')
