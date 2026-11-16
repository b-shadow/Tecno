import { useEffect, useId, useRef, useState } from 'react'
import { Contrast, KeyRound, LogOut, Moon, Palette, Search, Sun, UserCog } from 'lucide-react'
import { useLocation } from 'react-router-dom'
import { go, useRecursoActual } from '../servicios/navigation'
import { logout, updateProfile, useAuth } from '../servicios/auth'
import { cambiar, temaEfectivo, useApariencia } from '../servicios/theme'
import { Avatar, Aviso, Boton, Campo, Modal, erroresDe, nombre } from './ui'
import { apiErrorMessage } from '../servicios/errors'
import { leerArchivo } from '../servicios/archivos'
import * as authApi from '../api/auth'
import * as sitioApi from '../api/sitio'

const LEYENDA = 'mb-1.5 text-sm font-bold'
const SEGMENTOS = 'segmentos flex *:flex-1'
const OPCION = 'flex items-center gap-2.5 rounded-ui px-3 py-2.5 text-left hover:bg-niebla'

/** Búsqueda global predictiva (enunciado 9): sin sesión busca en la oferta; con sesión, también datos del negocio. */
export function Buscador({ placeholder = 'Buscar programa, módulo o prospecto…', className = '' }) {
  const [q, setQ] = useState('')
  const [resultados, setResultados] = useState([])
  const [abierto, setAbierto] = useState(false)
  const [activo, setActivo] = useState(0)
  const [buscando, setBuscando] = useState(false)
  const id = useId()
  const raiz = useRef(null)

  useEffect(() => {
    if (q.trim().length < 2) {
      setResultados([])
      return undefined
    }
    const t = setTimeout(async () => {
      setBuscando(true)
      try {
        const { data } = await sitioApi.buscar(q)
        setResultados(data.resultados)
        setActivo(0)
        setAbierto(true)
      } catch {
        setResultados([])
      } finally {
        setBuscando(false)
      }
    }, 250)
    return () => clearTimeout(t)
  }, [q])

  useEffect(() => {
    const fuera = (e) => !raiz.current?.contains(e.target) && setAbierto(false)
    document.addEventListener('mousedown', fuera)
    return () => document.removeEventListener('mousedown', fuera)
  }, [])

  function elegir(r) {
    if (!r) return
    setAbierto(false)
    setQ('')
    go(r.ruta)
  }

  function tecla(e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); setAbierto(true); setActivo((a) => Math.min(a + 1, resultados.length - 1)) }
    if (e.key === 'ArrowUp') { e.preventDefault(); setActivo((a) => Math.max(a - 1, 0)) }
    if (e.key === 'Enter') { e.preventDefault(); elegir(resultados[activo]) }
    if (e.key === 'Escape') setAbierto(false)
  }

  const mostrar = abierto && q.trim().length>= 2
  return (
    <div className={`relative ${className}`} ref={raiz} role="search">
      <div className="flex h-11 items-center gap-2 rounded-ui border border-filete-fuerte bg-niebla-2 px-3 focus-within:border-acento-texto focus-within:bg-papel focus-within:shadow-[0_0_0_3px_color-mix(in_srgb,var(--acento)_30%,transparent)]">
        <Search size={18} aria-hidden="true" className="shrink-0 text-tinta-suave" />
        <input
          type="search" value={q} placeholder={placeholder} aria-label="Buscar en UNEXO"
          role="combobox" aria-expanded={mostrar} aria-controls={`${id}-lista`} aria-autocomplete="list"
          aria-activedescendant={mostrar && resultados[activo] ? `${id}-${activo}` : undefined}
          onChange={(e) => setQ(e.target.value)} onFocus={() => setAbierto(true)} onKeyDown={tecla} maxLength={80}
          className="h-full min-w-0 flex-1 bg-transparent outline-none"
        />
      </div>
      {mostrar && (
        <ul className="absolute top-[calc(100%+6px)] right-0 left-0 z-40 max-h-[420px] overflow-auto rounded-hoja border border-filete bg-papel p-1.5 shadow-capa" id={`${id}-lista`} role="listbox">
          {resultados.map((r, i) => (
            <li key={`${r.tipo}-${r.ruta}`} id={`${id}-${i}`} role="option" aria-selected={i === activo} className="grid cursor-pointer grid-cols-[auto_1fr] gap-x-3 gap-y-0.5 rounded-ui px-3 py-2.5 aria-selected:bg-acento-suave" onMouseEnter={() => setActivo(i)} onMouseDown={(e) => { e.preventDefault(); elegir(r) }}>
              <span className="row-span-2 min-w-[72px] self-center text-xs font-[750] text-acento-texto">{r.tipo}</span>
              <strong>{r.titulo}</strong>
              <span className="text-xs text-tinta-suave">{r.detalle}</span>
            </li>
          ))}
          {!resultados.length && <li className="block cursor-default px-3 py-2.5 text-tinta-suave" role="option" aria-selected="false">{buscando ? 'Buscando…' : 'Sin resultados para esa búsqueda.'}</li>}
        </ul>
      )}
    </div>
  )
}

/** Día/noche rápido en el encabezado. */
export function BotonTema() {
  const ap = useApariencia()
  const oscuro = temaEfectivo(ap) === 'dark'
  const titulo = oscuro ? 'Modo claro' : 'Modo oscuro'
  return (
    <button type="button" className="btn btn-texto btn-icono" title={titulo} aria-label={titulo} onClick={() => cambiar({ modo: oscuro ? 'light' : 'dark' })}>
      {oscuro ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  )
}

/** Panel de apariencia (enunciado 5): público, día/noche, tamaño de letra y contraste. */
export function Apariencia() {
  const ap = useApariencia()
  const [abierto, setAbierto] = useState(false)
  const raiz = useRef(null)
  useEffect(() => {
    const fuera = (e) => !raiz.current?.contains(e.target) && setAbierto(false)
    const esc = (e) => e.key === 'Escape' && setAbierto(false)
    document.addEventListener('mousedown', fuera)
    document.addEventListener('keydown', esc)
    return () => { document.removeEventListener('mousedown', fuera); document.removeEventListener('keydown', esc) }
  }, [])
  const seg = (campo, valor, texto) => (
    <button type="button" aria-pressed={ap[campo] === valor} onClick={() => cambiar({ [campo]: valor })}>{texto}</button>
  )
  return (
    <div className="relative" ref={raiz}>
      <button type="button" className="btn btn-texto btn-icono" aria-expanded={abierto} aria-label="Apariencia y accesibilidad" title="Apariencia y accesibilidad" onClick={() => setAbierto(!abierto)}>
        <Palette size={20} />
      </button>
      {abierto && (
        <div className="absolute top-[calc(100%+8px)] right-0 z-45 grid w-[min(340px,calc(100vw-24px))] gap-4 rounded-hoja border border-filete bg-papel p-6 shadow-capa max-movil:fixed max-movil:top-16 max-movil:right-3 max-movil:left-3 max-movil:max-h-[calc(100dvh-76px)] max-movil:w-auto max-movil:overflow-y-auto" role="dialog" aria-label="Apariencia y accesibilidad">
          <h3 className="text-lg">Apariencia</h3>
          <fieldset>
            <legend className={LEYENDA}>Tema según el público</legend>
            <div className={SEGMENTOS}>{seg('audiencia', 'ninos', 'Niños')}{seg('audiencia', 'jovenes', 'Jóvenes')}{seg('audiencia', 'adultos', 'Adultos')}</div>
          </fieldset>
          <fieldset>
            <legend className={LEYENDA}>Día o noche</legend>
            <div className={SEGMENTOS}>{seg('modo', 'auto', 'Según la hora')}{seg('modo', 'light', 'Día')}{seg('modo', 'dark', 'Noche')}</div>
            <small className="text-tinta-suave">Automático: día de 07:00 a 19:00 en su reloj.</small>
          </fieldset>
          <fieldset>
            <legend id="letra-leyenda" className={LEYENDA}>Tamaño de letra</legend>
            <div className="flex items-center gap-2">
              <button type="button" className="btn btn-secundario btn-icono" aria-label="Letra más pequeña" disabled={ap.letra <= -1} onClick={() => cambiar({ letra: ap.letra - 1 })}>A−</button>
              <input type="range" className="flex-1 accent-navy dark:accent-acento" min={-1} max={3} step={1} value={ap.letra} aria-labelledby="letra-leyenda" onChange={(e) => cambiar({ letra: Number(e.target.value) })} />
              <button type="button" className="btn btn-secundario btn-icono" aria-label="Letra más grande" disabled={ap.letra>= 3} onClick={() => cambiar({ letra: ap.letra + 1 })}>A+</button>
            </div>
          </fieldset>
          <label className="check"><input type="checkbox" checked={ap.contraste === 'alto'} onChange={(e) => cambiar({ contraste: e.target.checked ? 'alto' : 'normal' })} /><Contrast size={16} aria-hidden="true" /> Alto contraste</label>
        </div>
      )}
    </div>
  )
}

/** Chip de perfil con "Mi perfil", "Cambiar contraseña" y "Cerrar sesión". */
export function Perfil() {
  const { usuario } = useAuth()
  const [menu, setMenu] = useState(false)
  const [modal, setModal] = useState(null)
  const raiz = useRef(null)
  useEffect(() => {
    const fuera = (e) => !raiz.current?.contains(e.target) && setMenu(false)
    document.addEventListener('mousedown', fuera)
    return () => document.removeEventListener('mousedown', fuera)
  }, [])
  if (!usuario) return null
  return (
    <div className="relative" ref={raiz}>
      <button type="button" className="inline-flex items-center gap-2.5 rounded-full border border-filete bg-papel py-1 pr-2.5 pl-1 max-movil:p-0.5" aria-expanded={menu} onClick={() => setMenu(!menu)}>
        <Avatar usuario={usuario} chica />
        <span className="text-left max-movil:hidden"><strong className="block text-sm leading-tight">{usuario.nombre}</strong><small className="block text-xs text-tinta-suave capitalize">{usuario.rol}</small></span>
      </button>
      {menu && (
        <div className="absolute top-[calc(100%+8px)] right-0 z-45 grid min-w-[220px] rounded-hoja border border-filete bg-papel p-1.5 shadow-capa">
          <button type="button" className={OPCION} onClick={() => { setModal('perfil'); setMenu(false) }}><UserCog size={18} /> Mi perfil</button>
          <button type="button" className={OPCION} onClick={() => { setModal('clave'); setMenu(false) }}><KeyRound size={18} /> Cambiar contraseña</button>
          <button type="button" className={OPCION} onClick={() => { setModal('salir'); setMenu(false) }}><LogOut size={18} /> Cerrar sesión</button>
        </div>
      )}
      {modal === 'perfil' && <ModalPerfil usuario={usuario} onCerrar={() => setModal(null)} />}
      {modal === 'clave' && <ModalClave onCerrar={() => setModal(null)} />}
      {modal === 'salir' && (
        <Modal titulo="¿Cerrar sesión?" descripcion="Tendrá que volver a ingresar con su correo y contraseña." onCerrar={() => setModal(null)}
          pie={<div className="acciones"><button type="button" className="btn btn-secundario" onClick={() => setModal(null)}>Cancelar</button><button type="button" className="btn btn-primario" onClick={async () => { await logout(); go('/login', { replace: true }) }}>Cerrar sesión</button></div>} />
      )}
    </div>
  )
}

function ModalPerfil({ usuario, onCerrar }) {
  const [form, setForm] = useState({ nombre: usuario.nombre, apellido: usuario.apellido, telefono: usuario.telefono || '', foto: null })
  const [errores, setErrores] = useState({})
  const [msg, setMsg] = useState(null)
  const [enviando, setEnviando] = useState(false)
  async function guardar(e) {
    e.preventDefault()
    setEnviando(true)
    try {
      await updateProfile(form)
      setMsg({ tipo: 'ok', texto: 'Perfil actualizado correctamente.' })
      setErrores({})
    } catch (err) {
      setErrores(erroresDe(err))
      setMsg({ tipo: 'error', texto: apiErrorMessage(err) })
    } finally {
      setEnviando(false)
    }
  }
  return (
    <Modal titulo="Mi perfil" descripcion={usuario.correo} onCerrar={onCerrar}>
      <form className="grid gap-4 grid-cols-2 max-movil:grid-cols-1" onSubmit={guardar}>
        <Campo etiqueta="Nombre" requerido error={errores.nombre}><input value={form.nombre} required maxLength={120} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></Campo>
        <Campo etiqueta="Apellido" requerido error={errores.apellido}><input value={form.apellido} required maxLength={120} onChange={(e) => setForm({ ...form, apellido: e.target.value })} /></Campo>
        <Campo etiqueta="Teléfono" error={errores.telefono}><input value={form.telefono} inputMode="tel" pattern="\+?[0-9 ]{7,20}" title="Entre 7 y 20 dígitos." onChange={(e) => setForm({ ...form, telefono: e.target.value })} /></Campo>
        <Campo etiqueta="Foto" ayuda="JPG, PNG o WEBP hasta 2 MB." error={errores.foto}><input type="file" accept="image/jpeg,image/png,image/webp" onChange={async (e) => { const f = e.target.files[0]; if (f) setForm({ ...form, foto: await leerArchivo(f) }) }} /></Campo>
        <div className="col-span-full"><Aviso tipo={msg?.tipo}>{msg?.texto}</Aviso></div>
        <div className="acciones col-span-full"><button type="button" className="btn btn-secundario" onClick={onCerrar}>Cerrar</button><Boton type="submit" cargando={enviando}>Guardar</Boton></div>
      </form>
    </Modal>
  )
}

function ModalClave({ onCerrar }) {
  const [form, setForm] = useState({ password_actual: '', password: '', password_confirmation: '' })
  const [errores, setErrores] = useState({})
  const [msg, setMsg] = useState(null)
  async function guardar(e) {
    e.preventDefault()
    if (form.password !== form.password_confirmation) {
      setErrores({ password_confirmation: 'Las contraseñas no coinciden.' })
      return
    }
    try {
      const { data } = await authApi.cambiarPassword(form)
      setMsg({ tipo: 'ok', texto: data.mensaje })
      setForm({ password_actual: '', password: '', password_confirmation: '' })
      setErrores({})
    } catch (err) {
      setErrores(erroresDe(err))
      setMsg({ tipo: 'error', texto: apiErrorMessage(err) })
    }
  }
  return (
    <Modal titulo="Cambiar contraseña" descripcion="Mínimo 8 caracteres, con letras y números." onCerrar={onCerrar}>
      <form className="grid gap-4" onSubmit={guardar}>
        <Campo etiqueta="Contraseña actual" requerido error={errores.password_actual}><input type="password" autoComplete="current-password" required value={form.password_actual} onChange={(e) => setForm({ ...form, password_actual: e.target.value })} /></Campo>
        <Campo etiqueta="Nueva contraseña" requerido error={errores.password}><input type="password" autoComplete="new-password" required minLength={8} pattern="(?=.*[A-Za-z])(?=.*\d).{8,}" title="Al menos 8 caracteres con letras y números." value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></Campo>
        <Campo etiqueta="Repetir nueva contraseña" requerido error={errores.password_confirmation}><input type="password" autoComplete="new-password" required value={form.password_confirmation} onChange={(e) => setForm({ ...form, password_confirmation: e.target.value })} /></Campo>
        <Aviso tipo={msg?.tipo}>{msg?.texto}</Aviso>
        <div className="acciones"><button type="button" className="btn btn-secundario" onClick={onCerrar}>Cerrar</button><button type="submit" className="btn btn-primario">Actualizar contraseña</button></div>
      </form>
    </Modal>
  )
}

/** Contador de visitas persistente de la página (enunciado 7), en el pie de cada vista. */
// Una visita por navegación: en desarrollo, StrictMode monta el efecto dos veces y sin esto cada página sumaba 2.
let ultimaVisita = { clave: null, peticion: null }

export function Pie() {
  const path = useRecursoActual()
  const { key } = useLocation()
  const [visitas, setVisitas] = useState(null)
  useEffect(() => {
    let vivo = true
    if (ultimaVisita.clave !== `${key}|${path}`) ultimaVisita = { clave: `${key}|${path}`, peticion: sitioApi.visita(path) }
    ultimaVisita.peticion.then(({ data }) => vivo && setVisitas(data.visitas)).catch(() => vivo && setVisitas(null))
    return () => { vivo = false }
  }, [key, path])
  return (
    <footer className="flex items-center justify-between gap-4 border-t border-filete bg-papel px-[clamp(16px,3vw,40px)] py-2 text-xs text-tinta-suave">
      <span className="min-w-0 truncate">UNEXO</span>
      <span className="inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap" aria-live="polite"><b className="font-bold text-tinta tabular-nums">{visitas == null ? '—' : visitas.toLocaleString('es-BO')}</b> visitas a esta página</span>
    </footer>
  )
}

export { nombre }
