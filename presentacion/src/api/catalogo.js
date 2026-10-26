import { cliente } from './cliente'

// CatalogoController y registro público de interés (CU2).
export const programas = () => cliente.get('/catalogo')
export const sincronizar = () => cliente.post('/catalogo/sincronizar')
export const registrarInteres = (datos) => cliente.post('/registro-interes', datos)
