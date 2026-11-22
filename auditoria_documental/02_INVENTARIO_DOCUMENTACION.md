# Inventario de documentación y guía por capítulo

Commit auditado: `5bf47b2e863631908e37718fb343fd776003fb5b`. Fecha: 26/11/2026 (America/La_Paz). Solo lectura de originales.

## Fuentes y riesgo de sobrescritura

Editar posteriormente textos en contenido.py y el DOCX manual solo con una estrategia de sincronización. documento_p2.py reconstruye el DOCX completo; exportar.ps1 abre con Word, reemplaza imágenes por EMF, actualiza campos, produce DOC/PDF/DOCX temporales y reemplaza los tres entregables. insertar_diagramas.py y actualizar_figura_docx.py son actualizaciones parciales; actualizar_secuencias.py refresca ocho figuras. ea_p2.py y ea_faltantes.py escriben el EAPX y exportan imágenes; no se ejecutaron. codigo.py, esquema.py y nuestras extracciones se leyeron/verificaron sin regenerar originales. README y REGLAS son fuentes auxiliares con contradicciones ARQ-001/MC-001.

Portada p1; índice pp2–6; diez capítulos pp7–103; conclusión104; bibliografía105–107; anexo108. Hay43 tablas Word: portada1, actores1, lista CU1, prioridades1, especificaciones CU8 y mapeos31. Solo tres pies numerados de ilustración. No se encontraron anexos oficiales del docente ni un diccionario semántico completo.

| Capítulo | Páginas | Qué representa | Disciplina/PUDS | Qué explicar |
| --- | --- | --- | --- | --- |
| I Perfil | 7–11 | Delimita problema, objetivos, alcance de ocho CU y fases PUDS. | Inicio: visión y alcance. | ¿La matrícula exige pagar todo? No: primera cuota aprobada y datos completos. |
| II Fundamentación Teórica | 12–16 | Explica servidor, HTTP, PHP/Laravel, capas, REST, CSS/Tailwind, JavaScript/React, router/Axios, datos, token y RBAC. | Disciplinas transversales de arquitectura y diseño. | ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth. |
| III Organización | 17–19 | Describe UNEXO, misión/visión funcionales, objetivo, ubicación, infraestructura y organigrama Administración–Coordinación–Vendedores. | Inicio: contexto del negocio. | ¿Es un organigrama oficial? El texto aclara que representa el proceso comercial modelado, no la estructura oficial de la facultad. |
| IV Especificación de Requerimientos | 20–21 | Enumera trece reglas funcionales del negocio, desde acceso hasta recordatorios. | Requisitos, principalmente inicio/elaboración. | ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración. |
| V Captura de Requisitos | 22–33 | Identifica cuatro actores humanos, ocho CU, prioridades, especificaciones y diagrama general. | Requisitos; casos de uso dirigidos por objetivos de actores. | ¿Cliente tiene cuenta? No existe ese rol; el pagador usa enlaces públicos con token. |
| VI Análisis de Arquitectura | 34–47 | Identifica seis paquetes, traza paquetes a CU y muestra ocho comunicaciones y ocho clases P/N/D. | Análisis y arquitectura en elaboración, refinados durante construcción. | ¿P son clases PHP? No: páginas React funcionales y módulos JS representan presentación. |
| VII Diseño | 48–96 | Incluye despliegue, conceptual de31 tablas, mapeo, físico, ocho secuencias, navegación de cuatro actores y apartado pendiente de interfaces. | Diseño en elaboración/construcción. | ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento. |
| VIII Implementación | 97–98 | Lista herramientas y versiones, modelado y control de versiones. No contiene un listado completo del código. | Implementación/construcción. | ¿Dónde corre datos? Es paquete Composer dentro del proceso PHP; tres capas no exige tres servidores separados. |
| IX Resultados | 99–99 | Presenta resultados esperados y disponibilidad de páginas por rol; no es un acta de aceptación. | Evaluación y transición propuestas. | ¿Resultado esperado prueba funcionamiento? No. Debe vincularse a evidencia de ejecución. |
| X Pruebas | 100–103 | Contiene12 casos llamados de caja blanca y7 de caja negra, con objetivos y criterios. | Pruebas en construcción/transición y regresión por iteración. | ¿Se ejecutaron ahora? No: las suites escriben y quedan reservadas a QA aislada. |
| 11 Conclusión | 104–104 | Cinco conclusiones vinculadas a objetivos. Reconoce que la publicación sigue pendiente. | Evaluación | Distinguir construido, verificado y desplegado. |
| 12 Bibliografía | 105–107 | 24 entradas bibliográficas primarias y documentos internos. Fechas de consulta25/11/2026. | Soporte de todos los artefactos | No confundir síntesis de clases con la fuente oficial; enlaces externos no fueron comprobados en esta auditoría. |
| 13 Anexo | 108–108 | Solo URL del repositorio; no incorpora enunciado, resultados de QA ni DDL completo. | Entrega | Identificar commit y versiones de fuentes editables. |

## Subsecciones reales, propósito y revisión

Los intervalos son inclusivos y pueden compartir página; se asigna el final antes de la siguiente sección del mismo nivel. En secciones sin texto propio, sus hijos desarrollan el contenido. La estructura fuente exacta y párrafos están en secciones_revisadas.json.

### Capítulo I: Perfil

Páginas 7–11. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para inicio: visión y alcance. Se relaciona con Perfil y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, PAG-001, DOC-001. Revisión personal: ¿La matrícula exige pagar todo? No: primera cuota aprobada y datos completos.

### 1 Introducción

Páginas 7–7. El presente proyecto desarrolla el Sistema de Control de Prospectos (CRM Educativo) de UNEXO, una aplicación web para la venta de programas de formación de una institución educativa: programas de cinco a seis módulos y módulos independientes. El sistema capta prospectos desde un catálogo público, los asigna a los vendedores, los lleva por un embudo de ventas en un tablero Kanban, registra el seguimiento comercial y procesa el pago hasta convertir al prospecto en alumno matriculado. El sistema se construye con una arquitectura de 3 capas, como exige el enunciado del Proyecto 2 de la materia Tecnología Web (INF513): la capa de presentación es una aplicación de una sola página en React que consume, mediante Axios, una API RESTful desarrollada en Laravel (capa de lógica de negocio), y esta accede a una base de datos PostgreSQL (capa de datos) compartida con el Proyecto 1, el sistema vía correo electrónico.

Sirve para inicio: visión y alcance. Se relaciona con Perfil y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, PAG-001, DOC-001. Revisión personal: ¿La matrícula exige pagar todo? No: primera cuota aprobada y datos completos.

### 2 Antecedentes y Justificación

Páginas 7–7. El Grupo 05 SA abordó primero el dominio de captación y seguimiento de prospectos en el Proyecto 1 de INF513. Aquel sistema utilizó comandos enviados por correo electrónico para registrar interesados, asignarlos a vendedores, seguir sus oportunidades en un embudo y tramitar la conversión a matrícula. El Proyecto 2 conserva los ocho casos de uso del proceso comercial y la base de datos compartida, pero ofrece una interfaz web y una API RESTful (Grupo 05 SA, 2026). El alcance web responde a cuatro formas de trabajo documentadas para este proyecto: el visitante consulta programas y módulos y comunica su interés; el vendedor atiende su cartera desde el celular; coordinación distribuye prospectos y revisa pagos; y administración gestiona cuentas, permisos y auditoría. Cada interés se trata como una oportunidad con estado, historial, contactos y condiciones de pago, de modo que las acciones de estos actores se consulten desde un mismo sistema (Grupo 05 SA, «Product», 2026).

Sirve para inicio: visión y alcance. Se relaciona con Perfil y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, PAG-001, DOC-001. Revisión personal: ¿La matrícula exige pagar todo? No: primera cuota aprobada y datos completos.

### 3 Planteamiento de Problema

Páginas 8–8. El escenario comercial descrito en el Proyecto 1 requería registrar cada contacto y conocer la etapa de cada interesado. Cuando esa información permanece repartida entre planillas, mensajes y la memoria de cada vendedor, resulta difícil identificar prospectos sin atención, reconstruir una conversación o conocer por qué se perdió una oportunidad. El canal de correo del P1 resolvió el registro transaccional, pero el Proyecto 2 necesita presentar el mismo proceso mediante vistas web para visitantes, vendedores, coordinación y administración (Grupo 05 SA, 2026). La causa funcional es la falta de una vista compartida del prospecto que reúna interés, asignación, etapa del embudo, interacciones, recordatorios y pagos con permisos diferenciados. Si el canal web no integra estos datos, el seguimiento puede quedar fragmentado, la distribución del trabajo no resulta visible y coordinación carece de información consistente para revisar conversiones y motivos de pérdida.

Sirve para inicio: visión y alcance. Se relaciona con Perfil y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, PAG-001, DOC-001. Revisión personal: ¿La matrícula exige pagar todo? No: primera cuota aprobada y datos completos.

### 4 Objetivo

Páginas 9–9. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para inicio: visión y alcance. Se relaciona con Perfil y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, PAG-001, DOC-001. Revisión personal: ¿La matrícula exige pagar todo? No: primera cuota aprobada y datos completos.

### 4.1 Objetivo General

Páginas 9–9. Desarrollar un sistema web de control de prospectos para UNEXO, con arquitectura de 3 capas (React, Laravel API RESTful y PostgreSQL), que gestione la captación, asignación, seguimiento y conversión a matrícula de los prospectos de sus programas de formación.

Sirve para inicio: visión y alcance. Se relaciona con Perfil y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, PAG-001, DOC-001. Revisión personal: ¿La matrícula exige pagar todo? No: primera cuota aprobada y datos completos.

### 4.2 Objetivos Específicos

Páginas 9–9. Identificar los requerimientos, los actores y los casos de uso del proceso comercial de UNEXO. Analizar la arquitectura del sistema mediante paquetes, diagramas de colaboración y análisis de clases por caso de uso.

Sirve para inicio: visión y alcance. Se relaciona con Perfil y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, PAG-001, DOC-001. Revisión personal: ¿La matrícula exige pagar todo? No: primera cuota aprobada y datos completos.

### 5 Alcance

Páginas 9–9. CU1. Gestión de Usuarios (Propietario, Clientes): Registro, modificación y cambio de estado de usuarios con rol, vigencia (fecha de inicio y de fin) y foto con nombre legible; inicio y cierre de sesión con token; perfil y cambio de contraseña; matriz de acceso editable (lectura, modificación y eliminación por rol y recurso) y bitácora de accesos. CU2. Gestión de Captar, Consumir Oferta: Catálogo público por programas y módulos, con búsqueda y registro de interés del visitante; sincronización de la oferta académica desde el cliente API del catálogo, simulado hasta que el Grupo 06 publique su servicio.

Sirve para inicio: visión y alcance. Se relaciona con Perfil y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, PAG-001, DOC-001. Revisión personal: ¿La matrícula exige pagar todo? No: primera cuota aprobada y datos completos.

### 6 Metodología

Páginas 10–11. Para el desarrollo del sistema se utiliza el Proceso Unificado de Desarrollo de Software (PUDS), un proceso iterativo e incremental, dirigido por casos de uso y centrado en la arquitectura, con el Lenguaje Unificado de Modelado (UML) para elaborar los modelos. El proceso se organiza en cuatro fases: Inicio (Inception). Se identifican los requerimientos del grupo y del enunciado, los actores y los ocho casos de uso aprobados por el docente. Entregables: requerimientos funcionales, actores y casos de uso con su priorización y detalle.

Sirve para inicio: visión y alcance. Se relaciona con Perfil y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, PAG-001, DOC-001. Revisión personal: ¿La matrícula exige pagar todo? No: primera cuota aprobada y datos completos.

### Capítulo II: Fundamentación Teórica

Páginas 12–16. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1. Programación del lado del servidor

Páginas 12–16. La programación del lado del servidor procesa solicitudes recibidas por HTTP, aplica reglas de negocio, consulta datos y devuelve una respuesta al cliente. En una aplicación con interfaz separada, esa respuesta puede ser JSON en lugar de una página HTML. En este proyecto, React presenta la información y Laravel atiende las solicitudes de la API, valida las entradas y coordina el acceso a PostgreSQL (MDN Web Docs, «Introduction to the server side», s. f.; Laravel, «Routing», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.1. Fundamentos de la programación del lado del servidor

Páginas 12–12. El navegador envía una petición a una ruta del servidor; este identifica la operación, comprueba los datos y permisos, ejecuta la lógica correspondiente y devuelve un estado HTTP y una representación del resultado. La validación y la autorización deben repetirse en el servidor aunque la interfaz también limite las acciones. En el CRM, las clases de negocio N* atienden las rutas y delegan la persistencia a las clases D* (MDN Web Docs, «Introduction to the server side», s. f.; Laravel, «Validation», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.2. Servicios Web

Páginas 12–12. Un servicio web expone operaciones para que otro programa intercambie información con él mediante una red. En este sistema, la interfaz React consume un servicio HTTP que recibe parámetros y devuelve respuestas JSON: por ejemplo, consulta el catálogo o registra un interés. El contrato de rutas y respuestas permite separar la interfaz de la lógica que procesa la solicitud (MDN Web Docs, «Overview of HTTP», s. f.; Laravel, «Routing», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.3. Protocolo HTTP

Páginas 12–12. HTTP organiza la comunicación en solicitudes y respuestas. Sus métodos expresan la intención de la operación: GET consulta, POST envía datos para crear o procesar, y PUT, PATCH y DELETE se usan para modificar o eliminar recursos según el contrato de la API. Las respuestas incluyen un código de estado y pueden transportar JSON. La interfaz del CRM utiliza estos métodos al llamar a las rutas de Laravel (MDN Web Docs, «Overview of HTTP», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.4. Lenguaje HTML

Páginas 13–13. HTML es el lenguaje de marcado que estructura el contenido de una página mediante elementos como títulos, enlaces y formularios. Proporciona significado y organización al documento, mientras CSS define su aspecto y JavaScript aporta comportamiento. El proyecto entrega un documento HTML inicial y React compone la interfaz que ve el usuario (MDN Web Docs, «HTML», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.5. Lenguaje PHP

Páginas 13–13. PHP es un lenguaje de programación que puede ejecutarse en el servidor para recibir datos de formularios, consultar servicios y producir respuestas dinámicas. En este proyecto se usa PHP 8.3 o superior para las clases de negocio, las reglas de validación y el acceso a datos que utiliza Laravel; el navegador no ejecuta ese código PHP (PHP Documentation Group, «Introduction», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.6. Framework Laravel

Páginas 13–13. Laravel organiza en PHP el ciclo de una solicitud HTTP y ofrece rutas, middleware, validación y herramientas de acceso a datos. El proyecto utiliza Laravel 13 como base de la API: las rutas públicas y privadas están en routes/api.php; middleware propio autentica el token y exige el permiso del recurso antes de ejecutar la operación. Las clases de negocio se mantienen separadas de las clases de datos (Laravel, «Routing», s. f.; Laravel, «Middleware», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.7. Arquitectura de 3 capas (Presentación, Lógica de Negocio y Datos)

Páginas 13–13. Una arquitectura de tres capas distribuye las responsabilidades entre presentación, reglas de negocio y persistencia. La primera recoge y muestra información; la segunda decide qué operaciones son válidas; la tercera consulta y modifica los datos. En el proyecto, presentacion/ contiene React y Axios, negocio/ contiene la API Laravel y sus reglas, y datos/ contiene los accesos a PostgreSQL. La interfaz no consulta la base directamente (Microsoft, «Using a Three-Tier Architecture Model», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.8. API RESTful

Páginas 14–14. REST es un estilo arquitectónico para sistemas distribuidos que separa cliente y servidor y define una interfaz uniforme sobre recursos. Una API HTTP inspirada en REST identifica recursos mediante rutas, emplea métodos HTTP y devuelve representaciones y estados de respuesta. Las rutas del CRM exponen usuarios, prospectos, intereses y pagos mediante ese esquema; llamar a la API «RESTful» describe su diseño de recursos y operaciones, sin afirmar que implemente todas las restricciones formales de REST (Fielding, 2000; Laravel, «Routing», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.9. Hojas de estilo CSS

Páginas 14–14. CSS define la presentación de los elementos HTML: colores, tipografía, espacios, disposición y adaptación a distintos tamaños de pantalla. Su uso permite mantener reglas visuales comunes a las páginas. El CRM combina una hoja de estilos propia con utilidades de Tailwind para la identidad visual y la disposición responsiva (MDN Web Docs, «CSS», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.10. Framework Tailwind CSS

Páginas 14–14. Tailwind CSS proporciona clases de utilidad para expresar estilos directamente en los componentes, como espaciado, color, tamaño y estados. También admite variantes para puntos de quiebre y modo oscuro. En este proyecto, Tailwind 4 complementa las reglas CSS propias de la interfaz React; las clases de utilidad se usan para construir vistas adaptables sin que Tailwind determine la lógica de negocio (Tailwind Labs, «Styling with utility classes», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.11. JavaScript

Páginas 14–14. JavaScript es el lenguaje de programación de la interfaz web: responde a eventos, modifica el estado visible y solicita datos al servidor. En el CRM se emplea en componentes JSX, funciones de acceso a la API y controles de navegación. La ejecución en el navegador mejora la interacción, pero las decisiones de autorización siguen verificándose en Laravel (MDN Web Docs, «JavaScript», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.12. Biblioteca React

Páginas 15–15. React construye interfaces mediante componentes que combinan estructura, lógica de presentación y estado. Un cambio de estado vuelve a representar la parte pertinente de la pantalla. El CRM usa React 18 para el catálogo público y los paneles de administrador, coordinador y vendedor, mientras el servidor entrega datos mediante la API (React, «Quick Start», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.13. Enrutamiento en el cliente (React Router)

Páginas 15–15. El enrutamiento del cliente relaciona la dirección del navegador con la vista que debe mostrarse sin solicitar un documento HTML completo en cada navegación. React Router permite configurar el árbol de rutas con createBrowserRouter. En el proyecto, rutas.jsx declara las páginas; AppShell comprueba el menú recibido desde la API para redirigir cuando el usuario no tiene acceso (React Router, «createBrowserRouter», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.14. Cliente HTTP Axios

Páginas 15–15. Axios es un cliente HTTP para JavaScript que permite enviar solicitudes y manejar respuestas de forma asíncrona. El proyecto centraliza su configuración en presentacion/src/api/cliente.js: define la URL base, solicita JSON, agrega el token Bearer cuando existe y procesa respuestas de sesión vencida o acceso denegado. Las páginas llaman a funciones de api/ y no a la base de datos (Axios, «First steps», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.15. Base de datos relacional

Páginas 15–15. Una base de datos relacional organiza la información en tablas con filas y columnas; las claves primarias identifican registros y las claves foráneas mantienen relaciones válidas. SQL permite consultar y modificar estos datos. En el CRM se relacionan prospectos, intereses, órdenes, cuotas e inscripciones, y las restricciones de la base complementan las validaciones de negocio (PostgreSQL Global Development Group, «Foreign Keys», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.16. PostgreSQL

Páginas 16–16. PostgreSQL es el gestor de base de datos utilizado para la persistencia del sistema. Admite consultas SQL, relaciones entre tablas, claves foráneas y transacciones. En este proyecto conserva los usuarios, la matriz de acceso, la actividad comercial y los pagos; las migraciones de datos/ definen las tablas y restricciones que utiliza la API Laravel (PostgreSQL Global Development Group, «Tutorial», s. f.).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.17. Autenticación con token de acceso (Bearer)

Páginas 16–16. Un token Bearer acredita una solicitud cuando se envía en el encabezado Authorization con el esquema Bearer; quien posea el token puede presentarlo, por lo que debe protegerse durante su transporte y almacenamiento. En el CRM, Laravel emite un token opaco al iniciar sesión, conserva su hash en la base y el middleware lo verifica en las rutas privadas.  (Jones y Hardt, 2012).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### 1.18. Control de acceso basado en roles (RBAC)

Páginas 16–16. RBAC vincula permisos con roles y asigna esos roles a usuarios, de modo que el acceso a un recurso depende del rol activo. El CRM utiliza Administrador, Coordinador y Vendedor; las tablas recursos y permisos definen lectura, modificación o eliminación. La API consulta esa matriz antes de ejecutar cada acción protegida, y el menú se construye con los recursos permitidos (Ferraiolo, Cugini y Kuhn, 1995).

Sirve para disciplinas transversales de arquitectura y diseño. Se relaciona con Fundamentación Teórica y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ACC-001. Revisión personal: ¿Bearer significa JWT? No: se genera token opaco, se guarda hash y se valida en NAuth.

### Capítulo III: Organización

Páginas 17–19. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para inicio: contexto del negocio. Se relaciona con Organización y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001. Revisión personal: ¿Es un organigrama oficial? El texto aclara que representa el proceso comercial modelado, no la estructura oficial de la facultad.

### 2. Empresa

Páginas 17–19. UNEXO ofrece un campus virtual de cursos y módulos en el entorno académico de la FICCT-UAGRM (UNEXO, «Campus virtual», s. f.). Este capítulo describe el servicio comercial que modela el CRM: sus funciones y roles de sistema. La misión, visión, objetivo y estructura siguientes corresponden a ese alcance funcional; no se presentan como declaraciones institucionales ni como organigrama oficial de la facultad.

Sirve para inicio: contexto del negocio. Se relaciona con Organización y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001. Revisión personal: ¿Es un organigrama oficial? El texto aclara que representa el proceso comercial modelado, no la estructura oficial de la facultad.

### 2.1. Misión

Páginas 17–17. Acompañar a las personas interesadas en programas y módulos desde la consulta inicial hasta la matrícula, registrando cada contacto, ofreciendo información clara sobre la oferta y conservando la trazabilidad de la atención comercial.

Sirve para inicio: contexto del negocio. Se relaciona con Organización y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001. Revisión personal: ¿Es un organigrama oficial? El texto aclara que representa el proceso comercial modelado, no la estructura oficial de la facultad.

### 2.2. Visión

Páginas 17–17. Mantener un proceso comercial en el que cada interesado tenga seguimiento oportuno y en el que coordinación pueda conocer el avance, las conversiones y los motivos de pérdida a partir de información compartida y verificable.

Sirve para inicio: contexto del negocio. Se relaciona con Organización y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001. Revisión personal: ¿Es un organigrama oficial? El texto aclara que representa el proceso comercial modelado, no la estructura oficial de la facultad.

### 2.3. Objetivo

Páginas 17–17. Organizar la captación, asignación, seguimiento y conversión a matrícula de los interesados en la oferta de formación, con responsabilidades diferenciadas para administración, coordinación y vendedores.

Sirve para inicio: contexto del negocio. Se relaciona con Organización y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001. Revisión personal: ¿Es un organigrama oficial? El texto aclara que representa el proceso comercial modelado, no la estructura oficial de la facultad.

### 2.4. Ubicación

Páginas 17–18. La unidad funciona en el edificio de la FICCT, módulo 236 de la Ciudad Universitaria de la UAGRM, sobre la avenida Dr. Enrique Aponte Canseco, entre la avenida Busch y la avenida 26 de Febrero (segundo anillo), en la ciudad de Santa Cruz de la Sierra, Bolivia (17°46'34" S, 63°11'42" O). Ilustración 1 Ubicación de la FICCT en Santa Cruz de la Sierra y en la Ciudad Universitaria

Sirve para inicio: contexto del negocio. Se relaciona con Organización y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001. Revisión personal: ¿Es un organigrama oficial? El texto aclara que representa el proceso comercial modelado, no la estructura oficial de la facultad.

### 2.5. Organigrama

Páginas 19–19. Ilustración 2 Organigrama funcional del proceso comercial modelado para UNEXO

Sirve para inicio: contexto del negocio. Se relaciona con Organización y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001. Revisión personal: ¿Es un organigrama oficial? El texto aclara que representa el proceso comercial modelado, no la estructura oficial de la facultad.

### Capítulo IV: Especificación de Requerimientos

Páginas 20–21. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### 3. Requisitos Específicos

Páginas 20–21. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### 3.1. Requerimiento Funcional

Páginas 20–21. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R1 Acceso por roles

Páginas 20–20. El sistema permitirá el acceso con correo y contraseña a tres roles: Administrador, Coordinador y Vendedor, solo mientras la cuenta esté activa y dentro de su periodo de vigencia.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R2 Cartera del vendedor

Páginas 20–20. El sistema permitirá que el Vendedor vea únicamente los prospectos de su cartera; los prospectos los reparten el Coordinador o el Administrador, sin bolsa común.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R3 Alcance del coordinador

Páginas 20–20. El sistema permitirá que el Coordinador vea solo las métricas y los prospectos de los programas a su cargo.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R4 Registro de prospectos

Páginas 20–20. El sistema permitirá registrar prospectos de forma manual o masiva mediante un archivo CSV, con nombre, teléfono, correo y origen del lead.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R5 Interés vinculado al catálogo

Páginas 20–20. El sistema permitirá vincular el interés de cada prospecto al catálogo activo: un programa de varios módulos o un módulo independiente.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R6 Asignación de prospectos

Páginas 20–20. El sistema permitirá asignar prospectos a los vendedores de forma manual, por el Administrador o el Coordinador, o automática por reparto Round-Robin.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R7 Tablero Kanban

Páginas 21–21. El sistema permitirá gestionar los prospectos como tarjetas que se mueven en un tablero Kanban.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R8 Estados del embudo

Páginas 21–21. El sistema permitirá llevar cada tarjeta por los estados Nuevo, En Contacto, Seguimiento, Promesa de Pago, Convertido y Perdido.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R9 Motivo de pérdida

Páginas 21–21. El sistema permitirá marcar un prospecto como Perdido solo con un motivo clasificado por categoría: Económico, Horario, Incompatibilidad, Contacto u Otro.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R10 Validación de conversión

Páginas 21–21. El sistema permitirá pasar un prospecto a Convertido solo con sus datos completos y la primera cuota de su orden de pago aprobada, y entonces registrará su matrícula.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R11 Historial de interacciones

Páginas 21–21. El sistema permitirá consultar el historial cronológico de las interacciones de cada tarjeta.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R12 Notas manuales

Páginas 21–21. El sistema permitirá registrar notas manuales sobre cada contacto con el prospecto.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### R13 Recordatorios de contacto

Páginas 21–21. El sistema permitirá agendar recordatorios de contacto con fecha y hora futuras y marcarlos como realizados o cancelados.

Sirve para requisitos, principalmente inicio/elaboración. Se relaciona con Especificación de Requerimientos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001, REQ-002. Revisión personal: ¿R5 significa temas? En este capítulo R5 es interés vinculado al catálogo; los diez criterios del enunciado usan otra numeración.

### Capítulo V: Captura de Requisitos

Páginas 22–33. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para requisitos; casos de uso dirigidos por objetivos de actores. Se relaciona con Captura de Requisitos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, CU-002, CU-003, CU-004, PAG-001. Revisión personal: ¿Cliente tiene cuenta? No existe ese rol; el pagador usa enlaces públicos con token.

### 4. Identificación De Casos De Uso Y Actores

Páginas 22–33. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para requisitos; casos de uso dirigidos por objetivos de actores. Se relaciona con Captura de Requisitos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, CU-002, CU-003, CU-004, PAG-001. Revisión personal: ¿Cliente tiene cuenta? No existe ese rol; el pagador usa enlaces públicos con token.

### 4.1. Identificar Actores

Páginas 22–22. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para requisitos; casos de uso dirigidos por objetivos de actores. Se relaciona con Captura de Requisitos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, CU-002, CU-003, CU-004, PAG-001. Revisión personal: ¿Cliente tiene cuenta? No existe ese rol; el pagador usa enlaces públicos con token.

### 4.2. Identificación de casos de uso

Páginas 22–22. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para requisitos; casos de uso dirigidos por objetivos de actores. Se relaciona con Captura de Requisitos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, CU-002, CU-003, CU-004, PAG-001. Revisión personal: ¿Cliente tiene cuenta? No existe ese rol; el pagador usa enlaces públicos con token.

### 4.3. Priorización de casos de uso

Páginas 23–23. La prioridad Alta corresponde a las funciones necesarias para acceder, captar y asignar prospectos, seguir su avance y convertirlos en matrícula. La prioridad Media corresponde a la clasificación de pérdidas, el seguimiento complementario y la consulta de indicadores. La prioridad expresa el orden de implementación del grupo; no elimina ningún caso de uso.

Sirve para requisitos; casos de uso dirigidos por objetivos de actores. Se relaciona con Captura de Requisitos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, CU-002, CU-003, CU-004, PAG-001. Revisión personal: ¿Cliente tiene cuenta? No existe ese rol; el pagador usa enlaces públicos con token.

### 4.4. Detalle de Casos de Uso

Páginas 24–32. CU1. Gestión de Usuarios (Propietario, Clientes) CU2. Gestión de Captar, Consumir Oferta

Sirve para requisitos; casos de uso dirigidos por objetivos de actores. Se relaciona con Captura de Requisitos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, CU-002, CU-003, CU-004, PAG-001. Revisión personal: ¿Cliente tiene cuenta? No existe ese rol; el pagador usa enlaces públicos con token.

### 4.5. Diagrama General de Caso de Uso

Páginas 33–33. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para requisitos; casos de uso dirigidos por objetivos de actores. Se relaciona con Captura de Requisitos y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CU-001, CU-002, CU-003, CU-004, PAG-001. Revisión personal: ¿Cliente tiene cuenta? No existe ese rol; el pagador usa enlaces públicos con token.

### Capítulo VI: Análisis de Arquitectura

Páginas 34–47. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para análisis y arquitectura en elaboración, refinados durante construcción. Se relaciona con Análisis de Arquitectura y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CL-001, CL-002, SEC-001, FMT-001, ARQ-002. Revisión personal: ¿P son clases PHP? No: páginas React funcionales y módulos JS representan presentación.

### 5. Análisis de la Arquitectura

Páginas 34–47. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para análisis y arquitectura en elaboración, refinados durante construcción. Se relaciona con Análisis de Arquitectura y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CL-001, CL-002, SEC-001, FMT-001, ARQ-002. Revisión personal: ¿P son clases PHP? No: páginas React funcionales y módulos JS representan presentación.

### 5.1. Modelo de Dominio

Páginas 34–34. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para análisis y arquitectura en elaboración, refinados durante construcción. Se relaciona con Análisis de Arquitectura y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CL-001, CL-002, SEC-001, FMT-001, ARQ-002. Revisión personal: ¿P son clases PHP? No: páginas React funcionales y módulos JS representan presentación.

### 5.1.1. Identificar Paquetes

Páginas 34–34. Seguridad y Acceso Gestiona los usuarios, sus roles y vigencia, los tokens de sesión, la matriz de acceso (recursos y permisos) y la bitácora de accesos.

Sirve para análisis y arquitectura en elaboración, refinados durante construcción. Se relaciona con Análisis de Arquitectura y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CL-001, CL-002, SEC-001, FMT-001, ARQ-002. Revisión personal: ¿P son clases PHP? No: páginas React funcionales y módulos JS representan presentación.

### 5.2. Relacionar Paquetes con casos de uso

Páginas 35–36. Módulo de Seguridad y Acceso Ilustración 3 Relacionar Paquetes con casos de uso. Módulo de Seguridad y Acceso

Sirve para análisis y arquitectura en elaboración, refinados durante construcción. Se relaciona con Análisis de Arquitectura y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CL-001, CL-002, SEC-001, FMT-001, ARQ-002. Revisión personal: ¿P son clases PHP? No: páginas React funcionales y módulos JS representan presentación.

### 5.3. Análisis de Caso de Uso

Páginas 37–47. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para análisis y arquitectura en elaboración, refinados durante construcción. Se relaciona con Análisis de Arquitectura y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CL-001, CL-002, SEC-001, FMT-001, ARQ-002. Revisión personal: ¿P son clases PHP? No: páginas React funcionales y módulos JS representan presentación.

### 5.3.1. Diagramas de Colaboración

Páginas 37–39. CU1. Gestión de Usuarios (Propietario, Clientes) CU2. Gestión de Captar, Consumir Oferta

Sirve para análisis y arquitectura en elaboración, refinados durante construcción. Se relaciona con Análisis de Arquitectura y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CL-001, CL-002, SEC-001, FMT-001, ARQ-002. Revisión personal: ¿P son clases PHP? No: páginas React funcionales y módulos JS representan presentación.

### 5.3.2. Análisis de clases

Páginas 40–47. CU1. Gestión de Usuarios (Propietario, Clientes) CU2. Gestión de Captar, Consumir Oferta

Sirve para análisis y arquitectura en elaboración, refinados durante construcción. Se relaciona con Análisis de Arquitectura y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias CL-001, CL-002, SEC-001, FMT-001, ARQ-002. Revisión personal: ¿P son clases PHP? No: páginas React funcionales y módulos JS representan presentación.

### Capítulo VII: Diseño

Páginas 48–96. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 6. Diseño de la Arquitectura

Páginas 48–48. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 6.1. Diseño Físico de la Arquitectura (Diagrama de Despliegue)

Páginas 48–48. Representa despliegue si es6.1, y DDL por tabla si es7.3. Distinguir ubicación/protocolo de estructura de datos.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7. Diseño de Datos

Páginas 49–96. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7.1. Diseño Conceptual de Base de Datos

Páginas 49–49. Figura global de31 entidades derivada del volcado. FK se expresan mediante asociaciones; multiplicidades deben leerse en ambos extremos.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7.2. Diseño Lógico

Páginas 50–54. Transforma entidades/asociaciones a tablas y columnas. Las43 tablas extraídas del DOCX incluyen31 mapeos, con PK/FK marcadas.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7.2.1. Mapeo

Páginas 50–54. Transforma entidades/asociaciones a tablas y columnas. Las43 tablas extraídas del DOCX incluyen31 mapeos, con PK/FK marcadas.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7.3. Diseño Físico

Páginas 55–68. CREATE TABLE api_tokens ( token_hash	character varying(64)	NOT NULL,

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7.4. Diseño de casos de uso (Diagrama de secuencia)

Páginas 69–76. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### CU1. Gestión de Usuarios (Propietario, Clientes)

Páginas 69–69. Presenta la vista específica de este caso de uso. Contrastar actor, objetivo y recorrido con04,03 y06, sin confundir el título de marco con la especificación.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### CU2. Gestión de Captar, Consumir Oferta

Páginas 70–70. Presenta la vista específica de este caso de uso. Contrastar actor, objetivo y recorrido con04,03 y06, sin confundir el título de marco con la especificación.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### CU3. Gestión de Asignar Prospectos (Leads)

Páginas 71–71. Presenta la vista específica de este caso de uso. Contrastar actor, objetivo y recorrido con04,03 y06, sin confundir el título de marco con la especificación.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### CU4. Gestión de Embudo de Ventas en Tablero Kanban

Páginas 72–72. Presenta la vista específica de este caso de uso. Contrastar actor, objetivo y recorrido con04,03 y06, sin confundir el título de marco con la especificación.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### CU5. Gestión de Pérdida de Prospectos y Clasificación de Motivos

Páginas 73–73. Presenta la vista específica de este caso de uso. Contrastar actor, objetivo y recorrido con04,03 y06, sin confundir el título de marco con la especificación.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### CU6. Gestión de Validar Datos y Procesar Conversión a Matrícula

Páginas 74–74. Presenta la vista específica de este caso de uso. Contrastar actor, objetivo y recorrido con04,03 y06, sin confundir el título de marco con la especificación.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### CU7. Gestión de Bitácora, Interacciones y Recordatorios

Páginas 75–75. Presenta la vista específica de este caso de uso. Contrastar actor, objetivo y recorrido con04,03 y06, sin confundir el título de marco con la especificación.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### CU8. Reportes y Estadísticas

Páginas 76–76. Presenta la vista específica de este caso de uso. Contrastar actor, objetivo y recorrido con04,03 y06, sin confundir el título de marco con la especificación.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7.5. Diseño de Navegación

Páginas 77–95. Conecta páginas, formularios, endpoints y tablas para el menú del actor. Las franjas son partes de una sola figura, no CU nuevos.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7.5.1. Diagrama de Navegación del Administrador

Páginas 77–83. Conecta páginas, formularios, endpoints y tablas para el menú del actor. Las franjas son partes de una sola figura, no CU nuevos.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7.5.2. Diagrama de Navegación del Coordinador

Páginas 84–89. Conecta páginas, formularios, endpoints y tablas para el menú del actor. Las franjas son partes de una sola figura, no CU nuevos.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7.5.3. Diagrama de Navegación del Vendedor

Páginas 90–93. Conecta páginas, formularios, endpoints y tablas para el menú del actor. Las franjas son partes de una sola figura, no CU nuevos.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7.5.4. Diagrama de Navegación del Visitante

Páginas 94–95. Conecta páginas, formularios, endpoints y tablas para el menú del actor. Las franjas son partes de una sola figura, no CU nuevos.

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### 7.6. Diagrama de interfaces

Páginas 96–96. [PENDIENTE: Capturas de pantalla: "Diagrama de Interfaz CUn. Nombre", 2 por página (crm-web/scripts/capturas_p2.mjs)]

Sirve para diseño en elaboración/construcción. Se relaciona con Diseño y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-001, BD-002, DEP-001, MC-001, SEC-002, UI-001, FMT-003. Revisión personal: ¿Se pueden defender todas las columnas? Las ocho columnas recientes requieren actualización del documento.

### Capítulo VIII: Implementación

Páginas 97–98. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para implementación/construcción. Se relaciona con Implementación y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ARQ-001, DEP-001. Revisión personal: ¿Dónde corre datos? Es paquete Composer dentro del proceso PHP; tres capas no exige tres servidores separados.

### 8. Implementación del Sistema

Páginas 97–98. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para implementación/construcción. Se relaciona con Implementación y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ARQ-001, DEP-001. Revisión personal: ¿Dónde corre datos? Es paquete Composer dentro del proceso PHP; tres capas no exige tres servidores separados.

### 8.1. Herramientas para Desarrollo

Páginas 97–98. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para implementación/construcción. Se relaciona con Implementación y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ARQ-001, DEP-001. Revisión personal: ¿Dónde corre datos? Es paquete Composer dentro del proceso PHP; tres capas no exige tres servidores separados.

### Herramientas de Programación y Desarrollo

Páginas 97–97. PHP 8.4: Lenguaje de la capa de negocio y de la capa de datos; el servidor de la facultad ejecuta PHP 8.4. Laravel 13.42.0: Framework de la capa de negocio: expone la API RESTful (negocio/routes/api.php) con controladores, requests de validación, servicios y los middleware de token y de matriz de acceso; sus migraciones crean la base de datos.

Sirve para implementación/construcción. Se relaciona con Implementación y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ARQ-001, DEP-001. Revisión personal: ¿Dónde corre datos? Es paquete Composer dentro del proceso PHP; tres capas no exige tres servidores separados.

### Herramientas de Gestión de Bases de Datos

Páginas 98–98. PostgreSQL 18: Gestor de la base de datos db_grupo05sa (esquema public), compartida con el Proyecto 1.

Sirve para implementación/construcción. Se relaciona con Implementación y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ARQ-001, DEP-001. Revisión personal: ¿Dónde corre datos? Es paquete Composer dentro del proceso PHP; tres capas no exige tres servidores separados.

### Herramientas de Diseño y Modelado

Páginas 98–98. Enterprise Architect 15 Trial: Modelado UML del sistema (casos de uso, paquetes, clases, base de datos y navegación), automatizado por COM desde generadorDocumento/ea.

Sirve para implementación/construcción. Se relaciona con Implementación y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ARQ-001, DEP-001. Revisión personal: ¿Dónde corre datos? Es paquete Composer dentro del proceso PHP; tres capas no exige tres servidores separados.

### Herramientas de Control de Versiones y Colaboración

Páginas 98–98. Git: Control de versiones del código fuente. GitHub: Repositorio remoto del grupo (ver 13. Anexo).

Sirve para implementación/construcción. Se relaciona con Implementación y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias ARQ-001, DEP-001. Revisión personal: ¿Dónde corre datos? Es paquete Composer dentro del proceso PHP; tres capas no exige tres servidores separados.

### Capítulo IX: Resultados

Páginas 99–99. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para evaluación y transición propuestas. Se relaciona con Resultados y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias QA-001. Revisión personal: ¿Resultado esperado prueba funcionamiento? No. Debe vincularse a evidencia de ejecución.

### 9. Resultado Esperado

Páginas 99–99. Se espera un sistema web de 3 capas publicado en el servidor de la facultad en el que cada usuario vea solo el menú que le da su rol en la matriz de acceso y en el que cada acción quede validada en el servidor. El Visitante podrá consultar el catálogo de programas y módulos, buscar en él y registrar su interés sin iniciar sesión.

Sirve para evaluación y transición propuestas. Se relaciona con Resultados y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias QA-001. Revisión personal: ¿Resultado esperado prueba funcionamiento? No. Debe vincularse a evidencia de ejecución.

### Capítulo X: Pruebas

Páginas 100–103. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para pruebas en construcción/transición y regresión por iteración. Se relaciona con Pruebas y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias QA-001, FMT-003. Revisión personal: ¿Se ejecutaron ahora? No: las suites escriben y quedan reservadas a QA aislada.

### 10. Plan de Pruebas

Páginas 100–103. Agrupa las subsecciones siguientes y su artefacto académico.

Sirve para pruebas en construcción/transición y regresión por iteración. Se relaciona con Pruebas y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias QA-001, FMT-003. Revisión personal: ¿Se ejecutaron ahora? No: las suites escriben y quedan reservadas a QA aislada.

### 10.1. Prueba de Caja Blanca

Páginas 100–100. 1. Bitácora de accesos Objetivo: Comprobar que el login fallido y el acceso denegado quedan registrados en la bitácora.

Sirve para pruebas en construcción/transición y regresión por iteración. Se relaciona con Pruebas y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias QA-001, FMT-003. Revisión personal: ¿Se ejecutaron ahora? No: las suites escriben y quedan reservadas a QA aislada.

### 10.2. Prueba de Caja Negra

Páginas 101–103. 1. Catálogo y registro público en el celular Objetivo: Comprobar que el visitante registra su interés desde un celular (390 × 844).

Sirve para pruebas en construcción/transición y regresión por iteración. Se relaciona con Pruebas y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias QA-001, FMT-003. Revisión personal: ¿Se ejecutaron ahora? No: las suites escriben y quedan reservadas a QA aislada.

### 11. Conclusión

Páginas 104–104. Se identificaron los actores del proceso comercial, sus permisos y los ocho casos de uso que abarcan desde la consulta pública de la oferta hasta los reportes de gestión. Esta definición permite relacionar cada función con una necesidad y un responsable. El análisis distribuyó las responsabilidades en paquetes y documentó las colaboraciones y clases de los casos de uso. Los diagramas permiten comprobar cómo se conectan las acciones de los usuarios con la lógica del sistema.

Sirve para evaluación Se relaciona con Conclusión y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias DOC-001. Revisión personal: Distinguir construido, verificado y desplegado.

### 12. Bibliografía

Páginas 105–107. Axios. (s. f.). First steps. https://axios.rest/pages/getting-started/first-steps (consulta: 25 de noviembre de 2026). Ferraiolo, D. F., Cugini, J. A. y Kuhn, D. R. (1995). Role-Based Access Control (RBAC): Features and Motivations. NIST. https://www.nist.gov/publications/role-based-access-control-rbac-features-and-motivations (consulta: 25 de noviembre de 2026).

Sirve para soporte de todos los artefactos Se relaciona con Bibliografía y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias REQ-001. Revisión personal: No confundir síntesis de clases con la fuente oficial; enlaces externos no fueron comprobados en esta auditoría.

### 13. Anexo

Páginas 108–108. URL Proyecto GitHub: https://github.com/b-shadow/Tecno

Sirve para entrega Se relaciona con Anexo y la traza de requisitos → CU → diseño → código → BD. Estado: Revisado con observaciones; referencias BD-002, QA-001. Revisión personal: Identificar commit y versiones de fuentes editables.

## Inventario completo de fuentes documentales

| Ruta | Formato | Bytes | Modificado | Propósito | Entrega | Editable | Generado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DESIGN.md | .md | 29066 | 2026-11-25T11:53:14.726717 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| P2_WEB.md | .md | 28763 | 2026-11-26T01:03:40.853318 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| PRODUCT.md | .md | 5028 | 2026-11-25T11:53:14.729677 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| README.md | .md | 10016 | 2026-11-26T01:03:40.855319 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| datos/README.md | .md | 722 | 2026-11-25T11:53:14.729677 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| datos/semillas/referencias.sql | .sql | 24322 | 2026-11-25T11:53:14.754481 | DDL y/o evolución de BD | False | True | False |
| docs/GUIA_DEFENSA_STRIPE.md | .md | 8195 | 2026-11-25T16:25:16.898827 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| docs/GUIA_DEFENSA_TEMAS.md | .md | 20563 | 2026-11-26T00:50:15.532031 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| docs/STRIPE_INTEGRACION.md | .md | 9440 | 2026-11-25T16:25:15.398315 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| generadorDocumento/PENDIENTES.md | .md | 3627 | 2026-11-26T01:03:40.867513 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| generadorDocumento/README.md | .md | 8505 | 2026-11-26T01:03:40.870777 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| generadorDocumento/REGLAS_DOCUMENTO_P2.md | .md | 19848 | 2026-11-26T01:03:40.870777 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| generadorDocumento/documento/P2-INF513-GRUPO05SA.doc | .doc | 15132160 | 2026-11-26T01:03:41.366960 | Salida de entrega | True | False | True |
| generadorDocumento/documento/P2-INF513-GRUPO05SA.docx | .docx | 14465709 | 2026-11-26T01:03:41.405547 | Salida de entrega | True | False | True |
| generadorDocumento/documento/P2-INF513-GRUPO05SA.pdf | .pdf | 6037593 | 2026-11-26T01:03:41.440370 | Salida de entrega | True | False | True |
| generadorDocumento/ea/crm-p2.eapx | .eapx | 7573504 | 2026-11-26T01:03:41.462331 | Modelo UML editable | False | True | False |
| generadorDocumento/fuentes/esquema.sql | .sql | 62656 | 2026-11-26T01:03:41.482085 | DDL y/o evolución de BD | False | True | False |
| generadorDocumento/referencias/CLASES_DOCENTE.md | .md | 24133 | 2026-11-25T11:53:15.591281 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| generadorDocumento/referencias/G07-documento-aprobado.pdf | .pdf | 10668887 | 2026-11-25T11:53:15.686108 | Documentación de apoyo/requisitos; autoridad por verificar | False | False | False |
| negocio/README.md | .md | 419 | 2026-11-25T11:53:15.702051 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| presentacion/README.md | .md | 612 | 2026-11-25T11:53:15.902131 | Documentación de apoyo/requisitos; autoridad por verificar | False | True | False |
| scripts/estructura_esquema.sql | .sql | 1449 | 2026-11-25T11:53:16.001939 | DDL y/o evolución de BD | False | True | False |
| scripts/verificar_integridad.sql | .sql | 3234 | 2026-11-25T11:53:16.001939 | DDL y/o evolución de BD | False | True | False |

Fechas son metadatos locales, no prueba de vigencia. SHA256 y duplicados están en documentacion_inventario.json. El inventario general archivos.json cubre también migraciones, scripts, imágenes y capturas. Dependencias/cachés/build/.git se excluyeron.

## Páginas y alcance de PDFs de referencia

- `generadorDocumento/documento/P2-INF513-GRUPO05SA.pdf`: 108 páginas.
- `generadorDocumento/referencias/G07-documento-aprobado.pdf`: 129 páginas.

El referente G07 se inventaría como ejemplo ajeno; no constituye el enunciado oficial del grupo.
