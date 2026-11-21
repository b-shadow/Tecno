# UNEXO — CRM Comercial Educativo (INF513 · Proyecto 2 · Grupo 05 SA)

Sistema web de captación y seguimiento comercial para una institución que vende programas de formación (programas
de varios módulos y módulos sueltos). Arquitectura de 3 capas pedida por el enunciado: **React** (cliente) +
**Laravel API REST** + **PostgreSQL**, sobre la **misma base que el Proyecto 1** (`db_grupo05sa`, esquema `public`).

- Qué exige el docente, cómo se cumple, estado y pendientes del equipo: **[`P2_WEB.md`](P2_WEB.md)** (leer primero).
- Producto y usuarios: [`PRODUCT.md`](PRODUCT.md). Sistema visual (tokens, temas, componentes): [`DESIGN.md`](DESIGN.md).

## Stack

| Capa | Tecnología | Dónde |
|---|---|---|
| Cliente | React 18 + `@inertiajs/react` (solo como enrutador de páginas), axios, Chart.js, lucide-react | `backend/resources/js/` |
| API | Laravel 13, token propio (`api_tokens`, middleware `auth.token`), matriz de acceso (`acceso:recurso,nivel`) | `backend/routes/api.php`, `backend/app/` |
| Datos | PostgreSQL; tablas creadas por migraciones con las claves del diseño (sin `id`); control de migraciones en el esquema `laravel` | `backend/database/migrations/` |

Estilos: CSS propio en archivos aparte (`backend/resources/js/styles/`: `tokens.css`, `base.css`, `layout.css`,
`components.css`, `catalogo.css`, `panel.css`). Fuentes alojadas en el sitio (sin CDN).

## Levantar el entorno local (Docker)

Requisitos: Docker con Compose y Node.js 22.12+ (para compilar el frontend en el equipo).

```sh
docker volume create tecno_postgres_data     # solo la primera vez en un equipo nuevo
docker compose up -d --build                 # app en http://localhost:8001
docker compose exec app php artisan db:seed  # datos de demostración (SOLO en local)
cd backend && npm ci && npm run build        # compila React a public/build
```

El contenedor `app` crea `.env` si falta, instala dependencias, genera `APP_KEY`, ejecuta
`php artisan crm:preparar-bd` (esquema `laravel`) y `php artisan migrate --force`.

- Catálogo público: http://localhost:8001/anuncios · Login: http://localhost:8001/login · Salud: `/up` y `/api/salud`.
- PostgreSQL local: puerto 55432, base `db_grupo05sa`, usuario `crm_user` (clave de desarrollo del Compose).
- Cuentas de demostración (las crea el seeder, solo en local): `admin@crm-educativo.local`, `coord@test.local`,
  `vendedor.demo@crm-educativo.local`; las claves están en `backend/database/seeders/DatabaseSeeder.php`.
  **Nunca** correr `db:seed` en el servidor de la facultad: allí se crean cuentas propias.

## Estructura

- `backend/routes/api.php`: las ~70 rutas de la API; cada ruta de negocio lleva `acceso:<recurso>,<nivel>`.
- `backend/routes/web.php`: qué página React sirve cada URL (`/anuncios`, `/login`, `/embudo`, `/agenda`…).
- `backend/app/Http/Controllers/Api/`: un controlador por área (Auth, Usuarios, Seguridad, Catálogo, Prospectos,
  Intereses, Pagos, Seguimiento, Reportes, Exportación, Notificaciones, Sitio).
- `backend/app/Services/`: `Acceso` (matriz y menú), `Alcance` (vendedor: su cartera; coordinador: sus programas),
  `Conversion` (matrícula al aprobar la 1.ª cuota), `Fotos` (nombres legibles), `CatalogoExternoDemo` (API simulada del Grupo 06).
- `backend/app/Models/`: un modelo por tabla, con `$primaryKey`/`$keyType`/`$incrementing` del diseño.
- `backend/database/migrations/`: `000001` esquema compartido con el P1 · `000002` estados RF3.2 · `000003` recursos y
  permisos (menú dinámico) · `000004` bitácora + trigger de visitas · `000005` métodos de pago y cuotas · `000006` foto de usuario.
- `backend/resources/js/Pages/`: una página por pantalla (Catalogo, Login, Dashboard, MiDia, Embudo, Agenda, …).
- `backend/resources/js/layouts/AppShell.jsx`: plantilla base (público e interno) con el menú leído de la BD.
- `backend/lang/es/validation.php`: mensajes de validación en español.

Cambiar algo de punta a punta (p. ej. un campo nuevo): migración nueva → modelo (`$fillable`) → `validate()` del
controlador → página en `Pages/` → `npm run build`. Una pantalla nueva además necesita su fila en `recursos` y
`permisos` (migración) para aparecer en el menú.

## Pruebas (siempre contra la base local, nunca contra producción)

```sh
python scripts/verificar_p2.py                                   # 32 casos de la API (repetible)
QA_BASE=http://localhost:8001 QA_ENGINES=chromium node scripts/verificar_navegadores.mjs   # 321 casos: 3 roles × 4 anchos × 2 temas
node scripts/capturas_p2.mjs                                     # capturas de cada página por rol
```

En PowerShell: `$env:QA_BASE='http://localhost:8001'; $env:QA_ENGINES='chromium'; node scripts/verificar_navegadores.mjs`.
Firefox y WebKit necesitan `npx playwright install firefox webkit` (desde `backend/`).
`scripts/estructura_esquema.sql` resume el esquema para compararlo con `p1/sql/esquema.sql`.

## Despliegue

Servidor de la facultad: `https://www.tecnoweb.org.bo/inf513/grupo05sa/proyecto2` (Apache + PHP 8.4, sin SSH).
Compilar con `CRM_ASSET_BASE=/inf513/grupo05sa/proyecto2/build/ npm run build`. El procedimiento completo y los
pasos previos de la migración de la base compartida están en [`P2_WEB.md`](P2_WEB.md) (§6 y pendientes): no migrar la
base del servidor sin respaldo, sin detener el lector del P1 y sin el JAR nuevo del P1.

No subir a Git: `.env`, `vendor/`, `node_modules/`, `public/build`, `public/hot`, respaldos ni credenciales.
