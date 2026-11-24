# Capa 1 · Presentación (React SPA)

React 18 + Vite + react-router-dom. Todo dato llega de la API REST de `negocio/` por `src/api/` (un módulo por
controlador; `api/cliente.js` es el único cliente HTTP). CSS propio en `src/estilos/`, sin estilos en línea.

- Desarrollo: `npm ci && npm run dev` (http://localhost:5173; `/api` se reenvía a `VITE_API_PROXY`, por defecto :8001).
- Facultad: `VITE_BASE=/inf513/grupo05sa/proyecto2/ npm run build` → `dist/`.

Instalación, pruebas y despliegue: [README del repositorio](../README.md).
