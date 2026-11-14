import { useMemo, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { go } from '../servicios/navigation'
import { useAuth } from '../servicios/auth'
import { Aviso, CabeceraPagina, Cargando, Etiqueta, Modal, Campo, bs, fecha, hora, nombre, useAviso, useDatos, HISTORIAL } from '../componentes/ui'
import * as reportesApi from '../api/reportes'
import * as seguimientoApi from '../api/seguimiento'

const DIAS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const clave = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

/** Inicio del vendedor: su resumen y la agenda del mes (RF4.3), con acceso directo a cada ficha. */
export default function PMiDia() {
  const { usuario } = useAuth()
  const [mes, setMes] = useState(() => { const d = new Date(); return new Date(d.getFullYear(), d.getMonth(), 1) })
  const [dia, setDia] = useState(clave(new Date()))
  const [completar, setCompletar] = useState(null)
  const aviso = useAviso()
  const stats = useDatos(async () => (await reportesApi.estadisticasVendedor()).data.estadisticas, [], { intervaloMs: 5000, refrescarAlEnfocar: true })
  const celdas = useMemo(() => {
    const inicio = new Date(mes)
    inicio.setDate(1 - ((mes.getDay() + 6) % 7))
    return Array.from({ length: 42 }, (_, i) => new Date(inicio.getFullYear(), inicio.getMonth(), inicio.getDate() + i))
  }, [mes])
  const agenda = useDatos(async () => (await seguimientoApi.recordatorios({ desde: clave(celdas[0]), hasta: clave(celdas[41]) })).data.recordatorios, [celdas], { intervaloMs: 5000, refrescarAlEnfocar: true })
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
        <dl className="cifras mb-6">
          <div><dt>Tarjetas abiertas</dt><dd>{s.abiertas}<small> de {s.tarjetas}</small></dd></div>
          <div><dt>Convertidos</dt><dd>{s.convertidos}</dd></div>
          <div><dt>Actividades pendientes</dt><dd>{s.actividades_pendientes}</dd></div>
          <div><dt>Contactos este mes</dt><dd>{s.interacciones_mes}</dd></div>
          <div><dt>Comisión por cobrar</dt><dd className="tabular-nums">{bs(s.comision_pendiente)}</dd></div>
        </dl>
      ) : <Cargando filas={1} />}
      <div className="grid grid-cols-[minmax(0,3fr)_minmax(0,2fr)] gap-6 max-movil:grid-cols-1">
        <section className="hoja">
          <header className="hoja-titulo">
            <h3 className="capitalize">{mes.toLocaleDateString('es-BO', { month: 'long', year: 'numeric' })}</h3>
            <div className="acciones">
              <button type="button" className="btn btn-texto btn-icono" aria-label="Mes anterior" onClick={() => setMes(new Date(mes.getFullYear(), mes.getMonth() - 1, 1))}><ChevronLeft size={18} /></button>
              <button type="button" className="btn btn-secundario" onClick={() => { const d = new Date(); setMes(new Date(d.getFullYear(), d.getMonth(), 1)); setDia(hoy) }}>Hoy</button>
              <button type="button" className="btn btn-texto btn-icono" aria-label="Mes siguiente" onClick={() => setMes(new Date(mes.getFullYear(), mes.getMonth() + 1, 1))}><ChevronRight size={18} /></button>
            </div>
          </header>
          <div className="hoja-cuerpo">
            <div className="grid grid-cols-7 overflow-hidden rounded-hoja border border-filete bg-papel">
              {DIAS.map((d) => <div key={d} className="border-b border-filete bg-niebla-2 p-2 text-center text-xs font-bold text-tinta-suave">{d}</div>)}
              {celdas.map((d) => {
                const k = clave(d)
                const items = porDia[k] || []
                return (
                  <button key={k} type="button" className={`grid min-h-[76px] content-start gap-1 border-r border-b border-filete px-2 py-1.5 text-left nth-[7n]:border-r-0 aria-pressed:shadow-[inset_0_0_0_2px_var(--acento)] max-movil:min-h-[52px] ${d.getMonth() !== mes.getMonth() ? 'bg-niebla-2 text-tinta-suave' : 'bg-papel'}`} aria-pressed={k === dia} aria-label={`${d.toLocaleDateString('es-BO')}: ${items.length} actividades`} onClick={() => setDia(k)}>
                    <span className={`grid size-[26px] place-items-center text-sm font-bold tabular-nums ${k === hoy ? 'rounded-full bg-navy text-white dark:bg-acento dark:text-sobre-acento' : ''}`}>{d.getDate()}</span>
                    <span className="flex flex-wrap gap-[3px]">{items.slice(0, 6).map((r) => <i key={r.nro_recordatorio} className={`size-2 rounded-full ${r.estado === 'Atrasada' ? 'bg-aviso' : 'bg-acento'}`} />)}</span>
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
            {!(porDia[dia] || []).length ? <p className="text-tinta-suave">Sin actividades este día.</p> : (
              <ol className={HISTORIAL.lista}>
                {porDia[dia].map((r) => (
                  <li key={r.nro_recordatorio} className={HISTORIAL.item}>
                    <span className={HISTORIAL.tipo}>{hora(r.fecha_programada)} · <Etiqueta estado={r.estado} /></span>
                    <p className={HISTORIAL.texto}><a href="#" onClick={(e) => { e.preventDefault(); go(`/agenda?interes=${r.nro_tarjeta}`) }}>{nombre(r.interes?.prospecto)}</a>: {r.descripcion}</p>
                    {['Pendiente', 'Atrasada'].includes(r.estado) && <small className={HISTORIAL.nota}><button type="button" className="btn btn-texto" onClick={() => setCompletar({ r, resultado: '' })}>Marcar realizada</button></small>}
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
          {new Date(completar.r.fecha_programada)> new Date() && <Aviso>Estaba agendada para el {fecha(completar.r.fecha_programada, true)}. ¿Está seguro de que ya se realizó?</Aviso>}
          <Campo etiqueta="Resultado" requerido><textarea value={completar.resultado} onChange={(e) => setCompletar({ ...completar, resultado: e.target.value })} /></Campo>
        </Modal>
      )}
      {aviso.nodo}
    </>
  )
}
