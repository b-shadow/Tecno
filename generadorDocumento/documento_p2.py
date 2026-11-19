"""Genera documento/P2-INF513-GRUPO05SA.docx con la estructura del documento aprobado del Grupo 07 (REGLAS_DOCUMENTO_P2.md).
  python documento_p2.py
  powershell -File exportar.ps1   (índice, .doc y .pdf en documento/, reemplazando los anteriores)
Textos: contenido.py · BD: esquema.py (fuentes/esquema.sql) · navegación: navegacion.py · diagramas: ea/ea_p2.py."""
import json, pathlib, re, sys

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from rutas import CRM_WEB, DIAGRAMAS, DOCUMENTO  # noqa: E402
import contenido as C  # noqa: E402
import codigo  # noqa: E402
import esquema  # noqa: E402
import navegacion  # noqa: E402
from formato_g07 import G07, PENDIENTES, MARGEN_NAV  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.shared import Cm  # noqa: E402
IZQ = WD_ALIGN_PARAGRAPH.LEFT   # 11.–13. sin línea de capítulo: B16 a la izquierda

DIAG = DIAGRAMAS
FRANJAS = DIAG / 'franjas'; FRANJAS.mkdir(parents=True, exist_ok=True)
d = G07()
cu_num = lambda cu: int(cu[2:])

# ------------------------------------------------------------------ carátula e índice
d.caratula(C.TITULO)
d.indice()

# ------------------------------------------------------------------ Capítulo I
d.h('Capítulo I: Perfil', 1)
d.h('1 Introducción', 2); d.texto(C.INTRODUCCION, 'Introducción')
d.h('2 Antecedentes y Justificación', 2); d.texto(C.ANTECEDENTES, 'Antecedentes y Justificación')
d.h('3 Planteamiento de Problema', 2); d.texto(C.PROBLEMA, 'Planteamiento de Problema')
d.h('4 Objetivo', 2)
d.h('4.1 Objetivo General', 3); d.texto(C.OBJETIVO_GENERAL, 'Objetivo General')
d.h('4.2 Objetivos Específicos', 3)
d.vinetas(C.OBJETIVOS_ESPECIFICOS) if C.OBJETIVOS_ESPECIFICOS else d.pendiente('Objetivos Específicos')
d.h('5 Alcance', 2)
for cu, nombre in C.CU.items():
    d.p(f'**{cu}. {nombre}:** ' + C.ALCANCE[cu]) if C.ALCANCE.get(cu) else d.pendiente(f'Alcance {cu}')
d.h('6 Metodología', 2); d.texto(C.METODOLOGIA, 'Metodología')
for fase, texto in C.FASES.items():
    d.p(f'**{fase}** {texto}') if texto else d.pendiente(f'Metodología: {fase}')
if C.METODOLOGIA_CIERRE: d.p(C.METODOLOGIA_CIERRE)

# ------------------------------------------------------------------ Capítulo II
d.h('Capítulo II: Fundamentación Teórica', 1)
d.h('1. Programación del lado del servidor', 2); d.texto(C.PROGRAMACION_SERVIDOR, 'Programación del lado del servidor')
for i, (tema, texto) in enumerate(C.TEORIA.items(), 1):
    d.h(f'1.{i}. {tema}', 3); d.texto(texto, tema)

# ------------------------------------------------------------------ Capítulo III
d.h('Capítulo III: Organización', 1)
d.h('2. Empresa', 2)
d.texto(C.ORGANIZACION_CONTEXTO, 'Contexto de la organización')
for i, (t, v) in enumerate((('Misión', C.MISION), ('Visión', C.VISION), ('Objetivo', C.OBJETIVO_EMPRESA),
                            ('Ubicación', C.UBICACION)), 1):
    d.h(f'2.{i}. {t}', 3); d.texto(v, t)
    if t == 'Ubicación':
        d.imagen(DIAG / 'ubicacion.png', pie=C.UBICACION_FIGURA, ancho=15.5, alto_max=7.5)
        d.p(C.UBICACION_FUENTE)
        d.texto(C.INFRAESTRUCTURA, 'Infraestructura')
        d.vinetas(C.INFRAESTRUCTURA_AREAS)
d.h('2.5. Organigrama', 3)
d.imagen(DIAG / 'organigrama.png', pie=C.ORGANIGRAMA, ancho=11.0, alto_max=14.5)

# ------------------------------------------------------------------ Capítulo IV
d.h('Capítulo IV: Especificación de Requerimientos', 1)
d.h('3. Requisitos Específicos', 2)
d.h('3.1. Requerimiento Funcional', 3)
for i, (titulo, texto) in enumerate(C.REQUERIMIENTOS, 1):
    d.h(f'R{i} {titulo}', 4); d.texto(texto, f'R{i} {titulo}')

# ------------------------------------------------------------------ Capítulo V
d.h('Capítulo V: Captura de Requisitos', 1)
d.h('4. Identificación De Casos De Uso Y Actores', 2)
d.h('4.1. Identificar Actores', 3)
d.imagen(DIAG / 'actores.png')
d.tabla_gris(['Usuario', 'Características'], [(a, c or '[PENDIENTE]') for a, c in C.ACTORES], negrita_primera=True, anchos=(3.5, 12.1))
d.h('4.2. Identificación de casos de uso', 3)
d.tabla_gris(['ID', 'NOMBRE'], list(C.CU.items()), anchos=(2.0, 13.6))
d.h('4.3. Priorización de casos de uso', 3)
d.p(C.PRIORIDAD_CRITERIO)
d.tabla_gris(['ID', 'NOMBRE', 'PRIORIDAD'], [(cu, n, C.PRIORIDAD.get(cu, '[PENDIENTE]')) for cu, n in C.CU.items()], anchos=(2.0, 10.6, 3.0))
d.h('4.4. Detalle de Casos de Uso', 3)
for cu, nombre in C.CU.items():
    x = C.DETALLE.get(cu, {})
    d.imagen(DIAG / f'uc-{cu.lower()}.png', f'{cu}. {nombre}', ancho=13)
    d.tabla_cu(f'CU{cu_num(cu):02d}', x.get('gestionar') or nombre, [
        ('Propósito', x.get('proposito')), ('Descripción', x.get('descripcion')),
        ('Actores', ', '.join(x.get('actores') or C.actores_cu(cu)) + '.'), ('Actor Iniciador', x.get('iniciador')),
        ('Precondición', x.get('precondicion')), ('Proceso', x.get('proceso')),
        ('Postcondición', x.get('postcondicion')),
        *(([('Flujos Alternativos', '\n'.join(x['alternativos']))]) if x.get('alternativos') else []),
        ('Excepciones', '\n'.join(x.get('excepciones', [])))])
d.h('4.5. Diagrama General de Caso de Uso', 3)
d.imagen(DIAG / 'uc-general.png')

# ------------------------------------------------------------------ Capítulo VI
d.h('Capítulo VI: Análisis de Arquitectura', 1)
d.h('5. Análisis de la Arquitectura', 2)
d.h('5.1. Modelo de Dominio', 3)
d.h('5.1.1. Identificar Paquetes', 4)
d.imagen(DIAG / 'paquetes.png')
for paq, x in C.PAQUETES.items():
    d.p(f'**{paq}**'); d.p(x['descripcion'])
if not C.PAQUETES: d.pendiente('Paquetes y su descripción')
d.h('5.2. Relacionar Paquetes con casos de uso', 3)
for i, paq in enumerate(C.PAQUETES):
    d.imagen(DIAG / f'paquete-{i + 1}.png', f'Módulo de {paq}', pie=f'Relacionar Paquetes con casos de uso. Módulo de {paq}' if i == 0 else None)
d.h('5.3. Análisis de Caso de Uso', 3)
d.h('5.3.1. Diagramas de Colaboración', 4)
for cu, nombre in C.CU.items():
    d.imagen(DIAG / f'com-{cu.lower()}.png', f'{cu}. {nombre}', alto_max=10)
d.h('5.3.2. Análisis de clases', 4)   # 3 capas reales por CU (codigo.py → ea_p2.clases_cu), una página cada uno
for i, (cu, nombre) in enumerate(C.CU.items()):   # una figura por área del CU (cls-cuN.png o cls-cuN-k.png)
    figs = sorted(DIAG.glob(f'cls-{cu.lower()}-*.png'), key=lambda f: int(f.stem.rsplit('-', 1)[1])) or [DIAG / f'cls-{cu.lower()}.png']
    for k, fig in enumerate(figs, 1):
        if i or k > 1: d.salto()
        d.imagen(fig, f'{cu}. {nombre}' + (f' ({k}/{len(figs)})' if len(figs) > 1 else ''), alto_max=20)

# ------------------------------------------------------------------ Capítulo VII
d.seccion(True)   # 6.1 apaisada para imprimir el despliegue legible: títulos y diagrama en la misma página
d.h('Capítulo VII: Diseño', 1)
d.h('6. Diseño de la Arquitectura', 2)
d.h('6.1. Diseño Físico de la Arquitectura (Diagrama de Despliegue)', 3)
d.imagen(DIAG / 'despliegue.png', ancho=25.9, alto_max=13.2)   # 13,2 cm: lo que dejan los tres títulos
d.seccion(False, MARGEN_NAV)   # el conceptual en una sola página, casi a todo el ancho (como G07 pág. 63)
d.h('7. Diseño de Datos', 2)
d.h('7.1. Diseño Conceptual de Base de Datos', 3)
d.imagen(DIAG / 'conceptual.png', ancho=19.5, alto_max=19.5)
d.seccion(False, MARGEN_NAV)   # Mapeo con 1 cm de margen lateral: cada tabla entera y horizontal (decisión del usuario)
d.h('7.2. Diseño Lógico', 3)   # el lógico es el mapeo (pedido del usuario: título 7.2 Diseño Lógico, luego Mapeo)
d.h('7.2.1. Mapeo', 4)
T, PK, FKC = esquema.tablas(), esquema.pks(), esquema.columnas_fk()
for t in esquema.orden_mapeo():
    marca = lambda c: ' '.join(m for m, si in (('pk', c in PK[t]), ('fk', (t, c) in FKC)) if si)
    cols = [c for c, *_ in T[t]]
    orden = [c for c in cols if c in PK[t]] + [c for c in cols if c not in PK[t] and (t, c) not in FKC] + \
            [c for c in cols if c not in PK[t] and (t, c) in FKC]
    d.tabla_mapeo(t, [(c, marca(c)) for c in orden], ancho=19.5)
d.seccion(False)
d.h('7.3. Diseño Físico', 3)
for t in sorted(T):
    d.fisico(t, T[t])
d.h('7.4. Diseño de casos de uso (Diagrama de secuencia)', 3)
for i, (cu, nombre) in enumerate(C.CU.items()):
    if i: d.salto()
    d.h(f'{cu}. {nombre}', 4)
    d.imagen(DIAG / f'sd-{cu.lower()}.png', alto_max=19)
for i, actor in enumerate(navegacion.ACTORES, 1):   # 7.5 va en la primera página apaisada, como G07
    titulos = [('7.5. Diseño de Navegación', 3)] if i == 1 else []
    d.franjas(DIAG / f'nav-{actor.lower()}.png', titulos + [(f'7.5.{i}. Diagrama de Navegación del {actor}', 4)], FRANJAS,
              primero=i == 1)
d.seccion(False)
d.h('7.6. Diagrama de interfaces', 3)
d.pendiente('Capturas de pantalla: "Diagrama de Interfaz CUn. Nombre", 2 por página (crm-web/scripts/capturas_p2.mjs)')

# ------------------------------------------------------------------ Capítulos VIII–X y cierre
d.h('Capítulo VIII: Implementación', 1)
d.h('8. Implementación del Sistema', 2)
d.h('8.1. Herramientas para Desarrollo', 3)
NEGOCIO, PRESENTACION = CRM_WEB / 'negocio', CRM_WEB / 'presentacion'
LOCK = {'composer': {x['name']: x['version'].lstrip('v') for x in json.loads((NEGOCIO / 'composer.lock').read_text(encoding='utf-8'))['packages']},
        'npm': {k.removeprefix('node_modules/'): v.get('version') for k, v in
                json.loads((PRESENTACION / 'package-lock.json').read_text(encoding='utf-8'))['packages'].items()}}
for grupo, items in C.HERRAMIENTAS.items():
    d.h(grupo, 4)
    for nombre, version, texto in items:
        if version and ':' in version:
            origen, paquete = version.split(':', 1); version = LOCK[origen][paquete]   # KeyError = paquete que ya no existe
        if version is None: PENDIENTES.append(f'versión de {nombre}')
        d.p(f'**{nombre}{" " + version if version else ""}{" [PENDIENTE versión]" if version is None else ""}:** ' + (texto or '[PENDIENTE]'))
        if not texto: PENDIENTES.append(f'descripción de {nombre}')
d.h('Capítulo IX: Resultados', 1)
d.h('9. Resultado Esperado', 2); d.texto(C.RESULTADO_ESPERADO, 'Resultado Esperado')
d.h('Capítulo X: Pruebas', 1)
d.h('10. Plan de Pruebas', 2)
for sub, titulo, pruebas in (('10.1.', 'Prueba de Caja Blanca', C.PRUEBAS_BLANCA), ('10.2.', 'Prueba de Caja Negra', C.PRUEBAS_NEGRA)):
    d.h(f'{sub} {titulo}', 3)
    if not pruebas: d.pendiente(titulo)
    for n, (t, obj, crit, *_) in enumerate(pruebas, 1):
        d.p(f'**{n}. {t}**'); d.vinetas([f'**Objetivo:** {obj}', f'**Criterio de éxito:** {crit}'], sub=True)
d.h('11. Conclusión', 1).alignment = IZQ
d.vinetas(C.CONCLUSIONES) if C.CONCLUSIONES else d.pendiente('Conclusión (una por objetivo específico)')
d.h('12. Bibliografía', 1).alignment = IZQ
for ref in sorted(C.BIBLIOGRAFIA):
    pf = d.p(ref).paragraph_format; pf.left_indent, pf.first_line_indent = Cm(1.27), Cm(-1.27)
if not C.BIBLIOGRAFIA: d.pendiente('Bibliografía')
d.h('13. Anexo', 1).alignment = IZQ
for i, (t, img) in enumerate(C.ANEXOS, 1):
    d.h(f'13.{i}. Anexo # {i}: {t}', 2); d.imagen(img)
_git = (CRM_WEB / '.git' / 'config').read_text(encoding='utf-8') if (CRM_WEB / '.git' / 'config').exists() else ''
URL_GITHUB = C.URL_GITHUB or next(iter(re.findall(r'url = (https://github\.com/\S+?)(?:\.git)?\s', _git)), None)
d.p(f'**URL Proyecto GitHub:** {URL_GITHUB}') if URL_GITHUB else d.pendiente('URL del repositorio GitHub')

# ------------------------------------------------------------------ coherencia del documento (falla si algo no cuadra)
def coherencia():
    errores = []
    if set(C.PRIORIDAD) != set(C.CU):
        errores.append(f'4.3: las prioridades deben cubrir exactamente los ocho casos de uso ({sorted(set(C.CU) ^ set(C.PRIORIDAD))})')
    for cu, prioridad in C.PRIORIDAD.items():
        if prioridad not in {'Alta', 'Media', 'Baja'}:
            errores.append(f'4.3 {cu}: prioridad no válida: {prioridad}')
    actores = [a for a, _ in C.ACTORES]
    if list(navegacion.ACTORES) != actores:
        errores.append(f'7.5 debe tener un diagrama de navegación por actor de 4.1 y en ese orden: {actores} vs {list(navegacion.ACTORES)}')
    for rol, permisos in C.PERMISOS.items():
        actor = rol.capitalize()
        paginas, _ = navegacion.ACTORES[actor]()
        if faltan := set(permisos) - set(paginas):
            errores.append(f'navegación de {actor}: faltan páginas de su menú {sorted(faltan)}')
        if sobran := {k for k in paginas if k in C.RECURSOS and not C.RECURSOS[k]['publico']} - set(permisos):
            errores.append(f'navegación de {actor}: páginas sin permiso {sorted(sobran)}')
        for r in permisos:
            if actor not in C.actores_cu(C.RECURSOS[r]['cu']):
                errores.append(f'{actor} usa "{C.RECURSOS[r]["nombre"]}" ({C.RECURSOS[r]["cu"]}) pero no es actor de ese CU')
    for cu in C.CU:
        if fuera := set(C.actores_cu(cu)) - set(actores): errores.append(f'{cu}: actores que no están en 4.1 {fuera}')
    # nada del stack ni de la organización de otros documentos (G07 era MVC con Inertia, Vue y JWT; el P1 era otra unidad)
    texto = chr(10).join([p.text for p in d.doc.paragraphs] + [c.text for t in d.doc.tables for f in t.rows for c in f.cells])
    for prohibido in ('MVC', 'Modelo-Vista', 'Vue', 'Inertia', 'JWT', 'Unidad de Capacitación', 'San Pablo'):
        if re.search(r'\b' + re.escape(prohibido) + r'\b', texto): errores.append(f'el documento menciona "{prohibido}", que no corresponde a este proyecto')
    # el documento no puede contradecir al código: BD, navegación, stack y cadena de clases se comparan con crm-web
    errores += [f'BD: {e} (refrescar fuentes/esquema.sql, ver README.md)' for e in esquema.diferencias_migraciones()]
    errores += [f'navegación: {e}' for e in navegacion.verificar()]
    errores += stack()
    errores += textos()
    errores += [f'código: {e}' for e in codigo.errores_codigo()]
    for cu in C.CU: errores += [f'5.3.2 {e}' for e in codigo.cadena(cu)[2]]
    if errores: raise SystemExit('INCOHERENCIAS:' + ''.join(chr(10) + ' - ' + e for e in errores))
    print('coherencia: actores = navegación = matriz de acceso = CU; esquema.sql = migraciones; navegación = páginas, '
          'api/ y rutas reales; Cap. II y herramientas = dependencias reales; 5.3.2 = clases y métodos reales')
    for r in codigo.rutas_sin_pantalla():   # no contradicen al documento (no aparecen en él), pero conviene saberlo
        print(f'  aviso: {r["verbo"]} {r["ruta"]} ({r["controlador"]}@{r["metodo"]}) no la llama ninguna pantalla')


def textos():
    """Lo escrito a mano en contenido.py que se puede verificar contra crm-web."""
    errores, codigo_neg = [], chr(10).join(f.read_text(encoding='utf-8') for d_ in (NEGOCIO / 'app', CRM_WEB / 'datos' / 'src')
                                        for f in d_.rglob('*.php'))
    for cu, x in C.DETALLE.items():   # cada mensaje citado en Excepciones existe en negocio/ o datos/
        for e in x.get('excepciones', []):
            for msg in re.findall(r'"([^"]+)"', e):
                if msg not in codigo_neg: errores.append(f'4.4 {cu}: el mensaje "{msg}" no está en negocio/ ni en datos/')
    for archivo, pruebas in (('verificar_p2.py', C.PRUEBAS_BLANCA), ('verificar_navegadores.mjs', C.PRUEBAS_NEGRA)):
        txt = (CRM_WEB / 'scripts' / archivo).read_text(encoding='utf-8')
        errores += [f'10: la prueba "{t}" no está en scripts/{archivo} ({caso})' for t, _, _, caso in pruebas if caso not in txt]
    todas, vistas = set(esquema.tablas()), [t for x in C.PAQUETES.values() for t in x['tablas']]
    if dup := {t for t in vistas if vistas.count(t) > 1}: errores.append(f'5.1.1: tablas en dos paquetes {sorted(dup)}')
    if falta := todas - set(vistas): errores.append(f'5.1.1: tablas sin paquete {sorted(falta)}')
    if sobra := set(vistas) - todas: errores.append(f'5.1.1: tablas que no existen {sorted(sobra)}')
    if sin := set(C.CU) - {c for x in C.PAQUETES.values() for c in x['cu']}: errores.append(f'5.1.1: CU sin paquete {sorted(sin)}')
    return errores


def stack():
    """Cap. II y 8.1 solo con lo que está en crm-web (C.EVIDENCIA); nada de otro stack en las dependencias."""
    comp = json.loads((NEGOCIO / 'composer.json').read_text(encoding='utf-8'))
    pkg = json.loads((PRESENTACION / 'package.json').read_text(encoding='utf-8'))
    deps = {'composer': {**comp['require'], **comp.get('require-dev', {})}, 'npm': {**pkg['dependencies'], **pkg['devDependencies']}}

    def hay(ev):
        origen, _, resto = ev.partition(':')
        if origen in deps: return resto in deps[origen]
        ruta, _, texto = ev.partition(':')
        p = CRM_WEB / ruta
        return p.exists() and (not texto or texto in (p.read_text(encoding='utf-8', errors='ignore') if p.is_file() else ''))

    errores = []
    for tema in C.TEORIA:
        if not (ev := C.EVIDENCIA.get(tema)): errores.append(f'Cap. II: "{tema}" no tiene evidencia en contenido.EVIDENCIA')
        elif not hay(ev): errores.append(f'Cap. II: "{tema}" ya no está en crm-web ({ev})')
    for items in C.HERRAMIENTAS.values():
        for nombre, version, _ in items:
            ev = version if version and ':' in version else C.EVIDENCIA.get(nombre)
            if not ev: errores.append(f'8.1: "{nombre}" no tiene evidencia en contenido.EVIDENCIA')
            elif ev == 'externa': continue   # Git, GitHub: se usan para trabajar, no están en el código
            elif not hay(ev): errores.append(f'8.1: "{nombre}" no es dependencia directa ni está en crm-web ({ev})')
    errores += [f'stack: {d} en las dependencias ({o}) es de otro stack' for o, ds in deps.items() for d in ds
                if any(x in d.lower() for x in C.STACK_AJENO)]
    if not LOCK['npm'].get('tailwindcss', '').startswith('4.'): errores.append('stack: el documento dice Tailwind CSS v4')
    return errores


coherencia()
DOCUMENTO.parent.mkdir(exist_ok=True)
d.guardar(DOCUMENTO)
print(f'\n{len(PENDIENTES)} PENDIENTES:'); [print(' -', x) for x in PENDIENTES]
print(f'\n{len(C.POR_CONFIRMAR)} POR CONFIRMAR con UNEXO:')
[print(' -', x) for x in C.POR_CONFIRMAR]
