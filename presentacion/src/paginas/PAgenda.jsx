import { useEffect, useMemo, useRef, useState } from 'react'
import { Ban, CreditCard, ExternalLink, MessageCircle, NotebookTabs, Pencil, Upload } from 'lucide-react'
import { leerArchivo } from '../servicios/archivos'
import { go, useAppRoute } from '../servicios/navigation'
import { puede, useAuth } from '../servicios/auth'
import { Aviso, Boton, Campo, Cargando, Etiqueta, Modal, Vacio, bs, erroresDe, fecha, hoyLocal, nombre, useAviso, useDatos, HISTORIAL } from '../componentes/ui'
import { apiErrorMessage } from '../servicios/errors'
import * as catalogoApi from '../api/catalogo'
import * as interesesApi from '../api/intereses'
import * as pagosApi from '../api/pagos'
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
  const lista = useDatos(async () => (await interesesApi.index({ buscar: buscar || undefined, estado: estado || undefined })).data, [buscar, estado])
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
  const { datos, cargando, error, recargar } = useDatos(async () => (await interesesApi.show(nro)).data, [nro])
  const fichaRef = useRef(null)
  // En celular la ficha queda debajo de la lista: al elegir una tarjeta se lleva a la vista cuando ya cargó.
  useEffect(() => {
    if (enfocar && datos && window.matchMedia('(max-width: 1100px)').matches) fichaRef.current?.scrollIntoView({ block: 'start' })
  }, [enfocar, datos])
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
        {pestana === 'pagos' && <Pagos t={t} esSuVendedor={esSuVendedor} editable={editable} aviso={aviso} onCambio={actualizar} />}
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

/** CU6 / enunciado 10: métodos de pago del prospecto, órdenes con pago único o cuotas, comprobantes y Stripe Checkout Sandbox. */
function Pagos({ t, esSuVendedor, editable, aviso, onCambio }) {
  const [modal, setModal] = useState(null)
  const [stripeCargando, setStripeCargando] = useState(null)
  const metodos = t.prospecto.metodos_pago || []
  const activos = metodos.filter((m) => m.estado === 'activo')
  const metodosStripe = activos.filter((m) => m.proveedor === 'stripe')

  async function abrirSetupStripe() {
    if (stripeCargando) return
    setStripeCargando('setup')
    try {
      const { data } = await pagosApi.crearSetupTarjeta(t.documento, t.nro_tarjeta)
      window.location.assign(data.url)
    } catch (e) {
      aviso.error(e)
      setStripeCargando(null)
    }
  }

  async function pagarConStripe(orden, cuota) {
    const clave = `${orden.nro_orden}-${cuota.nro_cuota}`
    if (stripeCargando) return
    setStripeCargando(clave)
    try {
      const { data } = await pagosApi.crearCheckout(orden.nro_orden, cuota.nro_cuota)
      window.location.assign(data.url)
    } catch (e) {
      aviso.error(e)
      setStripeCargando(null)
    }
  }

  return (
    <div className="grid gap-6">
      <section>
        <div className="hoja-titulo border-b-0 px-0 pt-0 pb-2 flex-wrap gap-2">
          <h4>Métodos de pago</h4>
          {editable && (
            <div className="acciones">
              <Boton className="btn-primario" cargando={stripeCargando === 'setup'} disabled={Boolean(stripeCargando && stripeCargando !== 'setup')} onClick={abrirSetupStripe}>
                <CreditCard size={16} /> Registrar tarjeta con Stripe
              </Boton>
              <button type="button" className="btn btn-secundario" onClick={() => setModal({ tipo: 'metodo' })}>QR / Transferencia</button>
            </div>
          )}
        </div>
        {!metodos.length ? <p className="text-tinta-suave">El prospecto todavía no tiene métodos registrados.</p> : (
          <div className="grid gap-2">{metodos.map((m) => (
            <div key={m.nro_metodo} className="flex flex-wrap items-center gap-2.5 rounded-ui border border-filete px-3 py-2.5">
              <CreditCard size={18} aria-hidden="true" />
              <span className="flex-1">
                <b>{m.tipo === 'Tarjeta' ? `${m.marca} ` : m.tipo}</b>
                {m.tipo === 'Tarjeta' && <span className="tracking-[0.04em] tabular-nums">•••• {m.ultimos_digitos} · vence {m.vencimiento}</span>}
                {' · '}{m.titular}
                {' · '}<small className="text-tinta-suave">{m.proveedor === 'stripe' ? 'Stripe Sandbox' : 'Manual'}</small>
              </span>
              <Etiqueta estado={m.estado} />
              {editable && <button type="button" className="btn btn-texto" onClick={async () => { try { aviso.ok((await pagosApi.cambiarEstadoMetodo(m.nro_metodo, m.estado === 'activo' ? 'inactivo' : 'activo')).data.mensaje); onCambio() } catch (e) { aviso.error(e) } }}>{m.estado === 'activo' ? 'Desactivar' : 'Activar'}</button>}
            </div>
          ))}</div>
        )}
      </section>
      <section>
        <div className="hoja-titulo border-b-0 px-0 pt-0 pb-2"><h4>Órdenes y cuotas</h4>{editable && esSuVendedor && t.estado !== 'Convertido' && <button type="button" className="btn btn-primario" onClick={() => setModal({ tipo: 'orden' })}>Generar orden de pago</button>}</div>
        {!t.ordenes_pago.length ? <p className="text-tinta-suave">{esSuVendedor ? 'Genere la orden cuando el prospecto confirme los módulos.' : 'Sin órdenes de pago.'}</p> : t.ordenes_pago.map((o) => {
          const anulada = o.estado === 'Anulada'
          const totalCuotas = o.cuotas.length
          const cuotasPagadas = o.cuotas.filter((c) => c.estado === 'Pago aprobado')
          const pagado = cuotasPagadas.reduce((s, c) => s + Number(c.monto || 0), 0)
          const saldo = Math.max(Number(o.total || 0) - pagado, 0)
          const anulable = editable && !anulada && !o.cuotas.some((c) => ['Pago aprobado', 'En revision'].includes(c.estado))
          return (
            <article key={o.nro_orden} className="hoja mb-3">
              <div className="hoja-titulo flex-wrap gap-2">
                <div>
                  <h4>Orden #{o.nro_orden} · {bs(o.total)} <small className="font-normal text-tinta-suave">(BOB)</small></h4>
                  <small>
                    {o.items.map((i) => i.modulo_nombre).join(', ')}
                    {Number(o.descuento_total) > 0 && ` · descuento ${bs(o.descuento_total)}`}
                    {' · '}Pagado {bs(pagado)} · Saldo pendiente <b className="tabular-nums">{bs(saldo)}</b> ({cuotasPagadas.length} de {totalCuotas} cuotas)
                  </small>
                </div>
                <div className="acciones">
                  {anulada ? <Etiqueta estado="Perdido">Anulada</Etiqueta> : <Etiqueta estado={saldo === 0 && totalCuotas > 0 ? 'Pago aprobado' : 'Pendiente de pago'}>{saldo === 0 && totalCuotas > 0 ? 'Liquidada' : 'Activa'}</Etiqueta>}
                  {anulable && <button type="button" className="btn btn-texto" onClick={() => setModal({ tipo: 'anular', orden: o })}><Ban size={15} /> Anular orden</button>}
                </div>
              </div>
              {anulada && o.motivo_anulacion && <div className="px-6 pt-3"><Aviso tipo="error">Orden anulada: {o.motivo_anulacion}</Aviso></div>}
              <div className="hoja-cuerpo grid gap-2">
                {o.cuotas.map((c) => {
                  const clave = `${o.nro_orden}-${c.nro_cuota}`
                  const pendiente = editable && !anulada && ['Pendiente de pago', 'Pago rechazado'].includes(c.estado)
                  const metodoTxt = c.metodo
                    ? (c.metodo.tipo === 'Tarjeta' ? `${c.metodo.marca} •••• ${c.metodo.ultimos_digitos}` : c.metodo.tipo)
                    : (metodosStripe[0] ? `${metodosStripe[0].marca} •••• ${metodosStripe[0].ultimos_digitos}` : 'Tarjeta en Stripe Checkout')
                  return (
                    <div key={c.nro_cuota} className="flex flex-wrap items-center justify-between gap-3 rounded-ui border border-filete px-3.5 py-3">
                      <div className="flex min-w-[240px] flex-1 items-start gap-3">
                        <b className="font-titulo text-xl leading-none text-acento-2-texto tabular-nums">{String(c.nro_cuota).padStart(2, '0')}</b>
                        <div className="min-w-0 flex-1">
                          <div><strong className="tabular-nums">{bs(c.monto)}</strong> <small className="text-xs text-tinta-suave">BOB · Cuota {c.nro_cuota} de {totalCuotas}</small></div>
                          <div className="text-xs text-tinta-suave">
                            Vence {fecha(c.fecha_vencimiento)}
                            {' · '}{c.proveedor === 'stripe' ? 'Stripe Sandbox' : 'Manual / histórico'}
                            {' · '}Método: {metodoTxt}
                            {c.stripe_pago_intent && <> · Ref: <span className="font-mono break-all">{c.stripe_pago_intent}</span></>}
                            {c.observacion && !c.stripe_pago_intent ? ` · ${c.observacion}` : ''}
                          </div>
                        </div>
                      </div>
                      <div className="acciones flex-wrap">
                        <Etiqueta estado={c.estado} />
                        {c.stripe_recibo_url && <a className="btn btn-texto" href={c.stripe_recibo_url} target="_blank" rel="noreferrer"><ExternalLink size={15} /> Recibo</a>}
                        {pendiente && <>
                          <Boton className="btn-acento" cargando={stripeCargando === clave} disabled={Boolean(stripeCargando && stripeCargando !== clave)} onClick={() => pagarConStripe(o, c)}>
                            <CreditCard size={16} /> Pagar con Stripe
                          </Boton>
                          <button type="button" className="btn btn-secundario" onClick={() => setModal({ tipo: 'comprobante', orden: o, cuota: c })}><Upload size={16} /> Comprobante</button>
                        </>}
                      </div>
                    </div>
                  )
                })}
              </div>
            </article>
          )
        })}
      </section>
      {modal?.tipo === 'metodo' && <NuevoMetodo documento={t.documento} onCerrar={() => setModal(null)} onListo={(m) => { aviso.ok(m); setModal(null); onCambio() }} />}
      {modal?.tipo === 'orden' && <NuevaOrden t={t} onCerrar={() => setModal(null)} onListo={(m) => { aviso.ok(m); setModal(null); onCambio() }} />}
      {modal?.tipo === 'comprobante' && <Comprobante {...modal} metodos={activos} onCerrar={() => setModal(null)} onListo={(m) => { aviso.ok(m); setModal(null); onCambio() }} />}
      {modal?.tipo === 'anular' && <AnularOrden orden={modal.orden} onCerrar={() => setModal(null)} onListo={(m) => { aviso.ok(m); setModal(null); onCambio() }} />}
    </div>
  )
}

function NuevoMetodo({ documento, onCerrar, onListo }) {
  const [form, setForm] = useState({ tipo: 'QR', titular: '' })
  const [errores, setErrores] = useState({})
  async function guardar(e) {
    e.preventDefault()
    try { onListo((await pagosApi.registrarMetodo(documento, form)).data.mensaje) } catch (err) { setErrores({ ...erroresDe(err), general: apiErrorMessage(err) }) }
  }
  return (
    <Modal titulo="Registrar método manual (QR / Transferencia)" descripcion="Para registrar una tarjeta de débito o crédito utilice el botón «Registrar tarjeta con Stripe»." onCerrar={onCerrar}>
      <form className="grid gap-4 grid-cols-2 max-movil:grid-cols-1" onSubmit={guardar}>
        <Campo etiqueta="Tipo" requerido><select value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}><option>QR</option><option>Transferencia</option></select></Campo>
        <Campo etiqueta="Titular" requerido error={errores.titular}><input required maxLength={120} value={form.titular} onChange={(e) => setForm({ ...form, titular: e.target.value })} autoComplete="off" /></Campo>
        {errores.general && <div className="col-span-full"><Aviso tipo="error">{errores.general}</Aviso></div>}
        <div className="acciones col-span-full"><button type="button" className="btn btn-secundario" onClick={onCerrar}>Cancelar</button><button type="submit" className="btn btn-primario">Registrar</button></div>
      </form>
    </Modal>
  )
}

function NuevaOrden({ t, onCerrar, onListo }) {
  const catalogo = useDatos(async () => (await catalogoApi.programas()).data.programas)
  const descuentos = useDatos(async () => (await pagosApi.descuentos()).data.descuentos)
  const programa = catalogo.datos?.find((p) => p.modulos.some((m) => m.codigo === t.modulo_codigo))
  const [modulos, setModulos] = useState([t.modulo_codigo])
  const [dctos, setDctos] = useState([])
  const [cuotas, setCuotas] = useState(1)
  const manana = hoyLocal(1)
  const [vence, setVence] = useState(manana)
  const [error, setError] = useState(null)
  const subtotal = (programa?.modulos || []).filter((m) => modulos.includes(m.codigo)).reduce((s, m) => s + m.precio, 0)
  const pct = (descuentos.datos || []).filter((d) => dctos.includes(d.codigo)).reduce((s, d) => s + Number(d.porcentaje), 0)
  const total = Math.max(subtotal * (1 - pct / 100), 0)
  const alternar = (lista, set, v) => set(lista.includes(v) ? lista.filter((x) => x !== v) : [...lista, v])
  async function generar(e) {
    e.preventDefault()
    try { onListo((await pagosApi.crearOrden(t.nro_tarjeta, { modulos, descuentos: dctos, cuotas, primer_vencimiento: vence })).data.mensaje) } catch (err) { setError(apiErrorMessage(err)) }
  }
  return (
    <Modal ancho titulo="Generar orden de pago" descripcion={`${nombre(t.prospecto)} · ${t.programa_nombre}`} onCerrar={onCerrar}>
      {!programa ? <Cargando /> : (
        <form className="grid gap-4" onSubmit={generar}>
          <fieldset className="grid gap-4 min-w-0">
            <legend className="mb-2 font-bold">Módulos</legend>
            <label className="check"><input type="checkbox" checked={modulos.length === programa.modulos.length} onChange={(e) => setModulos(e.target.checked ? programa.modulos.map((m) => m.codigo) : [t.modulo_codigo])} /> Programa completo ({programa.modulos.length} módulos)</label>
            {programa.modulos.map((m, i) => <label key={m.codigo} className="check"><input type="checkbox" checked={modulos.includes(m.codigo)} onChange={() => alternar(modulos, setModulos, m.codigo)} /> {String(i + 1).padStart(2, '0')} · {m.nombre} — {bs(m.precio)}</label>)}
          </fieldset>
          <fieldset className="grid gap-4 min-w-0">
            <legend className="mb-2 font-bold">Descuentos</legend>
            {(descuentos.datos || []).map((d) => <label key={d.codigo} className="check"><input type="checkbox" checked={dctos.includes(d.codigo)} onChange={() => alternar(dctos, setDctos, d.codigo)} /> {d.nombre} ({Number(d.porcentaje)}%)</label>)}
          </fieldset>
          <div className="grid gap-4 grid-cols-2 max-movil:grid-cols-1">
            <Campo etiqueta="Forma de pago" requerido><select value={cuotas} onChange={(e) => setCuotas(Number(e.target.value))}><option value={1}>Pago único</option>{[2, 3, 4, 5, 6, 8, 10, 12].map((n) => <option key={n} value={n}>Plan de {n} cuotas mensuales</option>)}</select></Campo>
            <Campo etiqueta={cuotas === 1 ? 'Vencimiento' : 'Vencimiento de la 1.ª cuota'} requerido><input type="date" min={hoyLocal()} required value={vence} onChange={(e) => setVence(e.target.value)} /></Campo>
          </div>
          <dl className="cifras"><div><dt>Subtotal</dt><dd>{bs(subtotal)}</dd></div><div><dt>Total</dt><dd>{bs(total)}</dd></div><div><dt>{cuotas === 1 ? 'Pago' : 'Cuota aprox.'}</dt><dd>{bs(total / cuotas)}</dd></div></dl>
          <Aviso tipo="error">{error}</Aviso>
          <div className="acciones"><button type="button" className="btn btn-secundario" onClick={onCerrar}>Cancelar</button><button type="submit" className="btn btn-primario" disabled={!modulos.length}>Generar orden</button></div>
        </form>
      )}
    </Modal>
  )
}

function Comprobante({ orden, cuota, metodos, onCerrar, onListo }) {
  const [form, setForm] = useState({ archivo: null, nro_metodo: '', remitente: '', hora_pago: '', observacion: '' })
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)
  async function enviar(e) {
    e.preventDefault()
    setEnviando(true)
    try {
      onListo((await pagosApi.registrarComprobante(orden.nro_orden, cuota.nro_cuota, { ...form, nro_metodo: form.nro_metodo || undefined, hora_pago: form.hora_pago || undefined })).data.mensaje)
    } catch (err) {
      setError(apiErrorMessage(err))
      setEnviando(false)
    }
  }
  return (
    <Modal titulo={`Comprobante · cuota ${cuota.nro_cuota} de la orden #${orden.nro_orden}`} descripcion={`${bs(cuota.monto)}. Coordinación lo revisará.`} onCerrar={onCerrar}>
      <form className="grid gap-4" onSubmit={enviar}>
        <Campo etiqueta="Archivo (imagen o PDF, hasta 5 MB)" requerido><input type="file" required accept="image/png,image/jpeg,image/webp,application/pdf" onChange={async (e) => { const f = e.target.files[0]; if (f) { if (f.size> 5 * 1024 * 1024) { setError('El archivo supera 5 MB.'); return } setError(null); setForm({ ...form, archivo: await leerArchivo(f) }) } }} /></Campo>
        <div className="grid gap-4 grid-cols-2 max-movil:grid-cols-1">
          <Campo etiqueta="Método usado"><select value={form.nro_metodo} onChange={(e) => setForm({ ...form, nro_metodo: e.target.value })}><option value="">Sin especificar</option>{metodos.map((m) => <option key={m.nro_metodo} value={m.nro_metodo}>{m.tipo}{m.ultimos_digitos ? ` •••• ${m.ultimos_digitos}` : ''}</option>)}</select></Campo>
          <Campo etiqueta="Hora del pago"><input type="datetime-local" value={form.hora_pago} onChange={(e) => setForm({ ...form, hora_pago: e.target.value })} /></Campo>
        </div>
        <Campo etiqueta="Quién lo envió"><input maxLength={160} value={form.remitente} onChange={(e) => setForm({ ...form, remitente: e.target.value })} placeholder="Ej. El mismo prospecto por WhatsApp" /></Campo>
        <Aviso tipo="error">{error}</Aviso>
        <div className="acciones"><button type="button" className="btn btn-secundario" onClick={onCerrar}>Cancelar</button><Boton type="submit" cargando={enviando} disabled={!form.archivo}>Enviar a revisión</Boton></div>
      </form>
    </Modal>
  )
}

function AnularOrden({ orden, onCerrar, onListo }) {
  const [motivo, setMotivo] = useState('')
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)
  async function enviar(e) {
    e.preventDefault()
    setEnviando(true)
    try {
      onListo((await pagosApi.anularOrden(orden.nro_orden, motivo)).data.mensaje)
    } catch (err) {
      setError(apiErrorMessage(err))
      setEnviando(false)
    }
  }
  return (
    <Modal titulo={`Anular orden #${orden.nro_orden}`} descripcion={`Monto: ${bs(orden.total)}. Si tiene sesiones Stripe abiertas se expirarán sin realizar cobros.`} onCerrar={onCerrar}>
      <form className="grid gap-4" onSubmit={enviar}>
        <Campo etiqueta="Motivo de anulación" requerido ayuda="Mínimo 5 caracteres. Queda registrado en el historial.">
          <textarea required minLength={5} maxLength={500} value={motivo} onChange={(e) => setMotivo(e.target.value)} />
        </Campo>
        <Aviso tipo="error">{error}</Aviso>
        <div className="acciones">
          <button type="button" className="btn btn-secundario" onClick={onCerrar}>Cancelar</button>
          <Boton type="submit" className="btn-peligro-suave" cargando={enviando} disabled={motivo.trim().length < 5}>Confirmar anulación</Boton>
        </div>
      </form>
    </Modal>
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
