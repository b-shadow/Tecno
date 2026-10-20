# CRM Comercial Educativo

Sistema de captacion y seguimiento comercial con roles de administrador, coordinador y vendedor.
Construido con Laravel, Inertia y Vue 3 en un unico proyecto dentro de `backend/`, con PostgreSQL.
Las paginas se sirven desde `routes/web.php`; Vue consume la API REST de `routes/api.php` mediante tokens Bearer.

## Funcionalidades

- Catalogo publico organizado por programas y modulos, con registro de interesados.
- Usuarios y permisos por rol; vendedores con acceso a su cartera asignada.
- Asignacion manual, reparto equitativo y reasignacion con historial de contactos.
- Agenda: contactos realizados, actividades futuras y registro de cumplimiento.
- Ordenes de pago, comprobantes, aprobacion por coordinacion y comisiones configurables.
- Alumnos inscritos, exportacion academica, reportes por vendedor y estadisticas.
- Interfaz adaptable a movil y escritorio, con modo claro y oscuro.

El catalogo externo usa datos simulados (`CatalogoExternoDemo`). El QR y los pagos son demostrativos;
no hay una pasarela bancaria integrada. La integracion academica real queda pendiente.

## Requisitos

- Docker con Compose para el entorno local; alternativamente PHP 8.3+, Composer, PostgreSQL y Node.js 22.12+.
- Las versiones exactas de las dependencias estan en `backend/composer.lock` y `backend/package-lock.json`.

## Desarrollo local con Docker

Desde la raiz del repositorio:

```sh
docker volume create tecno_postgres_data
docker compose up -d --build
```

El volumen externo `tecno_postgres_data` conserva la base entre reinicios. Crearlo es necesario en un equipo nuevo;
si ya existe, el comando no lo reemplaza. El contenedor de la aplicacion prepara `.env`, instala dependencias,
genera la clave cuando falta y ejecuta las migraciones.

- Aplicacion: http://localhost:8001 (catalogo en `/anuncios`, acceso interno en `/login`).
- Salud de la API: http://localhost:8001/api/health.
- PostgreSQL local: puerto 55432, base `crm_educativo`, usuario `crm_user`.
- Vite: puerto 5173, con recarga durante el desarrollo.

Las claves de PostgreSQL del Compose son valores de desarrollo. Las cuentas iniciales locales se crean
**solo en una base de pruebas o desarrollo** con:

```sh
docker compose exec app php artisan db:seed
```

El seeder define cuentas demostrativas; no usarlo en un despliegue publico. Crear cuentas propias y claves
unicas para produccion. Ninguna credencial del VPS o de la demo publicada forma parte del repositorio.

## Compilacion y despliegue

```sh
cd backend
npm ci
npm run build
composer install --no-dev --prefer-dist --optimize-autoloader
```

Publicar solamente `backend/public/` con Apache y PHP-FPM. Mantener el resto del proyecto fuera del directorio
publico, configurar `.env` a partir de `.env.production.example` y usar una base PostgreSQL independiente.
Configurar `APP_URL`, credenciales propias, `APP_KEY` y `APP_DEBUG=false`. Preparar permisos de escritura
solo en `storage/` y `bootstrap/cache/`, y ejecutar `php artisan migrate --force` tras respaldar la base.

Para una subruta, compilar con `CRM_ASSET_BASE` y ajustar `APP_URL` y `ASSET_URL`. Ejemplo para `/crm`:

```sh
CRM_ASSET_BASE=/crm/build/ npm run build
```

En PowerShell: `$env:CRM_ASSET_BASE='/crm/build/'; npm run build`.
Las rutas internas conservan el prefijo que publica Laravel. No subir `.env`, `public/hot`, dependencias locales,
sesiones ni respaldos a Git. El servidor de produccion debe usar los recursos compilados, sin Vite en desarrollo.

## Respaldos y migraciones

Los scripts `scripts/backup_postgres.ps1` y `scripts/restore_postgres.ps1` usan las herramientas de PostgreSQL.
Para el Compose local, indicar `-Port 55432`; suministrar la clave mediante `PGPASSWORD` o el mecanismo seguro
del cliente PostgreSQL. Los archivos de `backups/` estan excluidos de Git.

Las migraciones de normalizacion protegen las referencias historicas. Si encuentran ventas antiguas que no
pueden convertir automaticamente, se detienen para permitir su revision. No ejecutar `migrate:fresh` sobre una
base que tenga datos que se deban conservar.

## Verificacion

La auditoria completa usa Docker y una base desechable, separada de los datos de trabajo:

```sh
python scripts/qa_local.py start
python scripts/qa_local.py test
python scripts/qa_browsers.py
python scripts/qa_local.py stop
```

`qa_browsers.py` requiere descargar previamente
`docker pull mcr.microsoft.com/playwright:v1.64.1-noble`. La version de la imagen coincide con Playwright
en `backend/package-lock.json`. Ejecuta Chromium, Firefox y WebKit contra QA, con los tres roles,
anchos de 320, 390, 768 y 1280 pixeles y temas claro/oscuro. Comprueba navegacion, registro publico,
sesiones, permisos, errores JavaScript, recursos fallidos y desbordamientos. Las capturas y el resumen
quedan en `qa-artifacts/`, excluido de Git. WebKit cubre el motor; no sustituye una prueba en un iPhone real.

Las pruebas de API cubren carteras compartidas, CSV, actividades, sesiones revocadas, notificaciones,
comprobantes, pagos simultaneos, inscripciones, comisiones, reportes e integracion academica simulada.
No prueban cobros bancarios ni servicios externos reales: el catalogo y la integracion son de demostracion.

Los scripts Python usan solo la biblioteca estandar. Los dos primeros crean datos y requieren una base de
pruebas aislada, recien migrada y poblada con `DatabaseSeeder`; ejecutarlos en este orden:

```sh
python scripts/verificar_correcciones.py http://localhost:18001/api
python scripts/verificar_seguridad.py http://localhost:18001/api
```

El puerto 18001 es un ejemplo para una instancia de pruebas separada; no lo levanta el Compose de desarrollo.
No apuntar estos scripts a la demo ni a la base de trabajo. `scripts/verificar_integridad.sql` comprueba claves,
restricciones y relaciones con una transaccion de solo lectura y rollback.

Para revisar rutas y dependencias:

```sh
docker compose exec app php artisan route:list
docker compose exec app composer validate --no-check-publish
```

## Estructura

- `backend/app/`: controladores, modelos, servicios y control de acceso.
- `backend/resources/js/`: paginas Vue, componentes, estilos y cliente API.
- `backend/database/migrations/`: esquema versionado y normalizacion de datos.
- `backend/public/`: entrada web y recursos publicos del catalogo de demostracion.
- `scripts/`: respaldos, restauracion y verificaciones reproducibles.
