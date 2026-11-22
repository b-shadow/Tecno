# Plan de corrección posterior

Commit auditado: `5bf47b2e863631908e37718fb343fd776003fb5b`. Fecha: 26/11/2026 (America/La_Paz). Solo lectura de originales.

**No se ejecutó ninguna corrección del proyecto.** El plan evita redibujar figuras antes de fijar reglas y catálogo.

| Orden | Fase | Hallazgos | Capítulos | Editables/referencia | Depende de | Acción concreta | Ámbito |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Confirmar base de requisitos y reglas | REQ-001; REQ-002; MC-001; PAG-001; PAG-002 | I, IV, V, VII | Enunciado primario; contenido.py; REGLAS_DOCUMENTO_P2.md | Ninguna | Acordar nombres, pagos nuevos/históricos, comisión y nivel conceptual. | Solo documentación salvo cambio de política expresamente solicitado. |
| 2 | Sincronizar catálogo y diccionario | BD-001; BD-002 | VII | fuentes/esquema.sql; ea/crm-p2.eapx; contenido.py | 1 | Capturar schema-only validado en tarea posterior; incluir8 campos y2 UNIQUE. Mantener diseño manual. | Documentación; no migrar BD salvo defecto nuevo comprobado. |
| 3 | Actualizar actores y especificaciones | CU-001; CU-002; CU-003; CU-004 | I, V | contenido.py; EA casos/actores | 1 | Conservar CU1–CU8, incorporar subobjetivos públicos y postcondiciones por salida. | Documentación. |
| 4 | Corregir clases y relaciones | CL-001; CL-002; ARQ-001; ARQ-002 | VI, VIII | EA clases; código N/D como referencia; REGLAS y README | 2,3 | Actualizar firmas unión, incorporar pérdida CU5 y decidir regla de cálculo en modelo. | Documentación; eventual refactor requiere una tarea diferente. |
| 5 | Completar comportamiento | SEC-001; SEC-002; NOT-001 | VI, VII | EA secuencia/comunicación; ea_faltantes.py | 3,4 | Mostrar token, webhook, cuota/conversión y SMTP después de commit, condiciones de error. | Documentación, no recrear todos los diagramas sin preservar posiciones. |
| 6 | Despliegue, apariencia e interfaces | DEP-001; ACC-001; UI-001 | VII, VIII | EA despliegue; captura vigente por rol; DESIGN.md | 2–5 | Separar local/propuesto/real, SMTP/scheduler y paletas; capturas sin información sensible. | Documentación; operación remota pendiente de acceso/evidencia. |
| 7 | Pruebas y trazabilidad | QA-001; DOC-001 | X y transversal | scripts QA; documento; matrices | 1–6 | Actualizar escenarios de pagos y registrar ejecución con commit en BD QA aislada. | Puede escribir solo en nueva QA autorizada; prohibido ejecutar ahora. |
| 8 | Edición e impresión final | FMT-001; FMT-002; FMT-003; DOC-002 | Todos | DOCX y generador; fuentes EA | 1–7 | Numerar figuras, ajustar tamaños/franjas, huérfanos y actualizar índice usando exportación controlada. | Solo documentación; verificar DOC/DOCX/PDF y hashes de fuentes conservadas. |

## Procedimiento para conservar cambios manuales

1. Respaldar DOCX/DOC/PDF/EAPX, imágenes y posiciones con hash en una tarea de corrección autorizada.
2. Distinguir cambio manual ya presente de cambio en contenido.py; trasladar las ediciones deseadas a fuentes antes de regenerar.
3. Validar esquema real y actualizar fuentes sin ejecutar migraciones de producción.
4. Hacer cambios mínimos en EA y exportar solo figuras afectadas cuando sea posible.
5. Aplicar actualizar_figura_docx/actualizar_secuencias si el alcance es parcial; documento_p2.py reconstruye todo y perdería ediciones ajenas a su fuente.
6. Exportar los tres formatos de manera controlada al finalizar y comparar texto, páginas y figuras, con impresión de muestras.

Riesgo de propagación: cambiar campos afecta conceptual/mapeo/físico/modelos; cambiar actor/CU afecta casos, clases, comunicación, secuencia, navegación y pruebas; cambiar política de pago afecta casi toda la trazaCU6. Por eso formato y capturas se cierran al final. Conservar estructura académica de diez capítulos; no inventar una nueva estructura.
