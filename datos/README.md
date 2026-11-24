# Capa 3 · Datos (paquete `grupo05sa/datos`)

Única capa que habla con PostgreSQL (`db_grupo05sa.public`, compartida con el P1):

- `src/Repositorios/`: consultas, escrituras y transacciones que usan los Services de `negocio/`.
- `src/Modelos/`: una entidad Eloquent por tabla, con la clave del diseño (sin `id` extra).
- `migraciones/`: tablas, claves, triggers (`contar_visita`, cuotas, movimientos del embudo) y datos del menú dinámico.
  Las carga `DatosServiceProvider`; el control de migraciones vive en el esquema `laravel` (`php artisan crm:preparar-bd`).
- `semillas/`: datos de demostración, solo para una base local.

Instalación, pruebas y despliegue: [README del repositorio](../README.md).
