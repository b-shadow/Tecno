# Generador del documento P2 (INF513, Grupo 05 SA)

Carpeta **autosuficiente** dentro de `crm-web`: todo lo que necesita está aquí, y lo único que lee de fuera es el
propio sistema documentado (`../negocio`, `../presentacion`, `../datos`; ruta en `rutas.py`). Las reglas de forma y
contenido están en `REGLAS_DOCUMENTO_P2.md` (calco del aprobado del Grupo 07), que manda sobre todo lo demás.

Requisitos: Python 3.12 con `python-docx`, `Pillow`, `numpy` y `pywin32`; Microsoft Word (para `exportar.ps1`);
Enterprise Architect 15 Trial (solo para regenerar diagramas).

## Qué hay y dónde se edita

| Archivo | Para qué |
|---|---|
| `contenido.py` | **Textos y datos** del documento. `None`/lista vacía = sale `[PENDIENTE]` en rojo |
| `navegacion.py` | Diagramas de navegación por actor (páginas, formularios, enlaces) |
| `esquema.py` | Lee la BD real de `fuentes/esquema.sql` (conceptual, mapeo, físico) |
| `formato_g07.py`, `doc_ficct.py` | Formato G07 sobre la base FICCT (carátula, fuentes, tablas, franjas) |
| `documento_p2.py` | Arma el .docx y corre el chequeo de coherencia |
| `rutas.py` | Todas las rutas: `CRM_WEB`, `ESQUEMA`, `LOGO`, `DIAGRAMAS`, `DOCUMENTO` |
| `ea/ea_p2.py`, `ea/ea_base.py` | Diagramas en Enterprise Architect 15 Trial por COM → `diagramas/` (PNG + EMF) |
| `ea/crm-p2.eapx`, `ea/posiciones.json` | Repositorio EA y posiciones acomodadas a mano |
| `exportar.ps1` | Word real: índices, EMF en lugar de PNG, `.doc` y `.pdf` |
| `documento/` | **Solo la salida**: `P2-INF513-GRUPO05SA.docx/.doc/.pdf`, reemplazados en cada corrida |

## Regenerar (desde esta carpeta)

```
python ea/ea_p2.py [--solo datos|nav]   # solo si cambian BD o navegación; EA debe estar cerrado
python ea/ea_p2.py --guardar-posiciones  # tras mover cajas a mano en EA (abrir, mover, guardar, cerrar)
python documento_p2.py                   # → documento/P2-INF513-GRUPO05SA.docx + lista de PENDIENTES
powershell -ExecutionPolicy Bypass -File exportar.ps1   # → documento/*.doc y *.pdf (sobrescribe)
```

`documento_p2.py` **no guarda** si hay incoherencias: falta un diagrama de navegación por actor, un diagrama tiene
páginas fuera del menú del rol, un rol usa una página de un CU del que no es actor, o aparece un término ajeno
(MVC, Modelo-Vista, Vue, Inertia, JWT, Unidad de Capacitación, San Pablo).

## Actualizar

- **Texto:** `contenido.py`. Versiones de herramientas `composer:`/`npm:` se leen solas de los lock de crm-web.
- **BD cambió:** refrescar `fuentes/esquema.sql` con `pg_dump --schema-only --no-owner` de `db_grupo05sa` (en el servidor; la contraseña nunca
  entra en esta carpeta ni en el repositorio) y regenerar con `--solo datos`.
- **Matriz de acceso/menú:** sale de la migración `crm-web/datos/migraciones/…_crear_matriz_acceso.php`.
- **crm-web se movió:** cambiar `CRM_WEB` en `rutas.py`.

## Restricciones

- Stack real en 3 capas: **React SPA + Axios + Tailwind CSS** (presentación) / **Laravel API RESTful** (negocio) /
  **PostgreSQL** (datos). Nunca MVC, Vue, Inertia ni JWT (eso era G07).
- Nada inventado: cada dato sale de crm-web, de la BD o de `../P2_WEB.md`; lo que falta queda `[PENDIENTE]`.
- Diagramas solo en EA 15 Trial real por COM; nunca una copia crackeada. UML exacto: cada elemento existe de verdad.
- Conceptual sin PK/FK; navegación en franjas apaisadas (como G07).
- Organización: UNEXO. No reutilizar textos del P1 (Unidad de Capacitación de la FICCT).
- Nombre del entregable: `P2-INF513-GRUPO05SA` (.doc). Credenciales jamás en el documento ni en esta carpeta.
