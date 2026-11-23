# Generador del documento P2 (INF513, Grupo 05 SA)

## Mantenimiento del maestro con ediciones manuales

Tras integrar `respaldo-documentacion-leonardo` con `main`, el maestro es el
DOCX ampliado del respaldo. Sus 79 tablas incluyen un mapeo detallado de las
31 tablas y 287 columnas del esquema. Las ocho secuencias actualizadas de 7.4
se generaron en el subpaquete EA `Secuencias 7.4 integradas`, preservando los
diagramas originales, y se insertaron en este maestro. El conceptual se
sincronizó con el esquema y el DOCX se exportó a DOC y PDF.

`actualizar_datos_docx.py` corresponde al mapeo compacto anterior y no reconoce
el formato detallado del maestro integrado. Para un cambio posterior de esquema,
revisar `actualizar_documento.py bd` y conservar una copia del DOCX antes de
aplicarlo. El mapeo integrado se comprobó columna por columna contra
`fuentes/esquema.sql`.

Las tablas detalladas de 7.2 y 7.3 tienen ancho fijo para que Word no las
expanda fuera de la página. La sección 7.3 utiliza 1 cm de margen lateral.
Después de editar el DOCX, `python actualizar_documento.py margenes` restaura
solo esos anchos y márgenes; luego `exportar.ps1` actualiza el DOC y el PDF.
La opción `actualizar_documento.py bd` aplica el mismo ajuste al regenerar
estas tablas.

La actualización documental de noviembre de 2026 se realiza sobre
`documento/P2-INF513-GRUPO05SA.docx` y el proyecto original `ea/crm-p2.eapx`.
El maestro contiene ediciones manuales: **no ejecutar `documento_p2.py` ni los
comandos históricos de reconstrucción para actualizar esta entrega**.
Las instrucciones específicas de actualización prevalecen sobre las reglas
históricas de una página por CU, tamaños reducidos y franjas recortadas.
Los ocho CU, los actores, el diagrama de actores y el capítulo IV se conservan.

El mantenimiento incremental utiliza:

- `actualizacion_contenido.py`: especificaciones completas de los ocho CU y
  responsabilidades verificadas de las tres capas.
- `actualizar_documento.py cu|bd|arquitectura`: ediciones puntuales del Word,
  con comparación del capítulo IV antes y después de cada operación.
- `diccionario_actual.py`: descripciones de columnas y de los cinco triggers.
- `ea/sincronizar_documentacion.py`: catálogo de firmas desde código y edición
  de clases originales por COM oficial, con vistas completas complementarias.
- `ea/actualizar_interacciones.py`: secuencias y comunicaciones nativas de los
  recorridos implementados, con guardas y participantes reales.
- `ea/actualizar_datos_despliegue.py` y `ea/actualizar_navegacion.py`: vistas
  nativas complementarias que reutilizan los elementos originales.
- `ea/compatibilidad_emf.mjs`: normaliza el viewport omitido por ciertas
  exportaciones de EA 15; conserva idénticos todos los registros gráficos.
- `insertar_figuras_actuales.py`: sustituye las secciones gráficas autorizadas
  usando exportaciones nativas y páginas grandes, sin reducir la tipografía.
- `exportar.ps1`: actualiza campos con Microsoft Word y produce DOC y PDF.

Respaldar el maestro y el EAPX antes de editar. No ejecutar dos escritores COM
sobre el proyecto al mismo tiempo. Cerrar EA antes de versionar; excluir `.ldb`,
respaldos, QA, credenciales y auditorías locales. La base efectiva de Laravel
se verifica mediante consultas de metadatos de solo lectura; **no ejecutar
migraciones para actualizar la documentación**. El SQL documental no contiene
datos ni credenciales y no debe aplicarse sobre una base existente.

Las instrucciones de reconstrucción siguientes se conservan como referencia
histórica; no son el procedimiento de mantenimiento de este maestro.

Carpeta **autosuficiente** dentro de `crm-web`: todo lo que necesita está aquí, y lo único que lee de fuera es el
propio sistema documentado (`../negocio`, `../presentacion`, `../datos`, `../scripts`; ruta en `rutas.py`). Las reglas de
forma y contenido están en `REGLAS_DOCUMENTO_P2.md` (calco del aprobado del Grupo 07, en `referencias/`), que manda
sobre todo lo demás.

Requisitos (Windows): Python 3.12 + `pip install -r requirements.txt`; Microsoft Word (para `exportar.ps1`);
Enterprise Architect 15 Trial solo para regenerar diagramas (si se instaló en otra carpeta, cambiar `EA_BASE` en
`rutas.py`). Para editar textos y regenerar el .docx no hace falta EA: los diagramas ya están en `diagramas/`.

**Si `documento_p2.py` falla**, cada línea de `INCOHERENCIAS` dice qué no cuadra con el código y dónde: se corrige el
texto o el diagrama (o el código, si el error está ahí) y se vuelve a correr.

## Qué hay y dónde se edita

| Archivo | Para qué |
|---|---|
| `contenido.py` | **Textos y datos** del documento, incluidos los capítulos II/III y la bibliografía. `None`/lista vacía = sale `[PENDIENTE]` en rojo |
| `codigo.py` | Lee el código: rutas de `api.php`, funciones de `api/<area>.js`, páginas, y la cadena Controller → Request → Service → Repository → Model por CU (5.3.2). `python codigo.py` la imprime |
| `navegacion.py` | Diagramas de navegación por actor; `API` liga cada «server page» con su función de `api/<area>.js` |
| `esquema.py` | Lee la BD de `fuentes/esquema.sql` (conceptual, mapeo, físico) y la compara con las migraciones |
| `formato_g07.py`, `doc_ficct.py` | Formato G07 sobre la base FICCT (carátula, fuentes, tablas, franjas) |
| `documento_p2.py` | Arma el .docx y corre los chequeos de coherencia |
| `rutas.py` | Todas las rutas: `CRM_WEB`, `ESQUEMA`, `LOGO`, `DIAGRAMAS`, `DOCUMENTO`, `EA_BASE` |
| `ea/ea_p2.py`, `ea/ea_base.py` | Diagramas en Enterprise Architect 15 Trial por COM → `diagramas/` (PNG + EMF) |
| `ea/ea_faltantes.py` | Completa en el EAPX existente los 34 diagramas de requisitos, paquetes, comunicación, secuencia y despliegue; toma rutas y clases del código real |
| `insertar_diagramas.py` | Sustituye solo los marcadores de diagramas del DOCX actual, conservando el resto de las ediciones manuales |
| `actualizar_figura_docx.py` | Refresca solo una figura del DOCX actual (`conceptual` 7.1 o `despliegue` 6.1), conservando el resto de las ediciones manuales |
| `actualizar_datos_docx.py` | Pone al día el Mapeo (7.2.1) y el Físico (7.3) del DOCX actual con `fuentes/esquema.sql`: reemplaza solo las tablas que difieren y conserva las ediciones manuales |
| `actualizar_secuencias.py` | Reemplaza solo las ocho figuras de secuencia del DOCX actual, sin reconstruirlo: deja 7.4 en su sección de 1 cm de margen lateral y cada sd entero y lo más grande posible en su hoja carta |
| `ea/crm-p2.eapx`, `ea/posiciones.json` | Repositorio EA y posiciones acomodadas a mano |
| `exportar.ps1` | Word real: índices, EMF en lugar de PNG, `.doc` y `.pdf` |
| `referencias/` | Documento aprobado del Grupo 07 (modelo) y síntesis de las clases del docente |
| `documento/` | **Solo la salida**: `P2-INF513-GRUPO05SA.docx/.doc/.pdf`, reemplazados en cada corrida |

## Regenerar (desde esta carpeta)

```
python ea/ea_faltantes.py                          # abre el EAPX existente; conserva posiciones manuales
python ea/ea_p2.py --actualizar-conceptual          # sincroniza atributos con el esquema y aplica el acomodo de posiciones.json
python ea/ea_faltantes.py --despliegue             # rehace solo 6.1 (calco G07, letra 11 pt; la corrida completa también lo hace así)
python actualizar_figura_docx.py conceptual|despliegue   # sustituye solo esa figura en el documento manual actual
python actualizar_datos_docx.py                    # tras cambiar esquema.sql: Mapeo y Físico del documento manual actual
python insertar_diagramas.py                       # sustituye solo diagramas pendientes del DOCX actual
python ea/ea_faltantes.py --secuencias [CU1 CU6]   # rehace los sd de 7.4 desde el código (falla si un recorrido ya no coincide)
python actualizar_secuencias.py                    # si el DOCX ya tiene las figuras, refresca solo las ocho secuencias
python ea/ea_p2.py --recrear [--solo datos|nav|clases|org]   # reconstruye el EAPX completo: usar solo tras respaldarlo
python ea/ea_p2.py --guardar-posiciones             # tras mover cajas a mano en EA (abrir, mover, guardar, cerrar)
python documento_p2.py                              # reconstruye el DOCX completo: no conserva ediciones manuales
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
- **Organización:** misión, visión, objetivo y organigrama describen el proceso comercial modelado para UNEXO;
  no son declaraciones institucionales de la FICCT. Su texto y fuentes quedan en `contenido.py` y no requieren
  `proyectocorreo/` para regenerarse. La ubicación física e infraestructura se reproducen desde el P1 aprobado;
  el mapa de OpenStreetMap está guardado localmente en `diagramas/ubicacion.png`. El organigrama conserva su
  proporción al exportarse.
- **Prioridades:** `contenido.PRIORIDAD` debe contener exactamente los ocho CU; el generador rechaza claves faltantes
  y valores fuera de Alta/Media/Baja.
- **Índice:** `exportar.ps1` actualiza la tabla de contenido con Word y detiene la entrega si quedan marcadores rotos.

## Restricciones

- Stack real en 3 capas: **React SPA + Axios + Tailwind CSS** (presentación) / **Laravel API RESTful** (negocio) /
  **PostgreSQL** (datos). Nunca MVC, Vue, Inertia ni JWT (eso era G07).
- Nada inventado: cada dato sale de crm-web, de la BD o de `../P2_WEB.md` / `../PRODUCT.md`; lo que falta queda `[PENDIENTE]`.
- Diagramas solo en EA 15 Trial real por COM; nunca una copia crackeada. UML exacto: cada elemento existe de verdad.
- Conceptual con los atributos en orden de la BD y la **PK subrayada** (atributo static en EA), sin escribir «PK» ni «FK» (pedido del docente en la revisión; escribir PK/FK en un conceptual es causal de rechazo); las FK se representan mediante asociaciones. Entra entero en **una** página vertical (19,5 × 21 cm bajo los títulos, letra impresa ≈4,7 pt, EMF vectorial): el acomodo está en `ea/posiciones.json` (0 líneas sobre cajas, N-N junto a su asociación) y las cajas miden lo justo para su texto (`medida_conceptual`). Si se agrega una tabla, hay que reacomodar a mano en EA y `--guardar-posiciones`. Para actualizar solo el diagrama EA existente: `python ea/ea_p2.py --actualizar-conceptual` y luego `python actualizar_figura_docx.py conceptual`. Navegación en franjas apaisadas (como G07); 5.3.2 en 3 capas, no MVC.
- Organización: UNEXO. No reutilizar textos del P1 (Unidad de Capacitación de la FICCT).
- Nombre del entregable: `P2-INF513-GRUPO05SA` (.doc). Credenciales jamás en el documento ni en esta carpeta.
