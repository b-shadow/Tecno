import { useMemo, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { go } from '../servicios/navigation'
import { useAuth } from '../servicios/auth'
import { Aviso, CabeceraPagina, Cargando, Etiqueta, Modal, Campo, bs, fecha, nombre, useAviso, useDatos } from '../componentes/ui'
import * as reportesApi from '../api/reportes'
import * as seguimientoApi from '../api/seguimiento'

const DIAS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const clave = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

/** Inicio del vendedor: su resumen y la agenda del mes (RF4.3), con acceso directo a cada ficha. */
export default function MiDia() {
  const { usuario } = useAuth()
  const [mes, setMes] = useState(() => { const d = new Date(); return new Date(d.getFullYear(), d.getMonth(), 1) })
  const [dia, setDia] = useState(clave(new Date()))
  const [completar, setCompletar] = useState(null)
  const aviso = useAviso()
  const stats = useDatos(async () => (await reportesApi.estadisticasVendedor()).data.estadisticas)
  const celdas = useMemo(() => {
    const inicio = new Date(mes)
    inicio.setDate(1 - ((mes.getDay() + 6) % 7))
    return Array.from({ length: 42 }, (_, i) => new Date(inicio.getFullYear(), inicio.getMonth(), inicio.getDate() + i))
  }, [mes])
  const agenda = useDatos(async () => (await seguimientoApi.recordatorios({ desde: clave(celdas[0]), hasta: clave(celdas[41]) })).data.recordatorios, [celdas])
  const porDia = useMemo(() => (agenda.datos || []).reduce((g, r) => {
    const k = clave(new Date(r.fecha_programada))
    return { ...g, [k]: [...(g[k] || []), r] }
  }, {}), [agenda.datos])
  const hoy = clave(new Date())
  const s = stats.datos

  return (
    <>
      <CabeceraPagina titulo={`Buen día, ${usuario?.nombre}`}>Sus actividades agendadas y el estado de su cartera.</CabeceraPagina>
      {s ? (
        <dl className="cifras" style={{ marginBottom: 'var(--e-5)' }}>
          <div><dt>Tarjetas abiertas</dt><dd>{s.abiertas}<small> de {s.tarjetas}</small></dd></div>
          <div><dt>Convertidos</dt><dd>{s.convertidos}</dd></div>
          <div><dt>Actividades pendientes</dt><dd>{s.actividades_pendientes}</dd></div>
          <div><dt>Contactos este mes</dt><dd>{s.interacciones_mes}</dd></div>
          <div><dt>Comisión por cobrar</dt><dd className="cifra">{bs(s.comision_pendiente)}</dd></div>
        </dl>
      ) : <Cargando filas={1} />}
      <div className="rejilla-ancha">
        <section className="hoja">
          <header className="hoja-titulo">
            <h3 style={{ textTransform: 'capitalize' }}>{mes.toLocaleDateString('es-BO', { month: 'long', year: 'numeric' })}</h3>
            <div className="acciones">
              <button type="button" className="btn btn-texto btn-icono" aria-label="Mes anterior" onClick={() => setMes(new Date(mes.getFullYear(), mes.getMonth() - 1, 1))}><ChevronLeft size={18} /></button>
              <button type="button" className="btn btn-secundario" onClick={() => { const d = new Date(); setMes(new Date(d.getFullYear(), d.getMonth(), 1)); setDia(hoy) }}>Hoy</button>
              <button type="button" className="btn btn-texto btn-icono" aria-label="Mes siguiente" onClick={() => setMes(new Date(mes.getFullYear(), mes.getMonth() + 1, 1))}><ChevronRight size={18} /></button>
            </div>
          </header>
          <div className="hoja-cuerpo">
            <div className="calendario">
              {DIAS.map((d) => <div key={d} className="dia-nombre">{d}</div>)}
              {celdas.map((d) => {
                const k = clave(d)
                const items = porDia[k] || []
                return (
                  <button key={k} type="button" className={`${d.getMonth() !== mes.getMonth() ? 'fuera' : ''} ${k === hoy ? 'hoy' : ''}`} aria-pressed={k === dia} aria-label={`${d.toLocaleDateString('es-BO')}: ${items.length} actividades`} onClick={() => setDia(k)}>
                    <span className="n">{d.getDate()}</span>
                    <span className="marcas">{items.slice(0, 6).map((r) => <i key={r.nro_recordatorio} className={r.estado === 'Atrasada' ? 'atrasada' : ''} />)}</span>
                  </button>
                )
              })}
            </div>
          </div>
        </section>
        <section className="hoja">
          <header className="hoja-titulo"><h3>{new Date(`${dia}T12:00:00`).toLocaleDateString('es-BO', { weekday: 'long', day: 'numeric', month: 'long' })}</h3></header>
          <div className="hoja-cuerpo">
            {agenda.error && <Aviso tipo="error">{agenda.error}</Aviso>}
            {!(porDia[dia] || []).length ? <p style={{ color: 'var(--tinta-suave)' }}>Sin actividades este día.</p> : (
              <ol className="historial">
                {porDia[dia].map((r) => (
                  <li key={r.nro_recordatorio}>
                    <span className="tipo">{fecha(r.fecha_programada, true).split(' ').pop()} · <Etiqueta estado={r.estado} /></span>
                    <p><a href="#" onClick={(e) => { e.preventDefault(); go(`/agenda?interes=${r.nro_tarjeta}`) }}>{nombre(r.interes?.prospecto)}</a>: {r.descripcion}</p>
                    {['Pendiente', 'Atrasada'].includes(r.estado) && <small><button type="button" className="btn btn-texto" onClick={() => setCompletar({ r, resultado: '' })}>Marcar realizada</button></small>}
                  </li>
                ))}
              </ol>
            )}
          </div>
        </section>
      </div>
      {completar && (
        <Modal titulo="Marcar actividad como realizada" descripcion={completar.r.descripcion} onCerrar={() => setCompletar(null)}
          pie={<div className="acciones"><button type="button" className="btn btn-secundario" onClick={() => setCompletar(null)}>Cancelar</button><button type="button" className="btn btn-primario" disabled={completar.resultado.trim().length < 3} onClick={async () => {
            try { aviso.ok((await seguimientoApi.completarRecordatorio(completar.r.nro_recordatorio, completar.resultado)).data.mensaje); setCompletar(null); agenda.recargar(); stats.recargar() } catch (e) { aviso.error(e) }
          }}>Guardar</button></div>}>
          {new Date(completar.r.fecha_programada) > new Date() && <Aviso>Estaba agendada para el {fecha(completar.r.fecha_programada, true)}. ¿Está seguro de que ya se realizó?</Aviso>}
          <Campo etiqueta="Resultado" requerido><textarea value={completar.resultado} onChange={(e) => setCompletar({ ...completar, resultado: e.target.value })} /></Campo>
        </Modal>
      )}
      {aviso.nodo}
    </>
  )
}
