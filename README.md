# UNEXO — CRM Comercial Educativo (INF513 · Proyecto 2 · Grupo 05 SA)

Sistema web de captación y seguimiento comercial para una institución que vende programas de formación (programas
de varios módulos y módulos sueltos). Arquitectura de **3 capas** pedida por el enunciado, una carpeta por capa:
**React** (presentación) → **Laravel API REST** (lógica de negocio) → **PostgreSQL** (datos), sobre la **misma base que
el Proyecto 1** (`db_grupo05sa`, esquema `public`).

- Qué exige el docente, cómo se cumple, estado y pendientes del equipo: **[`P2_WEB.md`](P2_WEB.md)** (leer primero).
- Producto y usuarios: [`PRODUCT.md`](PRODUCT.md). Sistema visual (tokens, temas, componentes): [`DESIGN.md`](DESIGN.md).

## Las 3 capas

```
presentacion/   CAPA 1 · React 18 + Vite + react-router-dom + axios (SPA)
      │  JSON sobre HTTP (Bearer token) a /api
      ▼
negocio/        CAPA 2 · Laravel 13, solo API REST: ruta → middleware (token + matriz) → FormRequest → N<Area>
      │  usa el paquete grupo05sa/datos
      ▼
datos/          CAPA 3 · D<Area> + modelos Eloquent + migraciones (tablas, triggers, contadores) → PostgreSQL
```

Reglas que mantienen las capas separadas (se comprueban con `grep`, ver Pruebas):

| Capa | Carpeta | Puede usar | No usa |
|---|---|---|---|
| Presentación | `presentacion/src/paginas/P*.jsx` | `componentes/`, `servicios/`, `api/<area>.js` | axios, `api/cliente.js` ni URLs `/api` directas |
| | `presentacion/src/api/<area>.js` | `api/cliente.js` (único cliente HTTP, axios) | React |
| Negocio | `negocio/routes/api.php`, `app/Http/Middleware/` | token, matriz `acceso:<recurso>,<nivel>` | la BD (el middleware le pregunta a `NAuth`/`NAcceso`) |
| | `negocio/app/Http/Requests/` | reglas de forma; existencia/unicidad con `$this->segun(fn ($v) => app(D*::class)->…)` | `exists:`/`unique:` de Laravel (irían directo a la BD) |
| | `negocio/app/Negocio/N*.php` | toda regla de negocio: decisiones, cálculos (saldo), estados; métodos de `D*`; Stripe | `DB::`, consultas Eloquent, `save`/`load`, route-model binding |
| Datos | `datos/src/D*.php`, `datos/src/Modelos/` | Eloquent, `DB::`, transacciones: **solo leer y escribir** | HTTP, `App\Negocio`, decisiones de negocio |

## Levantar el entorno local (Docker)

Requisitos: Docker con Compose.

```sh
docker volume create tecno_postgres_data            # solo la primera vez en un equipo nuevo
docker compose up -d --build                        # API en :8001 y React (Vite) en :5173
docker compose exec app php artisan db:seed         # datos de demostración (SOLO en local)
```

Abrir **http://localhost:5173** (Vite reenvía `/api` a Laravel). El contenedor `app` crea `.env` si falta, instala
dependencias (incluido el paquete `datos/`), genera `APP_KEY`, ejecuta `php artisan crm:preparar-bd` (esquema `laravel`)
y `php artisan migrate --force`. Sin Docker: `cd negocio && composer install && php artisan serve --port=8001` y
`cd presentacion && npm ci && npm run dev`.

- Catálogo público: `/anuncios` · Login: `/login` · Salud de la API: `/api/salud` y `/up`.
- PostgreSQL local: puerto 55432, base `db_grupo05sa`, usuario `crm_user` (clave de desarrollo del Compose).
- Cuentas de demostración (las crea el seeder, solo en local): `admin@crm-educativo.local`, `coord@test.local`,
  `vendedor.demo@crm-educativo.local`; las claves están en `datos/semillas/DatabaseSeeder.php`.
  El seeder se niega a correr en producción: en el servidor de la facultad se crean cuentas propias.
- No usar `migrate:fresh`: borra las tablas de `public` (compartidas con el P1) pero deja el control de migraciones
  en el esquema `laravel`.

## Dónde está cada cosa

**Presentación (`presentacion/src/`)**
- `rutas.jsx`: una ruta por página del diagrama de navegación (+ `*` → página de error).
- `plantilla/AppShell.jsx`: plantilla base (pública e interna) con el menú leído de la BD.
- `paginas/P*.jsx`: una página por pantalla (`PCatalogo`, `PLogin`, `PDashboard`, `PAgenda`, `PPagoConfirmacion`, …, `PError404`).
- `api/<area>.js`: un módulo por clase de negocio (`pagos.js` ↔ `NPago`, mismos nombres de método).
- `servicios/`: sesión, permisos, tema/accesibilidad, validación en español del navegador.
- Estilos con **Tailwind CSS v4**: `estilos/tokens.css` (variables de cada tema: día/noche, público, letra, contraste)
  y `estilos/app.css` (único CSS global: `@theme` que expone los tokens a Tailwind, variantes `dark:`/`contraste:`/`bajo:`,
  base de los elementos y los componentes que se repiten: botones, campos, hojas, tablas, filtros). Lo propio de cada
  pantalla va con utilidades en su JSX; los colores que dependen de un dato, en `componentes/tonos.js`. Ningún estilo
  en línea. Fuentes alojadas en el sitio (sin CDN).

**Negocio (`negocio/`)**
- `routes/api.php`: las ~70 rutas; cada ruta de negocio lleva `auth.token` y `acceso:<recurso>,<nivel>` (matriz).
- `app/Http/Middleware/`: `TokenAuthMiddleware` (token y vigencia) y `AccesoRecurso` (matriz + bitácora de denegados).
- `app/Http/Requests/<Area>/`: validación de cada acción con mensajes en español (`lang/es/validation.php`).
- `app/Negocio/N*.php`: una clase por área (`NPago`, `NProspecto`, `NStripe`, …, `NAcceso`, `NAlcance`, `NConversion`,
  `NFoto`); cada acción recibe su FormRequest y el identificador, aplica las reglas, pide y guarda los datos con su `D*`
  y responde JSON; errores de negocio con `App\Exceptions\ReglaNegocioException`.

**Datos (`datos/`, paquete Composer `grupo05sa/datos`)**
- `src/D*.php`: todas las consultas y escrituras (una clase por área + `DBitacora`, `DAlcance`); no deciden nada.
- `src/Modelos/`: un modelo Eloquent por tabla, con la clave del diseño (`$primaryKey`/`$keyType`/`$incrementing`).
- `migraciones/`: `000001` esquema compartido con el P1 · `000002` estados RF3.2 · `000003` recursos y permisos (menú)
  · `000004` bitácora + trigger de visitas · `000005` métodos de pago y cuotas · `000006` foto · `000007` página de error
  · `000008` Stripe Sandbox (transacciones, webhooks, cliente y método Stripe).
- `semillas/`: datos de demostración (solo local).

Cambiar algo de punta a punta (p. ej. un campo nuevo): migración en `datos/migraciones` → modelo (`$fillable`) →
`D<Area>` → regla del FormRequest → `N<Area>` → `api/<area>.js` → página `P*.jsx`. Una pantalla nueva además
necesita su fila en `recursos` y `permisos` (migración) para aparecer en el menú.

## Pruebas (siempre contra la base local, nunca contra producción)

Las que escriben datos van contra una **copia** de la base (API en `:18001`, React en `:18002`), nunca contra la demo.
`python scripts/qa_local.py start|test|stop` arma una desde cero (migraciones + seeder) y corre los scripts de `test`.
En este orden (`verificar_fase_a.py` crea el usuario con foto que usa `verificar_fase_a_ui.mjs`; `verificar_auditoria.py`
va al final porque llena un minuto el límite de intentos de login):

```sh
python scripts/verificar_p2.py http://localhost:18001             # enunciado y CU de punta a punta (repetible)
python scripts/verificar_fase_a.py http://localhost:18001         # seguridad, IDOR, fotos, búsquedas ILIKE
QA_BASE=http://localhost:18002 node scripts/verificar_fase_a_ui.mjs   # fechas, horas, temas, accesibilidad
QA_PHP="docker exec -w /repo crm-web-app-1 php" python scripts/verificar_stripe_api.py http://localhost:18001
QA_BASE=http://localhost:18002 QA_API=http://127.0.0.1:18001/api node scripts/verificar_stripe_e2e_ui.mjs   # pago real en Stripe Sandbox
python scripts/verificar_seguridad.py                             # barrido por rol, comprobante ajeno, doble aprobación, logout
python scripts/verificar_administradores.py                       # siempre queda un administrador (también con bajas simultáneas)
python scripts/verificar_reenvio_comprobante.py                   # rechazo y reenvío de comprobante
python scripts/verificar_correcciones.py                          # registro por programa, reparto, reasignación, comisión, exportación
QA_BASE=http://localhost:18002 QA_ENGINES=chromium,firefox,webkit node scripts/verificar_navegadores.mjs   # 3 roles × 4 anchos × 2 temas
python scripts/verificar_auditoria.py                             # actividades, sesiones, CSV, órdenes simultáneas, límite 429
node scripts/verificar_sesion.mjs                                 # sesión del navegador (sin servidor)
psql ... -f scripts/verificar_integridad.sql                      # sin tablas sueltas, sin id extra, FK completas (solo lectura)
node scripts/capturas_p2.mjs                                      # capturas de cada página por rol
```

En PowerShell: `$env:QA_BASE='http://localhost:5173'; $env:QA_ENGINES='chromium'; node scripts/verificar_navegadores.mjs`.
Firefox y WebKit necesitan `npx playwright install firefox webkit` (desde `presentacion/`).

Comprobación de capas (debe imprimir `[]` y los grep, 0 líneas):

```sh
cd generadorDocumento && python -c "import codigo; print(codigo.errores_codigo())" && cd ..   # N sin BD, D sin N, sin exists/unique
grep -rn "DB::" negocio/app
grep -rlnE "axios|api/cliente" presentacion/src/paginas presentacion/src/componentes
grep -rn "style={{" presentacion/src                       # sin estilos en línea
```

## Despliegue

Servidor de la facultad: `https://www.tecnoweb.org.bo/inf513/grupo05sa/proyecto2` (Apache + PHP 8.4, sin SSH).
Frontend: `cd presentacion && VITE_BASE=/inf513/grupo05sa/proyecto2/ npm run build` (sale en `presentacion/dist/`).
El procedimiento completo y los pasos previos de la migración de la base compartida están en
[`P2_WEB.md`](P2_WEB.md) (§6 y pendientes): no migrar la base del servidor sin respaldo, sin detener el lector del P1
y sin el JAR nuevo del P1.

No subir a Git: `.env`, `vendor/`, `node_modules/`, `dist/`, respaldos ni credenciales.
