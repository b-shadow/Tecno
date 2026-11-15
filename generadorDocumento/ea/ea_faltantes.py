"""Completa en el EAPX de P2 los diagramas que el documento ya solicita.

Usa la notación del generador de proyectocorreo/doc/ea/ea_p1.py y extrae
actores, CU, paquetes y llamadas entre capas de contenido.py y codigo.py.
No recrea el proyecto ni borra diagramas que se hayan movido manualmente.
"""
import pathlib
import re
import sys
import uuid

HERE = pathlib.Path(__file__).resolve().parent
DOC = HERE.parent
sys.path[:0] = [str(DOC), str(HERE)]

import codigo
import contenido as C
import ea_base

PREFERIDAS = {
    'CU1': ['POST /login', 'POST /usuarios', 'PUT /matriz'],
    'CU2': ['GET /catalogo', 'POST /registro-interes'],
    'CU3': ['POST /prospectos', 'PATCH /intereses/{interes}/asignar'],
    'CU4': ['PATCH /intereses/{interes}/estado'],
    'CU5': ['PATCH /intereses/{interes}/estado', 'POST /motivos'],
    'CU6': ['POST /intereses/{interes}/ordenes-pago', 'PATCH /ordenes-pago/{orden}/cuotas/{cuota}/aprobar', 'POST /exportaciones'],
    'CU7': ['POST /intereses/{interes}/interacciones', 'POST /intereses/{interes}/recordatorios', 'GET /notificaciones'],
    'CU8': ['GET /reportes/estadisticas', 'GET /comisiones/resumen'],
}

# Métodos D realmente invocados por cada método N. Se comprueban contra
# codigo._llamadas al generar; si el código cambia, la generación falla.
PREFERIDAS_D = {
    'CU1': [['usuarioPorCorreo', 'crearToken'], ['crear'], ['guardarPermiso']],
    'CU2': [['programasAbiertos'], ['crear']],
    'CU3': [['crear'], ['transaccion', 'refrescarDetalle']],
    'CU4': [['guardar', 'actualizarEstadoProspecto']],
    'CU5': [['guardar', 'actualizarEstadoProspecto'], ['crear']],
    'CU6': [['crearOrden', 'insertarCuotas'], ['cambiarEstadoCuota'], ['exportarPendientes']],
    'CU7': [['registrarInteraccion'], ['crearRecordatorio'], ['listar']],
    'CU8': [['estadisticas'], ['resumenComisiones']],
}

ea_base.EAPX = HERE / 'crm-p2.eapx'
ea_base.SALIDA = DOC / 'diagramas'


def paquete(ea, padre, nombre):
    return next((p for p in padre.Packages if p.Name == nombre), None) or ea.paquete(padre, nombre)


def elemento(ea, pkg, nombre, tipo):
    return next((e for e in pkg.Elements if e.Name == nombre and e.Type == tipo), None) or ea.elemento(pkg, nombre, tipo)


def diagrama(ea, pkg, nombre, tipo, archivo):
    """Si ya se creó en EA, solo vuelve a exportarlo: conserva su ubicación manual."""
    anterior = next((d for d in pkg.Diagrams if d.Name == nombre), None)
    if anterior:
        ea.exportar(anterior, archivo)
        return None
    return ea.diagrama(pkg, nombre, tipo)


def requisitos(ea, modelo):
    req = paquete(ea, modelo, 'Captura de Requisitos')
    actores = {a: elemento(ea, req, a, 'Actor') for a, _ in C.ACTORES}
    casos = {cu: elemento(ea, req, f'{cu}: {C.DETALLE[cu]["gestionar"]}', 'UseCase') for cu in C.CU}
    for cu, caso in casos.items():
        for a in C.actores_cu(cu):
            if not any(c.SupplierID == caso.ElementID and c.Type == 'Association' for c in actores[a].Connectors):
                ea.conector(actores[a], caso, 'Association')

    d = diagrama(ea, req, 'Actores del sistema', 'Use Case', 'actores.png')
    if d:
        sistema = ea.elemento(req, 'CRM Comercial Educativo', 'Boundary')
        ea.poner(d, sistema, 310, 25, 320, 490, seq=50)
        for i, a in enumerate(actores.values()):
            ea.poner(d, a, 70, 55 + i * 112, 78, 80)
            ea.conector(a, sistema, 'Association')
        ea.exportar(d, 'actores.png')

    for cu, nombre in C.CU.items():
        d = diagrama(ea, req, f'{cu}: {nombre}', 'Use Case', f'uc-{cu.lower()}.png')
        if d:
            ac = C.actores_cu(cu)
            for i, a in enumerate(ac):
                ea.poner(d, actores[a], 50, 45 + i * 116, 65, 82)
            ea.poner(d, casos[cu], 355, 45 + (len(ac) - 1) * 58, 240, 95)
            ea.exportar(d, f'uc-{cu.lower()}.png')

    d = diagrama(ea, req, 'Diagrama general de casos de uso', 'Use Case', 'uc-general.png')
    if d:
        marco = ea.elemento(req, 'CRM Comercial Educativo: tres capas', 'Boundary')
        ea.poner(d, marco, 390, 15, 390, 8 * 105 + 40, seq=50)
        for i, cu in enumerate(C.CU): ea.poner(d, casos[cu], 445, 55 + i * 105, 270, 72, seq=1)
        for i, a in enumerate(actores.values()):
            x = 45 if i < 2 else 980
            y = 170 + (i % 2) * 420
            ea.poner(d, a, x, y, 78, 88)
        ea.exportar(d, 'uc-general.png')
    return req, actores, casos


def paquetes(ea, modelo, actores, casos):
    raiz = paquete(ea, modelo, 'Análisis de Paquetes')
    ps = {n: paquete(ea, raiz, n) for n in C.PAQUETES}
    d = diagrama(ea, raiz, 'Paquetes del sistema', 'Package', 'paquetes.png')
    if d:
        for i, p in enumerate(ps.values()):
            ea.poner(d, p, 35 + (i % 3) * 230, 45 + (i // 3) * 175, 190, 105)
        ea.exportar(d, 'paquetes.png')
    for i, (n, spec) in enumerate(C.PAQUETES.items(), 1):
        d = diagrama(ea, raiz, f'{n}: casos de uso', 'Package', f'paquete-{i}.png')
        if not d: continue
        p = ps[n]; cus = spec['cu']
        ea.poner(d, p, 45, 55 + (len(cus) - 1) * 58, 235, 100)
        for j, cu in enumerate(cus):
            ea.conector(p, casos[cu], 'Dependency', st='trace', dirigido=True)
            ea.poner(d, casos[cu], 455, 45 + j * 118, 270, 80)
        ea.exportar(d, f'paquete-{i}.png')


def interacciones(cu):
    """Recorrido representativo P→N→D por área; cada método se extrae del código."""
    clases, deps, errores = codigo.cadena(cu)
    if errores: raise ValueError('; '.join(errores))
    if cu == 'CU5':
        # Marcar Perdido se realiza en el embudo (ruta clasificada como CU4),
        # pero su formulario y NInteres implementan la pérdida con motivo.
        extra, _, errores = codigo.cadena('CU4')
        if errores: raise ValueError('; '.join(errores))
        clases.update(extra)
    rutas = [r for r in codigo.rutas_api() if
             (r['cu'] == cu or (cu == 'CU5' and r['ruta'] == '/intereses/{interes}/estado'))
             and f'{r["verbo"]} {r["ruta"]}' in PREFERIDAS[cu]]
    rutas.sort(key=lambda r: PREFERIDAS[cu].index(f'{r["verbo"]} {r["ruta"]}'))
    php = codigo.clases_php()
    funciones = codigo.funciones_api()
    usos = codigo.usos_api()
    pasos = []
    if len(rutas) != len(PREFERIDAS[cu]):
        raise ValueError(f'{cu}: faltan rutas verificadas para la secuencia: {PREFERIDAS[cu]}')
    for indice, r in enumerate(rutas):
        n = r['controlador']
        fn = next((k for k, f in funciones.items() if f['verbo'] == r['verbo'] and
                   f['ruta'] == codigo.norm(r['ruta'])), None)
        if not fn: continue
        api = f'api/{fn.split(".")[0]}.js'
        paginas = [a.rsplit('/', 1)[-1] for a, fns in usos.items()
                   if fn in fns and a.rsplit('/', 1)[-1] in clases]
        pagina = next((p for p in paginas if p == {'CU2': 'PCatalogo.jsx', 'CU4': 'PEmbudo.jsx',
                                                  'CU5': 'PEmbudo.jsx'}.get(cu)),
                      paginas[0] if paginas else ('PLogin.jsx' if r['ruta'] == '/login' else api))
        actor = ('Coordinador' if cu == 'CU6' and
                 ('/aprobar' in r['ruta'] or r['ruta'] == '/exportaciones') else
                 'Administrador' if cu == 'CU5' and r['ruta'] == '/motivos' else
                 C.DETALLE[cu]['iniciador'])
        pasos.append((f'@{actor}', pagina, f'abrir {pagina}' if pagina != api else 'iniciar'))
        if pagina != api: pasos.append((pagina, api, f'{funciones[fn]["nombre"]}()'))
        etiqueta = f'{r["verbo"]} {r["ruta"]}'
        if cu == 'CU5' and r['ruta'] == '/intereses/{interes}/estado': etiqueta += ' (Perdido + motivo)'
        pasos.append((api, n, etiqueta))
        disponibles = [(dato, metodo) for dato, metodo in codigo._llamadas(n, r['metodo'], php)
                       if dato in clases and clases[dato]['estereotipo'] == 'datos']
        for nombre_metodo in PREFERIDAS_D[cu][indice]:
            real = next(((dato, metodo) for dato, metodo in disponibles if metodo == nombre_metodo), None)
            if real is None:
                raise ValueError(f'{cu}: {n}::{r["metodo"]} ya no llama a {nombre_metodo}() en la capa D')
            dato, metodo = real
            pasos.append((n, dato, f'{metodo}()'))
    if not pasos: raise ValueError(f'{cu} no tiene rutas de secuencia verificadas')
    return clases, pasos


def diagrama_interaccion(ea, raiz, cu, tipo, archivo):
    clases, pasos = interacciones(cu)
    nombre = f'{cu}. {C.CU[cu]}: {tipo} (recorridos principales)'
    d = diagrama(ea, raiz, nombre, 'Sequence' if tipo == 'Secuencia' else 'Collaboration', archivo)
    if not d: return
    d.StyleEx = 'SuppressBrackets=1;'; d.Update()
    if tipo == 'Secuencia':
        php = codigo.clases_php()
        nombres_actores = list(dict.fromkeys(a[1:] for a, _, _ in pasos if a.startswith('@')))
        actores = {n: ea.elemento(raiz, n, 'Actor') for n in nombres_actores}
        # Una línea de vida por responsabilidad mantiene legibles las ocho
        # secuencias en la hoja vertical. Cada flecha conserva el nombre de la
        # clase y método concretos del código, aunque el CU use varias clases N/D.
        vidas = [('Pantalla React', 'boundary'), ('Cliente HTTP', 'boundary'),
                 ('Negocio Laravel', 'control'), ('Datos PostgreSQL', 'entity')]
        objetos = {n: ea.elemento(raiz, n, 'Object', st) for n, st in vidas}
        def grupo(n):
            if n.startswith('@'): return actores[n[1:]]
            x = clases[n]
            if x['estereotipo'] == 'client page': return objetos['Pantalla React']
            if x['capa'] == 'Presentacion': return objetos['Cliente HTTP']
            if x['capa'] == 'Negocio': return objetos['Negocio Laravel']
            return objetos['Datos PostgreSQL']
        escenas = []
        for paso in pasos:
            if paso[0].startswith('@'): escenas.append([])
            escenas[-1].append(paso)

        def retorno_php(nombre, metodo):
            firma = php.get(nombre, {}).get('metodos', {}).get(metodo, {}).get('firma', '')
            m = re.search(r'\):\s*([?\w\\|]+)$', firma)
            return m.group(1) if m else 'resultado'

        mensajes, marcos = [], []
        for j, escena in enumerate(escenas):
            inicio = len(mensajes) + 1
            ruta = PREFERIDAS[cu][j]
            for a, b, txt in escena:
                if not a.startswith('@') and a.startswith('api/'):
                    met = next((r['metodo'] for r in codigo.rutas_api() if
                                r['controlador'] == b and f'{r["verbo"]} {r["ruta"]}' == ruta), None)
                    etiqueta = f'{b}::{met}()' if met else txt
                elif not a.startswith('@') and a in php and b in php:
                    etiqueta = f'{b}::{txt}'
                elif not a.startswith('@') and a in clases and clases[a]['estereotipo'] == 'client page':
                    etiqueta = f'{b.rsplit("/", 1)[-1]}::{txt}'
                else: etiqueta = txt
                mensajes.append((a, b, etiqueta, 'call'))
                if not a.startswith('@') and a in php and b in php and clases[b]['estereotipo'] == 'datos':
                    metodo = txt.partition('(')[0]
                    mensajes.append((b, a, retorno_php(b, metodo), 'return'))
            for a, b, txt in reversed(escena):
                if not a.startswith('@') and a in php and b in php and clases[b]['estereotipo'] == 'datos':
                    continue  # la clase D ya respondió justo después de su llamada
                if a.startswith('@'): etiqueta = 'resultado mostrado'
                elif a.startswith('api/'):
                    controlador = b
                    metodo = next((r['metodo'] for r in codigo.rutas_api() if
                                   r['controlador'] == controlador and
                                   f'{r["verbo"]} {r["ruta"]}' == ruta), None)
                    etiqueta = retorno_php(controlador, metodo) if metodo else 'respuesta JSON'
                else: etiqueta = 'respuesta JSON'
                mensajes.append((b, a, etiqueta, 'return'))
            metodo_guardia = next((r['metodo'] for r in codigo.rutas_api() if
                                   f'{r["verbo"]} {r["ruta"]}' == ruta), ruta)
            marcos.append((f'{metodo_guardia}()', inicio, len(mensajes)))

        # En EA 15 los mensajes usan una separación vertical fija de 35.
        alto = 190 + len(mensajes) * 35
        for i, a in enumerate(actores.values()): ea.poner(d, a, 35 + i * 85, 35, 65, alto)
        for i, (n, _) in enumerate(vidas):
            ea.poner(d, objetos[n], 240 + i * 230, 35, 140, alto)
        for i, (a, b, mensaje, clase_mensaje) in enumerate(mensajes, 1):
            ea.mensaje_seq(d, grupo(a), grupo(b), mensaje.replace("'", '´'), i, clase_mensaje)
        for guarda, inicio, fin in marcos:
            fr = ea.elemento(raiz, '', 'InteractionFragment')
            fr.Subtype = 1  # opt, igual que el generador del P1
            fr.Update()
            parte = fr.Partitions.AddNew('x', ''); parte.Size = 100; fr.Update()
            y = 133 + (inicio - 1) * 35 - 26
            h = (fin - inicio + 1) * 35 + 34
            guid = '{' + str(uuid.uuid4()).upper() + '}'
            descripcion = f'@PAR;Name={guarda};Size={h};GUID={guid};@ENDPAR;'
            ea.r.Execute(f"UPDATE t_xref SET Description='{descripcion}' "
                         f"WHERE Client='{fr.ElementGUID}' AND Name='Partitions'")
            ea.poner(d, fr, 15, y, 1100, h, seq=60)
    else:
        # Una fila por recorrido evita cruces entre pantallas o actores cuando
        # el CU abarca varias acciones. Los objetos y enlaces son los del P1.
        escenas = []
        for paso in pasos:
            if paso[0].startswith('@'): escenas.append([])
            escenas[-1].append(paso)
        numero = 0
        for fila, escena in enumerate(escenas):
            y = 65 + fila * 210
            nombres = list(dict.fromkeys([x for a, b, _ in escena for x in (a, b)]))
            objetos = {}
            for col, n in enumerate(nombres):
                tipo_obj = 'Actor' if n.startswith('@') else 'Object'
                st = '' if tipo_obj == 'Actor' else {
                    'client page': 'boundary', 'module': 'boundary', 'negocio': 'control',
                    'datos': 'entity', 'model': 'entity'}.get(clases[n]['estereotipo'], 'control')
                e = ea.elemento(raiz, n.lstrip('@'), tipo_obj, st)
                objetos[n] = e
                ea.poner(d, e, 35 + col * 220, y, 65, 65)
            for a, b, txt in escena:
                numero += 1
                enlace = ea.conector(objetos[a], objetos[b], 'Association')
                corto = txt if len(txt) <= 36 else txt[:33] + '...'
                ea.mensaje_com(d, enlace, objetos[a], objetos[b], corto.replace("'", '´'), str(numero), numero, 0)
    ea.exportar(d, archivo)


def despliegue(ea, modelo):
    raiz = paquete(ea, modelo, 'Diseño de Despliegue')
    d = diagrama(ea, raiz, 'Diagrama de despliegue del sistema', 'Deployment', 'despliegue.png')
    if not d: return
    # El compose actual corre localmente. El VPS Contabo es destino previsto,
    # sin atribuir al proyecto un despliegue de producción inexistente.
    especificaciones = [
        ('Usuario', 'Device', None, 35, 300, 145, 100),
        ('Navegador web', 'ExecutionEnvironment', 'Usuario', 50, 350, 115, 45),
        ('Servidor local Docker', 'Device', None, 230, 35, 950, 510),
        ('Presentación React + Vite :5173', 'ExecutionEnvironment', 'Servidor local Docker', 270, 110, 240, 145),
        ('Negocio Laravel API REST :8001', 'ExecutionEnvironment', 'Servidor local Docker', 590, 110, 240, 145),
        ('Datos PostgreSQL :5432', 'ExecutionEnvironment', 'Servidor local Docker', 900, 110, 240, 145),
        ('VPS Contabo (despliegue previsto)', 'Device', None, 260, 610, 850, 150),
    ]
    el = {}
    for n, tipo, padre, x, y, w, h in especificaciones:
        el[n] = ea.elemento(raiz, n, tipo, padre=el.get(padre))
        ea.poner(d, el[n], x, y, w, h, seq=8 if tipo == 'Device' else 1)
    for a, b, protocolo in [
        ('Navegador web', 'Presentación React + Vite :5173', 'HTTP 5173'),
        ('Presentación React + Vite :5173', 'Negocio Laravel API REST :8001', 'HTTP/JSON REST'),
        ('Negocio Laravel API REST :8001', 'Datos PostgreSQL :5432', 'SQL TCP 5432'),
    ]: ea.conector(el[a], el[b], 'CommunicationPath', protocolo, dirigido=True)
    ea.exportar(d, 'despliegue.png')


def main():
    ea_base.SALIDA.mkdir(exist_ok=True)
    ea = ea_base.EA.abrir_existente()
    try:
        _, actores, casos = requisitos(ea, ea.modelo)
        paquetes(ea, ea.modelo, actores, casos)
        col = paquete(ea, ea.modelo, 'Análisis de Colaboración')
        seq = paquete(ea, ea.modelo, 'Diseño de Secuencia')
        for cu in C.CU:
            diagrama_interaccion(ea, col, cu, 'Comunicación', f'com-{cu.lower()}.png')
            diagrama_interaccion(ea, seq, cu, 'Secuencia', f'sd-{cu.lower()}.png')
        despliegue(ea, ea.modelo)
    finally:
        ea.cerrar()
    print(f'Exportados {len(ea.exportados)} diagramas PNG y EMF en {ea_base.SALIDA}')


if __name__ == '__main__': main()
