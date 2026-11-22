from pathlib import Path
p=Path('auditoria_documental/15_CONTROL_ACTUALIZACION_DOCUMENTAL.md')
p.write_text('''# Control de actualización documental UNEXO

Commit inicial: `2b6ab3158f946b507765e236706708ae3e71ddc9`. Fecha: 26/11/2026.

## Alcance y preservación

Se continúa la auditoría original y la actualización documental posteriormente autorizada, sin repetir inventarios válidos. Se preservan los ocho nombres/identificadores de CU, los cuatro actores, el diagrama de actores, el capítulo IV, diez capítulos y PUDS. No modificar código funcional, reglas comerciales, migraciones ni estructura PostgreSQL. Commit y push únicamente después de verificar la entrega completa.

Respaldo original: `backups/documental-20261126/generadorDocumento/`. Huellas: `tmp/actualizacion_documental/archivos_iniciales.json`. No ejecutar documento_p2.py ni los generadores EA antiguos que recrean diagramas o escriben tablas internas.

## Estado verificado al reanudar

| Fase | Estado | Evidencia / pendiente |
|---|---|---|
| Preparación | Completada | Respaldo e inventario original: 52 paquetes, 47 diagramas. EAPX abre por COM oficial tras habilitar JET4 en EA. |
| 1 PostgreSQL documental | Actualizada; validación final pendiente | Lectura exclusiva de PostgreSQL; SQL, mapeo, físico, diccionario de 287 columnas, restricciones, índices y cinco triggers actualizados en DOCX. Tres atributos incorporados al modelo EA. |
| 2 Ocho CU | Word y fuente actualizados; EA pendiente | Ocho especificaciones completas conservan encabezados literales. Capítulo IV protegido por comparación OOXML. |
| 3 Clases | Modelo sincronizado; presentación en revisión | Ocho diagramas originales y 255 vistas de clase complementarias, elementos reutilizados. Métodos, constructores, visibilidad, parámetros/defaults y tipos propios del código. Corrección de visibilidad oficial en curso antes de insertar imágenes. |
| 4 Secuencia/comunicación | Pendiente | Actualizar ocho originales y vistas complementarias de flujos reales, sin nuevos CU ni actores. |
| 5 Conceptual | Atributos actualizados; legibilidad pendiente | cuotas.token_pago, transacciones_stripe.token_publico y expira_en; relaciones originales preservadas. |
| 6 Despliegue | Pendiente | Conservar equipos y red; separar entorno local, institucional previsto y Stripe/Gmail externos. |
| 7 Arquitectura/implementación | Pendiente | Actualizar puntualmente los capítulos autorizados, sin regenerar el maestro. |
| 8 Pruebas | Pendiente | Únicamente QA aislado existente; no pagos reales, migraciones ni correos comerciales reales. |
| 9 Capturas | Pendiente | Capturas reales después de las pruebas. |
| 10 Word/DOC/PDF | Pendiente | Insertar exportaciones EA vigentes, actualizar campos, exportar e inspeccionar todas las páginas. |
| 11 Consistencia | Pendiente | Comparar GUID, actores/diagrama protegido, capítulo IV, miembros, PostgreSQL y hashes funcionales. |
| 12 Publicación | Pendiente | Revisar cambios, secretos y tamaños; commit y push al completar la entrega. |

## Evidencias reutilizables

- `postgres_actual.json`: 31 tablas, 287 columnas, 31 PK, 46 FK, siete UNIQUE, 28 CHECK, 55 índices y cinco triggers en public; 32 tablas/290 columnas contando laravel.migrations. Las 113 restricciones fueron comparadas. Sin escrituras en la base comercial.
- `fase1_word.json`, `fase2_word.json`: ediciones puntuales completadas y capítulo IV intacto.
- `ea_antes_edicion.json`: modelo inicial; `ea_despues_clases.json`: modelo tras sincronización de miembros.
- `catalogo_fuente.json`, `cambios_clases.json`, `exportaciones_clases.json`: trazabilidad de clases, fuente y vistas.
- En EA 15 los marcadores internos de estilo no equivalen a booleanos de mostrar. Las propiedades oficiales ShowPublicOperations/ShowPrivateOperations y equivalentes resuelven la ocultación. Prueba visual: `prueba-api.png`.
- Parámetros destructurados JavaScript con apóstrofos exponen un defecto de EA 15: la notación UML usa comillas dobles equivalentes y conserva la sintaxis literal en Notes. No se inventan tipos.
- El control visual de la ventana EA devuelve actualmente `encode capture bitmap failed: window crop is outside captured monitor`; se detuvo la interacción UI tras el reintento permitido. COM oficial y exportaciones nativas continúan disponibles.

## Siguiente paso

Terminar la reparación de presentación de clases, revisar visualmente sus miembros y continuar las fases pendientes. No presentar exports ocultos como diagramas completos. No generar ni publicar una entrega incompleta. Auditoría y temporales permanecen locales.
''',encoding='utf-8')
