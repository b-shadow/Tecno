import { cliente } from './cliente'

// ProspectoController (CU3).
export const index = (params) => cliente.get('/prospectos', { params })
export const store = (datos) => cliente.post('/prospectos', datos)
export const update = (documento, datos) => cliente.put(`/prospectos/${documento}`, datos)
export const importarCSV = (csv) => cliente.post('/prospectos/importar', { csv })
