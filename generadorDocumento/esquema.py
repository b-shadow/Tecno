"""Lee la estructura real de db_grupo05sa.public desde fuentes/esquema.sql (volcado de pg_dump, idéntico a las migraciones
de crm-web). Conceptual, Mapeo y Físico salen de aquí: los campos del documento son los de la BD, uno a uno (clase 46)."""
import re
from rutas import ESQUEMA

SQL = ESQUEMA.read_text(encoding='utf-8')
NO_NEGOCIO = {'migrations'}   # control de Laravel: vive en el esquema `laravel`, no en el modelo

_DEF_SEQ = dict(((t, c), d) for t, c, d in re.findall(
    r'ALTER TABLE ONLY public\.(\w+) ALTER COLUMN (\w+) SET DEFAULT (.+?);\n', SQL))


def tablas():
    """{tabla: [(columna, tipo, not_null, default)]} en el orden del CREATE TABLE (el DEFAULT nextval va en su columna)."""
    res = {}
    for nombre, cuerpo in re.findall(r'CREATE TABLE public\.(\w+) \((.*?)\n\);', SQL, re.S):
        if nombre in NO_NEGOCIO: continue
        cols = []
        for l in cuerpo.splitlines():
            l = l.strip().rstrip(',')
            if not l or l.startswith('CONSTRAINT'): continue
            col, resto = l.split(' ', 1)
            nn = resto.endswith(' NOT NULL')
            if nn: resto = resto[:-9]
            tipo, _, defecto = resto.partition(' DEFAULT ')
            cols.append((col, tipo, nn, defecto or _DEF_SEQ.get((nombre, col), '')))
        res[nombre] = cols
    return res


def pks():
    return {t: [c.strip() for c in cs.split(',')] for t, cs in
            re.findall(r'ALTER TABLE ONLY public\.(\w+)\s+ADD CONSTRAINT \w+ PRIMARY KEY \(([^)]+)\);', SQL)}


def fks():
    """[(hija, (columnas), padre, (columnas_padre))], también las compuestas."""
    sep = lambda s: tuple(c.strip() for c in s.split(','))
    return [(h, sep(c), p, sep(cp)) for h, c, p, cp in re.findall(
        r'ALTER TABLE ONLY public\.(\w+)\s+ADD CONSTRAINT \w+ FOREIGN KEY \(([^)]+)\) REFERENCES public\.(\w+)\(([^)]+)\)', SQL)]


def unicas():
    return {(t, c) for t, c in re.findall(r'ALTER TABLE ONLY public\.(\w+)\s+ADD CONSTRAINT \w+ UNIQUE \((\w+)\);', SQL)}


def columnas_fk():
    return {(h, c) for h, cs, _, _ in fks() for c in cs}


def intermedias():
    """Tablas N-N: su PK son solo columnas FK hacia dos tablas distintas. {intermedia: (fuerte_a, fuerte_b)}."""
    res, fk, pk = {}, fks(), pks()
    for t, cols in pk.items():
        padres = [p for h, cs, p, _ in fk if h == t and set(cs) <= set(cols)]
        if len(padres) == 2 and padres[0] != padres[1] and set(cols) <= {c for h, cs, _, _ in fk if h == t for c in cs}:
            res[t] = tuple(padres)
    return res


def orden_mapeo():
    """Tablas referenciadas primero (como el Mapeo de G07), luego alfabético."""
    pend, fk, listo = sorted(tablas()), fks(), []
    while pend:
        for t in pend:
            if all(p in listo or p == t for h, _, p, _ in fk if h == t):
                listo.append(t); pend.remove(t); break
        else:
            listo.append(pend.pop(0))
    return listo


if __name__ == '__main__':   # chequeo: ninguna tabla suelta, toda FK apunta a una tabla del modelo
    t, f = tablas(), fks()
    relacionadas = {x for h, _, p, _ in f for x in (h, p)}
    assert set(t) == relacionadas, f'tablas sueltas: {set(t) - relacionadas}'
    assert all(h in t and p in t for h, _, p, _ in f)
    assert set(pks()) == set(t), f'tablas sin PK: {set(t) - set(pks())}'
    print(len(t), 'tablas,', len(f), 'FK, intermedias N-N:', intermedias())
