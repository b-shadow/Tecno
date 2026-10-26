import { refreshSession } from '../servicios/auth'
import { Aviso, CabeceraPagina, Cargando, useAviso, useDatos } from '../componentes/ui'
import * as seguridadApi from '../api/seguridad'

const NIVEL = { '': 'Sin acceso', lectura: 'Lectura', modificacion: 'Modificación', eliminacion: 'Eliminación' }

/**
 * Enunciado 2 y 4: matriz de acceso rol × recurso guardada en la BD. El menú de cada rol sale de aquí
 * y la API la aplica en cada ruta (middleware acceso). Cada nivel incluye a los anteriores.
 */
export default function Matriz() {
  const { datos, cargando, error, recargar } = useDatos(async () => (await seguridadApi.matriz()).data)
  const aviso = useAviso()
  if (cargando && !datos) return <Cargando filas={8} />
  if (error) return <Aviso tipo="error">{error}</Aviso>
  const valor = (rol, recurso) => datos.permisos.find((p) => p.rol === rol && p.recurso_codigo === recurso)?.acceso || ''

  async function cambiar(rol, recurso, acceso) {
    try {
      aviso.ok((await seguridadApi.asignar({ rol, recurso_codigo: recurso, acceso: acceso || null })).data.mensaje)
      recargar()
      refreshSession().catch(() => {})
    } catch (e) { aviso.error(e) }
  }

  return (
    <>
      <CabeceraPagina titulo="Matriz de acceso">Qué puede hacer cada rol en cada página. El cambio se aplica de inmediato en la API y en el menú del rol al volver a cargar.</CabeceraPagina>
      <div className="tabla-marco">
        <table className="tabla matriz">
          <thead><tr><th>Recurso (página)</th><th>CU</th>{datos.roles.map((r) => <th key={r.nombre} style={{ textTransform: 'capitalize' }}>{r.nombre}</th>)}</tr></thead>
          <tbody>
            {datos.recursos.map((rec) => (
              <tr key={rec.codigo}>
                <td><strong>{rec.nombre}</strong><br /><small className="cifra" style={{ color: 'var(--tinta-suave)' }}>{rec.ruta}</small></td>
                <td className="cu">{rec.caso_uso}</td>
                {datos.roles.map((r) => (
                  <td key={r.nombre}>
                    <select className="control" aria-label={`Acceso de ${r.nombre} a ${rec.nombre}`} value={valor(r.nombre, rec.codigo)}
                      disabled={r.nombre === 'administrador' && ['matriz', 'usuarios'].includes(rec.codigo)}
                      onChange={(e) => cambiar(r.nombre, rec.codigo, e.target.value)}>
                      {Object.entries(NIVEL).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                    </select>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {aviso.nodo}
    </>
  )
}
