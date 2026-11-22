# Continuación documental — UNEXO

Este directorio conserva de forma versionada el subconjunto limpio e indispensable de control, trazabilidad, cobertura y scripts de reanudación recuperados desde `tmp/actualizacion_documental/` (directorio temporal ignorado por `.gitignore`), para que el equipo pueda retomar la actualización sin depender de archivos locales no versionados.

## Qué contiene

- **Orquestación y scripts de continuación:**
  - `modelo_final.py`, `modelo_final_progreso.json`: orquestador secuencial por etapas (`final-01` a `final-15`) y estado exacto de avance (`final-01` a `final-05` completadas; `final-06-relaciones` detenida de forma controlada en `clases-relacion-357.emf`).
  - `continuar_modelo.ps1`: script PowerShell anterior de continuación por lotes.
  - `retirar_masivas_seguro.py`, `plan_retirada_masivas.json`: verificador/limpiador de vistas complementarias en `crm-p2.eapx` (**ejecutado únicamente en dry-run**, nunca con `--aplicar`; distingue 47 diagramas originales y 1,624 vistas complementarias).
  - `auditar_avance.py`, `actualizar_control.py`, `sincronizar_fuentes.py`, `preparar_fase1.py`, `qa_controlado.py`.
  - `solicitar_reinicio.flag`: bandera que provocó la detención controlada de `final-06-relaciones` tras guardar el EMF nativo `clases-relacion-357.emf`.
- **Evidencias, cobertura y manifiestos:**
  - `avance_exacto_diagramas.txt` / `.json`: corte de inventario de las 12:16 p. m. (luego siguió hasta `clases-relacion-356` en JSON / `clases-relacion-357.emf` en disco).
  - `cobertura_relaciones_clases.json`, `exportaciones_relaciones_clases.json`: registro exacto de 356 vistas de relación exportadas y sus aristas cubiertas.
  - `exportaciones_clases.json`, `exportaciones_clases_visibles.json`: 427 vistas de clase (8 diagramas principales `cls-cu1..8` + 419 detalles `cls-cu*-detalle-*`).
  - `exportaciones_interacciones.json`, `trazas_interacciones.json`: 895 exportaciones y trazas de interacciones registradas en pasadas previas (pendiente completar lote completo en `final-09` y pasada `IsReturn` en `final-10`).
  - `catalogo_fuente.json`, `postgres_actual.json`, `esquema_actual.sql`, `estructura_word_actual.json`, `inventario_ea_inicial.json`, `inventario_ea_reutilizado.json`, `plan_retirada_masivas.json`, `vistas_fuera_pagina.json`, `organizacion_clases_nuevas.json`, `cambios_clases.json`, `cambios_fase1_ea.json`, `conteos_fuente_final.json`, `fase1_word.json`, `fase2_ea.json`, `fase2_word.json`, `fase7_word.json`, `navegacion-diferencias.json`, `diagnostico_vitalidad_20261126.json`, `fuente_exportacion_ea.json`, `resolucion_exportacion_ea.json`, `archivos_iniciales.json`.
- **Logs relevantes (renombrados a `.log.txt` para no quedar ocultos por `.gitignore`):**
  - `modelo-final-control.log.txt`
  - `final-06-relaciones.log.txt`

## Qué NO se incluyó por peso / limpieza

No se copiaron los snapshots EA masivos (~20 MB c/u: `ea_antes_edicion.json`, `ea_antes_clases.json`, `ea_despues_clases.json`, `ea_antes_retirar_masivas.json`), ni `tmp/actualizacion_documental/emf_nativos/` (~66.8 MB), ni `exportaciones_retiradas/` (~6.3 MB), ni archivos de prueba (`prueba-vector.docx`, etc.), ni copias redundantes de `.eapx`/`.doc`/`.docx`.

## Nota importante antes de reanudar

1. Los scripts en `generadorDocumento/ea/` y `generadorDocumento/` leen y escriben en `tmp/actualizacion_documental/`. Antes de reanudar una etapa, copiar el contenido de este directorio a `tmp/actualizacion_documental/` y revisar `modelo_final.py` / `continuar_modelo.ps1` porque apuntan a `CODEX_DOCUMENT_NODE` con una ruta local de Codex en WindowsApps.
2. Quitar o mover `tmp/actualizacion_documental/solicitar_reinicio.flag` antes de relanzar cualquier script que invoque `generadorDocumento/ea/compatibilidad_emf.mjs`, ya que su sola presencia detiene la exportación tras el primer EMF.
3. Revisar primero la divergencia en GitHub con `origin/main` (`1d71fa4`, trabajo previo de compañeros sobre `P2-INF513-GRUPO05SA.*`, `crm-p2.eapx`, `conceptual.*` y `sd-cu1..8.*`).
