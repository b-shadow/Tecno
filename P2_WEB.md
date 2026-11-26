# P2 — Sistema vía Web (Proyecto Final)

Brief único del P2: qué exige el docente, cómo lo cumplimos y cómo se comprueba. Leerlo antes de tocar el código.

> Copia para el equipo del brief que vive en la carpeta del curso (`TecnoTarea/P2_WEB.md`). Las rutas `referencias/`,
> `p1/`, `tools/`, `CLASES_DOCENTE.md`, `CRM_WEB.md` y `GUIA_DOCUMENTO_PUDS.md` son de esa carpeta, no de este repositorio;
> `crm-web/` es la raíz de este repositorio.
Historia técnica del código (normalización, demo de la clienta, verificaciones previas): `CRM_WEB.md`.
Base de datos compartida con el P1: `p1/BASE_DATOS.md` (autoridad del esquema).

| Dato | Valor |
|---|---|
| Enunciado vigente | `referencias/enunciado-P2-2026-2.txt` (Laravel + **React** + API REST, 3 capas, 10 requisitos). Manda sobre `referencias/enunciado-P2.txt` (aula 10/10, decía Inertia + Vue) |
| Cierre | **viernes 27/11/2026 15:15** (fecha confirmada por el usuario; el enunciado dice "antes de las 20:00 del último día de clases": entregar antes de la más temprana) |
| Tarball | `2026-2_INF513-P2_grupo05sa.tar.gz`: documentación técnica completa + código fuente de Laravel y React (sin `vendor/`, `node_modules/`, `.env`) |
| Servidor | `https://www.tecnoweb.org.bo/inf513/grupo05sa/proyecto2` (Apache + PHP 8.4, **sin SSH**: build local y FTP) |
| BD | PostgreSQL `db.tecnoweb.org.bo`, base `db_grupo05sa`, esquema `public` (la misma del P1) |
| Repo | `github.com/b-shadow/Tecno` → renombrar a `inf513-proyecto2`, **público**, historial de commits del grupo |
| Orden de trabajo | primero el software; el documento PUDS (`GUIA_DOCUMENTO_PUDS.md`) después |

## 1. Casos de uso aprobados (obligatorios)

Literal del docente (foro, respuesta a Serrate Basma Leonardo, lunes 5/10/2026 09:34): "CASOS DE USO: (APROBADOS)"

| CU | Nombre | Cómo se cumple en la web |
|---|---|---|
| CU1 | Gestión de Usuarios (Propietario, Clientes) | CRUD con rol, vigencia (`fecha_inicio`/`fecha_fin`) y **foto con nombre legible**; matriz de acceso editable |
| CU2 | Gestión de Captar, Consumir Oferta | Catálogo público por programas → módulos, registro de interés; cliente API del catálogo (simulado hasta que el Grupo 06 publique) |
| CU3 | Gestión de Asignar Prospectos (Leads) | Alta manual y CSV con origen; asignación manual y Round-Robin por coordinador/administrador; reasignación con historial |
| CU4 | Gestión de Embudo de Ventas en Tablero Kanban | Tablero con 6 columnas (RF3.2), tarjetas arrastrables y "Mover a…" en móvil |
| CU5 | Gestión de Pérdida de Prospectos y Clasificación de Motivos | Pasar a Perdido exige un motivo de `motivos_perdida` (con categoría) |
| CU6 | Gestión de Validar Datos y Procesar Conversión a Matrícula | Convertido valida datos completos y 1.ª cuota aprobada; inscripción, comisión y exportación al SIS |
| CU7 | Gestión de Bitácora, Interacciones y Recordatorios | Historial cronológico por tarjeta, notas manuales y recordatorios |
| CU8 | Reportes y Estadísticas | Reportes = listados; estadísticas = representación porcentual (gráficos) de negocio y de acceso |

## 2. Requerimientos del grupo (propios; se ajustan al CU y al docente)

Publicados por el grupo el 14/09/2026. Ajustes acordados el 20/11/2026 en **negrita**.

| Código | Requerimiento |
|---|---|
| RF1.1 | Acceso con credenciales a tres roles: Administrador, Coordinador y Vendedor |
| RF1.2 | El Vendedor ve los prospectos de su cartera **(sin bolsa común: la clienta pidió quitar la autoasignación; solo reparten Coordinador/Administrador)** |
| RF1.3 | El Coordinador solo ve métricas y prospectos de los programas a su cargo (`programas_responsables`) |
| RF2.1 | Registro manual o masivo (CSV) de prospectos: nombre, teléfono, correo y origen del lead |
| RF2.2 | Interés vinculado al catálogo activo: programa de 6 módulos o módulo independiente |
| RF2.3 | Asignación manual (Administrador/Coordinador) o automática Round-Robin |
| RF3.1 | Tablero Kanban con los prospectos como tarjetas móviles |
| RF3.2 | Estados: Nuevo, En Contacto, Seguimiento, Promesa de Pago, Convertido, Perdido **(se migran en la BD, el P1 y el P2; antes eran Nuevo, Contactado, Interesado, Pago enviado, En revision, Convertido, Perdido)** |
| RF3.3 | Perdido exige motivo (Factor económico, Horario, Incompatibilidad…) |
| RF3.4 | Convertido valida datos completos antes de disparar la matrícula |
| RF4.1 | Historial cronológico de interacciones por tarjeta |
| RF4.2 | Notas manuales ("Se envió PDF del diplomado por WhatsApp") |
| RF4.3 | Recordatorios de contacto ("Llamar mañana a las 10:00") |
| RNF1 | Interfaz altamente responsive (los vendedores trabajan desde el celular) |
| RNF2 | Cliente API del catálogo de cursos del Proyecto 2 (Grupo 06 SA) |

## 3. Requisitos del enunciado y criterio de aceptación

| # | Requisito | Se acepta cuando |
|---|---|---|
| 1 | Diseño y navegación | La barra de navegación sale de los permisos del usuario logueado; plantilla base única; pantallas según el diagrama de navegación |
| 2 | RBAC + menú dinámico | Coordinador y Vendedor (+ Administrador). El menú se lee de la BD (`recursos` + `permisos` rol × recurso con tipo de acceso); cambiar un permiso cambia el menú sin tocar código |
| 3 | Laravel API REST + React | 3 carpetas: `presentacion/` (React SPA, react-router, axios por `src/api/`), `negocio/` (Laravel solo API) y `datos/` (repositorios, modelos, migraciones). Laravel no sirve páginas |
| 4 | Matriz + bitácora | Middleware por recurso y acción en cada ruta; tabla de bitácora con login exitoso, fallido, IP, recurso y fecha; pantalla con recursos más accedidos |
| 5 | Estilo único, 3 temas, día/noche, accesibilidad | Tailwind CSS v4 (tokens del tema en `@theme`, componentes repetidos en `app.css`, utilidades en cada JSX), sin estilos en línea; selector Niños/Jóvenes/Adultos; día/noche automático por la hora del cliente y manual; letra con deslizador o A−/A+; alto contraste (WCAG AA mínimo) |
| 6 | Validación en español | Cada formulario valida en cliente y servidor; todos los mensajes en español con tildes |
| 7 | Contador de visitas | Footer de **cada** vista muestra las visitas de esa página; persistente en BD (trigger) |
| 8 | Estadísticas de negocio y acceso | Dashboard con gráficos de ventas/embudo y de accesos (logins, fallos, páginas) |
| 9 | Búsqueda global | Campo de búsqueda predictiva en el header de la página principal (catálogo) e interno según permisos |
| 10 | Pagos | Métodos de pago del prospecto (tarjeta simulada: marca, últimos 4, vencimiento; QR; transferencia), pago único y plan de cuotas; inscripción y comisión al aprobar la 1.ª cuota |

## 4. Reglas del docente que se revisan en la defensa

De `CLASES_DOCENTE.md` (número de clase entre corchetes):
- **BD [46]:** abre el modelo con una herramienta. Ninguna tabla suelta ("si veo una tabla volando, ya no reviso ese
  proyecto"); la clave es la del diseño con su nombre, **sin `id` extra**; intermedia N-N con al menos un campo propio;
  campos del documento = campos de la BD, uno a uno.
- **Migraciones de Laravel [46–48]:** las tablas se crean con migraciones, fijando la PK del diseño
  (`$primaryKey`, `$incrementing`, `$keyType` en los modelos). El control de migraciones va en un esquema aparte para no
  dejar `migrations` suelta en `public`.
- **Menú dinámico [40]:** desde la BD, derivado del diagrama general de CU (actor → CU), con tipos de acceso lectura,
  modificación, eliminación. Modelo de referencia: MENU3C de la U4-4 (`persona`, `grupo`, `permiso`, `modulo`, `mod_grup`).
- **Archivos subidos [40]:** nombre legible y relacionado con el dato (`perez_juan.jpg`), guardado en la BD. Nombres "en
  chino" = no hizo la práctica. Aplica a fotos de usuario y comprobantes.
- **Credenciales [03, 37]:** fecha de inicio, fecha de fin, rol y estado; fuera de vigencia, acceso denegado.
- **Transacciones [28]:** todas las inserciones relacionadas en una transacción con ROLLBACK si falla.
- **CSS en archivos aparte; plantilla base heredada [40].**
- **Diseño [05, 06]:** paleta de colores y 3 temas definidos en el documento, una pantalla por cada página del diagrama
  de navegación (login, error, menú por rol, registrar + éxito/fallo, modificar, listar).
- **Reporte vs estadística:** "reporte es un listado, estadística es la representación porcentual".

## 5. Defensa en vivo

- Puede pedir la terminal y **borrar dependencias o archivos de configuración** para ver si el grupo lo levanta: tener
  una hoja de comandos de rescate (clonar, `composer install`, `npm ci && npm run build`, `.env`, migraciones) que deje el
  sistema arriba en menos de 2 minutos.
- **Desafío en vivo:** cambiar un texto, agregar un campo o una validación en minutos. Cada integrante debe saber dónde
  está cada capa (ruta → middleware → controlador → modelo → vista React).
- La IP de la facultad es dinámica: no depender de listas de IP fijas en `pg_hba`/firewall para la demo.
- Cuentas de prueba por rol (administrador, coordinador, vendedor), separadas de las reales; credenciales solo en
  `.secrets/credenciales.md` de la carpeta del curso (nunca en el repositorio).

## 6. Despliegue en tecnoweb (sin SSH)

**Regla de oro:** ≥3,2 s entre conexiones al servidor (BD o FTP); el docente bloquea conexiones más seguidas. Cada
comando `artisan` abre su propia conexión: esperar entre uno y otro. Credenciales solo en `.secrets/credenciales.md`.

**Estado de la base del servidor (revisado el 25/11/2026, solo lectura):** `db_grupo05sa.public` tiene las 24 tablas del
P1 y coinciden columna por columna con `000001_crear_esquema_compartido` (los SQL pendientes del P1 ya están aplicados);
no existe el esquema `laravel` (el P2 nunca se migró allá); `grupo05sa` es dueño de `public` y tiene `CREATE` sobre la
base; la zona horaria de PostgreSQL es `America/La_Paz` (igual que `APP_TIMEZONE`).

**¿Es seguro `crm:preparar-bd` contra la base del P1?** Sí: solo ejecuta `CREATE SCHEMA IF NOT EXISTS laravel`
(`datos/src/DatosServiceProvider.php`), es idempotente y no toca `public`. Lo delicado es `migrate`: `000001` crea las
tablas sin comprobar si existen, así que contra el servidor **primero se registra como aplicada** (paso 4); `000002`
cambia los CHECK de `estado` (estados RF3.2) y por eso el **JAR nuevo del P1** debe subir a la vez.

### Pasos

1. **Respaldo comprobado** (desde la PC, una conexión):
   `pg_dump -h db.tecnoweb.org.bo -U grupo05sa -Fc db_grupo05sa > backups/tecnoweb_antes_p2_AAAAMMDD.dump` y
   `pg_restore -l backups/tecnoweb_antes_p2_AAAAMMDD.dump | grep -c "TABLE DATA"` (debe listar las 24 tablas).
2. **Detener el lector del P1** (lee el correo cada 10 s y escribe en las mismas tablas).
3. **`.env` de producción** (`proyecto2-app/negocio/.env`, a partir de `negocio/.env.production.example`; nunca al repositorio):
   `APP_KEY` nuevo (`php artisan key:generate --show`), `APP_DEBUG=false`, `APP_URL`/`ASSET_URL`/`FRONTEND_URL` =
   `https://www.tecnoweb.org.bo/inf513/grupo05sa/proyecto2`, runtime `DB_HOST=127.0.0.1`, `DB_DATABASE=db_grupo05sa`,
   `DB_USERNAME=grupo05sa`, `DB_PASSWORD`, y Stripe (`STRIPE_KEY`/`STRIPE_SECRET` de prueba y `STRIPE_WEBHOOK_SECRET`
   del paso 7). El `.env` runtime no se reutiliza desde la PC: las migraciones externas usan
   `DB_HOST=db.tecnoweb.org.bo`, `DB_PORT=5432` (o el publicador, que pasa esas variables al proceso de migración).
4. **Migrar** (un comando por vez, ≥3,2 s entre ellos):
   ```sh
   php artisan migrate:status              # sin esquema laravel: "Migration table not found" (esperado)
   php artisan crm:preparar-bd             # CREATE SCHEMA IF NOT EXISTS laravel
   php artisan migrate:install             # crea laravel.migrations
   psql ... -c "INSERT INTO laravel.migrations (migration, batch) VALUES ('2026_11_21_000001_crear_esquema_compartido', 1)"
   php artisan migrate:status              # 000001 Ran; 000002…000008 Pending
   php artisan migrate --force             # cada migración corre en su transacción (si una falla, se revierte esa)
   php artisan migrate:status              # todas Ran
   ```
   Comprobar después: `psql ... -f scripts/verificar_integridad.sql` (sin tablas sueltas ni `id` extra).
   **Nunca** `migrate:fresh`, `db:wipe` ni `db:seed` en el servidor (el seeder se niega en producción).
5. **Subir el JAR nuevo del P1** y reanudar su lector.
6. **Código** (FTP, sin SSH): `proyecto2-app/` contiene `negocio/`, `datos/` y `presentacion/`; `proyecto2/` contiene
   el `index.php` de entrada, `.htaccess` y el build de React. Instalar `vendor/` localmente con
   `COMPOSER_MIRROR_PATH_REPOS=1 composer install --no-dev`, para que `datos` quede copiado y no enlazado; excluir los
   caches `bootstrap/cache/*.php`. Compilar desde PowerShell con `$env:VITE_BASE='/inf513/grupo05sa/proyecto2/'; npm run build`
   (Git Bash puede convertir esa ruta a `C:/Program Files/Git/...`). El `.htaccess` sirve archivos existentes, envía
   `^api/` y `^up$` a `index.php` y el resto a `index.html` (SPA en el mismo dominio, sin CORS). Crear solo los
   directorios de runtime necesarios con permisos de escritura; no aplicar `chmod -R` a miles de archivos. Comprobar
   `https://www.tecnoweb.org.bo/inf513/grupo05sa/proyecto2/api/salud` → `"base_de_datos":"conectada"`.
7. **Webhook de Stripe** (lo hace el dueño de la cuenta Stripe, en **modo prueba**):
   Dashboard → Desarrolladores → Webhooks → *Agregar destino* → URL
   `https://www.tecnoweb.org.bo/inf513/grupo05sa/proyecto2/api/stripe/webhook`, eventos `checkout.session.completed`,
   `checkout.session.expired`, `payment_intent.succeeded` y `payment_intent.payment_failed` → crear → copiar el
   **secreto de firma** (`whsec_…`). Ese valor va en `STRIPE_WEBHOOK_SECRET` del `.env` del servidor junto con las
   claves de prueba de la misma cuenta (Desarrolladores → Claves de API: `pk_test_…` en `STRIPE_KEY`, `sk_test_…` en
   `STRIPE_SECRET`). El `whsec_` que imprime `stripe listen` es otro y solo sirve en una PC local.
8. **Pago de prueba en el servidor:** cuentas de prueba por rol (administrador, coordinador, vendedor) creadas desde
   Usuarios; con el vendedor: Agenda → tarjeta → orden de 1 cuota → *Pagar con Stripe* → tarjeta `4242 4242 4242 4242`,
   vencimiento futuro, CVC cualquiera → vuelve a `/pagos/confirmacion` con la cuota en "Pago aprobado". Luego en Stripe →
   Webhooks → el destino muestra las entregas con respuesta 200, y en la BD
   `select tipo, estado from webhook_eventos_stripe order by created_at desc limit 5` muestra los eventos `procesado`.
   Repetir con `4000 0000 0000 0002` (rechazada): la cuota sigue pendiente.
9. **Si algo falla:** el código se revierte volviendo a subir la versión anterior; la base, con
   `pg_restore --clean --if-exists -d db_grupo05sa backups/tecnoweb_antes_p2_AAAAMMDD.dump` (lector del P1 detenido).

### Estado real del despliegue (25/11/2026)

- El FTP confirmó que `proyecto2/` y `proyecto2-app/` no existían; no había contenido anterior que eliminar. Las
  carpetas de U4 y prácticas quedaron intactas.
- Por instrucción explícita del usuario no se creó un respaldo. En `db_grupo05sa.public` ya estaban las 24 tablas P1;
  se registró `000001` como aplicada y corrieron `000002`–`000008`. La comprobación de integridad terminó con **31 tablas,
  46 claves foráneas, sin tablas desconectadas ni columnas `id` extra**. Los datos P1 existentes se conservaron; RF3.2
  actualizó los nombres de estados antiguos.
- El ZIP público se compiló con `VITE_BASE=/inf513/grupo05sa/proyecto2/`. Ningún ZIP contiene `.env`; su copia activa está
  en `proyecto2-app/negocio/.env`, fuera de la raíz pública. La ruta privada respondió 403 y se eliminó la copia
  adicional que había quedado en el directorio padre.
- La primera extracción por `ZipArchive::extractTo()` dejó archivos vacíos. Se reparó con extracción por streams y
  comprobación de bytes. La portada y `/api/salud` responden HTTP 200; el endpoint confirma PostgreSQL conectado.
- El primer diagnóstico por DNS público encontró rechazo TCP desde el hosting web. Los apuntes del despliegue de
  1-2026 indicaban `DB_HOST=127.0.0.1`; un `SELECT` de solo lectura desde PHP por `127.0.0.1:5432` confirmó la misma
  base `db_grupo05sa`, esquema `public`. Se cambió el `.env` de ejecución de la web a loopback. Las migraciones desde
  la PC continúan usando `db.tecnoweb.org.bo:5432`.
- `STRIPE_KEY`, `STRIPE_SECRET` y `STRIPE_WEBHOOK_SECRET` están vacíos porque las claves de prueba no estaban en
  `.secrets/credenciales.md`; checkout con Stripe queda pendiente de esa configuración.
- No se crearon cuentas de acceso de prueba por rol en producción. Las cuentas de `DatabaseSeeder` son solo locales y
  el seeder aborta en producción; no entregarlas como accesos válidos del sitio.

#### Precauciones aprendidas en esta subida

- **No usar `ZipArchive::extractTo()` en este hosting:** creó los archivos, pero quedaron en cero bytes. Extraer cada
  entrada por stream y comparar los bytes escritos con el tamaño del ZIP.
- **No usar el host DNS público desde PHP en este servidor:** `db.tecnoweb.org.bo:5432` fue rechazado desde el hosting.
  La prueba de solo lectura confirmó que `127.0.0.1:5432` llega a la misma `db_grupo05sa.public`. En producción web usar
  `DB_HOST=127.0.0.1`; desde la PC, las migraciones externas usan `db.tecnoweb.org.bo:5432`.
- **No poner `.env` en el ZIP ni en `proyecto2/`:** va únicamente en `proyecto2-app/negocio/.env`; proteger esa carpeta
  y confirmar HTTP 403 antes de transferir archivos privados.
- **No volver a ejecutar migraciones ni seeders por el fallo HTTP:** `000001`–`000008` ya están aplicadas. No usar
  `migrate:fresh`, `db:wipe` o `db:seed` sobre la base compartida.
- **No borrar carpetas ajenas del FTP ni volver a ejecutar el alta inicial sobre carpetas existentes.** El primer
  despliegue confirmó que las carpetas P2 no existían y dejó intactas las prácticas y carpetas de otros semestres.
- El usuario pidió que esta subida no tuviera respaldos; no se creó ninguno. Durante esta operación se esperaron
  4 segundos entre consultas remotas, por encima de los 3 segundos solicitados.
- Tecnoweb se usa como hosting Apache/PHP por FTP, sin SSH confirmado. Docker no se ejecuta allí; sirve para desarrollo
  local. No se configuró CI/CD ni se copiaron credenciales a GitHub.

## 7. Plan de trabajo (20–27/11)

| Fase | Días | Contenido |
|---|---|---|
| 0 | 20/11 | Contextos, repo (`git pull`, rama `p2-final`), BD local idéntica a producción desde `p1/sql/` |
| 1 | 21–23/11 | Backend sobre el esquema compartido (claves naturales), estados RF3.2 (+ P1), Kanban/motivos/conversión, RBAC + menú, bitácora, contador con trigger, búsqueda, pagos con cuotas, validación en español, estadísticas de acceso |
| 2 | 21–22/11 | Sistema visual con impeccable (PRODUCT.md, dirección, tokens, 3 temas, día/noche, accesibilidad); paleta del logo UNEXO: navy `#083456`, teal `#10aeb5` |
| 3 | 23–25/11 | Frontend React escrito una sola vez sobre el sistema nuevo, vista por vista |
| 4 | 26–27/11 | Verificación, despliegue, repo público, tarball |

## 7b. Estado (21/11/2026, rama `p2-final` de `crm-web`)

- **Fase 0 y 1 hechas.** Migraciones de Laravel = esquema compartido idéntico a `p1/sql/esquema.sql` (comparado con
  `crm-web/scripts/estructura_esquema.sql`) + estados RF3.2 + `recursos`/`permisos` + `bitacora` (trigger
  `contar_visita`) + `metodos_pago`/`cuotas` (triggers `pagos_crear_cuota`, `pagos_copiar_estado`) + `usuarios.foto`:
  29 tablas, 39 FK, ningún `id`, ninguna suelta; control de migraciones en el esquema `laravel` (`php artisan
  crm:preparar-bd` antes de `migrate`). API reescrita (70 rutas, middleware `acceso:` en cada ruta de negocio).
  P1 ajustado a RF3.2 (14/14 pruebas de integración sobre la base nueva).
- **Fase 2 y 3 hechas.** Frontend en React (`@inertiajs/react`), 17 páginas, CSS propio en `resources/js/styles/`
  (tokens con día/noche por hora, Niños/Jóvenes/Adultos, tamaño de letra y alto contraste), fuentes alojadas en el sitio.
  Dos mundos visuales (detalle en `crm-web/DESIGN.md`):
  - **Catálogo público y login: "Malla de la oferta"** (rehecho el 21/11 a pedido del usuario, porque las pestañas por
    programa no escalaban). Cada programa es una fila y sus módulos casillas codificadas (DAT-1…) en orden de cursado,
    agrupadas y filtradas por área; la fila abierta muestra descripciones e imágenes de la API; barra inferior con la
    elección y "Me interesa"; en celular, programas plegados con su tira de códigos. El área sale de los datos del
    catálogo externo (`CatalogoExternoDemo`, campo `area`), no de la BD. Login: solo el logo de UNEXO y el formulario,
    entra en una pantalla sin scroll (probado de 320×568 a 1440×900).
  - **Panel interno: "Prospecto de admisión"** en versión sobria (sin cambios).
  - Contador de visitas: una línea discreta al pie de cada página (requisito 7; el usuario decidió mantenerlo).
- **Orden de los módulos:** se ordenaban por `codigo` como texto (`m10` antes de `m2`). Corregido con
  `ORDER BY length(codigo), codigo` en `CatalogoController` (P2) y en `ProspectoService` (P1, listado por correo).
- **Pruebas:** `python scripts/verificar_p2.py` (32 casos de API, repetible: el CSV usa un carnet único por corrida) y
  `QA_BASE=http://localhost:8001 QA_ENGINES=chromium node scripts/verificar_navegadores.mjs` (321 casos) en verde.
  Firefox/WebKit no se probaron (faltan los navegadores de Playwright: `npx playwright install firefox webkit`).
  Siempre sobre la base local sembrada (`php artisan db:seed`), nunca en producción.

### Pendientes (auditoría del 21/11, por prioridad)

Bloqueantes para la defensa:
1. **El vendedor aprueba su propio pago con tarjeta** (`POST /ordenes-pago/{o}/cuotas/{n}/pagar` con `acceso:agenda`):
   la pasarela debe dejar la cuota "En revisión" para que coordinación la valide (`PagoController`, `Conversion`).
2. **Los prospectos del CSV no llegan al Kanban ni al Round-Robin**: se crean sin interés. Agregar `modulo_codigo` o
   `programa_codigo` al CSV, o un botón "Agregar interés" en Prospectos (el endpoint `POST /prospectos/{p}/intereses` ya existe).
3. **81 estilos inline (`style={{…}}`)** en 20 archivos JSX: el docente exige CSS en archivos aparte [40]. Pasarlos a clases.
4. **Fechas de vencimiento un día antes** en Ficha → Pagos y Validación de pagos: `new Date('YYYY-MM-DD')` se lee en
   UTC (`components/ui.jsx`, función `fecha`); también el `min` y el valor por defecto en `Agenda.jsx`.
5. **Despliegue §6 no viable tal cual** (viene de un grupo con SSH): falta `usePublicPath` en `index.php`, subir
   `vendor/` por FTP no es viable (adaptar `tools/deploy_jetstream.py`: zip + instalador PHP), excluir
   `bootstrap/cache/packages.php`/`services.php`, `composer install --no-dev` en el contenedor, `.env` de producción
   con `APP_KEY` nuevo y `APP_DEBUG=false`.
6. **Migración del servidor:** antes de marcar `000001` aplicar los pendientes `p1/sql/migraciones/2026-11-20_retirar_bandeja.sql`
   y `2026-11-20_quitar_redundancias.sql`; comparar la estructura; `crm:preparar-bd` → `migrate:install` → insertar la
   fila de `000001` en `laravel.migrations` → `migrate --force`; JAR nuevo del P1 a la vez (el viejo falla con los estados nuevos).

Importantes:
- RF1.3 en comisiones: el coordinador ve y paga comisiones de todos y cambia el porcentaje global (`SeguimientoController`);
  `ExportacionController::registrarResultado` sin alcance.
- Venta duplicada: el P2 permite inscribir dos veces el mismo módulo y abrir una orden con otra pendiente (el P1 lo rechaza).
- El seeder demo no se bloquea en producción (`if (app()->isProduction()) throw …`).
- No hay página de error (404 de Laravel en inglés y sin contador).
- Un 403 no refresca el menú (`services/api.js`: llamar `refreshSession()`).
- Límite de intentos de login solo por correo+IP; agregar límites por IP y por correo.
- `scripts/verificar_integridad.sql` usa `orden_pago_id` (no existe) y no comprueba columnas `id`.
- `README.md` de `crm-web` y `backend` dicen Vue/Inertia (corregido el de `crm-web` el 21/11; falta el de `backend`).
- Hoja de comandos de rescate del P2.

Menores: "En revision" sin tilde en Agenda y Embudo; `pattern` del cliente desigual entre formularios; Luhn solo en el
servidor; `programas_responsables` sin campo propio; líneas de más de 150 caracteres (formatear con Pint/Prettier);
5 endpoints sin pantalla; buscador muestra "Sin resultados" mientras espera; Jóvenes y Adultos se parecen poco.

## 7c. Estado (24/11/2026): 3 capas estrictas (rama `p2-final`, base = rama `b-shadow` de Brandon)

Pedido del usuario: "3 capas estricto" para que el diseño procedimental salga limpio. Decisiones: carpetas separadas,
partir de la rama de Brandon (Services + Repositories). Después (24/11), a pedido del usuario: **estilos migrados a
Tailwind CSS v4** (ver abajo).
- **Estructura:** `presentacion/` (React + Vite + react-router-dom, sin Inertia), `negocio/` (Laravel solo API: sin
  Blade ni `web.php`), `datos/` (paquete Composer `grupo05sa/datos`: `Datos\Repositorios`, `Datos\Modelos`,
  migraciones y semillas; `negocio` lo carga como repositorio `path`).
- **Capa 1:** `src/api/<area>.js` = un módulo por controlador, mismos nombres de método; las páginas no usan axios.
  Página 404 con contador (recurso `error`, migración `000007`). Un 403 relee el menú. **Sin estilos en línea** (71 →
  0; barras con `<progress>` y tono por clase). **Tailwind v4:** `estilos/tokens.css` (temas) + `estilos/app.css`
  (`@theme inline`, variantes `dark:`/`contraste:`/`claro:`/`bajo:`, base y componentes repetidos); cada pantalla con
  utilidades en su JSX; colores por dato en `componentes/tonos.js`. Comparado contra capturas previas (día y noche).
- **Capa 2:** cada acción = FormRequest (`app/Http/Requests/<Area>`) → Controller → Service; ningún Service usa
  `Request`/`response()`/`abort`/`DB::` (errores con `ReglaNegocioException`); middleware sin acceso a la BD.
- **Capa 3:** solo `datos/` toca la BD; bitácora por `BitacoraRepository` (el modelo ya no recibe el Request).
- **Bloqueantes 1–4 resueltos:** tarjeta → cuota "En revisión" y la aprueba coordinación (el vendedor recibe 403);
  CSV con `modulo_codigo`/`programa_codigo` opcionales entra al Kanban y al Round-Robin; 71 estilos inline fuera;
  "En revisión" con tilde. Importantes resueltos: RF1.3 en comisiones y exportaciones (porcentaje solo administrador),
  una sola orden abierta por tarjeta (como el P1), seeder bloqueado en producción, 404 propia, 403 refresca el menú,
  login limitado por correo+IP, por IP y por correo, `verificar_integridad.sql` corregido (+ chequeo de `id` extra).
- **Pruebas:** `verificar_p2.py` en verde y repetible sobre la misma base; navegadores 321/0 contra Vite (:5173);
  integridad OK sobre una base creada desde cero con las migraciones de `datos/`.
- **Pendiente:** despliegue en tecnoweb (§6, adaptado a 3 carpetas), repo `inf513-proyecto2` público, tarball, documento
  (diseño procedimental: ver `generadorDocumento/REGLAS_DOCUMENTO_P2.md` §6b) y hoja de rescate.

## 8. Lista de verificación final

- [ ] Los 8 CU funcionan de punta a punta con los 3 roles.
- [ ] `verificar_integridad.sql`: ninguna tabla suelta, ningún `id` extra, intermedias con campo propio.
- [ ] Menú cambia al editar la matriz; ruta sin permiso responde 403 y la UI redirige.
- [ ] Login fallido y exitoso quedan en la bitácora con IP; pantalla de recursos más accedidos.
- [ ] Contador de visitas visible en el footer de cada vista y persistente.
- [ ] Búsqueda en el header de la página principal.
- [ ] 3 temas + día/noche automático y manual + tamaño de letra + alto contraste.
- [ ] Todos los formularios validan en cliente y servidor, mensajes en español.
- [ ] Métodos de pago, pago único y plan de cuotas; inscripción al aprobar la 1.ª cuota.
- [ ] Fotos y comprobantes con nombre legible guardado en la BD.
- [ ] Funciona en `https://www.tecnoweb.org.bo/inf513/grupo05sa/proyecto2` con las cuentas de prueba.
- [ ] Repo `inf513-proyecto2` público con historial; tarball con el nombre exacto.
- [ ] Hoja de comandos de rescate probada desde cero.
