# Informe incremental: comunicaciones comerciales manuales

Fecha: 26 de noviembre de 2026. Base histórica: commit `5bf47b2e863631908e37718fb343fd776003fb5b`.

Este informe complementa la auditoría existente. No reemplaza ni modifica sus evidencias, los documentos académicos ni los diagramas originales. La carpeta de auditoría, sus archivos comprimidos, los respaldos y las evidencias QA quedan fuera del commit.

## Implementación

Se retiraron las llamadas de correo al crear órdenes y confirmar pagos, la programación de pagos, el endpoint de configuración y sus controles React. Se mantienen vencimientos, mora, saldos, enlaces públicos, historial de notificaciones y actividades comerciales independientes.

El único origen de correo comercial es `NNotificacion::enviar`, invocado por `POST /api/notificaciones`, con `auth.token` y permiso `acceso:notificaciones|agenda,modificacion`. Conserva la autorización de cartera del vendedor, destinatario, asunto, mensaje, HTML, enlace, Gmail SMTP, resultado y error SMTP. No se cambiaron las credenciales ni los archivos de entorno SMTP.

### Archivos y clases retirados

- `negocio/app/Console/Commands/RecordatoriosPagosComando.php`: clase y comando `unexo:recordatorios-pago`.
- `negocio/app/Http/Requests/Pago/ConfigurarEnvioOrdenRequest.php`: clase de validación del endpoint retirado.
- `negocio/config/pagos_recordatorios.php`: configuración exclusiva del proceso eliminado.

### Métodos retirados

| Clase | Métodos |
|---|---|
| NPago | configurarEnvioAutomatico, procesarEnviosAutomaticos, enviarSolicitudInicialOrden |
| NStripe | enviarNotificacionesPostPago |
| NNotificacion | notificarPagoConfirmado, enviarCorreoSistema |
| DPago | cuotasPendientesParaRecordatorio, marcarEnvioCuota |
| DNotificacion | existeNotificacionEnviada |

También se retiraron la función React `esCorreoValido` exclusiva del checkbox, `sumarDias`, `proximoRecordatorio`, `alternarAuto` y la función API `configurarEnvioAutomatico`, junto con sus estados, constantes y avisos exclusivos.

### Métodos y archivos modificados

- `NPago`: constructor y `crearOrden`; conserva cálculos, descuentos, cuotas y creación de `token_pago`.
- `NStripe`: constructor y `confirmarPagoDesdeSesion`; conserva conciliación, bloqueos, idempotencia, interacciones y conversión. Se retiró el indicador interno `recien_confirmado`, cuyo único consumidor era el correo.
- `NNotificacion` y `DNotificacion`: permanecen el envío explícito y la persistencia del historial; se limpiaron dependencias exclusivas de los métodos retirados.
- `DPago`, modelos `Cuota` y `OrdenPago`, `CrearOrdenRequest`: retirada de consultas y atributos exclusivos.
- `negocio/routes/api.php`: eliminado `PATCH /api/ordenes-pago/{orden}/envio-automatico`; conservados los endpoints manuales, Stripe y públicos.
- `negocio/bootstrap/app.php`: retirada de la programación y del registro explícito del directorio de comandos que quedó vacío.
- `FormularioOrdenPago.jsx`, `PlanPagos.jsx`, `PagosProspecto.jsx` y `presentacion/src/api/pagos.js`: eliminación de checkbox, interruptor, fechas e indicadores de envío, parámetros y estado de avisos.
- `iniciar-proyecto.ps1`, `detener-proyecto.ps1`: retirada del proceso de Scheduler; conservados PostgreSQL, Laravel, Vite y Stripe CLI. Se detuvo la instancia local del Scheduler identificada al iniciar la tarea.
- `scripts/verificar_stripe_api.py`, `scripts/verificar_stripe_e2e_ui.mjs`: sustituidas las comprobaciones de la funcionalidad retirada por el flujo manual; conservadas las pruebas de descuentos, seguridad, tokens, Stripe, cuotas, Setup, temas y accesibilidad. La prueba de fallo SMTP ahora invoca una solicitud manual. Se corrigió una expectativa antigua del texto de confirmación de tarjeta para coincidir con la interfaz vigente.
- `docs/STRIPE_INTEGRACION.md`: descrito el flujo manual operativo en la copia local. Este directorio ya está ignorado por Git; el archivo se mantiene local y no se añadió forzadamente al repositorio.
- Nueva migración `datos/migraciones/2026_11_26_000011_retirar_envios_automaticos_pago.php`.

Se inspeccionaron también `ResumenPagos.jsx`, `ModalCompartirPago.jsx`, `PAgenda.jsx`, `servicios/pagosCompartir.js`, `DStripe`, configuración de producción y plantillas de entorno; sus funciones vigentes se conservaron. Las referencias restantes a recordatorios de agenda y a `scheduler` de React son independientes de los pagos.

## PostgreSQL real y preservación

Respaldo local completo: `backups/manual-email-20261126/completo.dump`; estructura: `estructura.sql`; inventario comprobado con `pg_restore --list`. Estos archivos contienen datos privados y no se publican.

Antes de ejecutar se revisaron dependencias de columnas en PostgreSQL: solo existía el valor predeterminado de `ordenes_pago.envio_automatico`; ninguna FK, UNIQUE, CHECK, índice o trigger dependía de las cinco columnas. Se ejecutó únicamente la nueva migración en la base de trabajo. El rollback reconstruye las columnas, pero sus valores anteriores requieren el respaldo.

Columnas eliminadas:

- `ordenes_pago.envio_automatico`.
- `cuotas.primer_envio_en`.
- `cuotas.recordatorio_previo_en`.
- `cuotas.recordatorio_vencimiento_en`.
- `cuotas.recordatorio_mora_en`.

| Elemento | Auditoría 5bf47b2: public | Actual: public | Actual: public + laravel |
|---|---:|---:|---:|
| Tablas | 31 | 31 | 32 |
| Columnas | 292 | 287 | 290 |
| PK | 31 | 31 | 32 |
| FK | 46 | 46 | 46 |
| UNIQUE | 7 | 7 | 7 |
| CHECK | 28 | 28 | 28 |
| Índices | 55 | 55 | 56 |
| Triggers | 5 | 5 | 5 |

El esquema auxiliar `laravel` conserva `migrations`, con tres columnas, una PK y un índice. El total anterior incluyendo ese esquema era 32 tablas y 295 columnas. No se eliminó ninguna restricción ni relación. Las 113 restricciones y los cinco triggers coinciden con las definiciones de la auditoría histórica. Se conservaron también las cinco funciones y catorce secuencias.

Las huellas de todas las filas de las 31 tablas públicas, excluyendo exclusivamente las cinco columnas retiradas, coincidieron antes e inmediatamente después de la migración. No se borraron órdenes, cuotas, prospectos, matrículas, comisiones, transacciones ni correos históricos.

Las pruebas usan una base QA separada, pero comparten la cuenta Stripe Sandbox con la escucha existente del entorno de trabajo. Se detectó que esta escucha añade eventos técnicos y que el fallback histórico por número de orden/cuota puede conciliar transacciones de otra base con números coincidentes. Dos efectos de QA en metadatos de las transacciones 4 y 9 se restauraron selectivamente desde el respaldo, comparando primero el contenido completo de la fila para evitar sobrescribir cambios concurrentes. La comparación posterior confirmó su recuperación. No se cambiaron importes, pagos ni saldos. En la transacción 138 solo se observó una actualización de URL de recibo y fecha de actualización por la conciliación existente; se conservó esa información. También hubo actividad técnica normal en tokens, bitácora y contadores durante el trabajo. Para futuras pruebas conviene usar una cuenta Sandbox separada o identificadores QA sin coincidencias; no se amplió esta modificación para rediseñar los webhooks.

Se conservaron `cuotas.token_pago`, su UNIQUE, `transacciones_stripe.token_publico`, su UNIQUE y `expira_en`.

## Verificación

Se creó una base QA nueva mediante `CREATE DATABASE`, migraciones normales y seed, sin `migrate:fresh`, `migrate:refresh`, borrados de bases ni reinicialización de la base de trabajo. Esto comprueba además la instalación desde cero con el historial intacto.

La regresión P2 se ejecutó en `http://127.0.0.1:18001`, en lugar del puerto de trabajo 8001, para que los cambios de permisos, reparto e importación de la prueba afectaran exclusivamente a QA. Las comprobaciones del navegador usaron React en el puerto 18003, el mismo backend QA, SMTP local en 1026 y Stripe Sandbox con webhooks reenviados a QA. No se realizaron pagos reales ni envíos de prueba a prospectos reales.

Resultados:

| Verificación | Resultado |
|---|---|
| `python generadorDocumento/codigo.py` | `errores entre capas: []`, repetido tras integrar el cambio remoto. |
| `python scripts/verificar_p2.py http://127.0.0.1:18001` | TODO OK; puerto QA en sustitución del 8001 de trabajo. |
| API Stripe Sandbox | TODO OK: BOB, descuentos, IDOR, sesiones concurrentes/idempotencia, validaciones, rechazo de métodos manuales nuevos, tokens, regeneración tras expiración, firma e idempotencia de webhook. |
| Correo manual | Destinatario visible y editable; asunto y mensaje modificados; envío explícito, historial enviado y mensaje HTML capturado en SMTP local con enlace público de cuota. WhatsApp y portapapeles verificados. |
| Error SMTP manual | Conexión controlada al puerto cerrado 19999: respuesta 502 y estado fallida en historial. |
| Generación de órdenes | Pago único y cuotas con importes correctos; ninguna notificación al crear la orden. |
| Pagos Checkout | Visa, Mastercard, 3DS, rechazo y cancelación; confirmación pública, cuota ya pagada sin nuevo cobro, liquidación completa. |
| Webhook sin retorno | Pago real de Sandbox confirmado en PostgreSQL aunque el navegador abortó el retorno a UNEXO. |
| Setup | Tarjeta registrada mediante solicitud manual, confirmación pública, persistencia, desactivación y filtro histórico. |
| Conversión comercial | Cinco órdenes pagadas de QA verificadas: estado Convertido, una matrícula y una comisión por ítem, fórmula de comisión vigente, suma de cuotas igual al total y saldo cero cuando liquidadas. |
| Ausencia de correo por pago | Ninguna notificación de confirmación de PaymentIntent; correo manual preservado. |
| UI de pagos | 320/390/768/1280 px, seis temas, alto contraste y letra grande sin desbordamiento en los recorridos ejecutados. |
| Regresión UI integrada | `FASE A UI: TODO OK`: temas, accesibilidad, horas, vencimientos, agenda móvil, agregar interés y eliminación de foto con cancelación/confirmación y persistencia. Sin errores JS ni HTTP 500 en ese recorrido. Se creó el usuario FotoTest exclusivamente en QA porque no pertenece al seed base. |
| PHP / scripts | Sintaxis PHP de todos los archivos afectados correcta; sintaxis Python/Node y análisis de ambos scripts PowerShell correctos. |
| Compilaciones | `npm run build` normal y con `VITE_BASE=/inf513/grupo05sa/proyecto2/`, ambas correctas, repetidas sobre la versión integrada. |
| Referencias exclusivas | Cero coincidencias en archivos propios versionados fuera de migraciones; Scheduler sin tareas programadas. |

La prueba de navegador se ejecutó por recorridos: los flujos de orden, correo, descuentos y pagos pasaron; se corrigieron dos expectativas antiguas en Setup (texto y selector de Visa repetida) y se continuó sobre la misma tarjeta hasta completar métodos y webhook. No se suprimieron casos para conseguir un resultado correcto. La captura SMTP local acredita la entrega al transporte controlado, no recepción en Gmail ni en la bandeja de un cliente real.

## Publicación

- Commit de implementación: `0d5399ec4496c25689870a122689dab394b8cc9e`, mensaje exacto solicitado: `Simplify payment communications to manual email and remove scheduled payment reminders`.
- Respaldo local del commit: rama `backup/manual-email-20261126`.
- Se integró el commit remoto `242ebfd` (tema día/noche según la hora del dispositivo) sin conflictos ni pérdida de cambios del compañero.
- Commit integrado publicado: `2b6ab3158f946b507765e236706708ae3e71ddc9`.
- `git push origin main`: correcto; `HEAD` y `origin/main` iguales y diferencia `0 0`.
- La implementación incluye 22 archivos: 18 modificados, tres eliminados y una migración nueva. La integración conserva además los tres archivos del cambio remoto de temas.
- Se revisaron diff, sintaxis, exclusiones y patrones de credenciales. El commit no contiene auditoría, zip, respaldo, caché, temporales, datos de QA ni secretos.
- El único estado Git pendiente corresponde a `auditoria_documental/` y `auditoria_documental.zip`, ya locales y excluidos expresamente del commit.
- No se realizó despliegue institucional, force push ni reescritura del historial.

## Impacto documental posterior

- CU6: generación de orden, solicitud manual, pagador público, Checkout/Setup, webhook, conversión, matrícula y comisión. Retirar el correo como consecuencia de generar o pagar una orden.
- CU7: diferenciar el correo manual y su historial de las actividades de seguimiento; conservar estas últimas.
- CU8: conservar los cálculos vigentes de ventas y comisiones y su trazabilidad desde la conversión.
- Revisar EA-15, EA-23, EA-138, EA-141 y EA-142 para CU6; EA-7, EA-16, EA-24, EA-105 y EA-130 para CU7; modelo de datos EA-133; navegación de vendedor EA-136 y despliegue EA-152. Revisar también las dependencias de clases hacia `NNotificacion`.
- Documento académico: especificaciones CU6/CU7, clases, comunicaciones y secuencias, modelo físico/diccionario, interfaz de pagos y requisitos de ejecución. Actualizar las capturas de pagos sin controles de correo programado.

Hallazgos anteriores afectados, sin alterar su evidencia histórica:

| Hallazgo | Cambio de alcance |
|---|---|
| BD-001 | De ocho columnas omitidas quedan tres necesarias por documentar: token_pago, token_publico y expira_en, más sus dos UNIQUE. |
| NOT-001 | La parte de correo programado queda superada por la eliminación; documentar ahora únicamente el envío manual SMTP y distinguirlo de la agenda comercial. |
| SEC-002 | Representar conciliación, webhook, matrícula y comisión; excluir las notificaciones posteriores al pago ya retiradas. |
| CU-002 / CU-003 / CU-004 | Mantener la revisión del pagador público, Stripe y alcance de permisos; la eliminación de correos no resuelve esas discrepancias documentales. |
| UI-001 | Requiere capturas actuales, sin checkbox, interruptor ni próximo envío. |
| PAG-002 | Fórmula de comisión y redondeo se conservan; siguen necesitando explicación documental. |
| API-001 | Recordatorios independientes de agenda intactos; su hallazgo histórico no se cierra por este cambio. |

Las migraciones históricas conservan las referencias mínimas necesarias para instalaciones existentes y nuevas. No se modificaron DOC/DOCX/PDF, EA, UML ni se realizó despliegue institucional.
