# Control de actualización documental UNEXO

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

## Avance incremental de interacciones

Especificaciones EA de los ocho CU incorporadas mediante Notes de los elementos originales; asociación Visitante–CU6 agregada sin modificar el diagrama de actores. Evidencia: fase2_ea.json. Los diagramas de secuencia/comunicación se actualizan con participantes clasificados por las clases existentes, firmas validadas, condiciones del código, enlaces nativos y fragmentos opt/loop. Exportaciones y trazas incrementales: exportaciones_interacciones.json y trazas_interacciones.json. Generación en curso; falta inspección integral y no se declaran terminadas las fases 4–12.

Preparados, todavía sin ejecutar: actualizar_datos_despliegue.py (fases 5/6), actualizar_documento.py arquitectura (fase 7), qa_controlado.py (fase 8). Ninguna nueva prueba de escritura ejecutada aún.

## Continuación y compatibilidad de exportación

Confirmado un defecto del EMF nativo de EA 15: falta el viewport para coordenadas Y negativas y Word recorta el contenido. `compatibilidad_emf.mjs` conserva byte por byte todos los registros gráficos originales y agrega únicamente dos registros de viewport, ajustando el encabezado. No redibuja UML. El EMF bruto permanece local en tmp/actualizacion_documental/emf_nativos. Prueba Word/PDF `prueba-importacion.pdf`: clase Stripe completa; tipografía técnica medida 18,23 pt y marco 11,39 pt. Al insertar en Word es obligatorio fijar ancho Y alto con LockAspectRatio=0 antes de bloquear.

EA PNG se exporta a 400% mediante preferencia de imágenes del usuario. No se modificó licencia ni autenticación. La prueba visual usa `prueba-encuadre-correcto.png`. El catálogo actualizado resuelve también imports propios App y excepciones; 286 participaciones de clases en los ocho CU, con reutilización de elementos. Sincronización de clases finales en ejecución, log clases-finales.log. Valores predeterminados requieren notas nativas porque EA no los imprime en las firmas.

La generación de interacciones anterior llegó a CU6 y EA de 32 bits lanzó excepción de exportación. No se da por terminada. Se incorporó cierre de cada diagrama tras exportar y reanudación por lotes. La versión 3 del trazado corrige el ámbito de condiciones/case/return, orden real del SDK y Stripe API, validaciones ReglaNegocioException y apilamiento de notas extensas. Debe ejecutarse completa y verificarse antes de insertar figuras.

Fase 7 aplicada puntualmente al maestro (fase7_word.json); ocho especificaciones actualizadas nuevamente con el catálogo ampliado. Capítulo IV guardado por igualdad OOXML en ambas operaciones. No ejecutar documento_p2.py. Preparados insertar_figuras_actuales.py y actualizar_navegacion.py, todavía sin ejecutar. Sin nuevas pruebas QA ni commit/push en esta continuación; no publicar entrega parcial.

## Estado de la continuación 26 de noviembre 10:43

- Clases sincronizadas: 143 clasificadores propios únicos y 707 métodos propios únicos; 286 participaciones de clases y 1356 participaciones de métodos entre los ocho CU. Los tipos ausentes del código no se inventan. Completadas 286 vistas de detalle y 335 vistas de dependencias/herencia; los miembros se reutilizan, no se clonan clases para imprimir.
- Ejecutadas `presentacion-clases`, `relaciones-clases`, `defaults-clases` y `capas`. Los valores iniciales de atributos, que EA abrevia visualmente, se conservan íntegros en notas nativas junto con los defaults de parámetros. Las notas de todos los detalles fueron exportadas; falta control visual total.
- Medición automática de 619 vistas detectó 130 relaciones demasiado anchas al ampliar sus rótulos de 8 pt. Se configuró la preferencia **de usuario** FONTSIZE13=12 antes de iniciar cada proceso EA; no escribe las tablas del modelo ni los estilos del diagrama 9. Los nuevos EMF muestran únicamente LOGFONT 16 y resultan a 12,2 pt efectivos en Word. **Pendiente reexportar las 335 relaciones con esta preferencia** mediante `exportar-relaciones`, después del escritor activo.
- La reanudación de interacciones ahora utiliza revisión **5**: cachés COM, orden real de llamadas/SDK/persistencia, condiciones con ámbito, rutas HTTP, firmas completas en notas numeradas, mensajes breves enlazados por número y supresión de asociaciones ajenas a cada vista de comunicación. Pruebas visuales `revision5-com-cu1.png` y `revision5-sd-cu1.png` confirman notas completas sin superposición. Se añadió escritura oficial `Connector.Properties.Item('IsReturn').Value` para distinguir llamadas de retornos; requiere ejecutar la pasada final `actualizar_interacciones.py presentacion` sobre todas las vistas y verificar MiscData(3), sin escrituras SQL.
- Escritor activo: `continuar_modelo.ps1`, sesión de exec **54521**, espera las fases y ejecuta interacciones por lotes de 80, luego conceptual, despliegue, navegación y exportación base. Logs `interacciones-v3-lote-N.log` (nombre histórico; revisar el campo revision=5 en trazas), `continuacion-modelo.log`. No iniciar otro escritor EA mientras siga activo. La anterior sesión **26659** terminó sus clases/relaciones antes de este controlador.
- Fuente `navegacion.py` corregida: elimina formularios activos de QR/transferencia/comprobantes, incorpora pagos públicos por token y correo manual, y resuelve llamadas desde componentes importados. `navegacion.verificar()` devuelve **0 diferencias**. `actualizar_navegacion.py` sincronizará los originales por COM conservando los elementos correctos, retirando únicamente representaciones/enlaces obsoletos y sin crear actores. Luego genera vistas nativas pequeñas con todos los enlaces y campos.
- Preparado **sin ejecutar** `asociaciones_fuente.py`: asociaciones Eloquent reales contrastadas con FK, NULL y PK/UNIQUE. Ejecutar cuando termine el controlador; luego reexportar relaciones y verificar su encuadre. Incorporar `exportaciones_asociaciones.json` a Word (el insertador ya lo exige).
- Corregida puntualmente la descripción obsoleta del alcance de CU6 en la fuente y el maestro; no cambia su nombre. Corregidos espacios OOXML de SQL y captions fuera del capítulo IV. Arquitectura y herramientas actualizadas. El maestro continúa sin regeneración completa.
- `exportar.ps1` conserva el maestro DOCX: actualiza campos y genera PDF antes de convertir la copia DOC. No vuelve del formato DOC antiguo al maestro.
- Diagnóstico del renderer empaquetado: `render_docx.py` se ejecutó con el Python autorizado y falla porque no existe soffice.exe instalado. Log `renderer-diagnostico.log`. Usar Word nativo y Poppler para inspección final; ejecutar igualmente el intento requerido sobre el documento final y conservar diagnóstico. No declarar que el renderer empaquetado funcionó.
- No se ejecutaron todavía pruebas QA nuevas ni capturas. Puertos QA libres y sin procesos stripe.exe activos en la comprobación de preparación. Mantener QA existente y secuencias altas; volver a verificar aislamiento antes de escribir. No tocar la base comercial.
- Pendientes principales: terminar/limpiar modelo y exportaciones; asociaciones Eloquent y pasada final IsReturn; conceptual/despliegue/navegación/base; insertar figuras con escala por fuente (no ajustar para encajar); pruebas/capturas/capítulo X; numeración y revisión integral Word/DOC/PDF; protección de IV/actores/GUID/código; manifiesto documental sin secretos; commit y push solo al finalizar.

## Comprobación de vitalidad — 26/11/2026 12:16 (hora local)

El lote activo es final-06-relaciones, con un único escritor EA. Medidas de CPU a las 16:14:14Z y 16:14:30Z: EA 398,84375→412,5 s; Python trabajador 45,140625→45,984375 s; controlador 0,125 s (espera normal). Se completaron seis exportaciones nuevas en ese intervalo. COM respondió en 1,041 s y confirmó el EAPX original; GetCurrentDiagram devolvió null, por lo que no se inventa una pestaña actual. Sky no expone ventanas ni confirmaciones de EA. Hay progreso real, sin indicios de bloqueo COM ni bucle infinito.

Corte de inventario: 427 vistas de clases (419 detalles y 8 generales), 271 vistas de relaciones exportadas. Última al corte: clases-relacion-271, EA 1183, «Relación de clases — DSeguimiento / DAlcance / InscripcionComercial», CU6. Quedan 220 aristas únicas sin representación exportada en este lote; no equivalen a 220 diagramas porque cada vista agrupa una o dos aristas. Las listas completas por nombre/ID/stem están en tmp/actualizacion_documental/avance_exacto_diagramas.{txt,json}. Esto acredita generación/exportación, todavía no aprobación visual final del Word/PDF.

Log trabajador escrito 12:16:26, EAPX 12:16:23, controlador 12:06:28 (registra solo límites de fase). EAPX 17.076.224 bytes; respaldo cerrado anterior checkpoint-interacciones.eapx 16.437.248 bytes de las 11:40:12. No se cerró ni terminó EA, no se abrió un segundo escritor. El controlador modelo_final.py omite etapas 01–05 ya completadas; etapas 07–15 siguen pendientes. Diagnóstico reproducible local: tmp/actualizacion_documental/diagnostico_vitalidad_20261126.json. No se repite monitoreo de logs sin señal nueva.
