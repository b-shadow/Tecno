import { useEffect, useMemo, useRef, useState } from 'react'
import { MessageCircle, NotebookTabs, Pencil } from 'lucide-react'
import { go, useAppRoute } from '../servicios/navigation'
import { puede, useAuth } from '../servicios/auth'
import { Aviso, Boton, Campo, Cargando, Etiqueta, Modal, Vacio, erroresDe, fecha, nombre, useAviso, useDatos, HISTORIAL } from '../componentes/ui'
import { apiErrorMessage } from '../servicios/errors'
import { ErrorBoundary } from '../componentes/ErrorBoundary'
import PagosProspecto from '../componentes/pagos/PagosProspecto'
import * as interesesApi from '../api/intereses'
import * as prospectosApi from '../api/prospectos'
import * as seguimientoApi from '../api/seguimiento'

const TIPOS = ['WhatsApp', 'Llamada', 'Correo electronico', 'Reunion', 'Nota comercial']
const TIPO_TEXTO = { 'Correo electronico': 'Correo electrónico', 'Reunion': 'Reunión' }

/** CU7 (historial, contactos, recordatorios) y CU6 (pagos y matrícula) sobre la ficha de cada tarjeta. */
export default function PAgenda() {
  const { query } = useAppRoute()
  const sesion = useAuth()
  const [buscar, setBuscar] = useState('')
  const [estado, setEstado] = useState('')
  const lista = useDatos(async () => (await interesesApi.index({ buscar: buscar || undefined, estado: estado || undefined })).data, [buscar, estado], { intervaloMs: 3000, refrescarAlEnfocar: true })
  const [sel, setSel] = useState(query.interes ? Number(query.interes) : null)
  const [enfocar, setEnfocar] = useState(0)

  useEffect(() => {
    if (query.interes) setSel(Number(query.interes))
  }, [query.interes])
  useEffect(() => {
    if (!sel && lista.datos?.intereses?.length) setSel(lista.datos.intereses[0].nro_tarjeta)
  }, [lista.datos, sel])

  return (
    <div className="grid grid-cols-[minmax(280px,360px)_minmax(0,1fr)] items-start gap-6 max-ficha:grid-cols-1">
      <aside className="hoja sticky top-21 flex max-h-[calc(100dvh-110px)] flex-col overflow-hidden max-ficha:static max-ficha:max-h-[360px]" aria-label="Tarjetas" id="lista-tarjetas">
        <div className="grid gap-2 border-b border-filete p-3">
          <input className="control" type="search" placeholder="Buscar prospecto o módulo…" aria-label="Buscar en mis tarjetas" value={buscar} onChange={(e) => setBuscar(e.target.value)} />
          <select className="control" aria-label="Filtrar por etapa" value={estado} onChange={(e) => setEstado(e.target.value)}>
            <option value="">Todas las etapas</option>
            {(lista.datos?.estados || []).map((e) => <option key={e}>{e}</option>)}
          </select>
        </div>
        {lista.cargando && !lista.datos ? <div className="p-3"><Cargando /></div> : (
          <ul className="overflow-y-auto p-1.5">
            {(lista.datos?.intereses || []).map((t) => (
              <li key={t.nro_tarjeta}>
                <button type="button" aria-current={t.nro_tarjeta === sel} onClick={() => {
                  setSel(t.nro_tarjeta)
                  window.history.replaceState(null, '', `?interes=${t.nro_tarjeta}`)
                  setEnfocar((n) => n + 1)
                }}
                  className="grid h-max w-full shrink-0 gap-0.5 rounded-ui px-3 py-2.5 text-left hover:bg-niebla-2 aria-[current=true]:bg-acento-suave aria-[current=true]:outline aria-[current=true]:-outline-offset-1 aria-[current=true]:outline-[color-mix(in_srgb,var(--acento-texto)_55%,transparent)]">
                  <strong className="font-[650]">{nombre(t.prospecto)}</strong>
                  <small className="text-xs text-tinta-suave">{t.modulo_nombre}</small>
                  <span><Etiqueta estado={t.estado} /></span>
                </button>
              </li>
            ))}
            {!lista.datos?.intereses?.length && <li><Vacio titulo="Sin tarjetas" icono={NotebookTabs}>No hay tarjetas con ese filtro.</Vacio></li>}
          </ul>
        )}
      </aside>
      {sel ? <Ficha key={sel} nro={sel} sesion={sesion} enfocar={enfocar} onCambio={lista.recargar} /> : <div className="hoja"><Vacio titulo="Elija una tarjeta">Su historial, agenda y pagos aparecen aquí.</Vacio></div>}
    </div>
  )
}

function Ficha({ nro, sesion, enfocar, onCambio }) {
  const { datos, cargando, error, recargar } = useDatos(async () => (await interesesApi.show(nro)).data, [nro], { intervaloMs: 5000, refrescarAlEnfocar: true })
  const fichaRef = useRef(null)
  const hayDatos = Boolean(datos)
  // En celular la ficha queda debajo de la lista: al elegir una tarjeta se lleva a la vista cuando ya cargó.
  useEffect(() => {
    if (enfocar && hayDatos && window.matchMedia('(max-width: 1100px)').matches) fichaRef.current?.scrollIntoView({ block: 'start' })
  }, [enfocar, hayDatos, nro])
  const [pestana, setPestana] = useState('historial')
  const [editar, setEditar] = useState(false)
  const aviso = useAviso()
  const actualizar = () => { recargar(); onCambio() }

  if (cargando && !datos) return <div className="hoja hoja-cuerpo"><Cargando filas={6} /></div>
  if (error) return <Aviso tipo="error">{error}</Aviso>
  const t = datos.interes
  const p = t.prospecto
  const esSuVendedor = t.vendedor_correo === sesion.usuario?.correo
  const editable = puede('agenda', 'modificacion', sesion) && !['Perdido'].includes(t.estado)
  const telefono = String(p.telefono || '').replace(/\D/g, '')

  return (
    <section ref={fichaRef} id="ficha-detalle" className="hoja" aria-label={`Ficha de ${nombre(p)}`}>
      <header className="grid grid-cols-[minmax(0,1fr)_auto] items-end gap-4 rounded-t-hoja bg-portada p-6 text-portada-tinta max-movil:grid-cols-1">
        <div>
          <h2 className="text-3xl">{nombre(p)}</h2>
          <p className="mt-1.5 text-portada-suave">{t.modulo_nombre} · {t.programa_nombre} · Tarjeta #{t.nro_tarjeta}</p>
        </div>
        <div className="acciones">
          <button type="button" className="btn btn-secundario hidden max-ficha:inline-flex" onClick={() => document.getElementById('lista-tarjetas')?.scrollIntoView({ block: 'start' })}>Volver a los interesados</button>
          <Etiqueta estado={t.estado} sobreOscuro />
          {telefono && <a className="btn btn-acento" href={`https://wa.me/591${telefono.slice(-8)}`} target="_blank" rel="noreferrer"><MessageCircle size={16} /> WhatsApp</a>}
        </div>
      </header>
      <dl className="my-4 grid grid-cols-[repeat(auto-fit,minmax(170px,1fr))] gap-x-6 gap-y-3 border-b border-filete px-6 py-4">
        <Dato titulo="Carnet" cifra>{p.documento}</Dato>
        <Dato titulo="Teléfono" cifra>{p.telefono}</Dato>
        <Dato titulo="Correo">{p.correo}</Dato>
        <Dato titulo="Origen">{p.origen}</Dato>
        <Dato titulo="Profesión · ciudad">{p.profesion || '—'} · {p.ubicacion || '—'}</Dato>
        <Dato titulo="Vendedor">{t.vendedor ? nombre(t.vendedor) : 'Sin asignar'}</Dato>
      </dl>
      <div className="hoja-cuerpo grid gap-4">
        {t.estado !== 'Convertido' && datos.faltantes_conversion?.length> 0 && (
          <Aviso>Para matricular falta: {datos.faltantes_conversion.join(' ')}</Aviso>
        )}
        {t.estado === 'Perdido' && <Aviso tipo="error">Perdido. Motivo: {t.motivo_perdida}{t.observacion ? ` — ${t.observacion}` : ''}</Aviso>}
        <div className="acciones justify-start">
          {editable && <button type="button" className="btn btn-secundario" onClick={() => setEditar(true)}><Pencil size={16} /> Editar datos</button>}
          <button type="button" className="btn btn-texto" onClick={() => go('/embudo')}>Ver en el embudo</button>
          {editable && t.estado !== 'Convertido' && datos.faltantes_conversion?.length === 0 && (
            <button type="button" className="btn btn-primario" onClick={async () => {
              try { aviso.ok((await interesesApi.mover(nro, { estado: 'Convertido' })).data.mensaje); actualizar() } catch (e) { aviso.error(e) }
            }}>Convertir a matrícula</button>
          )}
        </div>
        <div className="pestanas" role="tablist">
          {[['historial', 'Historial'], ['contacto', 'Registrar contacto'], ['agenda', 'Agendar'], ['pagos', 'Pagos']].map(([id, texto]) => (
            <button key={id} type="button" role="tab" aria-selected={pestana === id} onClick={() => setPestana(id)}>{texto}</button>
          ))}
        </div>
        {pestana === 'historial' && <Historial t={t} />}
        {pestana === 'contacto' && (editable ? <Contacto nro={nro} onListo={(m) => { aviso.ok(m); actualizar(); setPestana('historial') }} /> : <Aviso>Esta tarjeta ya está cerrada.</Aviso>)}
        {pestana === 'agenda' && <Recordatorios t={t} editable={editable} aviso={aviso} onCambio={actualizar} />}
        {pestana === 'pagos' && (
          <ErrorBoundary key={`pagos-${nro}`} nombreSeccion="módulo de pagos">
            <PagosProspecto t={t} esSuVendedor={esSuVendedor} editable={editable} aviso={aviso} onCambio={actualizar} />
          </ErrorBoundary>
        )}
      </div>
      {editar && <EditarProspecto p={p} onCerrar={() => setEditar(false)} onListo={(m) => { aviso.ok(m); setEditar(false); actualizar() }} />}
      {aviso.nodo}
    </section>
  )
}

/** RF4.1: historial cronológico, más reciente primero, numerado como índice. */
function Historial({ t }) {
  const eventos = useMemo(() => [
    ...t.movimientos.map((m) => ({ fecha: m.fecha, tipo: 'Cambio de etapa', texto: `${m.estado_anterior || 'Registro'} → ${m.estado_nuevo}`, quien: m.usuario, detalle: m.detalle })),
    ...t.interacciones.map((i) => ({ fecha: i.fecha, tipo: TIPO_TEXTO[i.tipo] || i.tipo, texto: i.descripcion, quien: i.usuario, detalle: i.resultado })),
    ...t.recordatorios.filter((r) => r.estado === 'Cancelado').map((r) => ({ fecha: r.updated_at, tipo: 'Actividad cancelada', texto: r.descripcion, quien: r.usuario })),
  ].sort((a, b) => new Date(b.fecha) - new Date(a.fecha)), [t])
  if (!eventos.length) return <Vacio titulo="Sin historial todavía">El primer contacto que registre aparecerá aquí.</Vacio>
  return (
    <ol className={HISTORIAL.lista}>
      {eventos.map((e, i) => (
        <li key={i} className={HISTORIAL.item}>
          <span className={HISTORIAL.tipo}>{e.tipo} · {fecha(e.fecha, true)}</span>
          <p className={HISTORIAL.texto}>{e.texto}</p>
          <small className={HISTORIAL.nota}>{e.quien ? nombre(e.quien) : 'Sistema'}{e.detalle ? ` · ${e.detalle}` : ''}</small>
        </li>
      ))}
    </ol>
  )
}

/** RF4.2: contacto ya ocurrido o nota manual. */
function Contacto({ nro, onListo }) {
  const [form, setForm] = useState({ tipo: 'WhatsApp', descripcion: '', resultado: '' })
  const [errores, setErrores] = useState({})
  const [enviando, setEnviando] = useState(false)
  async function guardar(e) {
    e.preventDefault()
    setEnviando(true)
    try {
      onListo((await seguimientoApi.registrarInteraccion(nro, form)).data.mensaje)
    } catch (err) {
      setErrores(erroresDe(err))
    } finally {
      setEnviando(false)
    }
  }
  return (
    <form className="grid gap-4 grid-cols-2 max-movil:grid-cols-1" onSubmit={guardar}>
      <Campo etiqueta="Medio" requerido><select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>{TIPOS.map((x) => <option key={x} value={x}>{TIPO_TEXTO[x] || x}</option>)}</select></Campo>
      <Campo etiqueta="Resultado" error={errores.resultado}><input maxLength={500} value={form.resultado} onChange={(e) => setForm({ ...form, resultado: e.target.value })} placeholder="Ej. Pidió el plan de cuotas" /></Campo>
      <div className="col-span-full"><Campo etiqueta="¿Qué pasó?" requerido error={errores.descripcion}><textarea required minLength={3} maxLength={2000} value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} placeholder="Ej. Se envió el PDF del diplomado por WhatsApp." /></Campo></div>
      <div className="acciones col-span-full"><Boton type="submit" cargando={enviando}>Registrar contacto</Boton></div>
    </form>
  )
}

/** RF4.3: actividades a futuro. Al marcarlas realizadas se pide el resultado y se avisa si es antes de lo agendado. */
function Recordatorios({ t, editable, aviso, onCambio }) {
  const [form, setForm] = useState({ fecha_programada: '', descripcion: '' })
  const [errores, setErrores] = useState({})
  const [completar, setCompletar] = useState(null)
  const pendientes = t.recordatorios.filter((r) => ['Pendiente', 'Atrasada'].includes(r.estado))
  async function agendar(e) {
    e.preventDefault()
    try {
      aviso.ok((await seguimientoApi.crearRecordatorio(t.nro_tarjeta, form)).data.mensaje)
      setForm({ fecha_programada: '', descripcion: '' })
      setErrores({})
      onCambio()
    } catch (err) {
      setErrores(erroresDe(err))
      aviso.error(err)
    }
  }
  return (
    <div className="grid gap-6">
      {editable && (
        <form className="grid gap-4 grid-cols-2 max-movil:grid-cols-1" onSubmit={agendar}>
          <Campo etiqueta="Fecha y hora" requerido error={errores.fecha_programada}><input type="datetime-local" required value={form.fecha_programada} onChange={(e) => setForm({ ...form, fecha_programada: e.target.value })} /></Campo>
          <Campo etiqueta="Actividad" requerido error={errores.descripcion}><input required minLength={3} maxLength={1000} placeholder="Ej. Llamar mañana a las 10:00" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} /></Campo>
          <div className="acciones col-span-full"><button type="submit" className="btn btn-primario">Agendar actividad</button></div>
        </form>
      )}
      <div>
        <h4 className="mb-2">Pendientes</h4>
        {!pendientes.length ? <p className="text-tinta-suave">No hay actividades pendientes.</p> : (
          <div className="tabla-marco"><table className="tabla"><thead><tr><th>Fecha</th><th>Actividad</th><th>Estado</th><th /></tr></thead><tbody>
            {pendientes.map((r) => (
              <tr key={r.nro_recordatorio}>
                <td className="tabular-nums">{fecha(r.fecha_programada, true)}</td><td>{r.descripcion}</td><td><Etiqueta estado={r.estado} /></td>
                <td className="acciones">{editable && <>
                  <button type="button" className="btn btn-secundario" onClick={() => setCompletar({ r, resultado: '' })}>Marcar realizada</button>
                  <button type="button" className="btn btn-texto" onClick={async () => { try { aviso.ok((await seguimientoApi.cancelarRecordatorio(r.nro_recordatorio)).data.mensaje); onCambio() } catch (e) { aviso.error(e) } }}>Cancelar</button>
                </>}</td>
              </tr>
            ))}
          </tbody></table></div>
        )}
      </div>
      {completar && (
        <Modal titulo="Marcar actividad como realizada" descripcion={completar.r.descripcion} onCerrar={() => setCompletar(null)}
          pie={<div className="acciones"><button type="button" className="btn btn-secundario" onClick={() => setCompletar(null)}>Cancelar</button><button type="button" className="btn btn-primario" disabled={completar.resultado.trim().length < 3} onClick={async () => {
            try { aviso.ok((await seguimientoApi.completarRecordatorio(completar.r.nro_recordatorio, completar.resultado)).data.mensaje); setCompletar(null); onCambio() } catch (e) { aviso.error(e) }
          }}>Guardar</button></div>}>
          {new Date(completar.r.fecha_programada)> new Date() && <Aviso>Estaba agendada para el {fecha(completar.r.fecha_programada, true)}. ¿Está seguro de que ya se realizó?</Aviso>}
          <Campo etiqueta="Resultado" requerido ayuda="Queda en el historial con la fecha de hoy."><textarea value={completar.resultado} onChange={(e) => setCompletar({ ...completar, resultado: e.target.value })} /></Campo>
        </Modal>
      )}
    </div>
  )
}

function EditarProspecto({ p, onCerrar, onListo }) {
  const [form, setForm] = useState({ nombre: p.nombre, apellido: p.apellido, correo: p.correo, telefono: p.telefono, profesion: p.profesion || '', ubicacion: p.ubicacion || '', origen: p.origen })
  const [errores, setErrores] = useState({})
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })
  async function guardar(e) {
    e.preventDefault()
    try { onListo((await prospectosApi.update(p.documento, form)).data.mensaje) } catch (err) { setErrores({ ...erroresDe(err), general: apiErrorMessage(err) }) }
  }
  return (
    <Modal titulo="Editar datos del prospecto" descripcion={`CI ${p.documento}`} onCerrar={onCerrar}>
      <form className="grid gap-4 grid-cols-2 max-movil:grid-cols-1" onSubmit={guardar}>
        <Campo etiqueta="Nombre" requerido error={errores.nombre}><input required maxLength={120} value={form.nombre} onChange={set('nombre')} /></Campo>
        <Campo etiqueta="Apellido" requerido error={errores.apellido}><input required maxLength={120} value={form.apellido} onChange={set('apellido')} /></Campo>
        <Campo etiqueta="Correo" requerido error={errores.correo}><input type="email" required value={form.correo} onChange={set('correo')} /></Campo>
        <Campo etiqueta="Teléfono" requerido error={errores.telefono}><input required pattern="\+?[0-9 ]{7,20}" title="Entre 7 y 20 dígitos." value={form.telefono} onChange={set('telefono')} /></Campo>
        <Campo etiqueta="Profesión" error={errores.profesion}><input maxLength={120} value={form.profesion} onChange={set('profesion')} /></Campo>
        <Campo etiqueta="Ciudad" error={errores.ubicacion}><input maxLength={160} value={form.ubicacion} onChange={set('ubicacion')} /></Campo>
        <Campo etiqueta="Origen" requerido><select value={form.origen} onChange={set('origen')}>{['Facebook', 'Instagram', 'TikTok', 'WhatsApp', 'Referido', 'Web', 'Correo', 'Feria', 'Otro'].map((o) => <option key={o}>{o}</option>)}</select></Campo>
        {errores.general && <div className="col-span-full"><Aviso tipo="error">{errores.general}</Aviso></div>}
        <div className="acciones col-span-full"><button type="button" className="btn btn-secundario" onClick={onCerrar}>Cancelar</button><button type="submit" className="btn btn-primario">Guardar</button></div>
      </form>
    </Modal>
  )
}

/** Un dato del prospecto en la franja bajo la portada de la ficha. */
function Dato({ titulo, cifra = false, children }) {
  return (
    <div>
      <dt className="text-xs text-tinta-suave">{titulo}</dt>
      <dd className={`mt-0.5 font-semibold wrap-anywhere ${cifra ? 'tabular-nums' : ''}`}>{children}</dd>
    </div>
  )
}
