# CRM Comercial Educativo

Base tecnica de Fase 0 para el Sistema CRM Comercial Educativo.

## Stack obligatorio

- Backend: Laravel PHP
- Frontend: Vue.js
- Base de datos: PostgreSQL
- Arquitectura: Modular + MVC

## Modulos preparados

1. Seguridad y acceso
2. Gestion academica comercial
3. Captacion, compras y pagos
4. Seguimiento comercial
5. Reportes, comunicacion e integracion

## Ejecucion local

1. Iniciar PostgreSQL:

```powershell
docker compose up -d postgres
```

2. Iniciar backend:

```powershell
.\.tools\php\php.exe .\backend\artisan serve --host=127.0.0.1 --port=8001
```

3. Iniciar frontend:

```powershell
cd frontend
npm run dev
```

## Endpoints base

- Backend: http://localhost:8001
- API salud: http://localhost:8001/api/health
- Frontend: http://localhost:5173

## Navegacion publica e interna

- Visitantes: ingresan a `/anuncios`, ven cursos disponibles y realizan el flujo completo de solicitud, registro de interes, pago y envio de comprobante sin sidebar.
- Acceso interno: el boton superior derecho `Iniciar sesion` abre `/login`; al autenticarse se habilita el sidebar y las vistas internas.
- Sidebar interno: puede ocultarse/mostrarse desde el boton del encabezado.
- Tema visual: el encabezado incluye cambio manual entre modo claro y modo oscuro.

## Fase 1: Seguridad y usuarios

Credenciales iniciales:

- Correo: admin@crm-educativo.local
- Contrasena: Admin12345

Endpoints implementados:

- POST /api/login
- GET /api/me
- POST /api/logout
- GET /api/usuarios
- POST /api/usuarios
- PUT /api/usuarios/{id}
- PATCH /api/usuarios/{id}/estado

Reglas aplicadas:

- Solo usuarios activos pueden iniciar sesion.
- Las contrasenas se almacenan cifradas.
- La administracion de usuarios queda restringida al rol administrador.
- La desactivacion de un usuario invalida sus tokens activos.

## Fase 2: Catalogo academico comercial

Rutas frontend:

- /anuncios
- /programas
- /modulos
- /cursos
- /gestion-anuncios

Endpoints implementados:

- GET /api/ofertas
- GET /api/ofertas/{id}
- GET /api/programas
- POST /api/programas
- PUT /api/programas/{id}
- GET /api/modulos
- POST /api/modulos
- PUT /api/modulos/{id}
- GET /api/cursos
- POST /api/cursos
- PUT /api/cursos/{id}
- GET /api/anuncios
- POST /api/anuncios
- PUT /api/anuncios/{id}

Reglas aplicadas:

- Administrador y coordinador gestionan el catalogo.
- Vendedor no puede administrar catalogo.
- El tablon publico no requiere autenticacion.
- Solo anuncios publicados con curso, modulo y programa activos aparecen en ofertas.
- Programas, modulos, cursos y anuncios conservan estado para activar/desactivar o publicar/despublicar.

## Fase 3: Registro comercial y prospectos

Rutas frontend:

- /anuncios: anuncios publicos, registro de interes, generacion de pago y envio de comprobante en un solo flujo.
- /prospectos: gestion interna de cartera comercial e importacion CSV.

Endpoints implementados:

- POST /api/registro-interes
- GET /api/prospectos
- POST /api/prospectos
- PUT /api/prospectos/{id}
- PATCH /api/prospectos/{id}/asignar
- PATCH /api/prospectos/{id}/estado
- POST /api/prospectos/importar
- POST /api/intereses
- GET /api/intereses/{prospecto}
- POST /api/solicitudes-compra

Reglas aplicadas:

- El registro publico crea prospecto, interes y solicitud de compra inicial.
- Se bloquean duplicados por documento o correo.
- Un prospecto puede tener varios intereses.
- Coordinador y administrador pueden importar CSV y asignar vendedores.
- Vendedor solo visualiza prospectos asignados.
- Estados comerciales disponibles: Nuevo, Contactado, Interesado, En proceso, Convertido, Perdido.

## Fase 4: Gestion de pagos

Rutas frontend:

- /anuncios: generacion publica de pago QR y envio de comprobante dentro de la solicitud del curso.
- /validacion-pagos: revision interna de pagos por administrador/coordinador.

Endpoints implementados:

- POST /api/pagos/generar
- GET /api/pagos
- GET /api/pagos/{id}
- POST /api/comprobantes
- GET /api/comprobantes/{pago}
- PATCH /api/pagos/{id}/aprobar
- PATCH /api/pagos/{id}/rechazar
- GET /api/solicitudes-compra

Estados de pago:

- Pendiente de pago
- En revision
- Pago aprobado
- Pago rechazado

Reglas aplicadas:

- Cada solicitud de compra genera un pago unico.
- El comprobante cambia el pago a En revision.
- Solo administrador y coordinador pueden aprobar o rechazar pagos.
- No se aprueban pagos sin comprobante.
- Un pago aprobado no puede recibir nuevos comprobantes.

## Fase 5: Seguimiento comercial

Rutas frontend:

- /seguimiento: interacciones, recordatorios, confirmacion de inscripcion y comisiones.

Endpoints implementados:

- GET /api/prospectos/{id}/interacciones
- POST /api/interacciones
- GET /api/recordatorios
- POST /api/recordatorios
- PATCH /api/recordatorios/{id}/completar
- PATCH /api/recordatorios/{id}/cancelar
- POST /api/inscripciones/confirmar
- GET /api/inscripciones
- GET /api/comisiones

Reglas aplicadas:

- Las interacciones conservan historial por prospecto y usuario.
- Los recordatorios usan estados Pendiente, Completado y Cancelado.
- Vendedor solo opera prospectos asignados y consulta su informacion.
- Solo administrador y coordinador confirman inscripciones comerciales.
- Solo pagos aprobados permiten confirmar inscripcion.
- Confirmar una inscripcion marca el prospecto como Convertido.
- La comision se calcula automaticamente como 1% del monto pagado.

## Fase 6: Reportes, comunicacion e integracion

Rutas frontend:

- /reportes: dashboard administrativo, comercial y metricas personales.
- /reportes-comerciales: reporte comercial enfocado en coordinacion.
- /estadisticas-vendedor: rendimiento individual del vendedor.
- /notificaciones: envio y consulta de comunicaciones.
- /exportaciones: preparacion, exportacion e historial academico.

Endpoints implementados:

- GET /api/reportes/administrativos
- GET /api/reportes/comerciales
- GET /api/estadisticas/vendedor
- POST /api/notificaciones/enviar
- GET /api/notificaciones
- PATCH /api/notificaciones/{id}/leida
- GET /api/exportaciones/preparar
- POST /api/exportaciones/academico
- PATCH /api/exportaciones/{id}
- GET /api/exportaciones

Reglas aplicadas:

- Administrador consulta reportes administrativos completos con filtros por fecha, programa, curso y estado.
- Administrador y coordinador consultan reportes comerciales y gestionan exportaciones.
- Vendedor consulta solo sus estadisticas personales.
- Las notificaciones se registran, se envian por el mailer configurado y pueden marcarse como leidas.
- La exportacion academica solo toma prospectos convertidos con pago aprobado e inscripcion comercial confirmada.
- Cada exportacion conserva usuario responsable, prospecto, fecha, estado y respuesta/payload para auditoria.

## Fase 7: Integracion y cierre

Documentacion final:

- docs/GUIA_TECNICA.md
- docs/GUIA_USUARIO.md
- docs/GUIA_DESPLIEGUE.md

Preparacion produccion:

- backend/.env.production.example
- frontend/.env.production.example
- scripts/backup_postgres.ps1
- scripts/restore_postgres.ps1

Validaciones realizadas:

- Flujo comercial completo cubierto por pruebas de integracion.
- Seguridad de login, rutas protegidas, usuario inactivo y permisos por rol.
- Catalogo, prospectos, pagos, seguimiento, reportes, notificaciones y exportaciones integrados.
- Errores API normalizados con mensajes JSON amigables.
- Indices agregados para consultas frecuentes de pagos, solicitudes, seguimiento, notificaciones y exportaciones.

Comandos de cierre:

```powershell
cd backend
..\.tools\php\php.exe artisan test
cd ..\frontend
npm run build
```
