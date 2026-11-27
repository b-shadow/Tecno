import { cliente } from './cliente'

// SitioController: contador de visitas (enunciado 7) y búsqueda global (enunciado 9).
export const visita = (ruta) => cliente.post('/visitas', { ruta })
export const buscar = (q) => cliente.get('/buscar', { params: { q } })
