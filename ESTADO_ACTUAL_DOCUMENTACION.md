# Estado Actual de la Documentación Técnica y Modelo EA — UNEXO (INF513)

> **Actualización de integración (26 de noviembre de 2026).** Este informe conserva
> el estado histórico del respaldo `3ed54a1` antes de fusionarlo con `main`
> (`1d71fa4`). La integración preservó el DOCX ampliado y el EAPX del respaldo,
> e incorporó el esquema SQL, el modelo conceptual y las ocho secuencias recientes
> de `main`. Las secuencias nuevas están en el paquete EA «Secuencias 7.4
> integradas», sin eliminar los 47 diagramas originales ni las vistas de trabajo.
> El modelo tiene ahora 1.679 diagramas. El mapeo del DOCX coincide con las
> 31 tablas y 287 columnas del esquema; las 79 tablas del Word se conservaron.
> Se exportaron el DOC y el PDF integrados (217 páginas, sin marcadores rotos).
> Las tareas descritas más abajo como pendientes reflejan el corte anterior y
> deben reevaluarse sobre este resultado. En particular, las vistas auxiliares
> de relaciones y comunicación todavía requieren revisión editorial, además
> de las capturas y las pruebas de aceptación.

Fecha de corte de recuperación: **2026-11-26**
Proyecto: **UNEXO — CRM Comercial Educativo** (Tecnología Web INF513, UAGRM, Grupo 05 SA)
Repositorio remoto: `https://github.com/b-shadow/Tecno.git`
Commit base del trabajo local: `2b6ab3158f946b507765e236706708ae3e71ddc9` (`2b6ab31`)
Estado de publicación de este corte: respaldado en rama de respaldo (ver sección de divergencia con `origin/main` en `1d71fa4`).

---

## 1. Contexto del proyecto

- **Sistema:** UNEXO — CRM Comercial Educativo desarrollado con arquitectura de tres capas (**Presentación / Negocio / Datos**):
  - `presentacion/`: React / Vite (`src/componentes/`, `src/api/`, `src/servicios/`, temas Niños/Jóvenes/Adultos).
  - `negocio/`: Laravel (`app/Negocio/`, `app/Http/`, rutas API/públicas, Stripe SDK, SMTP).
  - `datos/`: Modelos Eloquent (`src/Modelos/`) y capas de datos (`src/Datos/`) sobre PostgreSQL (`crm_educativo`, esquema `public`, 31 tablas y 287 columnas).
- **Documentación y modelado UML:**
  - Modelo Enterprise Architect 15: `generadorDocumento/ea/crm-p2.eapx`
  - Documento maestro Word/DOC/PDF: `generadorDocumento/documento/P2-INF513-GRUPO05SA.docx` (`.doc` y `.pdf` del corte previo `01:03` aún sin regenerar)
  - Esquema SQL documental: `generadorDocumento/fuentes/esquema.sql`
  - Auditoría técnica de base: `auditoria_documental/` (`00_CONTROL_AVANCE.md` a `15_CONTROL_ACTUALIZACION_DOCUMENTAL.md`, matrices `.xlsx` y scripts de análisis)
  - Artefactos versionados de continuación: `generadorDocumento/continuacion_documental/` (copiados desde `tmp/actualizacion_documental/`).

---

## 2. Estado actual exacto del trabajo

El trabajo automatizado previo (ejecutado con Codex sobre el commit base `2b6ab31`) fue **detenido de forma segura** y preservado sin pérdida de datos:

1. **Sin procesos activos ni bloqueos:** Se verificó que no existan procesos `EA.exe`, `python.exe` ni `WINWORD.EXE` ejecutándose, ni archivos de bloqueo (`.ldb`, `.laccdb`, `.tmp`, `~$*`) dentro de `generadorDocumento/`.
2. **Punto exacto de detención:**
   - El orquestador `tmp/actualizacion_documental/modelo_final.py` (copiado en `generadorDocumento/continuacion_documental/modelo_final.py`) completó las etapas `final-01-catalogo`, `final-02-integrar-clases`, `final-03-organizar-clases`, `final-04-presentacion-clases` y `final-05-capas`.
   - Durante `final-06-relaciones` (`generadorDocumento/ea/sincronizar_documentacion.py relaciones-clases`), tras exportar y registrar `clases-relacion-356` (EA `DiagramID = 1269`, `CU7 — DSeguimiento / InscripcionComercial`, `12:21:50–12:21:52`), exportó el archivo nativo `clases-relacion-357.emf` (`12:21:54`) y ejecutó `generadorDocumento/ea/compatibilidad_emf.mjs`.
   - `compatibilidad_emf.mjs` detectó la bandera `tmp/actualizacion_documental/solicitar_reinicio.flag` y lanzó una detención controlada (`Error: Reinicio controlado del lote EA tras guardar el EMF nativo.`), ejecutando `repo.CloseFile()` y `repo.Exit()` oficiales a las **12:21:55**.
   - Posteriormente (alrededor de las **12:23:16–12:23:46**), se ejecutó `retirar_masivas_seguro.py` **sin** `--aplicar` (modo simulación / dry-run), generando `plan_retirada_masivas.json` sin eliminar ningún diagrama de `crm-p2.eapx`.
3. **Integridad del `.eapx` verificada:** Se probó `generadorDocumento/ea/crm-p2.eapx` (`17,080,320` bytes) mediante una copia temporal de solo lectura usando la API COM oficial (`EA.Repository.OpenFile` -> `True`, `Models = 2`, `Packages = 52`, `Diagrams = 1671`, `CloseFile()`, `Exit()`). No presenta corrupción ni quedó abierto.
4. **Código funcional intacto:** No se modificó ningún archivo de `presentacion/`, `negocio/` ni `datos/`, ni la base de datos PostgreSQL.

---

## 3. Inventario técnico completo

### 3.1 Modelo Enterprise Architect (`generadorDocumento/ea/crm-p2.eapx`)

Conteo verificado en la instancia actual de `crm-p2.eapx` (`17,080,320` bytes):

- **Paquetes (`t_package`):** `52`
- **Diagramas totales (`t_diagram`):** `1,671`
  - `Logical`: `861`
  - `Collaboration`: `610`
  - `Sequence`: `182`
  - `Use Case`: `10`
  - `Package`: `7`
  - `Deployment`: `1`
- **Objetos (`t_object`):** `2,186`
- **Atributos (`t_attribute`):** `2,194`
- **Operaciones / Métodos (`t_operation`):** `1,370`
- **Parámetros (`t_operationparams`):** `1,047`
- **Conectores (`t_connector`):** `3,582`
- **Ocurrencias en diagramas (`t_diagramobjects`):** `5,206`
- **Enlaces en diagramas (`t_diagramlinks`):** `10,686`

Distinción registrada en `generadorDocumento/continuacion_documental/plan_retirada_masivas.json`:
- **Diagramas originales preservados:** `47`
- **Vistas complementarias / detalle en el modelo:** `1,624` (no eliminadas; `retirar_masivas_seguro.py` solo corrió en dry-run).

### 3.2 Exportaciones en disco (`generadorDocumento/diagramas/`)

Totales actuales en `generadorDocumento/diagramas/`:
- **Archivos `.emf`:** `1,711`
- **Archivos `.png`:** `1,702`
- **Subcarpeta adicional:** `franjas/` (`22` archivos)
- **Archivos de 0 bytes:** `0`

Desglose por categoría / prefijo:
- **Clases generales (`cls-cu1..8`):** `8` `.emf` (`811 KB` a `1.43 MB`); **los 8 `.png` (`cls-cu1..8.png`) fueron retirados** intencionalmente a `tmp/actualizacion_documental/exportaciones_retiradas/` por `sincronizar_documentacion.py` al superar el umbral `width * height >= 10,000,000` (protección de EA 32 bits).
- **Detalles de clase (`cls-cu*-detalle-*`):** `419` `.emf` + `419` `.png` (total `427` vistas de clase en `exportaciones_clases_visibles.json`).
- **Relaciones entre clases (`clases-relacion-*`):** `357` `.emf` + `356` `.png` (`clases-relacion-001` a `clases-relacion-356` completos; `clases-relacion-357.emf` guardado al detenerse sin `.png` ni entrada en JSON).
- **Comunicación (`com-*`):** `622` `.emf` + `621` `.png` (`com-cu1..8.*` y vistas por flujo `com-cu*-flujo-*`; `com-cu6-flujo-26-08.emf` de las `11:38:31` carece de `.png` tras el corte previo de EA 32 bits).
- **Secuencia (`sd-*` y `seq-*`):** `182` `sd-*.emf` / `182` `sd-*.png`, más `99` `seq-*.emf` / `99` `seq-*.png`.
- **Casos de uso (`uc-*`), Paquetes (`paquete*`), Navegación (`nav-*`) y diagramas base:** `uc-*` (`9`/`9`), `paquete*` (`7`/`7`), `nav-*` (`4`/`4`), `actores` (`1`/`1`), `conceptual` (`1`/`1`), `despliegue` (`1`/`1`), `organigrama` (`1`/`1`), más `ubicacion.png` sin `.emf`.

### 3.3 Documentos de entrega (`generadorDocumento/documento/`)

| Archivo | Tamaño | Última modificación | Estado |
|---|---:|---|---|
| `P2-INF513-GRUPO05SA.docx` | `14,463,511` B | `2026-11-26 11:21:34` | Editado parcialmente vía OOXML (BD 7.2/7.3, 8 CU, Arquitectura/Herramientas; **sin** las nuevas figuras EA de clases/relaciones/secuencias/conceptual/despliegue/navegación/pruebas). |
| `P2-INF513-GRUPO05SA.doc` | `15,132,160` B | `2026-11-26 01:03:41` | **Desactualizado** respecto al `.docx` (no se ejecutó `exportar.ps1`). |
| `P2-INF513-GRUPO05SA.pdf` | `6,037,593` B | `2026-11-26 01:03:41` | **Desactualizado** respecto al `.docx` (no se ejecutó `exportar.ps1`). |

---

## 4. Estado por fases

| Fase | Estado actual | Qué quedó hecho y evidencia | Qué falta exactamente |
|---|---|---|---|
| **0. Preparación y respaldos** | **Completada** | Respaldos locales en `backups/documental-20261126/` (no versionados). Inventario inicial `inventario_ea_inicial.json` (52 paquetes, 47 diagramas originales). | Mantener sin sobrescribir archivos base manualmente. |
| **1. Base de datos documental (PostgreSQL + SQL + DOCX)** | **Texto/SQL/EA conceptual actualizados; figura conceptual y revisión final pendientes** | `generadorDocumento/fuentes/esquema.sql` verificado contra PostgreSQL 17.4 (`31` tablas, `287` columnas, `113` restricciones, `5` triggers; sin columnas de envíos automáticos). Secciones `7.2` y `7.3` de `P2-INF513-GRUPO05SA.docx` actualizadas (`fase1_word.json`). Tres atributos añadidos al modelo conceptual EA (`cambios_fase1_ea.json`). | Regenerar y validar visualmente figuras de modelo conceptual (`final-11-conceptual` -> `conceptual` + `datos-relacion-*`) e integrar con lo publicado en `origin/main` (`e143f37`). |
| **2. Ocho Casos de Uso (CU1–CU8)** | **Word y EA Notes actualizados; revisión con flujo final pendiente** | Especificaciones actualizadas en `P2-INF513-GRUPO05SA.docx` (`fase2_word.json`, Cap. IV intacto) y en `Notes` de `crm-p2.eapx` (`fase2_ea.json`, más asociación Visitante–CU6). | Validar consistencia final tras terminar interacciones y capturas en el DOCX/PDF. |
| **3. Diagramas de clases y miembros (`final-01` a `final-06`)** | **En curso (clases completas; relaciones al ~83.9% de aristas únicas)** | `final-01-catalogo` a `final-05-capas` completadas: `143` clases propias únicas, `707` métodos propios únicos (`286` participaciones de clases, `1,356` participaciones de métodos). `427` vistas de clase exportadas (`exportaciones_clases_visibles.json`). En `final-06-relaciones`: `356` vistas `clases-relacion-001..356` exportadas cubriendo `767` de `914` aristas únicas del catálogo (`cobertura_relaciones_clases.json`), más `clases-relacion-357.emf` guardado en disco. | Completar las **147 aristas únicas restantes** de relaciones entre clases (`CU7`/`CU8`), completar el PNG/JSON de `clases-relacion-357`, ejecutar `final-07-asociaciones` (`asociaciones_fuente.py`), `final-08-algoritmos` (`algoritmos_documentados.py`) y `final-15-exportar-relaciones`. |
| **4. Secuencia y Comunicación (`final-09`, `final-10`)** | **Parcial de corrida previa; lote final pendiente** | Existen `895` exportaciones previas en `exportaciones_interacciones.json` (`616` comunicación, `279` secuencia; CU1–CU6) con revisión 5 preparada en `actualizar_interacciones.py`, pero falta CU7 y CU8 y falta la pasada oficial de `IsReturn`. Bajo `modelo_final.py`, `final-09-interacciones` y `final-10-presentacion-interacciones` **no han iniciado**. | Ejecutar `final-09-interacciones` (lotes de 80 hasta `INTERACCIONES_COMPLETAS` en CU1–CU8) y `final-10-presentacion-interacciones` (`actualizar_interacciones.py presentacion`), más validar que `trazas_interacciones.json` tenga secuencia == comunicación en todos los flujos y reconciliar con `sd-cu1..8` de `origin/main` (`1d71fa4`). |
| **5. Modelo Conceptual / Lógico / Físico gráfico (`final-11`)** | **Parcial (atributos agregados en EA; figuras pendientes)** | `cuotas.token_pago`, `transacciones_stripe.token_publico` y `transacciones_stripe.expira_en` agregados como atributos en EA (`cambios_fase1_ea.json`). `conceptual.emf`/`.png` siguen con fecha `01:03`. | Ejecutar `final-11-conceptual` (`actualizar_datos_despliegue.py conceptual`), revisar legibilidad de `conceptual` y `datos-relacion-*`, e insertar en Word. |
| **6. Diagrama de Despliegue (`final-12`)** | **Pendiente** | Script `generadorDocumento/ea/actualizar_datos_despliegue.py despliegue` preparado; `despliegue.emf`/`.png` siguen de las `01:03`. | Ejecutar `final-12-despliegue` y verificar separación entre entorno local, destino institucional previsto (`tecnoweb.org.bo`) y externos (Stripe/Gmail). |
| **7. Diagramas de Navegación Conallen (`final-13`, `final-14`)** | **Fuente lista; ejecución EA pendiente** | `generadorDocumento/navegacion.py` actualizado (`navegacion-diferencias.json` = `[]`, 0 diferencias respecto al código). Script `actualizar_navegacion.py` preparado sin ejecutar bajo `modelo_final.py`. | Ejecutar `final-13-navegacion` y `final-14-base` y validar visualmente `nav-*` y enlaces Conallen. |
| **8. Arquitectura y Herramientas (Word Cap. VIII / Sec. 5)** | **Texto aplicado en DOCX; revisión final pendiente** | Actualizado puntualmente en `P2-INF513-GRUPO05SA.docx` (`fase7_word.json`, Cap. IV intacto): PHP `8.4.24`, PostgreSQL `17.4`, EA 15, responsabilidades de capas P/N/D y alcance de CU6. | Validar estilos de títulos y paginación al consolidar el documento final. |
| **9. Pruebas QA aisladas y Capturas** | **Pendiente** | Script `qa_controlado.py` copiado en `continuacion_documental/`, sin ejecutar aún en esta fase. | Ejecutar pruebas QA aisladas (sin pagos reales, sin correos comerciales ni migraciones destructivas), obtener capturas reales vigentes e incorporarlas en el capítulo de pruebas. |
| **10. Inserción de figuras y generación DOCX/DOC/PDF** | **Pendiente** | `generadorDocumento/insertar_figuras_actuales.py`, `numerar_elementos.py`, `limpiar_medios_docx.py` y `exportar.ps1` actualizados en el repo. `P2-INF513-GRUPO05SA.doc` y `.pdf` siguen en versión `01:03`. | Insertar figuras actualizadas con `insertar_figuras_actuales.py`, actualizar numeración/índice, ejecutar `exportar.ps1` (DOCX -> PDF -> DOC) e inspeccionar visualmente todas las páginas generadas. |
| **11. Validación integral de consistencia** | **Pendiente** | `generadorDocumento/verificar_actualizacion.py` listo para contrastar `ea_antes_edicion.json` vs `ea_actual.json`. | Tomar snapshot `ea_actual.json`, ejecutar `verificar_actualizacion.py` verificando GUIDs originales, 4 actores/diagrama 9 intacto, Cap. IV intacto, códigos funcionales sin cambios, miembros/métodos y 100% de paridad SQL/código. |
| **12. Decisión sobre vistas masivas y publicación final** | **Pendiente (requiere decisión del equipo)** | `retirar_masivas_seguro.py` evaluado en dry-run (`plan_retirada_masivas.json`: 47 originales vs 1,624 complementarias). | Tras exportar todo e inspeccionar el Word/PDF final, decidir si se conservan las 1,624 vistas complementarias en `crm-p2.eapx` o se aplica `retirar_masivas_seguro.py --aplicar`, e integrar limpiamente con `origin/main` antes de entregar. |

---

## 5. Detalle de la base de datos (`token_pago`, `token_publico`, `expira_en` y restricciones)

Para claridad absoluta del equipo sobre los cambios recientes de Stripe/pagos públicos respecto a la auditoría:

- **Eliminación de columnas obsoletas de envíos automáticos:** Ya estaba aplicada en `2b6ab31` y reflejada en la documentación (`ordenes_pago.envio_automatico`, `cuotas.primer_envio_en`, `recordatorio_previo_en`, `recordatorio_vencimiento_en`, `recordatorio_mora_en` = **0 ocurrencias** en `esquema.sql`, `actualizacion_contenido.py` y EA). Quedan exactamente `31` tablas y `287` columnas en `public`.
- **Estado de las columnas y restricciones vigentes de enlaces públicos:**
  - `cuotas.token_pago` (`varchar(80)`, nullable)
  - `transacciones_stripe.token_publico` (`varchar(80)`, nullable)
  - `transacciones_stripe.expira_en` (`timestamp(0) without time zone`, nullable)
  - `cuotas_token_pago_unique` (`UNIQUE (token_pago)`)
  - `transacciones_stripe_token_publico_unique` (`UNIQUE (token_publico)`)
- **Dónde YA fueron actualizadas en este corte:**
  1. `generadorDocumento/fuentes/esquema.sql` (volcado estructural actualizado con las tres columnas y las dos restricciones `UNIQUE`).
  2. `generadorDocumento/documento/P2-INF513-GRUPO05SA.docx` (secciones `7.2. Diseño Lógico` y `7.3. Diseño Físico`, diccionario de `287` columnas, `113` restricciones, `55` índices y `5` triggers).
  3. `generadorDocumento/ea/crm-p2.eapx` (las tres columnas agregadas por API oficial en las entidades `cuotas` y `transacciones_stripe` del modelo conceptual; ver `cambios_fase1_ea.json`).
- **Qué sigue pendiente sobre este punto:**
  1. Ejecutar `final-11-conceptual` (`actualizar_datos_despliegue.py conceptual`) para regenerar los diagramas exportados (`conceptual` / `datos-relacion-*`) con los nuevos atributos visibles e insertarlos en el Word (`P2-INF513-GRUPO05SA.docx` sigue mostrando la figura `conceptual.emf` de las `01:03`).
  2. Coordinar con `e143f37` de `origin/main` (donde otro integrante actualizó por su lado `fuentes/esquema.sql`, `conceptual.emf`/`.png` y el `.docx`).

---

## 6. Instrucciones exactas para que el equipo continúe

Antes de ejecutar cualquier script:

1. **Revisar y resolver primero la divergencia Git con `origin/main` (`1d71fa4`)** (ver sección 8). No sobrescribir binarios sin acordar qué versión de `crm-p2.eapx` y `P2-INF513-GRUPO05SA.docx` se toma como base común.
2. **Restaurar el directorio de trabajo `tmp/actualizacion_documental/`** (ignorado por Git) desde la copia versionada:
   ```powershell
   New-Item -ItemType Directory -Force -Path "tmp/actualizacion_documental" | Out-Null
   Copy-Item -Path "generadorDocumento/continuacion_documental/*" -Destination "tmp/actualizacion_documental/" -Force
   ```
3. **Retirar la bandera de detención controlada** antes de relanzar cualquier script que llame a `compatibilidad_emf.mjs`:
   ```powershell
   Remove-Item "tmp/actualizacion_documental/solicitar_reinicio.flag" -ErrorAction SilentlyContinue
   ```
4. **Verificar Node.js y Enterprise Architect 15 (32 bits) en la PC donde se continúe:**
   - `modelo_final.py` y `continuar_modelo.ps1` tienen escrita la ruta local de Codex para `CODEX_DOCUMENT_NODE` (`C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime...\node.exe`). Si se corre en otra PC, eliminar esa asignación o apuntarla a su `node.exe` local (o dejar vacío para que `sincronizar_documentacion.py` use `shutil.which("node")`).
   - Confirmar que **solo haya un proceso escritor COM de EA a la vez** y con JET4 habilitado en EA 15.
5. **Reconciliar `clases-relacion-357` y reanudar `final-06-relaciones` hasta `final-15`:**
   - Como `clases-relacion-357.emf` se escribió en disco antes de registrar `exportaciones_relaciones_clases.json`, al reanudar `python tmp/actualizacion_documental/modelo_final.py` (o ejecutar `sincronizar_documentacion.py relaciones-clases`), verificar si crea/actualiza la vista siguiente sin duplicar y dejar que complete `final-06` a `final-15`.
   - **Nota sobre `modelo_final.py`:** antes de ejecutar `final-09-interacciones`..`final-15`, revisar que `ea_antes_edicion.json` exista en `tmp/actualizacion_documental/` si luego se ejecutará `verificar_actualizacion.py` (ese snapshot pesado de ~6.5–20 MB no se subió a Git; si hace falta contrastar el estado inicial, puede extraerse del `crm-p2.eapx` del commit `2b6ab31` mediante `sincronizar_documentacion.py snapshot` en una copia).
6. **NO ejecutar los scripts legacy destructivos** sobre el documento editado manualmente:
   - **No ejecutar** `documento_p2.py` (regenera el documento completo y pisa ediciones manuales del Capítulo IV y textos revisados).
   - **No ejecutar** `ea_p2.py` ni `ea_faltantes.py` sin revisar cómo interactúan con `sincronizar_documentacion.py` y con las ramas divergentes de `origin/main`.
7. **Cerrar ciclo Word/DOC/PDF y verificación:**
   - Correr `qa_controlado.py` / capturas reales si aplica.
   - Ejecutar `python generadorDocumento/insertar_figuras_actuales.py`, `numerar_elementos.py`, `limpiar_medios_docx.py` y `powershell -File generadorDocumento/exportar.ps1`.
   - Ejecutar `python generadorDocumento/ea/sincronizar_documentacion.py snapshot` y `python generadorDocumento/verificar_actualizacion.py`.

---

## 7. Reglas y restricciones del trabajo original

Deben mantenerse sin excepción durante toda la continuación:
- **Conservar intacto el Capítulo IV** (verificado mediante comparación OOXML en `actualizar_documento.py` y `verificar_actualizacion.py`).
- **Conservar los 8 nombres e identificadores originales de CU (`CU1`–`CU8`) y los 4 actores canónicos** (`Administrador`, `Coordinador`, `Vendedor`, `Visitante`) más el **diagrama de actores `Diagram_ID = 9` completamente intacto**.
- **Conservar la estructura original de 10 capítulos y metodología PUDS**, así como las **clases, diagramas y GUIDs originales** (reutilizando elementos mediante API COM oficial de EA; no usar SQL `Execute` directo sobre el `.eapx`).
- **No modificar código funcional** (`presentacion/`, `negocio/`, `datos/`), **PostgreSQL**, lógica de Stripe, correos ni permisos/roles.
- **No incluir secretos, credenciales, `.env`, claves de Stripe, contraseñas SMTP, tokens ni datos personales de prospectos** en scripts, documentos, SQL ni commits.

---

## 8. Problemas conocidos, riesgos y limitaciones (INCLUYE DIVERGENCIA CON `origin/main`)

1. **Divergencia crítica con `origin/main` (2 commits adelantados de compañeros):**
   - El trabajo local partió de `2b6ab31`. Mientras Codex ejecutaba estas etapas, el remoto `origin/main` recibió 2 commits de `vangiewz`:
     - `e143f37` (`2026-11-26 09:49:56`): *"Generador del documento: datos y figura conceptual actualizados"* — modificó `P2-INF513-GRUPO05SA.docx/.doc/.pdf`, `crm-p2.eapx`, `conceptual.{emf,png}`, `fuentes/esquema.sql`, `README.md`, `REGLAS_DOCUMENTO_P2.md`, `ea_p2.py`, `posiciones.json`, `actualizar_datos_docx.py`, etc.
     - `1d71fa4` (`2026-11-26 10:23:16`): *"Generador del documento: secuencias de 7.4 al día con el código y legibles al imprimir"* — modificó `P2-INF513-GRUPO05SA.docx/.doc/.pdf`, `crm-p2.eapx`, `sd-cu1..8.{emf,png}`, `codigo.py`, `actualizar_secuencias.py`, `ea_faltantes.py`, `formato_g07.py`, `documento_p2.py`, etc.
   - **Riesgo real de conflicto binario:** Tanto este avance local como `origin/main` modificaron `generadorDocumento/ea/crm-p2.eapx`, `generadorDocumento/documento/P2-INF513-GRUPO05SA.docx`, `generadorDocumento/diagramas/sd-cu1..6.{emf,png}`, `generadorDocumento/README.md` y `generadorDocumento/fuentes/esquema.sql`.
   - **Resolución adoptada:** Para no sobrescribir a ciegas el trabajo de `vangiewz` en `main` ni perder el avance de Codex, este estado queda publicado en la rama de respaldo explícita **`respaldo-documentacion-leonardo`**, dejando `origin/main` intacto en `1d71fa4` hasta que el equipo concilie ambos trabajos.
2. **PNGs de clases generales eliminados en esta copia (`cls-cu1..8.png`):** `sincronizar_documentacion.py` retiró intencionalmente los `.png` de los 8 diagramas de clase generales cuando su área lógica superó `10,000,000` (conservando sus `.emf` de alta resolución). Si el flujo final requiere `.png`, debe tenerse en cuenta esa regla o ajustarse `lim` con precaución por la memoria de EA 32 bits.
3. **Exportaciones inconclusas puntuales:**
   - `clases-relacion-357.emf` quedó escrito en disco sin `clases-relacion-357.png` ni registro en `exportaciones_relaciones_clases.json` por la detención controlada.
   - `com-cu6-flujo-26-08.emf` (`11:38:31`) quedó sin `.png` de una ejecución previa de interacciones que falló en EA 32 bits.
   - `ubicacion.png` existe sin `.emf` equivalente.
4. **Ruta hardcoded de Node.js en scripts de Codex:** `modelo_final.py` y `continuar_modelo.ps1` fijan `CODEX_DOCUMENT_NODE` a una ruta `WindowsApps\OpenAI.CodexPrimaryRuntime...`. Debe actualizarse o removerse fuera de ese entorno.
5. **Snapshots EA masivos (~20 MB c/u) y `emf_nativos/` (~66.8 MB) no versionados:** Por tamaño e higiene de Git, solo se versionó el subconjunto liviano (`7.57 MB`, `42` archivos) en `generadorDocumento/continuacion_documental/`. Si se requiere `ea_antes_edicion.json` para `verificar_actualizacion.py`, deberá regenerarse desde el `.eapx` del commit `2b6ab31`.
6. **Dependencia de Microsoft Word nativo en Windows:** Según `15_CONTROL_ACTUALIZACION_DOCUMENTAL.md`, `render_docx.py` falla porque no hay `soffice.exe` instalado; `exportar.ps1` depende de Word COM (`Word.Application`) en Windows para actualizar campos/TOC y generar PDF/DOC.
