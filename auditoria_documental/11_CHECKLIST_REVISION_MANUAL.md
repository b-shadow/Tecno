# Checklist de revisión manual y guía de defensa

Commit auditado: `5bf47b2e863631908e37718fb343fd776003fb5b`. Fecha: 26/11/2026 (America/La_Paz). Solo lectura de originales.

No ejecutar scripts QA contra la base de demostración. Los pasos siguientes son de lectura. La impresión real, enunciado primario y entorno institucional requieren intervención del grupo para cerrar lo no verificable.

## Imprescindible, por prioridad de defensa

### BD-001 — El modelo documental omite ocho columnas actuales y dos UNIQUE de tokens.

- [ ] Abrir capítuloVII, sección7.1–7.3, página49–68. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `datos/migraciones/2026_11_25_000009_agregar_token_publico_stripe.php; datos/migraciones/2026_11_25_000010_agregar_envio_automatico_y_recordatorios.php`; método/línea: up; pg_columnas; pg_restricciones; datos/migraciones/2026_11_25_000009_agregar_token_publico_stripe.php:5; datos/migraciones/2026_11_25_000010_agregar_envio_automatico_y_recordatorios.php:5.
- [ ] Procedimiento: Ejecutar consultas columnas, tipos_exactos y restricciones del archivo 10; comparar las ocho filas.
- [ ] Buscar: 31 tablas y 284 columnas en fuentes/esquema.sql; mapeo DOCX coincide con ese volcado.
- [ ] Debería encontrarse en la realidad: public tiene 292 columnas. Faltan cuotas.token_pago, primer_envio_en, recordatorio_previo_en, recordatorio_vencimiento_en, recordatorio_mora_en; ordenes_pago.envio_automatico; transacciones_stripe.token_publico y expira_en. UNIQUE adicionales cuotas_token_pago_unique y transacciones_stripe_token_publico_unique.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: 10: columnas/tipos_exactos/restricciones.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### PAG-001 — El documento presenta QR, transferencia y comprobantes nuevos como alternativas vigentes.

- [ ] Abrir capítuloI, V, sección5; 4.4 CU6, página10, 29–30. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `negocio/app/Negocio/NPago.php; presentacion/src/componentes/pagos/MetodosPago.jsx`; método/línea: registrarMetodo; registrarComprobante; aprobar; rechazar; negocio/app/Negocio/NPago.php:74; presentacion/src/componentes/pagos/MetodosPago.jsx.
- [ ] Procedimiento: Leer los dos métodos sin invocarlos y contrastar A1 de CU6.
- [ ] Buscar: Alcance CU6 y alternativa A1 permiten registrar método manual y comprobante.
- [ ] Debería encontrarse en la realidad: NPago::registrarMetodo y registrarComprobante lanzan 422 para nuevas operaciones. MetodosPago.jsx clasifica métodos anteriores como históricos. Aprobar/rechazar permanecen para comprobantes históricos.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### CU-001 — Los nombres heredados y los nombres detallados de CU no expresan el mismo alcance.

- [ ] Abrir capítuloI, V–VII, secciónCU1 y CU7, página9, 23–24, 31, 33, 40, 46, 69, 75. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/contenido.py; datos/migraciones/2026_11_21_000003_crear_matriz_acceso.php`; método/línea: CU; DETALLE; ACTORES; generadorDocumento/contenido.py:11; datos/migraciones/2026_11_21_000003_crear_matriz_acceso.php:10.
- [ ] Procedimiento: Comparar tabla 4.2, cabecera de 4.4 y elipses en 4.5.
- [ ] Buscar: CU1 dice Propietario, Clientes; su detalle dice Gestionar Usuarios. CU7 dice Bitácora, Interacciones y Recordatorios; detalle Gestionar Seguimiento del Prospecto.
- [ ] Debería encontrarse en la realidad: Roles reales: administrador, coordinador y vendedor. Visitante es público. La bitácora de accesos está en CU1 y la historia comercial en CU7.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### CU-002 — No se representa al pagador público ni a Stripe como participantes externos en el modelo de actores/CU.

- [ ] Abrir capítuloV, VII, sección4.1, 4.4 CU6, 4.5, 7.4, página22–23, 29–30, 33, 74. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `presentacion/src/paginas/PPagoConfirmacion.jsx; presentacion/src/rutas.jsx; negocio/routes/api.php`; método/línea: consultarRetornoPublico; abrirEnlaceCuotaPublico; webhook; presentacion/src/paginas/PPagoConfirmacion.jsx:30; presentacion/src/rutas.jsx; negocio/routes/api.php:37.
- [ ] Procedimiento: Rastrear PPagoConfirmacion: rama token frente a rama sesion.token.
- [ ] Buscar: Cuatro actores humanos; CU6 solo Administrador, Coordinador y Vendedor. Secuencia de confirmación inicia con Vendedor.
- [ ] Debería encontrarse en la realidad: PPagoCuota y PPagoConfirmacion atienden al prospecto sin sesión mediante token. NPago expone retorno público y webhook firmado.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### CU-004 — Las postcondiciones prometen conversión y exportación para cualquier terminación de CU6.

- [ ] Abrir capítuloV, sección4.4 CU6, página29–30. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `negocio/app/Negocio/NStripe.php; negocio/app/Negocio/NConversion.php; negocio/app/Negocio/NExportacion.php`; método/línea: confirmarPagoDesdeSesion; faltantes; exportar; negocio/app/Negocio/NStripe.php:109; negocio/app/Negocio/NConversion.php; negocio/app/Negocio/NExportacion.php.
- [ ] Procedimiento: Seguir rama cuota 1/datos completos y después acción de exportación.
- [ ] Buscar: Postcondición afirma alumno convertido, inscripción, comisión y exportación registradas.
- [ ] Debería encontrarse en la realidad: NStripe puede responder pendiente, rechazado, cancelado, expirado o faltantes. La conversión depende de primera cuota y datos; NExportacion::exportar es una acción posterior separada.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### REQ-002 — El capítulo de requisitos contiene trece reglas comerciales y no cubre explícitamente los diez criterios transversales.

- [ ] Abrir capítuloIV, sección3.1, página20–21. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/contenido.py; P2_WEB.md`; método/línea: REQUERIMIENTOS; generadorDocumento/contenido.py:300; P2_WEB.md.
- [ ] Procedimiento: No mapear R5 docente a R5 del documento por igualdad de número.
- [ ] Buscar: R1–R13 son requisitos del dominio; R5 allí significa interés vinculado, no temas.
- [ ] Debería encontrarse en la realidad: P2_WEB.md §3 incluye temas, contraste, visitas, búsqueda global, validaciones y arquitectura. No hay tabla de correspondencia en el documento.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### CL-001 — Dos operaciones UML conservan ?string donde PHP admite string|array|null.

- [ ] Abrir capítuloVI, sección5.3.2 CU6, página45. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `negocio/app/Negocio/NPago.php; datos/src/DPago.php`; método/línea: metodoActivo; negocio/app/Negocio/NPago.php:568; datos/src/DPago.php:141.
- [ ] Procedimiento: Usar comparacion_metodos_ea.json y firmas PHP; no confundir coincidencia del nombre con firma exacta.
- [ ] Buscar: EA diagrama 138: NPago.metodoActivo y DPago.metodoActivo.
- [ ] Debería encontrarse en la realidad: Ambos métodos declaran string|array|null $tipo. DPago además tiene valor predeterminado null.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### CL-002 — El diagrama de clases CU5 solo desarrolla la administración de motivos y omite el flujo de pérdida.

- [ ] Abrir capítuloVI, sección5.3.2 CU5, página44. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `negocio/app/Negocio/NInteres.php; presentacion/src/paginas/PEmbudo.jsx`; método/línea: mover; negocio/app/Negocio/NInteres.php:38; presentacion/src/paginas/PEmbudo.jsx:34.
- [ ] Procedimiento: Comparar cls-cu5, com-cu5 y sd-cu5.
- [ ] Buscar: cls-cu5 contiene PMotivos, api/motivos, NMotivo y DMotivo.
- [ ] Debería encontrarse en la realidad: Marcar Perdido se hace en PEmbudo → api/intereses → NInteres::mover → DInteres; sí aparece en comunicación y secuencia CU5.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### SEC-001 — Los recorridos de comportamiento no desarrollan condiciones de negocio, excepciones y parámetros.

- [ ] Abrir capítuloVI, VII, sección5.3.1; 7.4, página37–40, 69–76. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/ea/ea_faltantes.py; negocio/app/Negocio`; método/línea: PREFERIDAS; PREFERIDAS_D; secuencias; generadorDocumento/ea/ea_faltantes.py:22.
- [ ] Procedimiento: Revisar individualmente las tablas de mensajes del informe 06.
- [ ] Buscar: Ocho secuencias con fragmentos opt para operaciones elegidas; no representan alt de rechazo y éxito. Mensajes N/D muestran paréntesis vacíos.
- [ ] Debería encontrarse en la realidad: PHP recibe FormRequest e identificadores, valida permisos/cartera y puede lanzar errores. El inventario EA conserva operaciones con parámetros, pero los mensajes no los transportan.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### SEC-002 — La secuencia de conversión termina la verificación de sesión sin representar la conversión que da nombre al CU.

- [ ] Abrir capítuloVII, sección7.4 CU6, página74. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `negocio/app/Negocio/NStripe.php; negocio/app/Negocio/NConversion.php`; método/línea: confirmarPagoDesdeSesion; procesarWebhook; procesar; negocio/app/Negocio/NStripe.php:109; negocio/app/Negocio/NConversion.php.
- [ ] Procedimiento: Seguir NStripe desde verificarSesion hasta confirmarPagoDesdeSesion.
- [ ] Buscar: Mensajes 25–36: retorno → verificarSesion → transaccionPorSesion → Stripe retrieve → respuesta.
- [ ] Debería encontrarse en la realidad: confirmarPagoDesdeSesion actualiza cuota/transacción, registra interacción, llama NConversion para primera cuota y envía notificaciones posteriores. No hay recorrido de webhook o pagador público.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### NOT-001 — Correos SMTP y programación automática de pagos están insuficientemente documentados.

- [ ] Abrir capítuloI, V–VII, secciónCU6/CU7; 6.1, página10, 29–31, 48, 74–75. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `negocio/app/Negocio/NNotificacion.php; negocio/app/Negocio/NPago.php; negocio/bootstrap/app.php; negocio/config/pagos_recordatorios.php`; método/línea: enviarCorreo; enviarSolicitudInicialOrden; procesarEnviosAutomaticos; negocio/app/Negocio/NNotificacion.php:33; negocio/app/Negocio/NPago.php:374; negocio/bootstrap/app.php; negocio/config/pagos_recordatorios.php.
- [ ] Procedimiento: Leer configuración y clases; no ejecutar comando porque envía correos.
- [ ] Buscar: CU7 habla de notificaciones internas y recordatorios de contacto. Despliegue no muestra SMTP ni scheduler.
- [ ] Debería encontrarse en la realidad: NNotificacion usa Mail::raw/html, registra estado y errores. NPago genera solicitud inicial y avisos -3/0/+3 días; bootstrap programa 09:00 Bolivia con withoutOverlapping.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### UI-001 — No hay capturas de interfaces insertadas.

- [ ] Abrir capítuloVII, sección7.6, página96. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/documento/P2-INF513-GRUPO05SA.pdf; generadorDocumento/contenido.py`; método/línea: sección 7.6; generadorDocumento/contenido.py.
- [ ] Procedimiento: Abrir página 96; no ejecutar capturas_p2.mjs durante esta etapa.
- [ ] Buscar: La sección completa es un marcador rojo PENDIENTE.
- [ ] Debería encontrarse en la realidad: Hay capturas previas en qa-artifacts, pero ninguna sustituye la evidencia ausente en 7.6.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### FMT-001 — Los diagramas de clases densos y el conceptual se reducen excesivamente en papel.

- [ ] Abrir capítuloVI, VII, sección5.3.2; 7.1, página40–47, 49. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `auditoria_documental/evidencias/pagina_045.png; auditoria_documental/evidencias/pagina_049.png`; método/línea: revisión visual.
- [ ] Procedimiento: Leer una firma y una multiplicidad en impresión real; aumentar zoom en pantalla no demuestra legibilidad impresa.
- [ ] Buscar: PDF 45 y 49 muestran gran densidad y texto pequeño con espacio restante en la página.
- [ ] Debería encontrarse en la realidad: Inspección visual de páginas renderizadas y PNG base; CU1 y CU6 son especialmente densos.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### DEP-001 — El despliegue previsto incorpora versiones y topología institucional sin evidencia de comprobación.

- [ ] Abrir capítuloVII, VIII, sección6.1; 8.1, página48, 97–98. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/ea/ea_faltantes.py; negocio/.env.production.example; README.md`; método/línea: despliegue; contexto PostgreSQL; generadorDocumento/ea/ea_faltantes.py:322; README.md.
- [ ] Procedimiento: No presentar 18.6 como versión observada ni PC Cliente como rol Cliente autenticado.
- [ ] Buscar: Fedora, Apache PHP8.4, PostgreSQL18.6 y db_grupo05sa se dibujan como nodos concretos.
- [ ] Debería encontrarse en la realidad: La base local consultada es crm_educativo en PostgreSQL17.4 Windows. README describe además Docker 55432. No se verificó servidor institucional.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### MC-001 — Las instrucciones académicas locales se contradicen sobre claves en el conceptual.

- [ ] Abrir capítuloVII, sección7.1, página49. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/REGLAS_DOCUMENTO_P2.md; generadorDocumento/referencias/CLASES_DOCENTE.md`; método/línea: §4/§6; Diagrama Conceptual vs Clases; generadorDocumento/REGLAS_DOCUMENTO_P2.md; generadorDocumento/referencias/CLASES_DOCENTE.md.
- [ ] Procedimiento: Consultar consigna/clase original y mostrar ambos pasajes.
- [ ] Buscar: REGLAS_DOCUMENTO_P2 exige PK y una caja por tabla. CLASES_DOCENTE incorpora consejo de alumno que prohíbe PK/FK en conceptual.
- [ ] Debería encontrarse en la realidad: La figura 7.1 contiene PK, tablas técnicas y atributos de persistencia, omitiendo FK mediante asociaciones. Es un modelo de datos derivado del físico, no un dominio puro.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### BD-002 — El diseño físico impreso no presenta restricciones, índices, funciones ni triggers de forma completa.

- [ ] Abrir capítuloVII, sección7.2–7.3, página50–68. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/documento/P2-INF513-GRUPO05SA.docx; generadorDocumento/fuentes/esquema.sql`; método/línea: 7.2; 7.3; pg_restricciones; pg_triggers.
- [ ] Procedimiento: Comparar CREATE TABLE impreso de cuotas con constraints e índices del catálogo.
- [ ] Buscar: 7.2 enumera columnas/PK/FK; 7.3 contiene CREATE TABLE con columnas. No hay diccionario semántico por columna ni explicación de los cinco triggers.
- [ ] Debería encontrarse en la realidad: PostgreSQL tiene 46 FK, 28 CHECK, siete UNIQUE, 55 índices public, cinco triggers y cinco funciones. El volcado externo contiene más información que el texto impreso.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: 10: columnas/tipos_exactos/restricciones.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### QA-001 — El plan de pruebas no documenta resultados fechados vinculados al commit y hay escenarios manuales heredados.

- [ ] Abrir capítuloX, sección10.1–10.2, página100–104. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/contenido.py; qa-artifacts/summary.json; scripts/qa_comun.py; scripts/verificar_p2.py`; método/línea: PRUEBAS_BLANCA; PRUEBAS_NEGRA; generadorDocumento/contenido.py:628; scripts/qa_comun.py; scripts/verificar_p2.py.
- [ ] Procedimiento: Distinguir script existente, ejecución reportada y aprobado en HEAD. No ejecutar suites aquí.
- [ ] Buscar: 12 casos de caja blanca y siete de caja negra describen objetivos/criterios; no acta de ejecución ni cobertura completa reciente.
- [ ] Debería encontrarse en la realidad: qa-artifacts/summary.json reporta 321/321 y engines=[chromium], como evidencia histórica sin commit explícito. Scripts usan POST y pagos manuales ahora bloqueados.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### API-001 — La consulta de agenda cambia a Atrasada las actividades vencidas globalmente y ese comportamiento no se explica.

- [ ] Abrir capítuloV, VII, secciónCU7; 7.4, página31–32, 75. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `datos/src/DSeguimiento.php; negocio/app/Negocio/NSeguimiento.php; negocio/routes/api.php`; método/línea: listarRecordatorios; recordatorios; datos/src/DSeguimiento.php:54; negocio/app/Negocio/NSeguimiento.php:49; negocio/routes/api.php.
- [ ] Procedimiento: Leer UPDATE anterior al whereHas; no invocar endpoint durante revisión de solo lectura.
- [ ] Buscar: CU7 enumera consulta, creación, realización y cancelación; su secuencia no muestra transición automática por consulta.
- [ ] Debería encontrarse en la realidad: DSeguimiento::listarRecordatorios ejecuta UPDATE de Pendiente a Atrasada para fecha menor a now()-24h antes de aplicar alcance en el SELECT. GET /recordatorios no es una lectura pura.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### CU-003 — El detalle de captación no desarrolla la reutilización de prospectos ni intereses repetidos.

- [ ] Abrir capítuloV, sección4.4 CU2/CU3, página25–26. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `negocio/app/Negocio/NProspecto.php; datos/src/DProspecto.php`; método/línea: registrarInteres; crearIntereses; vendedorExistente; crearInteres; negocio/app/Negocio/NProspecto.php:58; datos/src/DProspecto.php.
- [ ] Procedimiento: Contrastar respuesta nuevo_prospecto y llamadas firstOrCreate.
- [ ] Buscar: Flujo CU2 registra prospecto e interés y termina listo para asignación.
- [ ] Debería encontrarse en la realidad: NProspecto::registrarInteres reutiliza por documento/correo, separa intereses nuevos/repetidos, rechaza todos repetidos y devuelve 200/201 según creación. DProspecto::vendedorExistente puede conservar vendedor.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### REQ-001 — No está disponible un enunciado docente primario que permita declarar conformidad oficial.

- [ ] Abrir capítuloIV, sección3.1, página20–21. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `P2_WEB.md; generadorDocumento/referencias/CLASES_DOCENTE.md`; método/línea: §3; fuentes declaradas; P2_WEB.md; generadorDocumento/referencias/CLASES_DOCENTE.md:97.
- [ ] Procedimiento: Obtener material oficial del aula y contrastar redacción. No hace falta para continuar esta auditoría.
- [ ] Buscar: P2_WEB.md §3 transcribe diez criterios; CLASES_DOCENTE.md es una síntesis.
- [ ] Debería encontrarse en la realidad: No se localizó en el inventario una copia primaria del enunciado o transcripciones citadas. G07 es un ejemplo aprobado de otro grupo.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### FMT-002 — La mayoría de diagramas carece de un número de figura y pie uniforme.

- [ ] Abrir capítuloV–VII, secciónfiguras, página22–95. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/documento/P2-INF513-GRUPO05SA.docx`; método/línea: parrafos_docx; VML.
- [ ] Procedimiento: Contrastar los tres pies numerados con diagramas del capítulo VII.
- [ ] Buscar: Solo tres párrafos Ilustración numerados: ubicación, organigrama y paquete Seguridad.
- [ ] Debería encontrarse en la realidad: 65 objetos de imagen Word; diagramas restantes se identifican por títulos de sección o marco EA.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### ARQ-001 — Persisten descripciones Controller/Service/Repository que no corresponden a las clases N/D actuales.

- [ ] Abrir capítuloVIII, sección8.1, página97. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/REGLAS_DOCUMENTO_P2.md; generadorDocumento/README.md; generadorDocumento/contenido.py; negocio/routes/api.php`; método/línea: §6b; HERRAMIENTAS; generadorDocumento/REGLAS_DOCUMENTO_P2.md:78; generadorDocumento/README.md; generadorDocumento/contenido.py; negocio/routes/api.php.
- [ ] Procedimiento: Comparar §6b con use App\Negocio de api.php.
- [ ] Buscar: 8.1 habla de controladores y servicios; reglas §6b exige AreaController/AreaService/AreaRepository.
- [ ] Debería encontrarse en la realidad: Rutas reales usan App\Negocio\N*, persistencia Datos\D*. codigo.py ya busca N/D y devuelve cero errores sintácticos.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### ARQ-002 — La separación de responsabilidades es menos estricta que la regla local que asigna todas las decisiones a N.

- [ ] Abrir capítuloVI, VIII, sección5.3.2; 8.1, página45, 97. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `datos/src/Modelos/Comision.php; datos/src/DConversion.php`; método/línea: registrar; porcentajeVigente; registrarInscripcionesYComisiones; datos/src/Modelos/Comision.php:23; datos/src/DConversion.php:32.
- [ ] Procedimiento: Explicar cálculo y ubicación real; no afirmar que solo N toma decisiones.
- [ ] Buscar: README: D y modelos solo leen/escriben; negocio decide cálculos.
- [ ] Debería encontrarse en la realidad: Comision::registrar calcula round(precio*porcentaje/100,2) y porcentajeVigente fija fallback 2. DConversion coordina inscripciones y comisión.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### PAG-002 — La base del cálculo de comisión y el redondeo de cuotas no están explicados.

- [ ] Abrir capítuloV, VII, secciónCU6; CU8, página29–32, 74, 76. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `negocio/app/Negocio/NPago.php; datos/src/DConversion.php; datos/src/Modelos/Comision.php`; método/línea: crearOrden; registrarInscripcionesYComisiones; registrar; negocio/app/Negocio/NPago.php:115; datos/src/DConversion.php; datos/src/Modelos/Comision.php.
- [ ] Procedimiento: Ejemplo teórico sin insertar: catálogo 1000, descuento 10 %, comisión2 %: total900, comisión20 si un ítem.
- [ ] Buscar: CU6 menciona comisión y descuentos, sin fórmula ni base.
- [ ] Debería encontrarse en la realidad: Items guardan precio_acordado igual al precio de catálogo antes del descuento global. DConversion pasa ese precio a Comision::registrar. Cuotas usan floor(total/n*100)/100 y última absorbe diferencia.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### ACC-001 — Los temas se mencionan, pero no se documentan las seis variantes, horario Bolivia y verificaciones de accesibilidad.

- [ ] Abrir capítuloII, VII, VIII, sección1.10; 7.6; 8.1, página14, 96–98. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `presentacion/src/servicios/theme.js; presentacion/src/estilos/temas; DESIGN.md`; método/línea: temaPorHora; cambiar; aplicar; DESIGN.md.
- [ ] Procedimiento: Ver horario 07:00/19:00 y conservar compatibilidad interna ninos, sin reemplazos indiscriminados.
- [ ] Buscar: Tailwind y tres temas se nombran sin paleta ni capturas en 7.6.
- [ ] Debería encontrarse en la realidad: theme.js usa America/La_Paz, día07–19, localStorage crm_apariencia y compatibilidad ninos→niños; CSS separa audiencias y contraste.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### DOC-001 — La metodología se declara iterativa, pero no se aporta una secuencia verificable de iteraciones y trazabilidad por entrega.

- [ ] Abrir capítuloI, VII–X, sección6; 7.4–7.6; 10, página10–11, 69–104. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/contenido.py; auditoria_documental/evidencias/historial_git.json`; método/línea: FASES; PRUEBAS; generadorDocumento/contenido.py:86.
- [ ] Procedimiento: Explicar que disciplinas atraviesan fases y justificar con commits reales.
- [ ] Buscar: Se describen cuatro fases PUDS y objetivos por fase.
- [ ] Debería encontrarse en la realidad: No hay registro documental de iteración, requisitos comprometidos y resultados por incremento; Git aporta evolución pero no reemplaza ese artefacto.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### DOC-002 — PENDIENTES.md y otras instrucciones auxiliares arrastran pendientes ya resueltos.

- [ ] Abrir capítuloTransversal, secciónfuentes de actualización, páginaNo aplica. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/PENDIENTES.md; generadorDocumento/README.md`; método/línea: estado de fuentes auxiliares; generadorDocumento/PENDIENTES.md; generadorDocumento/README.md.
- [ ] Procedimiento: Revisar cada pendiente frente a inventarios; no asumir que todos siguen abiertos.
- [ ] Buscar: PENDIENTES menciona conclusión ausente, scripts viejos y rutas no usadas.
- [ ] Debería encontrarse en la realidad: El documento contiene conclusión en 104 y el código tiene rutas y scripts refactorizados; su lista no es evidencia vigente por sí misma.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

### FMT-003 — Hay remates aislados y una franja de navegación casi vacía.

- [ ] Abrir capítuloVII, X, sección7.3; 7.5; 10.2, página69, 83, 103. Figura: Sin número estable; localizar por sección.
- [ ] Consultar `generadorDocumento/documento/P2-INF513-GRUPO05SA.pdf`; método/línea: páginas69,83,103.
- [ ] Procedimiento: Comprobar páginas a escala100 % y mantener juntos título, objetivo y criterio.
- [ ] Buscar: Página69 empieza con cierre aislado de DDL; 83 contiene esencialmente el borde final de navegación;103 solo remata dos viñetas de cierre de sesión.
- [ ] Debería encontrarse en la realidad: Inspección visual de las 108 páginas en láminas y texto extraído.
- [ ] Error si se presenta como actual la versión contradictoria o si se declara conformidad sin evidencia. SQL: No aplica.
- [ ] Registrar resultado, fecha, responsable y evidencia; no modificar originales en esta etapa.

## Revisión recomendada y automatización respaldada

- [ ] Revisar en papel al100 % clases CU1/CU6, conceptual y franjas de navegación; las ampliaciones digitales no garantizan legibilidad impresa.
- [ ] Revisar glifos/acentos y enlaces navegables del índice en Word/PDF. La comparación textual no garantiza interacción idéntica de hipervínculos.
- [ ] Leer todas las filas de cardinalidades.json en DBeaver y la asociación correspondiente;42 relaciones directas coinciden y4 FK se abstraen en2 N:N.
- [ ] Confirmar las2 operaciones con firma distinta en EA138: NPago.metodoActivo y DPago.metodoActivo.
- [ ] Mantener como automatizado y respaldado: inventario de292 columnas public, tipos exactos,31 PK,46 FK,28 CHECK,7 UNIQUE,34 permisos comparados y5 funciones. No revisar manualmente cientos de nombres ya coincidentes salvo cambio de versión.
- [ ] En una fase posterior QA aislada, ejecutar pagos/refrescos/SMTP con datos sintéticos y registrar commit; las evidencias históricas no validan HEAD por sí mismas.

## Preguntas y respuestas basadas en este código


| Pregunta del docente | Respuesta verificable |
| --- | --- |
| ¿Por qué hay cuatro actores y tres roles? | Administrador, Coordinador y Vendedor tienen cuenta; Visitante consulta y se registra sin login. El pagador público debe explicitarse como participante, y Stripe es un sistema externo. |
| ¿Qué representa un caso de uso? | Un objetivo de un actor, como captar interés o pagar una cuota; no cada método de guardar o cada endpoint. |
| ¿Qué es P/N/D? | P presenta y llama HTTP mediante api/*.js; N decide/valida y responde; D consulta y persiste. Eloquent vive en datos; alguna regla como cálculo de comisión está allí y debe declararse. |
| ¿Cómo seguir una acción? | PAgenda → api/pagos.js → routes/api.php → FormRequest/middleware → NPago → DPago/NStripe/DStripe → PostgreSQL. Stripe es red externa, JSON es la respuesta a React. |
| ¿Cómo interpretar una secuencia? | El tiempo baja, los participantes tienen líneas de vida y mensajes con argumentos. alt separa resultados excluyentes; opt indica fragmento condicionado. Las actuales simplifican condiciones y por eso requieren corrección. |
| ¿Una FK significa uno a uno? | No. Sin UNIQUE permite muchos hijos. Nulabilidad determina si el hijo exige padre; una FK no obliga al padre a tener un hijo. |
| ¿Cuándo ocurre matrícula? | Al aprobar primera cuota y tener datos completos/vendedor; NConversion registra inscripción/comisión por solicitud. No espera el total del plan. |
| ¿Comisión sobre qué importe? | DConversion pasa precio_acordado de cada ítem; crearOrden lo guarda al precio del módulo, antes del descuento global. Comision aplica porcentaje vigente, fallback2, y redondea2 decimales. |
| ¿Qué es Round-Robin aquí? | Reutiliza vendedor por documento; si falta elige menor carga y desempata por el primer vendedor en el orden. No es un anillo circular estricto. |
| ¿Setup es pagar? | No. Registra un método Stripe; Checkout payment concilia importe BOB y cuota. No hay soporte de cobro automático off-session con tarjeta guardada demostrado por estos flujos. |
| ¿Qué hacen los triggers? | Clasifican pérdida, guardan historial web, crean cuota inicial del canal legado, copian estado de pago a cuota1 y cuentan visitas. No llaman a Stripe ni envían correos. |
| ¿Un correo enviada llegó? | El estado indica que el transporte SMTP aceptó el envío; la bandeja del destinatario no se verificó. Fallida deja registro y no revierte pago. |
| ¿Cómo se ejecutan avisos? | bootstrap programa comando a las 09:00 Bolivia; NPago evalúa -3/0/+3 días y marcas persistentes. Se requiere proceso externo de schedule:run/work que no se verificó en el servidor. |
| ¿Hay tiempo real por WebSocket? | Las vistas observadas usan polling con intervalos3–10 segundos y refresco al enfocar. No se atribuye WebSocket si no existe. |
| ¿Dónde se guarda apariencia? | localStorage crm_apariencia. theme.js aplica audiencias niños/jovenes/adultos y día07–19 en America/La_Paz, escala y alto contraste. |
| ¿Despliegue significa tres servidores? | No: son tres responsabilidades. El servidor PHP ejecuta negocio y paquete datos; PostgreSQL es otro nodo propuesto y React corre en navegador tras servir sus assets. |
| ¿Tecnoweb está operativo? | No fue verificado. La conclusión del documento lo deja pendiente; el diagrama se debe defender como destino previsto. |
| ¿Por qué conservar snapshots de catálogo? | Permiten conservar condiciones y textos de venta aunque cambie catálogo. Su intención debe documentarse; no afirmar3FN global sin dependencias funcionales. |
| ¿Qué cambió recientemente? | Tokens públicos/expiración, avisos de cuotas, Stripe como único canal nuevo, componentes de pago y temas. Esos cambios no están completamente reflejados en el volcado ni CU6. |
| ¿Qué corregir primero? | Reglas vigentes y fuente oficial; después actores/CU, esquema real, clases y secuencias, despliegue/interfaces/pruebas, y al final formato. |
