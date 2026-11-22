# Informe de auditoría completa

Commit auditado: `5bf47b2e863631908e37718fb343fd776003fb5b`. Fecha: 26/11/2026 (America/La_Paz). Solo lectura de originales.

**Dictamen: el documento requiere actualización antes de imprimir o defender como versión final.** El sistema tiene evidencia estática sustancial y un catálogo verificable, pero pagos, columnas recientes, actores externos e interfaces no están representados de manera suficiente. Esto no es un porcentaje global de calidad.

## Método y alcance de evidencia

Se extrajeron DOCX, PDF, texto de DOC mediante copias de lectura, tablas y las nueve tablas de metadatos EA. Se consultó PostgreSQL en REPEATABLE READ READ ONLY y se cerró con ROLLBACK. Se inspeccionaron las 49 imágenes base en13 láminas y la composición de las 108 páginas en12 láminas; se ampliaron páginas críticas. Las miniaturas permiten revisar composición, no certificar cada carácter o cruce. No se hicieron login, GET autenticados, cobros, correos, migraciones, tests de negocio ni peticiones de pasarela. Algunos GET reales marcan uso o concilian pagos, por lo que no se invocaron.

Hecho comprobado = respaldado por archivo/catálogo o imagen. Inferencia = alcance posible deducido del código. Recomendación = propuesta posterior. No verificable = requiere fuente primaria, entorno remoto, impresión real o prueba en QA. El registro único es09 y evidencias/hallazgos.json; los demás informes lo referencian.

## Entregables y equivalencia

DOC y DOCX extraídos por Word tienen texto idéntico,43 tablas,65 imágenes y108 páginas. Los párrafos narrativos DOCX aparecen en PDF tras eliminar pies intercalados entre páginas. Esto acredita equivalencia textual de los párrafos comparados y paginación, no igualdad píxel a píxel de todos los objetos. Maestro de edición actual: DOCX. Maestro regenerable: contenido.py + esquema.sql + EA + formato; el generador completo descarta cambios manuales.

## I. Perfil (pp.7–11)

Delimita problema, objetivos, alcance de ocho CU y fases PUDS.

Propósito metodológico: Inicio: visión y alcance. Hallazgos: CU-001, PAG-001, DOC-001.

Para defender: ¿La matrícula exige pagar todo? No: primera cuota aprobada y datos completos.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## II. Fundamentación Teórica (pp.12–16)

Explica servidor, HTTP, PHP/Laravel, capas, REST, CSS/Tailwind, JavaScript/React, router/Axios, datos, token y RBAC.

Propósito metodológico: Disciplinas transversales de arquitectura y diseño. Hallazgos: ACC-001.

Para defender: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## III. Organización (pp.17–19)

Describe UNEXO, misión/visión funcionales, objetivo, ubicación, infraestructura y organigrama Administración–Coordinación–Vendedores.

Propósito metodológico: Inicio: contexto del negocio. Hallazgos: REQ-001.

Para defender: ¿Es un organigrama oficial? El texto aclara que representa el proceso comercial modelado, no la estructura oficial de la facultad.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## IV. Especificación de Requerimientos (pp.20–21)

Enumera trece reglas funcionales del negocio, desde acceso hasta recordatorios.

Propósito metodológico: Requisitos, principalmente inicio/elaboración. Hallazgos: REQ-001, REQ-002.

Para defender: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## V. Captura de Requisitos (pp.22–33)

Identifica cuatro actores humanos, ocho CU, prioridades, especificaciones y diagrama general.

Propósito metodológico: Requisitos; casos de uso dirigidos por objetivos de actores. Hallazgos: CU-001, CU-002, CU-003, CU-004, PAG-001.

Para defender: ¿Cliente tiene cuenta? No existe ese rol; el pagador usa enlaces públicos con token.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## VI. Análisis de Arquitectura (pp.34–47)

Identifica seis paquetes, traza paquetes a CU y muestra ocho comunicaciones y ocho clases P/N/D.

Propósito metodológico: Análisis y arquitectura en elaboración, refinados durante construcción. Hallazgos: CL-001, CL-002, SEC-001, FMT-001, ARQ-002.

Para defender: ¿P son clases PHP? No: páginas React funcionales y módulos JS representan presentación.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## VII. Diseño (pp.48–96)

Incluye despliegue, conceptual de31 tablas, mapeo, físico, ocho secuencias, navegación de cuatro actores y apartado pendiente de interfaces.

Propósito metodológico: Diseño en elaboración/construcción. Hallazgos: BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003.

Para defender: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

El mapeo identifica31 tablas y coincide con el volcado anterior.284 columnas existentes coinciden en nombre, tipo exacto, nulabilidad y default normalizado; faltan8 reales. Las 31 PK y46 FK del volcado coinciden con el catálogo, incluidas acciones referenciales.28 CHECK coinciden al normalizar paréntesis redundantes. Dos UNIQUE nuevas no están en el volcado. Las cinco funciones trigger tienen el mismo cuerpo. No se interpreta la omisión deliberada de una FK del conceptual como un error: se sustituye por asociación.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## VIII. Implementación (pp.97–98)

Lista herramientas y versiones, modelado y control de versiones. No contiene un listado completo del código.

Propósito metodológico: Implementación/construcción. Hallazgos: ARQ-001, DEP-001.

Para defender: ¿Dónde corre datos? Es paquete Composer dentro del proceso PHP; tres capas no exige tres servidores separados.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## IX. Resultados (pp.99–99)

Presenta resultados esperados y disponibilidad de páginas por rol; no es un acta de aceptación.

Propósito metodológico: Evaluación y transición propuestas. Hallazgos: QA-001.

Para defender: ¿Resultado esperado prueba funcionamiento? No. Debe vincularse a evidencia de ejecución.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## X. Pruebas (pp.100–103)

Contiene12 casos llamados de caja blanca y7 de caja negra, con objetivos y criterios.

Propósito metodológico: Pruebas en construcción/transición y regresión por iteración. Hallazgos: QA-001, FMT-003.

Para defender: ¿Se ejecutaron ahora? No: las suites escriben y quedan reservadas a QA aislada.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## 11. Conclusión (pp.104–104)

Cinco conclusiones vinculadas a objetivos. Reconoce que la publicación sigue pendiente.

Propósito metodológico: Evaluación Hallazgos: DOC-001.

Para defender: Distinguir construido, verificado y desplegado.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## 12. Bibliografía (pp.105–107)

24 entradas bibliográficas primarias y documentos internos. Fechas de consulta25/11/2026.

Propósito metodológico: Soporte de todos los artefactos Hallazgos: REQ-001.

Para defender: No confundir síntesis de clases con la fuente oficial; enlaces externos no fueron comprobados en esta auditoría.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## 13. Anexo (pp.108–108)

Solo URL del repositorio; no incorpora enunciado, resultados de QA ni DDL completo.

Propósito metodológico: Entrega Hallazgos: BD-002, QA-001.

Para defender: Identificar commit y versiones de fuentes editables.

El detalle por subsección se conserva en02 y evidencias/secciones_revisadas.json. Los modelos o pruebas específicos se desarrollan en03–07.

## Consistencia reciente y Git

`c0c64d1` incorporó Stripe y mejoras comerciales. `480a051` incorporó módulos de pagos, enlaces públicos, recordatorios, sincronización y temas. El merge `5bf47b2` también integra cambios de compañeros en documento, conceptual y despliegue. En HEAD conviven diagramas/textos actualizados parcialmente y un volcado que no incluye las migraciones000009/000010, aunque ambas están registradas en la BD. Evidencia: historial_git.json, diferencias_migraciones.json. No se hizo fetch/pull.

## Arquitectura y seguridad

React usa api/*.js y Axios HTTP/JSON. Laravel enruta a N*, valida FormRequest y middleware de token/permisos; N* delega persistencia a D* y modelos Eloquent. El paquete datos se carga por Composer. `errores_codigo=[]` confirma patrones que ese script reconoce; no garantiza semántica, concurrencia o reglas correctamente ubicadas. ARQ-002 demuestra una decisión comercial dentro de Comision. Los 34 permisos actuales coinciden con la matriz de migración; no existe rol Cliente. El token opaco se guarda por hash, hay vigencia de cuenta, rate limiting de login e IP en bitácora. Esto es revisión estática y de matriz, no prueba de penetración ni certificación de seguridad.

## Pagos y notificaciones reales

Crear orden selecciona módulos, calcula descuentos globales, conserva precio por ítem, divide1–12 cuotas y hace que la última absorba redondeo. La nueva entrada de dinero usa Checkout Sandbox. Setup registra método y no representa un cobro. El retorno público exige token y el webhook verifica firma y modo sandbox. La conciliación valida BOB e importe, bloquea filas, actualiza cuota y distingue repetición confirmada de reconciliación duplicada. La primera cuota con datos completos dispara inscripción y comisión por módulo. La exportación genera filas CSV y registra resultado por acción separada; no prueba conexión automática con SIS.

NNotificacion construye asuntos, texto y HTML con botón; `enviada` significa aceptación por el transporte SMTP, no recepción en bandeja. Un fallo no revierte el pago ya confirmado. NPago programa avisos previos, al vencimiento y de mora con marcas persistentes. Sin proceso externo que ejecute Scheduler no se demuestra entrega automática. WhatsApp abre enlace para compartir y no acredita envío programático por un proveedor de mensajes. No se envió nada durante la auditoría.

## Límites de cierre

No se verificó la instancia institucional, sus versiones/topología, cron, SMTP efectivo ni recepción de correos. El enunciado primario no está disponible. No se reprodujeron pruebas transaccionales, concurrencia, pasarela ni WCAG en HEAD. La navegación y ciertos diagramas densos fueron inventariados y evaluados estructuralmente, pero sus detalles visuales minúsculos requieren comprobación ampliada/impresa. El diccionario real describe estructura, no verifica todos los valores almacenados ni una demostración universal de3FN. Estas limitaciones se registran como No verificable y no como conformidad.
