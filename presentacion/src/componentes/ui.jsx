import { useCallback, useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { CircleCheck, Inbox, Info, LoaderCircle, TriangleAlert, X } from 'lucide-react'
import { apiErrorMessage } from '../servicios/errors'
import { TONO, colorEstado } from './tonos'

export const bs = (n) => `${Number(n || 0).toLocaleString('es-BO', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} Bs`

function parsearFecha(v) {
  // Las fechas de calendario sin hora (YYYY-MM-DD) se interpretan en hora local para no retroceder un día en UTC-4.
  if (typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v)) {
    const [anio, mes, dia] = v.split('-').map(Number)
    return new Date(anio, mes - 1, dia, 12, 0, 0)
  }
  if (typeof v === 'string' && /^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?$/.test(v)) {
    return new Date(`${v.replace(' ', 'T')}-04:00`)
  }
  return new Date(v)
}

export const fecha = (v, conHora = false) => (v ? parsearFecha(v).toLocaleString('es-BO', conHora
  ? { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }
  : { day: '2-digit', month: '2-digit', year: 'numeric' }) : '—')

/** Formatea una marca de tiempo en horario oficial de Bolivia (America/La_Paz, UTC-4) como dd/MM/yyyy HH:mm:ss. */
export function fechaHoraBolivia(v) {
  if (!v) return '—'
  const d = parsearFecha(v)
  if (Number.isNaN(d.getTime())) return '—'
  const partes = Object.fromEntries(
    new Intl.DateTimeFormat('es-BO', {
      timeZone: 'America/La_Paz',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hourCycle: 'h23',
    }).formatToParts(d).map((p) => [p.type, p.value]),
  )
  return `${partes.day}/${partes.month}/${partes.year} ${partes.hour}:${partes.minute}:${partes.second}`
}
export const hora = (v) => (v ? parsearFecha(v).toLocaleTimeString('es-BO', { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }) : '—')
export const hoyLocal = (dias = 0) => {
  const d = new Date()
  d.setDate(d.getDate() + dias)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
export const iniciales = (u) => `${u?.nombre?.[0] || ''}${u?.apellido?.[0] || ''}`.toUpperCase()
export const nombre = (u) => (u ? `${u.nombre} ${u.apellido}`.trim() : '')

// Valores de la BD (compartidos con el P1) que se muestran con tilde.
const TEXTO_ESTADO = { 'En revision': 'En revisión' }

/** Estado con punto de color; sobre la portada oscura de la ficha va en blanco. */
export function Etiqueta({ estado, children, sobreOscuro = false }) {
  const color = sobreOscuro ? 'border-white/70 bg-white/12 text-white' : `border-current bg-papel ${colorEstado(estado)}`
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-bold whitespace-nowrap before:size-[7px] before:rounded-full before:bg-current before:content-[''] ${color}`}>
      {children || TEXTO_ESTADO[estado] || estado}
    </span>
  )
}

export function Avatar({ usuario, chica = false }) {
  const tam = chica ? 32 : 36
  const clase = `${chica ? 'size-8' : 'size-9'} inline-grid shrink-0 place-items-center rounded-full bg-niebla object-cover text-xs font-[750] text-navy dark:text-tinta`
  if (usuario?.foto_url) return <img className={clase} src={usuario.foto_url} alt="" width={tam} height={tam} />
  return <span className={clase} aria-hidden="true">{iniciales(usuario)}</span>
}

/** Persona en una celda de tabla: avatar opcional, nombre y dato secundario. */
export function Persona({ usuario, detalle, avatar = false }) {
  return (
    <div className="flex min-w-0 items-center gap-2.5">
      {avatar && <Avatar usuario={usuario} />}
      <div>
        <strong className="block font-[650]">{nombre(usuario)}</strong>
        <small className="block text-xs text-tinta-suave">{detalle}</small>
      </div>
    </div>
  )
}

const TONO_AVISO = {
  ok: 'border-[color-mix(in_srgb,var(--exito)_40%,transparent)] bg-exito-suave text-exito',
  error: 'border-[color-mix(in_srgb,var(--peligro)_40%,transparent)] bg-peligro-suave text-peligro',
  info: 'border-[color-mix(in_srgb,var(--acento)_45%,transparent)] bg-acento-suave text-tinta',
}

export function Aviso({ tipo = 'info', children }) {
  if (!children) return null
  const Icono = tipo === 'ok' ? CircleCheck : tipo === 'error' ? TriangleAlert : Info
  return (
    <div className={`flex items-start gap-2.5 rounded-ui border px-3.5 py-3 text-sm ${TONO_AVISO[tipo]}`} role={tipo === 'error' ? 'alert' : 'status'}>
      <Icono size={18} aria-hidden="true" className="mt-px shrink-0" />
      <div className="[&_ul]:mt-1 [&_ul]:list-disc [&_ul]:pl-[18px]">{children}</div>
    </div>
  )
}

export function Vacio({ titulo, children, icono: Icono = Inbox }) {
  return (
    <div className="grid justify-items-center gap-2.5 px-6 py-12 text-center text-tinta-suave">
      <Icono size={36} aria-hidden="true" className="text-filete-fuerte" />
      <strong className="font-titulo text-lg font-(--titulo-peso) text-tinta">{titulo}</strong>
      {children && <p>{children}</p>}
    </div>
  )
}

export function Cargando({ filas = 4 }) {
  return (
    <div className="grid gap-2.5" aria-busy="true" aria-label="Cargando">
      {Array.from({ length: filas }, (_, i) => (
        <div key={i} className="h-11 animate-brillo rounded-ui bg-[linear-gradient(90deg,var(--niebla)_25%,var(--niebla-2)_50%,var(--niebla)_75%)] bg-size-[200%_100%]" />
      ))}
    </div>
  )
}

export function Boton({ cargando, children, className = 'btn-primario', ...props }) {
  return (
    <button type="button" className={`btn ${className}`} disabled={cargando || props.disabled} {...props}>
      {cargando && <LoaderCircle size={16} className="animate-girar" aria-hidden="true" />}
      {children}
    </button>
  )
}

export function Campo({ etiqueta, requerido, ayuda, error, children, className = '' }) {
  return (
    <label className={`campo ${className}`}>
      <span>{etiqueta}{requerido && <em aria-hidden="true">*</em>}</span>
      {children}
      {error ? <span className="error">{error}</span> : ayuda && <small>{ayuda}</small>}
    </label>
  )
}

/** Modal accesible: cierra con Esc o clic en el fondo, enfoca el primer campo y devuelve el foco. */
export function Modal({ titulo, descripcion, onCerrar, children, pie, ancho }) {
  const caja = useRef(null)
  useEffect(() => {
    const previo = document.activeElement
    const primero = caja.current?.querySelector('input, select, textarea, button:not([data-cerrar])')
    primero?.focus()
    const tecla = (e) => e.key === 'Escape' && onCerrar()
    document.addEventListener('keydown', tecla)
    return () => {
      document.removeEventListener('keydown', tecla)
      previo?.focus?.()
    }
  }, [onCerrar])

  return createPortal(
    <div className="fixed inset-0 z-70 grid animate-aparecer place-items-center bg-[rgb(4_29_49/0.55)] p-4" onMouseDown={(e) => e.target === e.currentTarget && onCerrar()}>
      <section ref={caja} className={`max-h-[calc(100dvh-32px)] animate-subir overflow-auto rounded-hoja bg-papel shadow-capa ${ancho ? 'w-[min(920px,100%)]' : 'w-[min(640px,100%)]'}`}
        role="dialog" aria-modal="true" aria-label={titulo}>
        <header className="sticky top-0 z-1 flex items-start justify-between gap-3 border-b border-filete bg-papel px-6 pt-6 pb-3">
          <div>
            <h3>{titulo}</h3>
            {descripcion && <p className="mt-1 text-sm text-tinta-suave">{descripcion}</p>}
          </div>
          <button type="button" data-cerrar className="btn btn-texto btn-icono" onClick={onCerrar} aria-label="Cerrar"><X size={18} /></button>
        </header>
        <div className="grid gap-4 p-6 max-movil:p-4">{children}</div>
        {pie && <footer className="sticky bottom-0 border-t border-filete bg-papel px-6 py-4">{pie}</footer>}
      </section>
    </div>,
    document.body,
  )
}

/** Notificación breve (éxito o error) que desaparece sola. */
export function useAviso() {
  const [aviso, setAviso] = useState(null)
  useEffect(() => {
    if (!aviso) return undefined
    const t = setTimeout(() => setAviso(null), aviso.tipo === 'error' ? 7000 : 4500)
    return () => clearTimeout(t)
  }, [aviso])
  const nodo = aviso && createPortal(
    <div className="pointer-events-none fixed right-5 bottom-5 z-90 max-w-[min(420px,calc(100vw-40px))] animate-subir shadow-capa">
      <Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso>
    </div>,
    document.body,
  )
  const ok = useCallback((texto) => setAviso({ tipo: 'ok', texto }), [])
  const error = useCallback((e, porDefecto) => setAviso({ tipo: 'error', texto: typeof e === 'string' ? e : apiErrorMessage(e, porDefecto) }), [])
  return { nodo, ok, error }
}

/** Carga datos de la API con estados de carga y error, respuestas en orden y revalidación silenciosa opcional. */
export function useDatos(cargar, deps = [], opciones = {}) {
  const { intervaloMs = 0, refrescarAlEnfocar = false } = opciones
  const [estado, setEstado] = useState({ datos: null, cargando: true, error: null })
  const secuencia = useRef(0)
  const enVuelo = useRef(false)
  const ultimaCarga = useRef(0)
  const huella = useRef(null)
  const montado = useRef(true)

  useEffect(() => {
    montado.current = true
    return () => { montado.current = false }
  }, [])

  const recargar = useCallback(async (op = {}) => {
    const silencioso = op?.silencioso === true
    if (silencioso && enVuelo.current) return
    const id = ++secuencia.current
    enVuelo.current = true
    ultimaCarga.current = Date.now()
    if (!silencioso && montado.current) {
      huella.current = null
      setEstado((s) => ({ ...s, cargando: true, error: null }))
    }
    try {
      const datos = await cargar()
      if (montado.current && id === secuencia.current) {
        const nuevaHuella = JSON.stringify(datos)
        if (!silencioso || nuevaHuella !== huella.current) {
          huella.current = nuevaHuella
          setEstado({ datos, cargando: false, error: null })
        }
      }
    } catch (e) {
      if (montado.current && id === secuencia.current && !silencioso) {
        huella.current = null
        setEstado({ datos: null, cargando: false, error: apiErrorMessage(e, 'No se pudo cargar la información.') })
      }
    } finally {
      if (id === secuencia.current) enVuelo.current = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => { recargar() }, [recargar])

  useEffect(() => {
    if (!intervaloMs && !refrescarAlEnfocar) return undefined
    const sincronizar = () => {
      if (document.visibilityState !== 'visible') return
      if (Date.now() - ultimaCarga.current < 800) return
      recargar({ silencioso: true })
    }
    const timer = intervaloMs > 0 ? setInterval(sincronizar, intervaloMs) : null
    if (refrescarAlEnfocar) {
      window.addEventListener('focus', sincronizar)
      document.addEventListener('visibilitychange', sincronizar)
    }
    return () => {
      if (timer) clearInterval(timer)
      if (refrescarAlEnfocar) {
        window.removeEventListener('focus', sincronizar)
        document.removeEventListener('visibilitychange', sincronizar)
      }
    }
  }, [recargar, intervaloMs, refrescarAlEnfocar])

  return { ...estado, recargar }
}

/** Errores de validación de Laravel por campo ({campo: 'mensaje'}). */
export function erroresDe(e) {
  const errores = e?.response?.data?.errores || {}
  return Object.fromEntries(Object.entries(errores).map(([k, v]) => [k, Array.isArray(v) ? v[0] : v]))
}

export function CabeceraPagina({ titulo, children, acciones }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h2>{titulo}</h2>
        {children && <p className="mt-1.5 max-w-[70ch] text-tinta-suave">{children}</p>}
      </div>
      {acciones && <div className="acciones">{acciones}</div>}
    </div>
  )
}

/** Barras porcentuales (CU8): <progress> nativo, color de la serie por tono (token del tema). */
export function Barras({ datos, tono, formato = (v) => v, porcentaje = true }) {
  const max = Math.max(...datos.map((d) => d.total), 1)
  if (!datos.length || datos.every((d) => !d.total)) return <Vacio titulo="Sin datos todavía">Aparecerán cuando haya registros en este periodo.</Vacio>
  return (
    <ul className="grid gap-2.5 [--c:var(--navy)] dark:[--c:var(--acento)]">
      {datos.map((d) => (
        <li key={d.etiqueta} className={`grid grid-cols-[minmax(110px,34%)_minmax(0,1fr)_4.5rem] items-center gap-2.5 text-sm max-movil:grid-cols-[minmax(0,1fr)_4rem] ${TONO[d.tono || tono] || ''}`}>
          <span>{d.etiqueta}</span>
          <progress max={max} value={d.total} aria-hidden="true"
            className="block h-3 w-full appearance-none overflow-hidden rounded-full bg-niebla text-c max-movil:col-span-full max-movil:row-start-2
              [&::-moz-progress-bar]:rounded-full [&::-moz-progress-bar]:bg-c [&::-webkit-progress-bar]:bg-niebla
              [&::-webkit-progress-value]:rounded-full [&::-webkit-progress-value]:bg-c [&::-webkit-progress-value]:transition-[width] [&::-webkit-progress-value]:duration-600" />
          <span className="text-right font-[650] tabular-nums">{porcentaje && d.porcentaje != null ? `${Number(d.porcentaje).toLocaleString('es-BO')} %` : formato(d.total)}</span>
        </li>
      ))}
    </ul>
  )
}

/** Historial cronológico (RF4.1) como índice numerado 01, 02…: lo usan la ficha y Mi día. */
export const HISTORIAL = {
  lista: '[counter-reset:paso]',
  item: `grid grid-cols-[3.2rem_minmax(0,1fr)] gap-x-3 gap-y-0.5 border-b border-filete py-3 [counter-increment:paso]
    before:row-span-3 before:font-titulo before:text-2xl before:leading-none before:font-bold before:text-acento-2-texto before:tabular-nums
    before:content-[counter(paso,decimal-leading-zero)]`,
  tipo: 'text-xs font-[750] text-tinta-suave',
  texto: 'wrap-anywhere',
  nota: 'text-xs text-tinta-suave',
}
