# Reglas del documento del P2 (Sistema vía Web)

**Modelo único:** `referencias/G07-documento-aprobado.pdf` (Grupo 07 SC, 129 pág., **aprobado por el
docente**). Estructura, títulos, orden, tablas, formato y forma de diagramar se copian de ahí. No se agrega ni se inventa
nada que G07 no tenga; lo que G07 hace mal se corrige (lista al final). Para este entregable el formato G07 **reemplaza**
la regla "12 secciones del Anexo B / APA" de los informes de las prácticas (decisión del grupo, 23/11/2026).
G07 es MVC (Inertia + Vue): se copia su **forma**, no su stack; donde G07 muestra MVC, aquí van las 3 capas reales.

Orden de prioridad ante un conflicto: **1) G07** (estructura y notación) → **2) reglas del docente**
(`referencias/CLASES_DOCENTE.md`, clases 03–07, 40, 46–48: corrección del contenido).

Generador: esta carpeta, `crm-web/generadorDocumento/` (autosuficiente; cómo regenerar, al final y en `README.md`). Todo dato sale del código o de la BD real; lo que falta sale en rojo
`[PENDIENTE: …]` y se lista al terminar.

---

## 1. Formato general (G07)

- Carta, Times New Roman en todo; cuerpo 12, interlineado ~1,5, alineado a la izquierda (no justificado), sin sangría
  de primera línea. Márgenes 3 cm izquierda/derecha, 2,5 cm arriba/abajo.
- Títulos: `Capítulo N: Nombre` Bold 16 centrado, cada capítulo en página nueva (sin páginas separadoras).
  Nivel numerado `3. …` Bold 14; `3.1.` y `5.1.1.` Bold 13. En el Capítulo I los títulos `1 Introducción`… van Bold 16
  y `4.1 …` Bold 14, sin punto final, como G07.
- La numeración continúa entre capítulos: II → `1.`, III → `2.`, IV → `3.`, V → `4.`, VI → `5.`, VII → `6.` y `7.`,
  VIII → `8.`, IX → `9.`, X → `10.`; luego `11. Conclusión`, `12. Bibliografía`, `13. Anexo` sin línea de capítulo.
- Pie de página en **todas** las páginas (también la carátula): a la derecha `N | P á g i n a` ("N | " negro,
  "Página" gris #7F7F7F espaciado) con una raya gris clara encima. Sin encabezado.
- Índice: título `INDICE` Bold 18 centrado + índice automático de Word (incluye R1…Rn, los CU de 7.4 y los grupos de
  herramientas porque son títulos).
- Figuras: **rótulo de texto encima** de la imagen (p. ej. `CU1. Gestión de Usuarios.`), sin "Figura N". Solo llevan pie
  "Ilustración N Texto" debajo: el organigrama y la primera figura de 5.2 (como G07).
- Diagramas: Enterprise Architect 15 Trial por COM, cada uno en su marco de EA (`uc`, `pkg`, `sd`, `class`,
  `deployment`). Nunca una copia crackeada.

## 2. Estructura capítulo por capítulo

| G07 | Contenido |
|---|---|
| Carátula | UNIVERSIDAD AUTÓNOMA / GABRIEL RENÉ MORENO (B24) · FACULTAD DE INGENIERÍA EN CIENCIAS DE / LA COMPUTACIÓN Y / TELECOMUNICACIONES (20) · logo · `Grupo 05` (B16) · título del sistema (B16) · **Materia:** Tecnología Web · **Sigla:** INF513-SA · **Integrantes:** tabla 2 columnas con bordes (nombre, registro) · **Docente:** Ing. Balcázar Veizaga Evans · **Semestre: 2/2026** · **Santa Cruz Bolivia** |
| Capítulo I: Perfil | 1 Introducción (3 párrafos) · 2 Antecedentes y Justificación (3 párrafos; justificación teórica, metodológica y práctica) · 3 Planteamiento de Problema (situación, causas, pronóstico, solución) · 4 Objetivo: 4.1 Objetivo General (una línea "Desarrollar un …"), 4.2 Objetivos Específicos (viñetas, verbo en infinitivo, alineados a las fases PUDS) · 5 Alcance (un párrafo por CU: "CUn. Nombre: …") · 6 Metodología (PUDS + UML; párrafos **Inicio (Inception).** / **Elaboración (Elaboration).** / **Construcción (Construction).** / **Transición (Transition).** cada uno con "Entregables: …") |
| Capítulo II: Fundamentación Teórica | `1. Programación del lado del servidor` + 1.1… un párrafo por tecnología **realmente usada** en crm-web. **Se copia la forma de G07, no su stack:** G07 era MVC con Inertia + Vue + Tailwind; nuestro enunciado exige **arquitectura de 3 capas** (presentación React SPA + Axios + Tailwind CSS, lógica Laravel API RESTful, datos PostgreSQL), así que va "Arquitectura de 3 capas", nunca "MVC", ni Vue ni Inertia (definición → creador y año → versión → ventajas y desventajas → "En el presente proyecto, …") |
| Capítulo III: Organización | `2. Empresa`: 2.1 Misión · 2.2 Visión · 2.3 Objetivo · 2.4 Ubicación · 2.5 Organigrama (EA, pie "Ilustración 1 Organigrama de …") |
| Capítulo IV: Especificación de Requerimientos | `3. Requisitos Específicos` → `3.1. Requerimiento Funcional` → por requerimiento: título `Rn Título` + un párrafo "El sistema permitirá…" |
| Capítulo V: Captura de Requisitos | `4. Identificación De Casos De Uso Y Actores` · 4.1 Identificar Actores (diagrama `pkg Actores` + tabla gris **Usuario \| Características**) · 4.2 Identificación de casos de uso (tabla **ID \| NOMBRE**) · 4.3 Priorización de casos de uso (**ID \| NOMBRE \| PRIORIDAD**, Alta/Media) · 4.4 Detalle de Casos de Uso (por CU: rótulo, diagrama `uc` del CU, tabla azul) · 4.5 Diagrama General de Caso de Uso |
| Capítulo VI: Análisis de Arquitectura | `5. Análisis de la Arquitectura` · 5.1 Modelo de Dominio · 5.1.1 Identificar Paquetes (diagrama + un párrafo "Gestiona …" por paquete) · 5.2 Relacionar Paquetes con casos de uso (un diagrama por paquete con «trace») · 5.3 Análisis de Caso de Uso · 5.3.1 Diagramas de Colaboración (uno por CU) · 5.3.2 Análisis de clases (uno por CU) |
| Capítulo VII: Diseño | `6. Diseño de la Arquitectura` · 6.1 Diseño Físico de la Arquitectura (Diagrama de Despliegue) · `7. Diseño de Datos` · 7.1 Diseño Conceptual de Base de Datos · 7.2 Diseño Lógico → 7.2.1 Mapeo (G07 lo titulaba solo "7.2. Mapeo"; el usuario pidió nombrar el nivel lógico) · 7.3 Diseño Físico · 7.4 Diseño de casos de uso (Diagrama de secuencia) — un CU por página · 7.5 Diseño de Navegación (7.5.n por actor) · 7.6 Diagrama de interfaces |
| Capítulo VIII: Implementación | `8. Implementación del Sistema` · 8.1 Herramientas para Desarrollo en 4 grupos (Programación y Desarrollo · Gestión de Bases de Datos · Diseño y Modelado · Control de Versiones y Colaboración); cada herramienta "**Nombre versión:** descripción"; la versión se lee de `composer.lock` / `package-lock.json` al generar (nunca a mano ni de G07) |
| Capítulo IX: Resultados | `9. Resultado Esperado`: prosa, un párrafo general, uno por actor, uno de cierre |
| Capítulo X: Pruebas | `10. Plan de Pruebas` · 10.1 Prueba de Caja Blanca · 10.2 Prueba de Caja Negra: intro + pruebas numeradas (título en negrita) con "o **Objetivo:** …" y "o **Criterio de éxito:** …"; deben corresponder a pruebas que existen (`crm-web/scripts/verificar_p2.py`, `verificar_navegadores.mjs`) |
| 11. Conclusión | Una viñeta por objetivo específico, en el mismo orden, en pasado |
| 12. Bibliografía | Sangría francesa, títulos en cursiva |
| 13. Anexo | 13.n Anexo # n: … y **URL Proyecto GitHub:** al final. Solo documentos que existan |

## 3. Tablas

- **Actores / CU / Prioridad:** bordes negros finos, encabezado gris #C9C9C9 en negrita; en Actores la primera columna
  en negrita.
- **Detalle de CU (tabla azul):** 2 columnas (etiqueta ~2,8 cm). Encabezado `Caso de Uso | CU01. Gestionar X` azul
  #4F94D9 con texto blanco negrita; etiquetas en azul; valores azul claro #D6E8F5; bordes blancos. Filas, en orden:
  **Caso de Uso, Propósito, Descripción, Actores, Actor Iniciador, Precondición, Proceso** (un paso numerado por
  subfila, etiqueta combinada), **Postcondición, Excepciones** (líneas "- …"). Docente: actores concretos (nunca
  "Usuario" genérico) y siempre excepciones (BD caída, sin conexión, credencial vencida, sin permiso).
- **Mapeo (7.2.1, dentro de 7.2 Diseño Lógico):** una tabla Word por tabla de la BD, Calibri 11: fila 1 nombre combinado (Calibri Bold 16 sobre azul
  #5C9CD4); fila 2 marcas `pk` (negrita) / `fk` (negrita cursiva) sobre azul claro; fila 3 los atributos (la PK en
  negrita). **Sin** las dos filas vacías de G07 (decisión del usuario, 24/11). **Una tabla por cada tabla de la BD,
  nunca partida en "continuación"** (G07 no lo hace). Nombres en renglones cortados después de cada "_"; las páginas del Mapeo
  llevan 1 cm de margen lateral (19,5 cm útiles) y la letra baja de 11 a 8 pt solo en las tablas anchas; `intereses`
  (18 columnas) es la única donde algún nombre se corta a media palabra. Orden de columnas: PK, atributos, FK al final. Orden de tablas: primero las referenciadas.

## 4. Diagramas (notación de G07 + reglas del docente)

| Diagrama | Cómo |
|---|---|
| Actores (4.1) | `pkg Actores`: nombre del sistema y un actor por rol real |
| CU (4.4, 4.5) | Uno por CU (`uc CUn. …`: actores + elipse) y el general con todos los actores y los 8 CU. General de CU = menú por actor = matriz de acceso (clase 40) |
| Paquetes (5.1.1, 5.2) | `pkg Identificar Paquetes`; por paquete su `pkg` con los CU unidos por dependencias «trace». Cada paquete dueño de sus tablas (clase 03) |
| Colaboración (5.3.1) | Por CU, marco `sd CU-0n - …`: actor → «boundary» = página React (`Pages/*.jsx`, capa 1) → «control» = controlador de la API (`Api\*Controller`, capa 2) → «entity» con el nombre de la tabla (capa 3); mensajes numerados `1: accion()`, `1.1: store()`, `1.2: create()` con los métodos reales |
| Análisis de clases (5.3.2) | Mismo lugar que G07, pero **3 capas** en vez de su trío MVC (interface / Controller / Entity): por CU, un diagrama de clases con las capas Presentación, Negocio y Datos (§6b), leído del código por `codigo.py` y dibujado por `ea_p2.py --solo clases`; una página por CU |
| Despliegue (6.1) | Calco de G07 pág. 62 (`ea/ea_faltantes.py --despliegue`): «device» `www.tecnoweb.org.bo` → «device» Sistema Operativo Fedora Linux → «executionEnvironment» Apache con PHP 8.4 (`/inf513/grupo05sa/proyecto2`) con los componentes `presentacion` (React), `negocio` (Laravel, API REST) y `datos` (paquete Composer); Router y Switch; **PC Administrador** (usuarios dentro de la red: Administrador, Coordinador, Vendedor) y **PC Cliente** (usuario de internet: Visitante), cada una con S. O. y navegador — como G07 y la clase de diseño del docente (por tipo de acceso, no una por rol; el generador falla si no cubren todos los actores de `contenido.ACTORES`); «device» Database Server `db.tecnoweb.org.bo` → Linux → PostgreSQL 18.6 → `db_grupo05sa (esquema public)`; «device» Pasarela de Pago Stripe → API REST Stripe (Sandbox) con solo lo que usa `NStripe.php`: Checkout Sessions, Customers y Webhooks firmados. Enlaces sin flecha y como G07: servidor–router HTTPS; router–switch, switch–cada PC, servidor–BD y servidor–pasarela TCP/IP. La pasarela solo se une al servidor (G07 no dibuja el salto del navegador a Stripe Checkout); va abajo, junto a la BD. Para imprimir: letra de 11 pt en cajas y rótulos, y 6.1 en página apaisada (1 cm a los lados), figura de 13,2 cm de alto con los títulos en la misma página. Versiones leídas de los lock; nada que el sistema no use |
| Conceptual (7.1) | `class`: una caja por tabla con los atributos en el orden del esquema, sin tipos ni métodos. La clave primaria va **subrayada** (atributo static en EA), sin escribir «PK»/«FK» ni estereotipos: lo pidió el docente en la revisión. Las FK se expresan por asociaciones con multiplicidad. N-N: asociación entre las dos fuertes y la intermedia unida con línea punteada. Ninguna tabla suelta. `ea_p2.py` audita los cruces sobre cajas. |
| Lógico = Mapeo (7.2 Diseño Lógico → 7.2.1 Mapeo) | Tablas Word (§3); aquí sí PK/FK |
| Físico (7.3) | `CREATE TABLE nombre ( col tipo NULL/NOT NULL DEFAULT … );` en TNR Bold 12, columnas alineadas, orden alfabético, sintaxis del volcado de PostgreSQL (como G07: solo las columnas) |
| Secuencia (7.4) | Por CU, una página, `sd CU-0n - …`: actor → página React (capa 1) → controlador de la API vía Axios/HTTP (capa 2) → tablas (capa 3), con los middleware `auth.token` y `acceso:` donde correspondan; fragmentos `alt` |
| Navegación (7.5) | Ver §5 |
| Interfaces (7.6) | Capturas reales del sistema, 2 por página, rótulo encima "Diagrama de Interfaz CUn. Nombre" |

## 5. Diagrama de navegación (lo que más mira el docente)

- **Uno por actor de 4.1** (Administrador, Coordinador, Vendedor, Visitante), **armado desde la matriz de acceso real**
  (`recursos` + `permisos` de la migración 000003): el diagrama de un rol tiene solo las páginas de su menú y, en cada una,
  solo las acciones que la interfaz le habilita con su nivel (la misma condición `puede(recurso, nivel)` de las páginas
  React). Ej.: el vendedor **no** registra ni importa prospectos (exige modificación en `interesados`) y **sí** envía
  notificaciones (modificación en `agenda`). Marco `class Diagrama de Navegacion - <Actor>`, con login → menú → CU en el orden de implementación.
  Exportado como **una sola imagen grande y cortada en franjas horizontales, una por página apaisada** (márgenes
  laterales chicos); el título `7.5.n. Diagrama de Navegación del <Actor>` solo en la primera franja. El corte se hace en
  la fila con menos tinta para no partir cajas.
- Elementos (estereotipos de Conallen que EA trae, como G07):
  - actor → `«link» usa el sistema` → página de login;
  - **client page** (icono de página): pantalla React; atributos `- dato {bag}`, operaciones de la UI;
  - **«Formulario»**: campos `{bag}` que envía y `guardar()`;
  - **server page** con nombre `ps …` (engranaje): el endpoint de la API; parámetros `{bag}` y su método real
    (`store()`, `update()`, `index()`…);
  - **«database» `BD: tabla`** (verde): columnas que se tocan;
  - mensaje de error como client page `PC Message`.
- Relaciones con estereotipo **y** texto (G07 escribe el texto; el docente exige el estereotipo): `«link»` entre
  páginas y hacia el detalle (parámetros en el texto), `«submit»` del formulario al server page (uno por formulario),
  `«build»` del server page a la página que arma (`redirect`, `page load`), `access SELECT|INSERT|UPDATE|DELETE campo`
  del server page a la tabla. Flechas en el sentido correcto.
- **Ninguna clase vacía**: toda página tiene atributos y operaciones (excepción del docente: el «Formulario» puede no
  tener operaciones). Cada recurso del menú del rol (`recursos` + `permisos`) aparece en su diagrama.

## 6. Base de datos (clase 46 y siguientes)

- Fuente única: `fuentes/esquema.sql` (volcado de `db_grupo05sa.public`, idéntico a las migraciones de
  `crm-web/datos/migraciones/`). Conceptual, Mapeo y Físico salen de ahí: **campos del documento = campos de la
  BD, uno a uno**; si la BD cambia, se regenera el volcado y el documento.
- Ninguna tabla suelta; una sola llave por tabla con el nombre del diseño (sin `id` extra); intermedia N-N con al menos
  un campo propio; `migrations` fuera de `public`.

## 6a. Título y organización

Título: **Sistema de Control de Prospectos (CRM Educativo)**. Organización: **UNEXO** (marca y logo del sistema). Los
textos institucionales del P1 (Unidad de Capacitación de la FICCT) **no** se atribuyen a UNEXO. El P1 solo aporta el
antecedente del proceso y la estructura documental. Misión, visión, objetivo y organigrama describen el **alcance
funcional del CRM**, no declaraciones institucionales; están fijados en `contenido.py` sin dependencia de `proyectocorreo`.
La ubicación e infraestructura se transcriben del P1 aprobado: edificio FICCT, módulo 236, dirección y coordenadas.
El mapa de referencia queda como recurso local `diagramas/ubicacion.png`, con crédito y fuente en el documento.
El organigrama funcional se inserta sin deformar su proporción. La prioridad de los ocho CU es una decisión del grupo
y se valida al generar. Solo las capturas de interfaces siguen marcadas `[PENDIENTE]`.

## 6b. Stack real (verificado en el código, 24/11/2026)

Una carpeta por capa en `crm-web/` (rehecho el 24/11/2026; ya **no hay Inertia ni Blade**):
- **Capa 1 Presentación — `presentacion/`:** React 18 SPA con Vite y react-router-dom; cada página (`src/paginas/*.jsx`)
  llama a un módulo `src/api/<area>.js` (uno por controlador, mismos nombres de método), que usa el único cliente HTTP
  `src/api/cliente.js` (axios, token Bearer, JSON). Estilos con Tailwind CSS v4 (`src/estilos/app.css` + `tokens.css`, utilidades en cada JSX; sin estilos en línea).
- **Capa 2 Lógica de negocio — `negocio/`:** Laravel solo API RESTful (`routes/api.php`); middleware `auth.token` y
  `acceso:` (matriz); `App\Http\Requests\<Area>\*Request` (validación en español) → `App\Http\Controllers\Api\*Controller`
  → `App\Services\*Service` (reglas; errores con `App\Exceptions\ReglaNegocioException`).
- **Capa 3 Datos — `datos/` (paquete Composer `grupo05sa/datos`):** `Datos\Repositorios\*Repository` (consultas y
  transacciones) y `Datos\Modelos\*` (Eloquent, una por tabla), migraciones con triggers; PostgreSQL
  `db.tecnoweb.org.bo`, `db_grupo05sa.public`.

**Clases por CU en 3 capas (5.3.2, diagrama de clases con dependencias):** marcos `Capa Presentación`, `Capa Negocio`,
`Capa Datos` (las clases viven en esos paquetes del modelo EA); clases reales con estereotipo y métodos con parámetros
como están en el código: `«client page» <Pagina>.jsx` → `«module» api/<area>.js` → (HTTP/JSON) `«controller»
<Area>Controller` → `«request» <Accion>Request` y `«service» <Area>Service` → `«repositorio» <Area>Repository` (EA dibuja
el estereotipo «repository» como cilindro y oculta los métodos) → `«model» <Modelo>` con las columnas de su tabla. Solo
dependencias «use» que bajan de capa o quedan en ella (nunca página→modelo ni controller→repositorio/modelo); `codigo.py`
falla si aparece una que sube. Todo diagrama y texto del documento usa estas capas.

## 7. Errores de G07 que NO se copian

`5.1.2. Análisis de clases` después de 5.3.1 → **5.3.2**; rótulos de CU con formatos distintos (`CU1.`, `CU01`, `CU 14.`)
→ uno solo (`CU1. Nombre`, y `CU01. Gestionar …` dentro de la tabla azul como G07); "Ilustración 1Organigrama" sin
espacio; tabla duplicada, columna repetida y filas vacías en el Mapeo; requerimiento R24 duplicado; "Capítulo X" alineado a la
izquierda (va centrado como los demás); página en blanco tras el índice; tabla de configuración suelta en el conceptual;
bibliografía sin orden (va alfabética).

## 8. Regenerar

```
cd crm-web/generadorDocumento
python ea/ea_p2.py [--solo datos|nav]      # EA 15 Trial → ea/crm-p2.eapx y diagramas/*.png|emf
python ea/ea_p2.py --guardar-posiciones     # tras acomodar a mano en EA: guarda posiciones (posiciones.json)
python documento_p2.py                      # → documento/P2-INF513-GRUPO05SA.docx + lista de PENDIENTES
powershell -ExecutionPolicy Bypass -File exportar.ps1   # → documento/*.doc + *.pdf con índice (reemplaza los anteriores)
```

`documento_p2.py` corre al final un chequeo de coherencia y **no genera** el documento si: falta un diagrama de
navegación por actor, un diagrama tiene páginas fuera del menú del rol (o le falta alguna), un rol usa una página de un CU
del que no es actor (`contenido.ACTORES_CU`), o aparece un término de otro stack u organización (MVC, Vue, Inertia, JWT,
Unidad de Capacitación…).

Dónde se edita (en `crm-web/generadorDocumento/`): textos y datos → `contenido.py`; navegación → `navegacion.py`; BD →
migraciones + `fuentes/esquema.sql` (pg_dump); formato → `formato_g07.py`; rutas → `rutas.py`.
