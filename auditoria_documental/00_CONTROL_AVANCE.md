# Control de avance y cobertura

Commit auditado: `5bf47b2e863631908e37718fb343fd776003fb5b`. Fecha: 26/11/2026 (America/La_Paz). Solo lectura de originales.

Estado inicial Git: limpio. Escrituras autorizadas: únicamente auditoria_documental/. Los extractores se ejecutaron con -B para no crear pycache en fuentes.

## Fuentes y conteos

Maestro actual de edición: generadorDocumento/documento/P2-INF513-GRUPO05SA.docx. Fuentes regenerables: contenido.py, esquema.sql, EA y generadores. DOC/DOCX con texto idéntico,108 páginas y65 imágenes; narrativa PDF comprobada tras quitar pies de página.47 diagramas EA,49 imágenes base,43 tablas Word,111 clases PHP,521 métodos. Base efectiva local crm_educativo/PostgreSQL17.4;31 tablas public y laravel.migrations.


| Etapa | Estado | Evidencia y observaciones |
| --- | --- | --- |
| A | Revisado con observaciones | documentacion_inventario.json; equivalencia_formatos.json; 02 |
| B | Revisado con observaciones | Inventarios DOCX/PDF/EA/clases/rutas y pg_* completos del alcance |
| C | Revisado con observaciones | 284 columnas coinciden;8 faltan;31 PK/46 FK/28 CHECK coinciden;2 UNIQUE ausentes;07 |
| D | Revisado con observaciones | 8 CU y4 actores humanos revisados; enunciado primario No verificable |
| E | Revisado con observaciones | 58 clases PHP documentadas existen;305 operaciones contrastadas;2 firmas diferentes; relaciones de datos contrastadas |
| F | Revisado con observaciones | 8 secuencias y8 comunicaciones, todos los mensajes extraídos; orden de recorridos seleccionado revisado; alternativas incompletas |
| G | Revisado con observaciones | Arquitectura y permisos estáticos;34 permisos coinciden. Despliegue institucional No verificable |
| H | Revisado con observaciones | Pagos/SMTP/recordatorios/temas leídos; sin cobros/correos; recepción y ejecución efectiva No verificable |
| I | Revisado con observaciones | Scripts inventariados; evidencia histórica existente; no se ejecutó suite transaccional.08 traza por ruta con tablas candidatas |
| J | Revisado con observaciones | 108 páginas inspeccionadas en miniaturas,49 imágenes base vistas; páginas críticas ampliadas. Papel y detalles densos no verificables |
| K | Revisado con observaciones | 14 entregables consolidados; hallazgos únicos, métricas, plan y checklist. Verificación de integridad final pendiente de script de cierre |

## Cobertura y limitaciones que permanecen

- Revisado: todos los encabezados del documento; catálogo de tablas/columnas/PK/FK/constraints/índices/triggers/funciones; todos los CU macro; todas las operaciones PHP representadas por EA y mensajes N/D explícitos.
- Revisado con observaciones: comportamiento seleccionado por diagrama y correspondencia macro por CU; no todas las llamadas internas están dibujadas ni toda figura es completa.
- No verificable visualmente en esta resolución: todos los textos diminutos, cruces y cortes individuales de las4 navegaciones y figuras muy densas. Se inspeccionó composición y se conservaron atributos/conectores para revisión ampliada.
- No verificable: firma completa con defaults/referencias/variádicos en todas las operaciones; valores heredados/framework; coincidencia píxel a píxel DOC/DOCX/PDF.
- No verificable: material docente primario; despliegue real institucional, versión remota, SMTP recibido y cron en servidor.
- No verificable por restricción de solo lectura: resultados actuales de pruebas de escritura/concurrencia, cobros, webhooks efectivamente entregados y correos. No se reemplazan por afirmaciones de funcionamiento.
- No certificada:3FN universal, contenido de todos los registros, seguridad integral o WCAG.

Estas limitaciones describen exactamente qué falta para certificarlo. No se detuvo ninguna etapa para pedir confirmaciones de contenido; solo se solicitaron autorizaciones del entorno de archivos/ejecución cuando el sandbox rechazó escrituras autorizadas por el usuario.

## Hallazgos

28 registros únicos en hallazgos.json y09. {"CRÍTICO": 2, "ALTO": 16, "MEDIO": 9, "BAJO": 1}. Registro por categoría en las hojas filtrables.

## Archivos de evidencia

- `evidencias/archivos.json`
- `evidencias/cadenas_cu.json`
- `evidencias/capitulos.json`
- `evidencias/cardinalidades.json`
- `evidencias/casos_uso_auditados.json`
- `evidencias/chequeo_generador.json`
- `evidencias/clases.json`
- `evidencias/clases_generador.json`
- `evidencias/comparacion_atributos_ea.json`
- `evidencias/comparacion_clases_ea.json`
- `evidencias/comparacion_columnas.json`
- `evidencias/comparacion_conceptual_ea.json`
- `evidencias/comparacion_funciones.json`
- `evidencias/comparacion_indices.json`
- `evidencias/comparacion_mapeo_docx.json`
- `evidencias/comparacion_metodos_ea.json`
- `evidencias/comparacion_permisos.json`
- `evidencias/comparacion_restricciones.json`
- `evidencias/comparacion_secuencias.json`
- `evidencias/comparacion_triggers.json`
- `evidencias/componentes_react.json`
- `evidencias/configuracion_efectiva.json`
- `evidencias/contenido_ACTORES.json`
- `evidencias/contenido_ACTORES_CU.json`
- `evidencias/contenido_ALCANCE.json`
- `evidencias/contenido_ANEXOS.json`
- `evidencias/contenido_BIBLIOGRAFIA.json`
- `evidencias/contenido_CU.json`
- `evidencias/contenido_DETALLE.json`
- `evidencias/contenido_EVIDENCIA.json`
- `evidencias/contenido_HERRAMIENTAS.json`
- `evidencias/contenido_PAQUETES.json`
- `evidencias/contenido_PERMISOS.json`
- `evidencias/contenido_POR_CONFIRMAR.json`
- `evidencias/contenido_PRUEBAS_BLANCA.json`
- `evidencias/contenido_PRUEBAS_NEGRA.json`
- `evidencias/contenido_RECURSOS.json`
- `evidencias/contenido_REQUERIMIENTOS.json`
- `evidencias/diagramas.json`
- `evidencias/diagramas_auditados.json`
- `evidencias/diferencias_migraciones.json`
- `evidencias/documentacion_inventario.json`
- `evidencias/ea_t_attribute.json`
- `evidencias/ea_t_connector.json`
- `evidencias/ea_t_diagram.json`
- `evidencias/ea_t_diagramlinks.json`
- `evidencias/ea_t_diagramobjects.json`
- `evidencias/ea_t_object.json`
- `evidencias/ea_t_operation.json`
- `evidencias/ea_t_operationparams.json`
- `evidencias/ea_t_package.json`
- `evidencias/endpoints_auditados.json`
- `evidencias/equivalencia_formatos.json`
- `evidencias/esquema_documental.json`
- `evidencias/estructura.json`
- `evidencias/funciones_api.json`
- `evidencias/git_final.txt`
- `evidencias/git_inicial.json`
- `evidencias/hallazgos.json`
- `evidencias/historial_git.json`
- `evidencias/imagenes_docx.json`
- `evidencias/imagenes_docx_vml.json`
- `evidencias/integridad_originales.json`
- `evidencias/mensajes_ea.json`
- `evidencias/metodos.json`
- `evidencias/metricas_extraccion.json`
- `evidencias/metricas_finales.json`
- `evidencias/paginas_pdf.json`
- `evidencias/parrafos_docx.json`
- `evidencias/pdf_texto.txt`
- `evidencias/pg_columnas.json`
- `evidencias/pg_contexto.json`
- `evidencias/pg_fk_columnas.json`
- `evidencias/pg_funciones.json`
- `evidencias/pg_indices.json`
- `evidencias/pg_materializadas.json`
- `evidencias/pg_migraciones.json`
- `evidencias/pg_permisos_aplicacion.json`
- `evidencias/pg_restricciones.json`
- `evidencias/pg_resultados.json`
- `evidencias/pg_roles_aplicacion.json`
- `evidencias/pg_secuencias.json`
- `evidencias/pg_tablas.json`
- `evidencias/pg_tipos.json`
- `evidencias/pg_tipos_exactos.json`
- `evidencias/pg_triggers.json`
- `evidencias/pg_vistas.json`
- `evidencias/pruebas_inventario.json`
- `evidencias/qa_libros.json`
- `evidencias/relaciones_ea.json`
- `evidencias/requisitos_enunciado.json`
- `evidencias/restricciones_documentales.json`
- `evidencias/resumen_comparaciones.json`
- `evidencias/rutas_estaticas.json`
- `evidencias/rutas_laravel.json`
- `evidencias/secciones_reales.json`
- `evidencias/secciones_revisadas.json`
- `evidencias/tablas_docx.json`
- `evidencias/trazabilidad_integral.json`
- `evidencias/validacion_entrega.json`
- `evidencias/variables_contenido.json`
- `evidencias/verificacion_claves_impresas.json`
- `evidencias/verificacion_xlsx.json`
- `evidencias/versiones_lock.json`
- `evidencias/word_doc.txt`
- `evidencias/word_doc_info.json`
- `evidencias/word_docx.txt`
- `evidencias/word_docx_info.json`

No reiniciar desde cero: continuar leyendo este control y reutilizar inventarios. Los JSON comparacion_* son evidencia de un momento y commit; si cambia HEAD, registrar una nueva captura antes de recomparar.

## Cierre de integridad y entrega

Los14 entregables existen y están poblados. Se reabrieron ambos XLSX:19 hojas de trazabilidad y1 de hallazgos, filtros y A2 congelado, sin fórmulas ni errores de celda. Comparadas PK/FK impresas de31 tablas. Ver validacion_entrega.json y qa_libros.json. Las vistas PIL revisan lectura de primeras filas/columnas; no se certifica render nativo Excel.

Recalculados SHA256 de los1028 originales inventariados:0 cambios,0 ausentes. La BD se consultó solo mediante transacciones de lectura; no se dispararon acciones comerciales. Estado Git final se registra por separado en git_final.txt. EtapaK: Revisado con observaciones por las limitaciones declaradas, sin pendientes ocultos.
