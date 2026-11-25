"""Distribución horizontal del administrador. Las posiciones agrupan flujos locales
de navegación y reservan el centro para las páginas compartidas (menú y ficha).
"""
import re
from collections import Counter
from heapq import heappop, heappush
from itertools import chain, pairwise
from math import hypot

from ea.franjas_navegacion import medir

# Cada fila es una guía de coordenadas, con desplazamientos locales para acercar
# una pantalla a sus formularios, resultados y procesos. Las guías no se dibujan.
FILAS = (
    'actor login f_login ps_login bd_usuarios',
    'error404 ps_logout error menu ps_me bitacora pie',
    'f_clave ps_clave ps_visita f_perfil ps_perfil',
    'ps_foto_usuario f_usuario usuarios ps_usuario_g ps_usuarios',
    'ps_matriz matriz dashboard ps_dash reporte_csv',
    'bd_comisiones ps_comis seguimiento reportes ps_listado',
    'ps_pagar f_porcentaje ps_porcentaje ps_est resultados_busqueda',
    'bd_programas ps_sinc gestion-anuncios ps_catalogo ps_buscar',
    'motivos f_motivo ps_motivo_g catalogo plantilla_csv',
    'f_csv ps_csv prospectos ps_prosp f_nuevo_interes',
    'ps_repartir interesados f_prospecto ps_alta ps_nuevo_interes',
    'f_perdida embudo ps_mover ps_intereses bd_intereses',
    'f_editar ps_update ficha agenda ps_show',
    'f_realizada ps_completar ps_estmetodo whatsapp f_contacto',
    'validacion-pagos f_revisar f_record ps_crearrec ps_interac',
    'ps_comp ps_aprobar ps_rechazar f_anular ps_anular_orden',
    'bd_cuotas ps_cuotas compartir f_correo ps_setup_stripe',
    'ps_resultado alumnos ps_exportar ps_enviar ps_checkout',
    'notificaciones ps_leida f_notif stripe pago_confirmacion',
    '- - pago_cancelado ps_cancelar_publico ps_retorno_publico',
    '- - ps_cancelar_checkout - ps_confirmar_checkout',
)
DESFASES = {
    'actor': (1, 0), 'ps_login': (0, 1), 'error': (-1, 0),
    'f_perfil': (0, -1), 'matriz': (0, 1), 'seguimiento': (0, -1),
    'prospectos': (0, -1), 'ps_prosp': (0, 1), 'ps_mover': (0, 1),
    'ficha': (0, -1), 'agenda': (0, 1), 'whatsapp': (0, -1),
    'f_revisar': (0, 1), 'compartir': (0, -1), 'stripe': (0, 1),
    'bitacora': (-65, 6),  # entre las dos primeras filas de opciones, a la izquierda
    'pie': (-52, 6),       # junto a Registrar Visita, entre Aviso y la fila de perfil
    'ps_cancelar_checkout': (0, -5), 'ps_confirmar_checkout': (0, -5),
}
TAMANOS = {'menu': (13, 6), 'error': (7, 5), 'f_login': (7, 6), 'f_revisar': (7, 5),
           'ps_cancelar_publico': (10, 4), 'ps_retorno_publico': (11, 4)}

PASO = 22
# Límites de las franjas aprobadas, en coordenadas del lienzo.
ALTURAS_DE_CORTE = (850, 1834, 2850, 3778, 4850)
DIRECCIONES = ((1, 0), (0, 1), (-1, 0), (0, -1))


def _puertos(caja):
    x, y, w, h = caja
    for i in range(x + 1, x + w):
        yield (i, y), (i, y - 1), 3
        yield (i, y + h), (i, y + h + 1), 1
    for j in range(y + 1, y + h):
        yield (x, j), (x - 1, j), 2
        yield (x + w, j), (x + w + 1, j), 0


def _trazar(a, b, cajas, libres, ocupadas, segmentos, transitos, bordes, altura_preferida=None):
    """Busca un camino corto con puertos exclusivos y penalización por cruces y quiebres."""
    salida = [(p, q, d) for p, q, d in _puertos(cajas[a]) if q in libres and q not in ocupadas and q not in transitos]
    llegada = {q: (p, (d + 2) % 4) for p, q, d in _puertos(cajas[b])
               if q in libres and q not in ocupadas and q not in transitos}
    assert salida and llegada, f'Sin puertos libres para {a} → {b}'
    xmin, xmax = min(x for x, y in llegada), max(x for x, y in llegada)
    ymin, ymax = min(y for x, y in llegada), max(y for x, y in llegada)

    def estimar(x, y):
        return max(xmin - x, x - xmax, 0) + max(ymin - y, y - ymax, 0)

    cola, anterior, costos = [], {}, {}
    ax, ay, aw, ah = cajas[a]
    bx, by, bw, bh = cajas[b]
    for p, (x, y), d in salida:
        # En caso de empate, sale cerca del centro de la cara de la caja.
        costo = abs(x - ax - aw / 2) * 0.02 + abs(y - ay - ah / 2) * 0.02
        if altura_preferida is not None:
            costo += 8 * abs(y - altura_preferida)
        estado = (x, y, d)
        anterior[estado], costos[estado] = p, costo
        heappush(cola, (costo + estimar(x, y), costo, estado))
    while cola:
        _, costo, estado = heappop(cola)
        x, y, d = estado
        if costo != costos[estado]:
            continue
        if d == 4:
            destino, _ = llegada[(x, y)]
            estado = anterior[estado]
            puntos = [destino]
            while len(estado) == 3:
                puntos.append(estado[:2])
                estado = anterior[estado]
            puntos.append(estado)
            return list(reversed(puntos))
        fin = llegada.get((x, y))
        if fin:
            _, direccion = fin
            total = costo + (d != direccion) * 2 + 0.02 * (
                abs(x - bx - bw / 2) + abs(y - by - bh / 2))
            if altura_preferida is not None:
                total += 8 * abs(y - altura_preferida)
            final = (x, y, 4)
            if total < costos.get(final, float('inf')):
                anterior[final], costos[final] = estado, total
                heappush(cola, (total, total, final))
            continue
        for nd, (dx, dy) in enumerate(DIRECCIONES):
            vecino = (x + dx, y + dy)
            if vecino not in libres or vecino in ocupadas:
                continue
            if ((x, y), vecino) in segmentos:
                continue
            actual = costo + 1 + (d != nd) * 2 + 12 * transitos[vecino] + 5 * (vecino in bordes and vecino not in llegada)
            nuevo = (*vecino, nd)
            if actual < costos.get(nuevo, float('inf')):
                anterior[nuevo], costos[nuevo] = estado, actual
                heappush(cola, (actual + estimar(*vecino), actual, nuevo))
    raise ValueError(f'No hay un trazado libre para {a} → {b}')


def _quiebres(puntos):
    giros = [p for a, p, b in zip(puntos, puntos[1:], puntos[2:]) if a[0] != b[0] and a[1] != b[1]]
    return [puntos[0], *giros, puntos[-1]]


def _pasos_ruta(tramos):
    """Registra todos los puntos de una ruta explícita en la cuadrícula."""
    tramos = [(x // PASO, y // PASO) for x, y in tramos]
    pasos = [tramos[0]]
    for (x, y), (u, v) in pairwise(tramos):
        assert x == u or y == v, 'La ruta explícita debe ser ortogonal'
        largo = abs(u - x) + abs(v - y)
        dx, dy = (u - x) // largo, (v - y) // largo
        pasos.extend((x + i * dx, y + i * dy) for i in range(1, largo + 1))
    return pasos


def nombre_visible(st, texto):
    """Rótulo breve. EA guarda el texto íntegro del enlace en sus notas."""
    if st == 'build' and texto in ('422 / 403: aviso de acceso', 'visitas'):
        return texto.replace(': aviso de acceso', '')
    if st in ('submit', 'build'):
        return ''
    texto = texto.split(' (', 1)[0]
    if re.match(r'^(GET|POST|PATCH|PUT|DELETE) ', texto):
        metodo, ruta = texto.split(' ', 1)
        parametros = re.findall(r'\{([^}]+)\}', ruta)
        consulta = ruta.partition('?')[2]
        if consulta:
            campos = consulta.split('&')
            parametros += ['?' + '&'.join(campos[:2]) + ('…' if len(campos) > 2 else '')]
        elif ruta.endswith(' token'):
            parametros.append('+ token')
        elif ruta.endswith(' ruta'):
            parametros.append('ruta')
        return ' '.join([metodo, *parametros])
    return (texto.replace('elegir una página permitida: resultado.ruta', 'resultado.ruta')
            .replace('/agenda?interes={nro_tarjeta}', '?interes')
            .replace('Editar datos', 'Editar')
            .replace('clic Exportar CSV con filas del listado', 'Exportar CSV'))


def _toca_recta(a, b, rect):
    """Intersección de un segmento con un rectángulo, incluidos sus bordes."""
    t0, t1 = 0, 1
    for inicio, fin, minimo, maximo in zip(a, b, rect[:2], rect[2:]):
        if inicio == fin:
            if not minimo <= inicio <= maximo:
                return False
            continue
        inferior, superior = sorted(((minimo - inicio) / (fin - inicio), (maximo - inicio) / (fin - inicio)))
        t0, t1 = max(t0, inferior), min(t1, superior)
    return t0 <= t1


def _cruce(a, b, c, d):
    def lado(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    return (lado(a, b, c) * lado(a, b, d) <= 0 and lado(c, d, a) * lado(c, d, b) <= 0
            and all(max(min(u, v), min(w, z)) <= min(max(u, v), max(w, z)) for u, v, w, z in zip(a, b, c, d)))


def _acortar(lineas, cajas, rutas):
    """Endereza tramos con vista libre cuando la diagonal evita los quiebres sin sumar cruces."""
    for l in lineas:
        puntos = l['puntos']
        a, b = puntos[0], puntos[-1]
        if l['enlace'][:2] in rutas or len(puntos) == 2 or a[0] == b[0] or a[1] == b[1]:
            continue
        extremos = l['enlace'][:2]
        # La diagonal debe salir hacia fuera por ambos puertos.
        if any(sum((q - p) * (v - p) for p, q, v in zip(puerto, paso, opuesto)) <= 0
               for puerto, paso, opuesto in ((a, puntos[1], b), (b, puntos[-2], a))):
            continue
        if any(_toca_recta(a, b, (x - 9, y - 9, x + w + 9, y + h + 9))
               for k, (x, y, w, h) in cajas.items() if k not in extremos):
            continue
        segmentos = [s for otra in lineas if otra is not l for s in pairwise(otra['puntos'])]
        antes = sum(_cruce(u, v, c, d) for u, v in pairwise(puntos) for c, d in segmentos)
        despues = sum(_cruce(a, b, c, d) for c, d in segmentos)
        if despues <= antes:
            l['puntos'] = [a, b]


def _posiciones_rotulo(puntos, sentido, nombre, bloqueos, trazos, ancho, alto, compacto=False, cortes=ALTURAS_DE_CORTE,
                       ajustado=False, cerca_destino=False):
    """Posiciones sin colisiones junto a los tramos de un conector."""
    filas = [nombre] if nombre else []
    w_st = 5.5 * len(sentido) + 12
    w_nom = (6 * len(nombre) + 12) if nombre else 0
    if ajustado and nombre:
        w_nom = 5.5 * len(nombre) + 7
    w, h = max(w_st, w_nom), 34 if nombre else 16
    ancho_estereotipo = w_st
    if compacto:
        ancho_estereotipo -= 4  # el EMF dibuja el texto más estrecho que su caja en EA
        espacio = 7 if not cortes and nombre else 0
        w, h = ancho_estereotipo + espacio + w_nom, 14
    segmentos = list(pairwise(puntos))
    segmentos.sort(key=lambda s: -abs(s[1][0] - s[0][0]) - abs(s[1][1] - s[0][1]))
    separaciones = (3.5, 5, 8, 12, 17, 24, 35, 52, 66, 84, 105, 130) if compacto else (
        5, 12, 20, 29, 39, 52, 66, 84, 105, 130)
    for distancia in separaciones:
        for (ax, ay), (bx, by) in segmentos:
            fracciones = (0.5, 0.28, 0.72, 0.15, 0.85, 0.0, 1.0, -0.18, 1.18)
            if compacto:
                horizontal = abs(ax - bx) >= abs(ay - by)
                longitud = max(abs(ax - bx), abs(ay - by))
                holgura = round((w if horizontal else h) / 2 + 12)
                desplazamientos = range(-holgura, longitud + holgura + 1, max(4, longitud // 28))
                fracciones = [i / longitud for i in sorted(desplazamientos, key=lambda i: abs(i - longitud / 2))]
            for f in fracciones:
                x, y = round(ax + f * (bx - ax)), round(ay + f * (by - ay))
                if abs(ax - bx) >= abs(ay - by):
                    opciones = ((x, y - distancia - h / 2), (x, y + distancia + h / 2))
                else:
                    opciones = ((x + distancia + w / 2, y), (x - distancia - w / 2, y))
                for cx, cy in opciones:
                    rect = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
                    if rect[0] < 8 or rect[1] < 8 or rect[2] > ancho - 8 or rect[3] > alto - 8:
                        continue
                    if cerca_destino and abs(cy - puntos[-1][1]) > 300:
                        continue
                    if any(rect[1] - 14 < corte < rect[3] + 14 for corte in cortes):
                        continue
                    margen = 0 if cortes else 5
                    if any(rect[0] - margen <= d and a <= rect[2] + margen and rect[1] <= e and b <= rect[3]
                           for a, b, d, e in bloqueos):
                        continue
                    holgura_x = 6 if compacto else 3
                    extendido = (rect[0] - holgura_x, rect[1] - 3, rect[2] + holgura_x, rect[3] + 3)
                    if any(_toca_recta(a, b, extendido) for a, b in trazos):
                        continue
                    if compacto:
                        est_x = rect[0] + ancho_estereotipo / 2
                        nom_x = rect[0] + ancho_estereotipo + espacio + w_nom / 2 - 2.5 * len(nombre)
                        yield rect, dict(estereotipo=((est_x, rect[1] + 7), w_st),
                                         nombre=(nom_x, rect[1], filas))
                    else:
                        yield rect, dict(estereotipo=((cx, rect[1] + 8), w_st),
                                         nombre=(cx - 2.5 * len(nombre), rect[1] + 18, filas))


def _rotular(puntos, sentido, nombre, bloqueos, trazos, ancho, alto, enlace_a_formulario=False,
             cortes=ALTURAS_DE_CORTE, cerca_destino=False):
    elegido = next(_posiciones_rotulo(puntos, sentido, nombre, bloqueos, trazos, ancho, alto, cortes=cortes,
                                      cerca_destino=cerca_destino), None)
    if elegido is None and (enlace_a_formulario or not cortes):
        elegido = next(_posiciones_rotulo(puntos, sentido, nombre, bloqueos, trazos, ancho, alto, compacto=True,
                                          cortes=cortes, cerca_destino=cerca_destino), None)
    if elegido is not None:
        rect, rotulo = elegido
        bloqueos.append(rect)
        return rotulo
    if nombre:
        return _rotular(puntos, sentido, '', bloqueos, trazos, ancho, alto, cortes=cortes, cerca_destino=cerca_destino)
    raise ValueError(f'Sin espacio para el rótulo «{sentido}», {puntos}')


def _distancia_rotulo(rect, trazo):
    """Distancia entre el contorno del rótulo y un tramo que no lo atraviesa."""
    x0, y0, x1, y1 = rect
    (ax, ay), (bx, by) = trazo
    dx, dy = bx - ax, by - ay
    if dx == 0:
        return hypot(max(x0 - ax, ax - x1, 0), max(y0 - max(ay, by), min(ay, by) - y1, 0))
    if dy == 0:
        return hypot(max(x0 - max(ax, bx), min(ax, bx) - x1, 0), max(y0 - ay, ay - y1, 0))

    def esquina(x, y):
        t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        return hypot(x - ax - t * dx, y - ay - t * dy)

    return min(esquina(x0, y0), esquina(x0, y1), esquina(x1, y0), esquina(x1, y1),
               *(hypot(max(x0 - x, x - x1, 0), max(y0 - y, y - y1, 0)) for x, y in trazo))


def _acercar_rotulos(lineas_rotuladas, rectangulos, cajas, trazos, ancho, alto, cortes, mensajes, rotulos_en_destino):
    """Mueve los rótulos dudosos hacia su conector y los aleja de conectores vecinos."""
    segmentos = [list(pairwise(l['puntos'])) for l in lineas_rotuladas]
    if cortes:
        cajas = [(x0 + 2, y0 + 2, x1 - 2, y1 - 2) for x0, y0, x1, y1 in cajas]
    for i, l in enumerate(lineas_rotuladas):
        propios = segmentos[i]
        ajenos = [s for s in trazos if s not in propios]

        def prioridad(rect):
            propio = min(_distancia_rotulo(rect, s) for s in propios)
            rival = min(_distancia_rotulo(rect, s) for s in ajenos)
            return (max(0, propio + 7 - rival), propio)

        actual = rectangulos[i]
        calidad = prioridad(actual)
        alcance = max(30, calidad[1])
        if calidad[0] == 0 and calidad[1] <= 20:
            continue
        bloqueos = cajas + rectangulos[:i] + rectangulos[i + 1:]
        st = l['enlace'][2]
        nombre = ''.join(l['rotulos']['nombre'][2])
        ajustado = l['enlace'][:3] in mensajes
        cerca_destino = l['enlace'][:2] in rotulos_en_destino
        posiciones = chain.from_iterable(_posiciones_rotulo(l['puntos'], st, nombre, bloqueos, trazos, ancho, alto,
                                                           compacto, cortes, ajustado, cerca_destino)
                                         for compacto in (False, True))
        for rect, rotulo in posiciones:
            nueva = prioridad(rect)
            if nueva[1] > alcance:
                continue
            if nueva < calidad:
                calidad = nueva
                rectangulos[i], l['rotulos'] = rect, rotulo
            if calidad[0] == 0 and calidad[1] <= 6:
                break


def armar(paginas, enlaces, filas=FILAS, desfases=DESFASES, tamanos=TAMANOS, cortes=ALTURAS_DE_CORTE,
          paso_fila=13, mensajes=None, alturas=None, rutas=None):
    claves = [k for fila in filas for k in fila.split() if k != '-']
    assert len(claves) == len(paginas) and set(claves) == set(paginas), (
        f'Actualizar posiciones del diagrama: {set(claves) ^ set(paginas)}')
    cajas = {}
    for fila, grupos in enumerate(filas):
        for columna, k in enumerate(grupos.split()):
            if k == '-':
                continue
            w, h = medir(*paginas[k])
            w, h = (w + PASO - 1) // PASO, (h + PASO - 1) // PASO
            w, h = tamanos.get(k, (w, h))
            if k == 'ficha':
                w, h = max(w, 12), max(h, 8)
            dx, dy = desfases.get(k, (0, 0))
            cajas[k] = (6 + 13 * columna + (13 - w) // 2 + dx,
                        4 + paso_fila * fila + (10 - h) // 2 + dy, w, h)
    limite_x = max(x + w for x, y, w, h in cajas.values()) + 7
    limite_y = max(y + h for x, y, w, h in cajas.values()) + 5
    bordes = {(i, j) for x, y, w, h in cajas.values()
              for i in range(x - 1, x + w + 2) for j in range(y - 1, y + h + 2)
              if i in (x - 1, x + w + 1) or j in (y - 1, y + h + 1)}
    libres = {(x, y) for x in range(1, limite_x) for y in range(1, limite_y)}
    for x, y, w, h in cajas.values():
        libres.difference_update((i, j) for i in range(x, x + w + 1) for j in range(y, y + h + 1))

    def distancia(e):
        a, b, _, _ = e
        x, y, w, h = cajas[a]
        u, v, p, q = cajas[b]
        return abs(x + w / 2 - u - p / 2) + abs(y + h / 2 - v - q / 2)

    lineas, ocupadas, segmentos, transitos = [], set(), set(), Counter()
    alturas = alturas or {}
    rutas = rutas or {}
    for e in sorted(enlaces, key=lambda e: (e[:2] not in rutas, e[:2] not in alturas, distancia(e))):
        a, b, st, _ = e
        if st == 'contiene':  # EA almacena la agregación de formulario a página.
            a, b = b, a
        altura = alturas.get(e[:2])
        if e[:2] in rutas:
            puntos = _pasos_ruta(rutas[e[:2]])
            assert all(p in libres for p in puntos[1:-1]), f'La ruta de {a} a {b} invade una caja'
        else:
            puntos = _trazar(a, b, cajas, libres, ocupadas, segmentos, transitos, bordes,
                             altura_preferida=altura // PASO if altura is not None else None)
        ocupadas.update((puntos[1], puntos[-2]))
        transitos.update(puntos[1:-1])
        for u, v in pairwise(puntos):
            segmentos.update(((u, v), (v, u)))
        lineas.append(dict(enlace=e, puntos=[(x * PASO, y * PASO) for x, y in _quiebres(puntos)], rotulos=None))

    ancho, alto = limite_x * PASO, limite_y * PASO
    cajas = {k: tuple(i * PASO for i in caja) for k, caja in cajas.items()}
    _acortar(lineas, cajas, rutas)
    bloqueos = [(x - 5, y - 5, x + w + 5, y + h + 5) for x, y, w, h in cajas.values()]
    num_cajas = len(bloqueos)
    trazos = [s for l in lineas for s in pairwise(l['puntos'])]
    rotuladas = []
    mensajes = mensajes or {}

    def texto_rotulo(l):
        a, b, st, texto = l['enlace']
        return mensajes.get((a, b, st), nombre_visible(st, texto))

    def abre_formulario(l):
        _, b, st, _ = l['enlace']
        return st == 'link' and paginas[b][0] == 'form'

    for l in sorted(lineas, key=lambda l: (l['enlace'][:3] not in mensajes, not abre_formulario(l), -len(texto_rotulo(l)))):
        _, _, st, _ = l['enlace']
        if st != 'contiene':
            importante = l['enlace'][:3] in mensajes
            l['rotulos'] = _rotular(l['puntos'], st, texto_rotulo(l), bloqueos, trazos,
                                    ancho, alto, enlace_a_formulario=abre_formulario(l), cortes=cortes,
                                    cerca_destino=l['enlace'][:2] in rutas)
            if importante and not l['rotulos']['nombre'][2]:
                raise ValueError(f'El mensaje de {l["enlace"][:3]} requiere espacio: {texto_rotulo(l)}')
            rotuladas.append(l)
    _acercar_rotulos(rotuladas, bloqueos[num_cajas:], bloqueos[:num_cajas], trazos, ancho, alto, cortes, mensajes, rutas)
    return dict(cajas=cajas, lineas=lineas, ancho=ancho, alto=alto)

