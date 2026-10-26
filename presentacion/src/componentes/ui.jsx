import { useCallback, useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { CircleCheck, Inbox, Info, LoaderCircle, TriangleAlert, X } from 'lucide-react'
import { apiErrorMessage } from '../servicios/errors'

export const bs = (n) => `${Number(n || 0).toLocaleString('es-BO', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} Bs`
export const fecha = (v, conHora = false) => (v ? new Date(v).toLocaleString('es-BO', conHora
  ? { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }
  : { day: '2-digit', month: '2-digit', year: 'numeric' }) : '—')
export const claseEstado = (estado = '') => `e-${String(estado).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/\s+/g, '-')}`
export const iniciales = (u) => `${u?.nombre?.[0] || ''}${u?.apellido?.[0] || ''}`.toUpperCase()
export const nombre = (u) => (u ? `${u.nombre} ${u.apellido}`.trim() : '')

export function Etiqueta({ estado, children }) {
  return <span className={`etiqueta ${claseEstado(estado)}`}>{children || estado}</span>
}

export function Avatar({ usuario, tam = 36 }) {
  if (usuario?.foto_url) return <img className="avatar" src={usuario.foto_url} alt="" width={tam} height={tam} style={{ width: tam, height: tam }} />
  return <span className="avatar" style={{ width: tam, height: tam }} aria-hidden="true">{iniciales(usuario)}</span>
}

export function Aviso({ tipo = 'info', children }) {
  if (!children) return null
  const Icono = tipo === 'ok' ? CircleCheck : tipo === 'error' ? TriangleAlert : Info
  return (
    <div className={`aviso aviso-${tipo}`} role={tipo === 'error' ? 'alert' : 'status'}>
      <Icono size={18} aria-hidden="true" />
      <div>{children}</div>
    </div>
  )
}

export function Vacio({ titulo, children, icono: Icono = Inbox }) {
  return (
    <div className="vacio">
      <Icono size={36} aria-hidden="true" />
      <strong>{titulo}</strong>
      {children && <p>{children}</p>}
    </div>
  )
}

export function Cargando({ filas = 4 }) {
  return (
    <div style={{ display: 'grid', gap: 10 }} aria-busy="true" aria-label="Cargando">
      {Array.from({ length: filas }, (_, i) => <div key={i} className="esqueleto" style={{ height: 44 }} />)}
    </div>
  )
}

export function Boton({ cargando, children, className = 'btn-primario', ...props }) {
  return (
    <button type="button" className={`btn ${className}`} disabled={cargando || props.disabled} {...props}>
      {cargando && <LoaderCircle size={16} className="girando" aria-hidden="true" />}
      {children}
    </button>
  )
}

export function Campo({ etiqueta, requerido, ayuda, error, children }) {
  return (
    <label className="campo">
      <span>{etiqueta}{requerido && <em aria-hidden="true">*</em>}</span>
      {children}
      {error ? <span className="error">{error}</span> : ayuda && <small>{ayuda}</small>}
    </label>
  )
}

/** Modal accesible: cierra con Esc o clic en el fondo, enfoca el primer campo y devuelve el foco. */
export function Modal({ titulo, descripcion, onCerrar, children, pie, ancho, className = '' }) {
  const caja = useRef(null)
  useEffect(() => {
    const previo = document.activeElement
    const primero = caja.current?.querySelector('input, select, textarea, button:not(.modal-x)')
    primero?.focus()
    const tecla = (e) => e.key === 'Escape' && onCerrar()
    document.addEventListener('keydown', tecla)
    return () => {
      document.removeEventListener('keydown', tecla)
      previo?.focus?.()
    }
  }, [onCerrar])

  return createPortal(
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onCerrar()}>
      <section ref={caja} className={`modal ${ancho ? 'ancho' : ''} ${className}`} role="dialog" aria-modal="true" aria-label={titulo}>
        <header className="modal-cabecera">
          <div>
            <h3>{titulo}</h3>
            {descripcion && <p>{descripcion}</p>}
          </div>
          <button type="button" className="btn btn-texto btn-icono modal-x" onClick={onCerrar} aria-label="Cerrar"><X size={18} /></button>
        </header>
        <div className="modal-cuerpo">{children}</div>
        {pie && <footer className="modal-pie">{pie}</footer>}
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
  const nodo = aviso && <div className="notificacion"><Aviso tipo={aviso.tipo}>{aviso.texto}</Aviso></div>
  const ok = useCallback((texto) => setAviso({ tipo: 'ok', texto }), [])
  const error = useCallback((e, porDefecto) => setAviso({ tipo: 'error', texto: typeof e === 'string' ? e : apiErrorMessage(e, porDefecto) }), [])
  return { nodo, ok, error }
}

/** Carga datos de la API con estados de carga y error. */
export function useDatos(cargar, deps = []) {
  const [estado, setEstado] = useState({ datos: null, cargando: true, error: null })
  const recargar = useCallback(async () => {
    setEstado((s) => ({ ...s, cargando: true, error: null }))
    try {
      setEstado({ datos: await cargar(), cargando: false, error: null })
    } catch (e) {
      setEstado({ datos: null, cargando: false, error: apiErrorMessage(e, 'No se pudo cargar la información.') })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
  useEffect(() => { recargar() }, [recargar])
  return { ...estado, recargar }
}

/** Errores de validación de Laravel por campo ({campo: 'mensaje'}). */
export function erroresDe(e) {
  const errores = e?.response?.data?.errores || {}
  return Object.fromEntries(Object.entries(errores).map(([k, v]) => [k, Array.isArray(v) ? v[0] : v]))
}

export function CabeceraPagina({ titulo, children, acciones }) {
  return (
    <div className="cabecera-pagina">
      <div>
        <h2>{titulo}</h2>
        {children && <p>{children}</p>}
      </div>
      {acciones && <div className="acciones">{acciones}</div>}
    </div>
  )
}

export function Barras({ datos, color, formato = (v) => v, porcentaje = true }) {
  const max = Math.max(...datos.map((d) => d.total), 1)
  if (!datos.length || datos.every((d) => !d.total)) return <Vacio titulo="Sin datos todavía">Aparecerán cuando haya registros en este periodo.</Vacio>
  return (
    <ul className="barras">
      {datos.map((d) => (
        <li key={d.etiqueta} style={{ '--c': d.color || color }}>
          <span>{d.etiqueta}</span>
          <span className="pista" aria-hidden="true"><span className="relleno" style={{ width: `${(d.total / max) * 100}%`, display: 'block' }} /></span>
          <span className="valor">{porcentaje && d.porcentaje != null ? `${Number(d.porcentaje).toLocaleString('es-BO')} %` : formato(d.total)}</span>
        </li>
      ))}
    </ul>
  )
}
