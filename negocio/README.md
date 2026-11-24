# Capa 2 · Lógica de negocio (Laravel, API REST)

Solo API: no sirve páginas. Flujo de cada petición: `routes/api.php` → middleware `auth.token` y `acceso:` →
FormRequest (`app/Http/Requests`) → Controller (`app/Http/Controllers/Api`) → Service (`app/Services`) → repositorio
del paquete `grupo05sa/datos` (`../datos`, capa 3).

Instalación, pruebas y despliegue: [README del repositorio](../README.md).
