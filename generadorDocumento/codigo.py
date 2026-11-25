"""Lee el código real de crm-web para que el documento no pueda contradecirlo:
rutas de negocio/routes/api.php, funciones de presentacion/src/api/<area>.js, páginas que las llaman, y la cadena
Controller → Request → Service → Repository → Model con sus métodos reales (REGLAS_DOCUMENTO_P2.md §6b).
Nada de aquí se escribe a mano: si el código cambia, el documento cambia o el chequeo falla.
Uso: python codigo.py  -> imprime la cadena de clases por CU y los errores."""
import re
from functools import cache

import esquema
from rutas import CRM_WEB

NEG, PRE, DAT = CRM_WEB / 'negocio', CRM_WEB / 'presentacion' / 'src', CRM_WEB / 'datos'
# rutas sin sección "// CUn —" en api.php (públicas y sesión): CU según la pantalla que las usa
CU_SIN_SECCION = {'login': 'CU1', 'me': 'CU1', 'actualizarPerfil': 'CU1', 'cambiarPassword': 'CU1', 'logout': 'CU1',
                  'visita': 'CU1', 'buscar': 'CU1', 'foto': 'CU1', 'salud': None,
                  'programas': 'CU2', 'registrarInteres': 'CU2'}


def _leer(p):
    return p.read_text(encoding='utf-8')


def norm(ruta):
    """'/intereses/{interes}/estado' y '/intereses/${nro}/estado' -> '/intereses/{}/estado'."""
    return '/' + re.sub(r'\$?\{[^}]*\}', '{}', ruta).strip('/')


def _args(texto):
    """Argumentos de una llamada (texto desde después del '(' ) separados en el primer nivel."""
    res, nivel, actual = [], 0, ''
    for ch in texto:
        if ch in '([{': nivel += 1
        elif ch in ')]}':
            if nivel == 0: break
            nivel -= 1
        if ch == ',' and nivel == 0: res.append(actual.strip()); actual = ''
        else: actual += ch
    return res + [actual.strip()] if actual.strip() else res


# ------------------------------------------------------------------ capa 2: rutas de la API
@cache
def rutas_api():
    """[dict(verbo, ruta, clave, controlador, metodo, recursos, cu)] en el orden de api.php."""
    import contenido
    recursos_cu = {c: r['cu'] for c, r in contenido.RECURSOS.items()}
    res, seccion, grupo = [], [], []
    for linea in _leer(NEG / 'routes' / 'api.php').splitlines():
        if m := re.match(r'\s*//\s*((?:CU\d\s*/?\s*)+)—', linea):
            seccion = re.findall(r'CU\d', m.group(1))
        if (m := re.search(r"Route::middleware\('acceso:([^']+)'\)->group", linea)): grupo = [m.group(1)]
        elif re.match(r'\s*}\);', linea) and grupo: grupo = []
        m = re.search(r"Route::(get|post|put|patch|delete)\('([^']+)',\s*\[(\w+)::class,\s*'(\w+)'\]\)", linea)
        if not m: continue
        verbo, ruta, ctrl, met = m.groups()
        acc = re.search(r"acceso:([^',]+)", linea)
        recs = (acc.group(1) if acc else grupo[0] if grupo else '').split('|')
        recs = [r for r in recs if r]
        if len(seccion) == 1: cu = seccion[0]
        elif seccion: cu = next((recursos_cu[r] for r in recs if recursos_cu.get(r) in seccion), seccion[0])
        else: cu = CU_SIN_SECCION.get(met, '?')
        res.append(dict(verbo=verbo.upper(), ruta=ruta, clave=(verbo.upper(), norm(ruta)), controlador=ctrl,
                        metodo=met, recursos=recs, cu=cu))
    return res


# ------------------------------------------------------------------ capa 1: api/<area>.js y páginas
@cache
def funciones_api():
    """{'intereses.index': dict(modulo, nombre, params, verbo, ruta)} de presentacion/src/api/*.js."""
    res = {}
    for f in sorted((PRE / 'api').glob('*.js')):
        if f.stem == 'cliente': continue
        txt = _leer(f)
        ayudas = {n: (ps, cuerpo) for n, ps, cuerpo in re.findall(r'const (\w+) = \(([^)]*)\) => `([^`]*)`', txt)}
        for nombre, params, verbo, resto in re.findall(r'export const (\w+) = \(([^)]*)\) => cliente\.(\w+)\((.*)', txt):
            ruta = _args(resto)[0]
            for n, (_, cuerpo) in ayudas.items():   # ruta(correo) / ${cuota(orden, nro)} -> plantilla del ayudante
                ruta = re.sub(r'\$?\{?\b%s\([^)]*\)\}?' % n, cuerpo, ruta)
            res[f'{f.stem}.{nombre}'] = dict(modulo=f.stem, nombre=nombre, params=[p.strip() for p in params.split(',') if p.strip()],
                                             verbo=verbo.upper(), ruta=norm(ruta.strip('\'"`')))
    return res


@cache
def usos_api():
    """{archivo relativo a src: {'intereses.index', …}}: qué funciones de api/ llama cada página o componente."""
    res = {}
    for f in sorted(PRE.rglob('*.js*')):
        if f.parent.name == 'api': continue
        txt = _leer(f)
        alias = dict((a, m) for a, m in re.findall(r"import \* as (\w+) from '(?:\.\./)+api/(\w+)'", txt))
        usos = {f'{alias[a]}.{n}' for a, n in re.findall(r'\b(\w+)\.(\w+)\(', txt) if a in alias}
        for a in alias:   # llamada dinámica pagosApi[accion](…) con accion = 'aprobar' | 'rechazar'
            if f'{a}[' in txt:
                usos |= {k for k in funciones_api() if k.startswith(alias[a] + '.') and f"'{k.split('.')[1]}'" in txt}
        if usos: res[f.relative_to(PRE).as_posix()] = usos
    return res


@cache
def usos_servicio_auth():
    """Archivos que llaman a la API de sesión a través de servicios/auth.js (login, logout, perfil, refrescar)."""
    txt = _leer(PRE / 'servicios' / 'auth.js')
    con_api = {n: f'+{n}({ps})' for n, ps, cuerpo in
               re.findall(r'export (?:async )?function (\w+)\(([^)]*)\)(.*?)(?=\nexport |\Z)', txt, re.S) if 'authApi.' in cuerpo}
    res = set()
    for f in PRE.rglob('*.jsx'):
        m = re.search(r"import \{([^}]*)\} from '(?:\.\./)+servicios/auth'", _leer(f))
        if m and set(con_api) & {x.strip() for x in m.group(1).split(',')}: res.add(f.name)
    return con_api, res


@cache
def paginas_router():
    """{'/embudo': 'Embudo', …} de presentacion/src/rutas.jsx."""
    txt = _leer(PRE / 'rutas.jsx').split('const PAGINAS')[1].split('}')[0]
    return dict(re.findall(r"'(/[\w-]+)': '(\w+)'", txt))


# ------------------------------------------------------------------ PHP: clases, métodos y llamadas
def _cuerpo(txt, inicio):
    nivel = 0
    for i in range(inicio, len(txt)):
        nivel += {'{': 1, '}': -1}.get(txt[i], 0)
        if nivel == 0: return txt[inicio + 1:i]
    return txt[inicio:]


def _param(p):
    """'?string $excepto = null' -> 'excepto: ?string'; 'OrdenPago $orden' -> 'orden: OrdenPago'."""
    p = p.split('=')[0].strip()
    tipo, _, nombre = p.rpartition(' ')
    return f'{nombre.lstrip("$&.")}: {tipo}' if tipo else nombre.lstrip('$&.')


@cache
def clases_php():
    """{Nombre: dict(capa, estereotipo, props {prop: Tipo}, metodos {m: dict(vis, firma, cuerpo, params)}, tabla, campos)}."""
    carpetas = [(NEG / 'app' / 'Http' / 'Controllers' / 'Api', 'Negocio', 'controller'),
                (NEG / 'app' / 'Http' / 'Requests', 'Negocio', 'request'),
                (NEG / 'app' / 'Services', 'Negocio', 'service'),
                (DAT / 'src' / 'Repositorios', 'Datos', 'repository'),
                (DAT / 'src' / 'Modelos', 'Datos', 'model')]
    res = {}
    for carpeta, capa, st in carpetas:
        for f in sorted(carpeta.rglob('*.php')):
            txt = _leer(f)
            m = re.search(r'^(?:final |abstract )?class (\w+)', txt, re.M)
            if not m: continue
            props = dict((n, t) for t, n in re.findall(r'(?:private|protected|public) readonly \??([\w\\]+) \$(\w+)', txt))
            metodos = {}
            for mm in re.finditer(r'(public|protected|private)( static)? function (\w+)\(([^)]*)\)(?:\s*:\s*([?\w\\|]+))?\s*\{', txt):
                vis, est, nombre, params, ret = mm.groups()
                if nombre == '__construct': continue
                ps = [_param(p) for p in params.split(',') if p.strip()]
                firma = f'{nombre}({", ".join(ps)})' + (f': {ret}' if ret else '')
                metodos[nombre] = dict(vis={'public': '+', 'protected': '#', 'private': '-'}[vis], firma=firma,
                                       cuerpo=_cuerpo(txt, mm.end() - 1), params=params)
            tabla = re.search(r"protected \$table = '(\w+)'", txt)
            campos = []
            if st == 'request' and 'rules' in metodos:
                campos = list(dict.fromkeys(re.findall(r"^\s*'([\w.*]+)' =>", metodos['rules']['cuerpo'], re.M)))
            res[m.group(1)] = dict(capa=capa, estereotipo=st, archivo=f, props=props, metodos=metodos,
                                   tabla=tabla.group(1) if tabla else None, campos=campos)
    return res


TIPO_CORTO = [(r'character varying', 'varchar'), (r'timestamp\((\d)\) without time zone', r'timestamp(\1)'),
              (r'timestamp without time zone', 'timestamp')]


def atributos_modelo(tabla):
    """Columnas de la tabla del modelo con su tipo de la BD (fuentes/esquema.sql), en el orden del CREATE TABLE."""
    res = []
    for col, tipo, *_ in esquema.tablas().get(tabla, []):
        for a, b in TIPO_CORTO: tipo = re.sub(a, b, tipo)
        res.append(f'{col}: {tipo}')
    return res


def _llamadas(clase, metodo, C):
    """[(Clase destino, método)] que hace clase::metodo: $this->prop->m(), $this->m() (se sigue), Clase::m() estático."""
    cuerpo = C[clase]['metodos'][metodo]['cuerpo']
    res = [(C[clase]['props'][p].rsplit('\\', 1)[-1], m) for p, m in re.findall(r'\$this->(\w+)->(\w+)\(', cuerpo)
           if p in C[clase]['props']]
    res += [(clase, m) for m in re.findall(r'\$this->(\w+)\(', cuerpo)]
    res += [(c, m) for c, m in re.findall(r'\b([A-Z]\w+)::(\w+)\(', cuerpo) if c in C and C[c]['estereotipo'] in ('service', 'repository')]
    return list(dict.fromkeys(res))


# ------------------------------------------------------------------ cadena por CU (5.3.2)
def cadena(cu):
    """Clases y dependencias del CU leídas del código. Devuelve (clases, dependencias, errores):
    clases = {nombre: dict(capa, estereotipo, atributos [str], metodos [str])}; dependencias = {(a, b)}."""
    C, F, U = clases_php(), funciones_api(), usos_api()
    por_ruta = {(f['verbo'], f['ruta']): k for k, f in F.items()}
    clases, deps, errores = {}, set(), []

    def clase(nombre, capa, st, atributos=()):
        x = clases.setdefault(nombre, dict(capa=capa, estereotipo=st, atributos=list(atributos), metodos={}))
        return x

    def metodo(nombre_clase, m, visitados):
        if (nombre_clase, m) in visitados: return
        visitados.add((nombre_clase, m))
        c = C[nombre_clase]
        if m not in c['metodos']:
            if c['estereotipo'] == 'model': return   # métodos heredados de Eloquent (query, create…)
            errores.append(f'{cu}: {nombre_clase} no tiene el método {m}()'); return
        x = clase(nombre_clase, c['capa'], c['estereotipo'],
                  atributos_modelo(c['tabla']) if c['tabla'] else c['campos'])
        x['metodos'][m] = c['metodos'][m]['vis'] + c['metodos'][m]['firma']
        for destino, mm in _llamadas(nombre_clase, m, C):
            if destino not in C: errores.append(f'{cu}: {nombre_clase}.{m}() llama a {destino}, que no está en crm-web'); continue
            if destino != nombre_clase: deps.add((nombre_clase, destino))
            metodo(destino, mm, visitados)
        if c['estereotipo'] == 'repository':   # modelos que usa el repositorio
            for mod in dict.fromkeys(re.findall(r'(?:new |\b)([A-Z]\w+)(?=::|\s+\$|\(\))', c['metodos'][m]['cuerpo'] + ' ' + c['metodos'][m]['params'])):
                if mod in C and C[mod]['estereotipo'] == 'model':
                    clase(mod, 'Datos', 'model', atributos_modelo(C[mod]['tabla']))
                    deps.add((nombre_clase, mod))

    visitados = set()
    for r in rutas_api():
        if r['cu'] != cu: continue
        fn = por_ruta.get(r['clave'])
        if not fn: continue   # ruta que ninguna pantalla llama: se informa aparte (rutas_sin_pantalla)
        ctrl = r['controlador']
        if ctrl not in C or r['metodo'] not in C[ctrl]['metodos']:
            errores.append(f'{cu}: {r["verbo"]} {r["ruta"]} apunta a {ctrl}@{r["metodo"]}, que no existe'); continue
        f = F[fn]
        modulo = f'api/{f["modulo"]}.js'
        clase(modulo, 'Presentacion', 'module')['metodos'][f['nombre']] = f'+{f["nombre"]}({", ".join(f["params"])})'
        deps.add((modulo, ctrl))
        for archivo, usos in U.items():
            if fn not in usos: continue
            if archivo == 'servicios/auth.js':   # sesión: Login.jsx / Shell.jsx → servicios/auth.js → api/auth.js
                funciones, paginas = usos_servicio_auth()
                clase(archivo, 'Presentacion', 'module')['metodos'].update(funciones); deps.add((archivo, modulo))
                for pagina in paginas:
                    clase(pagina, 'Presentacion', 'client page'); deps.add((pagina, archivo))
            elif archivo.startswith(('paginas/', 'componentes/', 'plantilla/')):
                pagina = archivo.rsplit('/', 1)[-1]
                clase(pagina, 'Presentacion', 'client page'); deps.add((pagina, modulo))
        metodo(ctrl, r['metodo'], visitados)
        for t in re.findall(r'(\w+Request) \$', C[ctrl]['metodos'][r['metodo']]['params']):
            if t in C:
                clase(t, 'Negocio', 'request', C[t]['campos'])['metodos'].setdefault('rules', '+rules(): array')
                deps.add((ctrl, t))
    # §6b: solo dependencias que bajan de capa o quedan en la misma
    orden = {'Presentacion': 0, 'Negocio': 1, 'Datos': 2}
    for a, b in deps:
        if orden[clases[a]['capa']] > orden[clases[b]['capa']]: errores.append(f'{cu}: dependencia que sube de capa {a} -> {b}')
    for x in clases.values(): x['metodos'] = list(x['metodos'].values())
    return clases, deps, errores


def rutas_sin_pantalla():
    """Rutas de api.php que ninguna función de presentacion/src/api llama."""
    usadas = {(f['verbo'], f['ruta']) for f in funciones_api().values()}
    return [r for r in rutas_api() if r['clave'] not in usadas]


def errores_codigo():
    """Lo que no cuadra entre capas: funciones de api/ sin ruta, rutas a métodos inexistentes, funciones sin uso."""
    errores, rutas = [], {r['clave']: r for r in rutas_api()}
    C = clases_php()
    for k, f in funciones_api().items():
        r = rutas.get((f['verbo'], f['ruta']))
        if not r: errores.append(f'api/{f["modulo"]}.js {f["nombre"]}(): {f["verbo"]} {f["ruta"]} no existe en routes/api.php'); continue
        if r['metodo'] not in C.get(r['controlador'], {}).get('metodos', {}):
            errores.append(f'{r["verbo"]} {r["ruta"]}: {r["controlador"]}@{r["metodo"]} no existe')
        if f['nombre'] != r['metodo']:
            errores.append(f'api/{f["modulo"]}.js {f["nombre"]}() llama a {r["controlador"]}@{r["metodo"]}: el nombre no coincide')
    usadas = set().union(*usos_api().values())
    errores += [f'api/{k.replace(".", ".js ")}() no la llama ninguna página' for k in funciones_api() if k not in usadas]
    errores += [f'{r["verbo"]} {r["ruta"]}: sin CU (agregar sección "// CUn —" en api.php)' for r in rutas_api() if r['cu'] == '?']
    return errores


if __name__ == '__main__':
    for cu in [f'CU{i}' for i in range(1, 9)]:
        cl, dp, er = cadena(cu)
        print(f'\n{cu}: {len(cl)} clases, {len(dp)} dependencias')
        for n, x in cl.items(): print(f'  «{x["estereotipo"]}» {n}: {", ".join(x["metodos"])[:150]}')
        for e in er: print('  ERROR', e)
    print('\nrutas sin pantalla:', [f'{r["verbo"]} {r["ruta"]}' for r in rutas_sin_pantalla()])
    print('errores entre capas:', errores_codigo())
