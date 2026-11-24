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
negocio/        CAPA 2 · Laravel 13, solo API REST: rutas → middleware → FormRequest → Controller → Service
      │  usa el paquete grupo05sa/datos
      ▼
datos/          CAPA 3 · Repositorios + modelos Eloquent + migraciones (tablas, triggers, contadores) → PostgreSQL
```

Reglas que mantienen las capas separadas (se comprueban con `grep`, ver Pruebas):

| Capa | Carpeta | Puede usar | No usa |
|---|---|---|---|
| Presentación | `presentacion/src/paginas/` | `componentes/`, `servicios/`, `api/<area>.js` | axios ni URLs `/api` directas |
| | `presentacion/src/api/` | `api/cliente.js` (único cliente HTTP) | React |
| Negocio | `negocio/app/Http/` | `Requests/`, `Services/` (modelos solo como tipo de la ruta) | `DB::`, repositorios |
| | `negocio/app/Services/` | repositorios de `datos/`, `ReglaNegocioException` | `Request`, `response()`, `abort`, `DB::` |
| Datos | `datos/src/Repositorios/`, `datos/src/Modelos/` | Eloquent, `DB::`, transacciones | nada de HTTP |

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
- `paginas/`: una página por pantalla (Catalogo, Login, Dashboard, MiDia, Embudo, Agenda, …, Error404).
- `plantilla/AppShell.jsx`: plantilla base (pública e interna) con el menú leído de la BD.
- `api/`: un módulo por controlador de la API (`pagos.js` ↔ `PagoController`, mismos nombres de método).
- `servicios/`: sesión, permisos, tema/accesibilidad, validación en español del navegador.
- `estilos/`: CSS propio en archivos aparte (`tokens.css`, `base.css`, `layout.css`, `components.css`, `catalogo.css`,
  `panel.css`); ningún estilo en línea. Fuentes alojadas en el sitio (sin CDN).

**Negocio (`negocio/`)**
- `routes/api.php`: las ~70 rutas; cada ruta de negocio lleva `auth.token` y `acceso:<recurso>,<nivel>` (matriz).
- `app/Http/Middleware/`: `TokenAuthMiddleware` (token y vigencia) y `AccesoRecurso` (matriz + bitácora de denegados).
- `app/Http/Requests/<Area>/`: validación de cada acción con mensajes en español (`lang/es/validation.php`).
- `app/Http/Controllers/Api/`: un controlador por área; cada acción = FormRequest → Service → JSON.
- `app/Services/`: reglas de negocio (`PagoService`, `ProspectoService`, …, `AccesoService`, `AlcanceService`,
  `ConversionService`, `FotoService`); errores de negocio con `App\Exceptions\ReglaNegocioException`.

**Datos (`datos/`, paquete Composer `grupo05sa/datos`)**
- `src/Repositorios/`: todas las consultas y escrituras (un repositorio por área + `BitacoraRepository`).
- `src/Modelos/`: un modelo Eloquent por tabla, con la clave del diseño (`$primaryKey`/`$keyType`/`$incrementing`).
- `migraciones/`: `000001` esquema compartido con el P1 · `000002` estados RF3.2 · `000003` recursos y permisos (menú)
  · `000004` bitácora + trigger de visitas · `000005` métodos de pago y cuotas · `000006` foto · `000007` página de error.
- `semillas/`: datos de demostración (solo local).

Cambiar algo de punta a punta (p. ej. un campo nuevo): migración en `datos/migraciones` → modelo (`$fillable`) →
repositorio → regla del FormRequest → Service → página en `presentacion/src/paginas`. Una pantalla nueva además
necesita su fila en `recursos` y `permisos` (migración) para aparecer en el menú.

## Pruebas (siempre contra la base local, nunca contra producción)

```sh
python scripts/verificar_p2.py                                    # casos de la API (repetible)
QA_BASE=http://localhost:5173 QA_ENGINES=chromium node scripts/verificar_navegadores.mjs   # 321 casos: 3 roles × 4 anchos × 2 temas
psql ... -f scripts/verificar_integridad.sql                      # sin tablas sueltas, sin id extra, FK completas
node scripts/capturas_p2.mjs                                      # capturas de cada página por rol
```

En PowerShell: `$env:QA_BASE='http://localhost:5173'; $env:QA_ENGINES='chromium'; node scripts/verificar_navegadores.mjs`.
Firefox y WebKit necesitan `npx playwright install firefox webkit` (desde `presentacion/`).

Comprobación de capas (todas deben dar 0 líneas):

```sh
grep -rn "DB::" negocio/app
grep -rlnE "Illuminate.Http|response\(|abort|::query\(" negocio/app/Services
grep -rlnE "axios|api/cliente" presentacion/src/paginas presentacion/src/componentes
grep -rn "style={{" presentacion/src
```

## Despliegue

Servidor de la facultad: `https://www.tecnoweb.org.bo/inf513/grupo05sa/proyecto2` (Apache + PHP 8.4, sin SSH).
Frontend: `cd presentacion && VITE_BASE=/inf513/grupo05sa/proyecto2/ npm run build` (sale en `presentacion/dist/`).
El procedimiento completo y los pasos previos de la migración de la base compartida están en
[`P2_WEB.md`](P2_WEB.md) (§6 y pendientes): no migrar la base del servidor sin respaldo, sin detener el lector del P1
y sin el JAR nuevo del P1.

No subir a Git: `.env`, `vendor/`, `node_modules/`, `dist/`, respaldos ni credenciales.
