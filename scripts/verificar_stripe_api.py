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
    'correo': f'unexouagrm+api{uid}@gmail.com', 'telefono': '71234567',
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

# P25: nueva orden sobre la misma tarjeta tras anular, con descuento permitido (Cliente recurrente)
_, d_res = req('/descuentos', token=vnd)
dctos_cliente = [d['codigo'] for d in d_res.get('descuentos', []) if d['codigo'] == 'CLIENTE_RECURRENTE']
st, ord2 = req(f'/intereses/{nro_tarjeta}/ordenes-pago', 'POST', {
    'modulos': [mod1['codigo']],
    'descuentos': dctos_cliente,
    'cuotas': 1,
    'primer_vencimiento': '2030-06-01',
}, vnd)
assert st == 201, f'Nueva orden tras anular fallo: {st} {ord2}'
nro_orden2 = ord2['orden']['nro_orden']
monto2 = float(ord2['orden']['total'])
st, chk2 = req(f'/ordenes-pago/{nro_orden2}/cuotas/1/checkout', 'POST', {}, vnd)
assert st == 201 and abs(float(chk2['monto']) - monto2) < 0.01
ok(f'P25 nueva orden #{nro_orden2} con descuento tras anular -> Checkout por Bs {monto2:.2f} BOB')

# D10 & P32: Reglas estrictas de descuentos y bloqueo de QR/Transferencia/Comprobante manual en API
prog_multi = next((p for p in cat['programas'] if len(p['modulos']) >= 4), cat['programas'][0])
m_cods = [m['codigo'] for m in prog_multi['modulos']]
st_p_d, pr_d = req('/prospectos', 'POST', {
    'documento': f'DSC{uid}', 'nombre': 'Elena', 'apellido': 'ReglasDcto',
    'correo': f'unexouagrm+dsc{uid}@gmail.com', 'telefono': '71234568',
    'profesion': 'Auditora', 'ubicacion': 'Santa Cruz', 'origen': 'Web',
    'modulo_codigo': m_cods[0],
}, adm)
assert st_p_d == 201, f'Alta prospecto D10 fallo: {st_p_d} {pr_d}'
tar_d = pr_d['prospecto']['intereses'][0]['nro_tarjeta']
req(f'/intereses/{tar_d}/asignar', 'PATCH', {'vendedor_correo': 'vendedor.demo@crm-educativo.local'}, adm)

st_qr, _ = req(f'/prospectos/DSC{uid}/metodos-pago', 'POST', {'tipo': 'QR', 'titular': 'Elena'}, vnd)
assert st_qr == 422, f'P32 QR manual debio retornar 422: {st_qr}'
st_d3_bad, _ = req(f'/intereses/{tar_d}/ordenes-pago', 'POST', {'modulos': m_cods[:2], 'descuentos': ['3_MAS_MODULOS'], 'cuotas': 1, 'primer_vencimiento': '2030-07-01'}, vnd)
assert st_d3_bad == 422, f'D10 3_MAS_MODULOS con 2 modulos debio retornar 422: {st_d3_bad}'
st_dpc_bad, _ = req(f'/intereses/{tar_d}/ordenes-pago', 'POST', {'modulos': m_cods[:-1], 'descuentos': ['PROGRAMA_COMPLETO'], 'cuotas': 1, 'primer_vencimiento': '2030-07-01'}, vnd)
assert st_dpc_bad == 422, f'D10 PROGRAMA_COMPLETO incompleto debio retornar 422: {st_dpc_bad}'

dctos_all = ['CLIENTE_RECURRENTE', 'PROGRAMA_COMPLETO'] + (['3_MAS_MODULOS'] if len(m_cods) >= 3 else [])
st_d_ok, ord_d = req(f'/intereses/{tar_d}/ordenes-pago', 'POST', {
    'modulos': m_cods,
    'descuentos': dctos_all,
    'cuotas': 2,
    'primer_vencimiento': '2030-07-15',
    'envio_automatico': True,
}, vnd)
assert st_d_ok == 201, f'D08/D10 orden valida completa fallo: {st_d_ok} {ord_d}'
sub_esp = round(sum(float(m['precio']) for m in prog_multi['modulos']), 2)
pcts = {'CLIENTE_RECURRENTE': 10, 'PROGRAMA_COMPLETO': 15, '3_MAS_MODULOS': 10}
dcto_esp = round(sum(round(sub_esp * pcts[c] / 100, 2) for c in dctos_all), 2)
assert abs(float(ord_d['orden']['descuento_total']) - dcto_esp) < 0.01, f'Descuento esperado {dcto_esp}, recibido {ord_d["orden"]}'
assert ord_d['orden']['envio_automatico'] is True

st_cmp_bad, _ = req(f'/ordenes-pago/{ord_d["orden"]["nro_orden"]}/cuotas/1/comprobante', 'POST', {
    'archivo': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
}, vnd)
assert st_cmp_bad == 422, f'P32 comprobante manual nuevo debio retornar 422: {st_cmp_bad}'

st_auto_off, d_off = req(f'/ordenes-pago/{ord_d["orden"]["nro_orden"]}/envio-automatico', 'PATCH', {'envio_automatico': False}, vnd)
assert st_auto_off == 200 and d_off['orden']['envio_automatico'] is False
st_auto_on, d_on = req(f'/ordenes-pago/{ord_d["orden"]["nro_orden"]}/envio-automatico', 'PATCH', {'envio_automatico': True}, vnd)
assert st_auto_on == 200 and d_on['orden']['envio_automatico'] is True

# Verificar token publico de cuota (/pagos/publico/cuotas/{token}) y regeneracion de sesion expirada (A10)
ord_dsc_nro = ord_d['orden']['nro_orden']
tok_cuota = subprocess.check_output([
    PSQL, '-U', 'postgres', '-d', 'crm_educativo', '-tAc',
    f"SELECT token_pago FROM cuotas WHERE nro_orden = {ord_dsc_nro} AND nro_cuota = 1;"
]).decode().strip()
assert tok_cuota, 'No se genero token_pago automatico al activar envio_automatico'
st_pub_bad, _ = req('/pagos/publico/cuotas/token-inexistente-xyz')
assert st_pub_bad == 404, f'Token inexistente debio ser 404, recibido {st_pub_bad}'
st_pub_c1, d_pub_c1 = req(f'/pagos/publico/cuotas/{tok_cuota}')
assert st_pub_c1 == 200 and d_pub_c1['estado_link'] == 'pendiente' and d_pub_c1['url_checkout'].startswith('https://checkout.stripe.com/')
for campo_priv in ('documento', 'correo', 'vendedor', 'nro_tarjeta', 'session_id'):
    assert campo_priv not in d_pub_c1, f'Campo privado o interno filtrado al endpoint publico de cuota: {campo_priv}'
ses_c1 = subprocess.check_output([
    PSQL, '-U', 'postgres', '-d', 'crm_educativo', '-tAc',
    f"SELECT stripe_sesion FROM transacciones_stripe WHERE nro_orden = {ord_dsc_nro} AND nro_cuota = 1 ORDER BY nro_transaccion DESC LIMIT 1;"
]).decode().strip()
assert ses_c1.startswith('cs_test_'), f'Sesion Stripe no persistida: {ses_c1}'
subprocess.check_call(['php', '-r', (
    "require 'negocio/vendor/autoload.php'; $app=require 'negocio/bootstrap/app.php'; "
    "$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap(); "
    f"$sc = new Stripe\\StripeClient(config('services.stripe.secret')); $sc->checkout->sessions->expire('{ses_c1}');"
)])
st_pub_c2, d_pub_c2 = req(f'/pagos/publico/cuotas/{tok_cuota}')
assert st_pub_c2 == 200 and d_pub_c2['url_checkout'] != d_pub_c1['url_checkout'] and d_pub_c2['url_checkout'].startswith('https://checkout.stripe.com/')
ses_c2 = subprocess.check_output([
    PSQL, '-U', 'postgres', '-d', 'crm_educativo', '-tAc',
    f"SELECT stripe_sesion FROM transacciones_stripe WHERE nro_orden = {ord_dsc_nro} AND nro_cuota = 1 ORDER BY nro_transaccion DESC LIMIT 1;"
]).decode().strip()
assert ses_c2 != ses_c1, 'Debio regenerarse una sesion nueva tras expirar'

# Limpiar ordenes previas solo de prospectos DSC* interrumpidos para no sesgar conteo del scheduler
subprocess.check_call([
    PSQL, '-U', 'postgres', '-d', 'crm_educativo', '-c',
    f"UPDATE ordenes_pago SET estado = 'Anulada', motivo_anulacion = 'Limpieza previa prueba API' WHERE nro_orden < {ord_dsc_nro} AND estado = 'Activa' AND nro_tarjeta IN (SELECT nro_tarjeta FROM intereses WHERE documento LIKE 'DSC%');"
], stdout=subprocess.DEVNULL)

# Scheduler A01-A09: correr recordatorios para cuota 2 (vence 2030-08-15) en -3d, 0d, +3d, duplicado e SMTP fallido
vence_c2 = ord_d['orden']['cuotas'][1]['fecha_vencimiento'][:10]
import datetime as _dt
dt_v = _dt.date.fromisoformat(vence_c2)
for etiqueta, delta, col in [('A01 previo -3d', -3, 'recordatorio_previo_en'), ('A02 vencimiento 0d', 0, 'recordatorio_vencimiento_en'), ('A03 mora +3d', 3, 'recordatorio_mora_en')]:
    fecha_cmd = (dt_v + _dt.timedelta(days=delta)).isoformat()
    out_sch = subprocess.check_output(['php', 'negocio/artisan', 'unexo:recordatorios-pago', f'--fecha={fecha_cmd}']).decode()
    assert 'evaluadas=' in out_sch, out_sch
    val_col = subprocess.check_output([
        PSQL, '-U', 'postgres', '-d', 'crm_educativo', '-tAc',
        f"SELECT {col} IS NOT NULL FROM cuotas WHERE nro_orden = {ord_dsc_nro} AND nro_cuota = 2;"
    ]).decode().strip()
    assert val_col == 't', f'{etiqueta} no marco {col} (output: {out_sch})'
out_dup = subprocess.check_output(['php', 'negocio/artisan', 'unexo:recordatorios-pago', f'--fecha={(dt_v + _dt.timedelta(days=3)).isoformat()}']).decode()
assert 'enviados=0' in out_dup, f'A08 duplicado envio de mas: {out_dup}'

# A09: Resetear recordatorio_mora_en en cuota 2 y ejecutar scheduler con puerto SMTP inexistente -> no marca enviado, registra fallida
subprocess.check_call([
    PSQL, '-U', 'postgres', '-d', 'crm_educativo', '-c',
    f"UPDATE cuotas SET recordatorio_mora_en = NULL WHERE nro_orden = {ord_dsc_nro} AND nro_cuota = 2;"
], stdout=subprocess.DEVNULL)
out_a09 = subprocess.check_output([
    'php', '-r',
    "require 'negocio/vendor/autoload.php'; $app=require 'negocio/bootstrap/app.php'; "
    "$kernel=$app->make(Illuminate\\Contracts\\Console\\Kernel::class); $kernel->bootstrap(); "
    "config(['mail.mailers.smtp.host'=>'127.0.0.1','mail.mailers.smtp.port'=>19999]); "
    f"Illuminate\\Support\\Facades\\Artisan::call('unexo:recordatorios-pago',['--fecha'=>'{(dt_v + _dt.timedelta(days=3)).isoformat()}']); "
    "echo Illuminate\\Support\\Facades\\Artisan::output();"
]).decode()
assert 'fallidos=1' in out_a09 and 'enviados=0' in out_a09, out_a09
val_mora_despues = subprocess.check_output([
    PSQL, '-U', 'postgres', '-d', 'crm_educativo', '-tAc',
    f"SELECT recordatorio_mora_en IS NULL FROM cuotas WHERE nro_orden = {ord_dsc_nro} AND nro_cuota = 2;"
]).decode().strip()
assert val_mora_despues == 't', 'A09 no debio marcar recordatorio_mora_en cuando fallo SMTP'

# A05 anular orden -> no vuelve a enviar
req(f'/ordenes-pago/{ord_dsc_nro}/anular', 'PATCH', {'motivo': 'Limpieza de orden de prueba automatizada'}, vnd)
out_anu = subprocess.check_output(['php', 'negocio/artisan', 'unexo:recordatorios-pago', f'--fecha={(dt_v + _dt.timedelta(days=3)).isoformat()}']).decode()
assert 'enviados=0' in out_anu, f'A05 orden anulada no debe reenviar recordatorios: {out_anu}'
ok('D10, P32, A01-A10 reglas de descuentos, bloqueo QR/manual, token publico regenerable y scheduler verificados')

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

# PRUEBA 15 / 12 Public return endpoint security checks
st_no_tok, _ = req(f'/pagos/publico/sesiones/{chk2["session_id"]}')
assert st_no_tok == 400, f'Retorno publico sin token debio ser 400, recibido {st_no_tok}'
st_bad_tok, _ = req(f'/pagos/publico/sesiones/{chk2["session_id"]}?token=falso123456')
assert st_bad_tok == 403, f'Retorno publico con token falso debio ser 403, recibido {st_bad_tok}'
tok_real = subprocess.check_output([
    PSQL, '-U', 'postgres', '-d', 'crm_educativo', '-tAc',
    f"SELECT token_publico FROM transacciones_stripe WHERE stripe_sesion = '{chk2['session_id']}';"
]).decode().strip()
assert tok_real, 'Falta token_publico guardado en transacciones_stripe'
st_pub, d_pub = req(f'/pagos/publico/sesiones/{chk2["session_id"]}?token={tok_real}')
assert st_pub == 200 and d_pub.get('publico') is True and d_pub.get('moneda') == 'BOB', f'Retorno publico fallo: {st_pub} {d_pub}'
for prohibido in ('nro_tarjeta', 'estado_comercial', 'faltantes_conversion', 'vendedor', 'prospecto'):
    assert prohibido not in d_pub, f'Campo interno filtrado al retorno publico: {prohibido}'
ok('PRUEBA 08/15 retorno publico protegido por token HMAC sin fuga de datos internos')

# PRUEBA 20 Expiracion de sesion y regeneracion limpia sin cobros duplicados
php_exp = (
    "require 'negocio/vendor/autoload.php'; $app=require 'negocio/bootstrap/app.php'; "
    "$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap(); "
    "$sc = new Stripe\\StripeClient(config('services.stripe.secret')); "
    f"$sc->checkout->sessions->expire('{chk2['session_id']}');"
)
subprocess.check_call(['php', '-r', php_exp])
st_exp, d_exp = req(f'/pagos/publico/sesiones/{chk2["session_id"]}?token={tok_real}')
assert st_exp == 200 and d_exp.get('estado_interno') == 'expirado', f'Debio detectar sesion expirada: {st_exp} {d_exp}'
st_reg, chk_reg = req(f'/ordenes-pago/{nro_orden2}/cuotas/1/checkout', 'POST', {}, vnd)
assert st_reg == 201 and chk_reg['session_id'] != chk2['session_id'] and chk_reg['reutilizada'] is False, f'Regeneracion tras expirar fallo: {st_reg} {chk_reg}'
ok('PRUEBA 20 sesion expirada permite regenerar enlace nuevo manteniendo cuota pendiente')

# PRUEBA 18 Fallo controlado de SMTP no deshace pago ni marca enviado
php_smtp_fail = (
    "require 'negocio/vendor/autoload.php'; $app=require 'negocio/bootstrap/app.php'; "
    "$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap(); "
    "config(['mail.mailers.smtp.host' => '127.0.0.1', 'mail.mailers.smtp.port' => 19999]); "
    "$n = $app->make(App\\Negocio\\NNotificacion::class); "
    "$n->notificarPagoConfirmado(['cliente_correo'=>'unexouagrm+fail@gmail.com','cliente_nombre'=>'Fail Test',"
    "'vendedor_correo'=>'vendedor.demo@crm-educativo.local','programa'=>'IA','modulo'=>'M1','nro_orden'=>999999,"
    "'nro_cuota'=>1,'total_cuotas'=>1,'monto'=>100,'referencia'=>'pi_test_smtp_fail']); "
    "echo 'SMTP_FAIL_SAFE_OK';"
)
out_smtp = subprocess.check_output(['php', '-r', php_smtp_fail]).decode().strip()
assert 'SMTP_FAIL_SAFE_OK' in out_smtp
fallida_cnt = int(subprocess.check_output([
    PSQL, '-U', 'postgres', '-d', 'crm_educativo', '-tAc',
    "SELECT count(*) FROM notificaciones WHERE destinatario='unexouagrm+fail@gmail.com' AND estado='fallida';"
]).decode().strip())
assert fallida_cnt >= 1, 'Fallo SMTP controlado no registro estado fallida'
ok('PRUEBA 18 fallo SMTP controlado registrado como fallida sin lanzar excepcion fatal')

print('\nSTRIPE API & SEGURIDAD: TODO OK')
