# Generador del documento P2 (INF513, Grupo 05 SA)

Carpeta **autosuficiente** dentro de `crm-web`: todo lo que necesita está aquí, y lo único que lee de fuera es el
propio sistema documentado (`../negocio`, `../presentacion`, `../datos`, `../scripts`; ruta en `rutas.py`). Las reglas de
forma y contenido están en `REGLAS_DOCUMENTO_P2.md` (calco del aprobado del Grupo 07, en `referencias/`), que manda
sobre todo lo demás.

Requisitos: Python 3.12 con `python-docx`, `Pillow`, `numpy` y `pywin32`; Microsoft Word (para `exportar.ps1`);
Enterprise Architect 15 Trial (solo para regenerar diagramas).

## Qué hay y dónde se edita

| Archivo | Para qué |
|---|---|
| `contenido.py` | **Textos y datos** del documento. `None`/lista vacía = sale `[PENDIENTE]` en rojo |
| `codigo.py` | Lee el código: rutas de `api.php`, funciones de `api/<area>.js`, páginas, y la cadena Controller → Request → Service → Repository → Model por CU (5.3.2). `python codigo.py` la imprime |
| `navegacion.py` | Diagramas de navegación por actor; `API` liga cada «server page» con su función de `api/<area>.js` |
| `esquema.py` | Lee la BD de `fuentes/esquema.sql` (conceptual, mapeo, físico) y la compara con las migraciones |
| `formato_g07.py`, `doc_ficct.py` | Formato G07 sobre la base FICCT (carátula, fuentes, tablas, franjas) |
| `documento_p2.py` | Arma el .docx y corre los chequeos de coherencia |
| `rutas.py` | Todas las rutas: `CRM_WEB`, `ESQUEMA`, `LOGO`, `DIAGRAMAS`, `DOCUMENTO` |
| `ea/ea_p2.py`, `ea/ea_base.py` | Diagramas en Enterprise Architect 15 Trial por COM → `diagramas/` (PNG + EMF) |
| `ea/crm-p2.eapx`, `ea/posiciones.json` | Repositorio EA y posiciones acomodadas a mano |
| `exportar.ps1` | Word real: índices, EMF en lugar de PNG, `.doc` y `.pdf` |
| `referencias/` | Documento aprobado del Grupo 07 (modelo) y síntesis de las clases del docente |
| `documento/` | **Solo la salida**: `P2-INF513-GRUPO05SA.docx/.doc/.pdf`, reemplazados en cada corrida |

## Regenerar (desde esta carpeta)

```
python ea/ea_p2.py [--solo datos|nav|clases|org]   # EA debe estar cerrado; sin --solo rehace todos
python ea/ea_p2.py --guardar-posiciones             # tras mover cajas a mano en EA (abrir, mover, guardar, cerrar)
python documento_p2.py                              # → documento/P2-INF513-GRUPO05SA.docx + PENDIENTES
powershell -ExecutionPolicy Bypass -File exportar.ps1   # → documento/*.doc y *.pdf (sobrescribe)
```

## Chequeos: el documento no puede contradecir al código

`documento_p2.py` **no guarda** el documento y lista lo que falla si:

| Qué | Contra qué |
|---|---|
| Actores, menú y CU | Un diagrama de navegación por actor; cada página del menú del rol (matriz de la migración 000003) en su diagrama y en un CU del que el rol es actor |
| BD | Tablas y columnas de `fuentes/esquema.sql` = las que dejan las migraciones de `../datos/migraciones` |
| Navegación | Cada client page existe en `presentacion/src`; cada «server page» es una función real de `api/<area>.js`, su ruta existe en `api.php`, el método existe en el controlador y se llama igual; la página que la envía la llama de verdad; toda función que usa la interfaz y toda página `.jsx` aparece en algún diagrama |
| Stack (Cap. II y 8.1) | Cada tema y herramienta tiene evidencia en `contenido.EVIDENCIA` (dependencia directa en `composer.json`/`package.json` o archivo real); nada de Inertia, Vue, JWT, Livewire o Blade en las dependencias; Tailwind 4.x |
| 5.3.2 | Cada método llamado existe en su clase; ninguna dependencia sube de capa |
| Textos | Cada mensaje citado en Excepciones (4.4) existe tal cual en `negocio/` o `datos/`; cada prueba de 10 existe en `scripts/`; los paquetes de 5.1.1 cubren todas las tablas sin repetir |
| Términos | El documento no dice MVC, Modelo-Vista, Vue, Inertia, JWT, Unidad de Capacitación ni San Pablo |

También avisa (sin fallar) de las rutas de `api.php` que ninguna pantalla llama.

## Actualizar

- **Texto:** `contenido.py`. Versiones `composer:`/`npm:` se leen solas de los lock de crm-web; la URL de GitHub, de `.git/config`.
- **BD — fuente de verdad: las migraciones** (`../datos/migraciones`). `fuentes/esquema.sql` es su volcado (lo usan el
  conceptual, el mapeo y el físico porque trae tipos, PK y FK exactos). Si el chequeo dice que difieren: correr las
  migraciones en una base local vacía y `pg_dump --schema-only --no-owner --schema=public <base> > fuentes/esquema.sql`
  (nunca con la contraseña del servidor en esta carpeta); después `python ea/ea_p2.py --solo datos`.
- **Matriz de acceso/menú:** sale de las migraciones (`…_crear_matriz_acceso.php` y las que agregan recursos).
- **Navegación:** si una pantalla llama a una función nueva de `api/`, agregarla en `navegacion.py` (nodo `ps` + `API`).
- **crm-web se movió:** cambiar `CRM_WEB` en `rutas.py`.
- **Organización:** misión, visión, objetivo y organigrama son propuesta del grupo (`contenido.POR_CONFIRMAR`); al
  confirmarlos con la clienta, vaciar esa lista.

## Restricciones

- Stack real en 3 capas: **React SPA + Axios + Tailwind CSS** (presentación) / **Laravel API RESTful** (negocio) /
  **PostgreSQL** (datos). Nunca MVC, Vue, Inertia ni JWT (eso era G07).
- Nada inventado: cada dato sale de crm-web, de la BD o de `../P2_WEB.md` / `../PRODUCT.md`; lo que falta queda `[PENDIENTE]`.
- Diagramas solo en EA 15 Trial real por COM; nunca una copia crackeada. UML exacto: cada elemento existe de verdad.
- Conceptual sin PK/FK; navegación en franjas apaisadas (como G07); 5.3.2 en 3 capas, no MVC.
- Organización: UNEXO. No reutilizar textos del P1 (Unidad de Capacitación de la FICCT).
- Nombre del entregable: `P2-INF513-GRUPO05SA` (.doc). Credenciales jamás en el documento ni en esta carpeta.
