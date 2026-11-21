import { useState } from 'react'
import { Send, School } from 'lucide-react'
import { api, descargarCsv } from '../services/api'
import { puede, useAuth } from '../services/auth'
import { Aviso, Boton, CabeceraPagina, Cargando, Etiqueta, Vacio, bs, fecha, nombre, useAviso, useDatos } from '../components/ui'

/** CU6: matrículas confirmadas y su envío al sistema académico (SIS del Grupo 06), hoy como CSV con constancia. */
export default function Matriculas() {
  const sesion = useAuth()
  const editable = puede('alumnos', 'modificacion', sesion)
  const inscripciones = useDatos(async () => (await api.get('/inscripciones')).data.inscripciones)
  const pendientes = useDatos(async () => (await api.get('/exportaciones/pendientes')).data)
  const [enviando, setEnviando] = useState(false)
  const aviso = useAviso()

  async function exportar() {
    setEnviando(true)
    try {
      const { data } = await api.post('/exportaciones')
      descargarCsv(data.archivo, data.filas)
      aviso.ok(data.mensaje)
      inscripciones.recargar()
      pendientes.recargar()
    } catch (e) { aviso.error(e) } finally { setEnviando(false) }
  }
  async function resultado(exp, estado) {
    try { aviso.ok((await api.patch(`/exportaciones/${exp.nro_exportacion}`, { estado })).data.mensaje); inscripciones.recargar() } catch (e) { aviso.error(e) }
  }

  return (
    <>
      <CabeceraPagina titulo="Matrículas y SIS" acciones={editable && <Boton cargando={enviando} disabled={!pendientes.datos?.total} onClick={exportar}><Send size={16} /> Exportar {pendientes.datos?.total || 0} pendiente(s)</Boton>}>
        Alumnos matriculados por el CRM. La exportación genera el CSV para el sistema académico y registra el envío.
      </CabeceraPagina>
      {inscripciones.error && <Aviso tipo="error">{inscripciones.error}</Aviso>}
      {inscripciones.cargando && !inscripciones.datos ? <Cargando /> : !inscripciones.datos?.length ? <Vacio titulo="Todavía no hay matrículas" icono={School}>Aparecen al aprobar la primera cuota de un prospecto con datos completos.</Vacio> : (
        <div className="tabla-marco">
          <table className="tabla">
            <thead><tr><th>Alumno</th><th>Módulo</th><th className="num">Precio</th><th>Vendedor</th><th>Confirmación</th><th>Envío al SIS</th></tr></thead>
            <tbody>
              {inscripciones.datos.map((i) => {
                const s = i.solicitud_compra
                const exp = i.exportaciones?.[i.exportaciones.length - 1]
                return (
                  <tr key={i.nro_solicitud}>
                    <td><strong>{nombre(s.orden_pago.interes.prospecto)}</strong><br /><small className="cifra">CI {s.orden_pago.interes.prospecto.documento}</small></td>
                    <td>{s.modulo_nombre}<br /><small style={{ color: 'var(--tinta-suave)' }}>{s.programa_nombre}</small></td>
                    <td className="num">{bs(s.precio_acordado)}</td>
                    <td>{nombre(s.orden_pago.vendedor)}</td>
                    <td className="cifra">{fecha(i.fecha_confirmacion)}</td>
                    <td>
                      {exp ? <div className="acciones" style={{ justifyContent: 'flex-start' }}>
                        <Etiqueta estado={exp.estado} />
                        {editable && exp.estado === 'exportada' && <>
                          <button type="button" className="btn btn-texto" onClick={() => resultado(exp, 'recibida')}>Marcar recibida</button>
                          <button type="button" className="btn btn-texto" onClick={() => resultado(exp, 'error')}>Con error</button>
                        </>}
                      </div> : <Etiqueta estado="Pendiente">Pendiente</Etiqueta>}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
      {aviso.nodo}
    </>
  )
}
