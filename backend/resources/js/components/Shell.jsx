import { useEffect, useId, useRef, useState } from 'react'
import { Contrast, KeyRound, LogOut, Moon, Palette, Search, Sun, UserCog } from 'lucide-react'
import { api } from '../services/api'
import { go, useAppRoute } from '../services/navigation'
import { logout, updateProfile, useAuth } from '../services/auth'
import { cambiar, temaEfectivo, useApariencia } from '../services/theme'
import { Avatar, Aviso, Boton, Campo, Modal, erroresDe, nombre } from './ui'
import { apiErrorMessage } from '../services/errors'
import { leerArchivo } from '../services/api'

/** Búsqueda global predictiva (enunciado 9): sin sesión busca en la oferta; con sesión, también datos del negocio. */
export function Buscador({ placeholder = 'Buscar programa, módulo o prospecto…' }) {
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
        const { data } = await api.get('/buscar', { params: { q } })
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

  const mostrar = abierto && q.trim().length >= 2
  return (
    <div className="buscador" ref={raiz} role="search">
      <div className="buscador-campo">
        <Search size={18} aria-hidden="true" />
        <input
          type="search" value={q} placeholder={placeholder} aria-label="Buscar en UNEXO"
          role="combobox" aria-expanded={mostrar} aria-controls={`${id}-lista`} aria-autocomplete="list"
          aria-activedescendant={mostrar && resultados[activo] ? `${id}-${activo}` : undefined}
          onChange={(e) => setQ(e.target.value)} onFocus={() => setAbierto(true)} onKeyDown={tecla} maxLength={80}
        />
      </div>
      {mostrar && (
        <ul className="buscador-lista" id={`${id}-lista`} role="listbox">
          {resultados.map((r, i) => (
            <li key={`${r.tipo}-${r.ruta}`} id={`${id}-${i}`} role="option" aria-selected={i === activo} onMouseEnter={() => setActivo(i)} onMouseDown={(e) => { e.preventDefault(); elegir(r) }}>
              <span className="tipo">{r.tipo}</span>
              <strong>{r.titulo}</strong>
              <span className="detalle">{r.detalle}</span>
            </li>
          ))}
          {!resultados.length && <li className="nada" role="option" aria-selected="false">{buscando ? 'Buscando…' : 'Sin resultados para esa búsqueda.'}</li>}
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
    <div className="apariencia" ref={raiz}>
      <button type="button" className="btn btn-texto btn-icono" aria-expanded={abierto} aria-label="Apariencia y accesibilidad" title="Apariencia y accesibilidad" onClick={() => setAbierto(!abierto)}>
        <Palette size={20} />
      </button>
      {abierto && (
        <div className="apariencia-panel" role="dialog" aria-label="Apariencia y accesibilidad">
          <h3>Apariencia</h3>
          <fieldset>
            <legend>Tema según el público</legend>
            <div className="segmentos">{seg('audiencia', 'ninos', 'Niños')}{seg('audiencia', 'jovenes', 'Jóvenes')}{seg('audiencia', 'adultos', 'Adultos')}</div>
          </fieldset>
          <fieldset>
            <legend>Día o noche</legend>
            <div className="segmentos">{seg('modo', 'auto', 'Según la hora')}{seg('modo', 'light', 'Día')}{seg('modo', 'dark', 'Noche')}</div>
            <small style={{ color: 'var(--tinta-suave)' }}>Automático: día de 07:00 a 19:00 en su reloj.</small>
          </fieldset>
          <fieldset>
            <legend id="letra-leyenda">Tamaño de letra</legend>
            <div className="letra">
              <button type="button" className="btn btn-secundario btn-icono" aria-label="Letra más pequeña" disabled={ap.letra <= -1} onClick={() => cambiar({ letra: ap.letra - 1 })}>A−</button>
              <input type="range" min={-1} max={3} step={1} value={ap.letra} aria-labelledby="letra-leyenda" onChange={(e) => cambiar({ letra: Number(e.target.value) })} />
              <button type="button" className="btn btn-secundario btn-icono" aria-label="Letra más grande" disabled={ap.letra >= 3} onClick={() => cambiar({ letra: ap.letra + 1 })}>A+</button>
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
    <div style={{ position: 'relative' }} ref={raiz}>
      <button type="button" className="profile-chip" aria-expanded={menu} onClick={() => setMenu(!menu)}>
        <Avatar usuario={usuario} tam={32} />
        <span><strong>{usuario.nombre}</strong><small>{usuario.rol}</small></span>
      </button>
      {menu && (
        <div className="menu-flotante">
          <button type="button" onClick={() => { setModal('perfil'); setMenu(false) }}><UserCog size={18} /> Mi perfil</button>
          <button type="button" onClick={() => { setModal('clave'); setMenu(false) }}><KeyRound size={18} /> Cambiar contraseña</button>
          <button type="button" onClick={() => { setModal('salir'); setMenu(false) }}><LogOut size={18} /> Cerrar sesión</button>
        </div>
      )}
      {modal === 'perfil' && <ModalPerfil usuario={usuario} onCerrar={() => setModal(null)} />}
      {modal === 'clave' && <ModalClave onCerrar={() => setModal(null)} />}
      {modal === 'salir' && (
        <Modal className="logout-card" titulo="¿Cerrar sesión?" descripcion="Tendrá que volver a ingresar con su correo y contraseña." onCerrar={() => setModal(null)}
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
    <Modal className="profile-card" titulo="Mi perfil" descripcion={usuario.correo} onCerrar={onCerrar}>
      <form className="formulario dos" onSubmit={guardar}>
        <Campo etiqueta="Nombre" requerido error={errores.nombre}><input value={form.nombre} required maxLength={120} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></Campo>
        <Campo etiqueta="Apellido" requerido error={errores.apellido}><input value={form.apellido} required maxLength={120} onChange={(e) => setForm({ ...form, apellido: e.target.value })} /></Campo>
        <Campo etiqueta="Teléfono" error={errores.telefono}><input value={form.telefono} inputMode="tel" pattern="\+?[0-9 ]{7,20}" title="Entre 7 y 20 dígitos." onChange={(e) => setForm({ ...form, telefono: e.target.value })} /></Campo>
        <Campo etiqueta="Foto" ayuda="JPG, PNG o WEBP hasta 2 MB." error={errores.foto}><input type="file" accept="image/jpeg,image/png,image/webp" onChange={async (e) => { const f = e.target.files[0]; if (f) setForm({ ...form, foto: await leerArchivo(f) }) }} /></Campo>
        <div className="ancho"><Aviso tipo={msg?.tipo}>{msg?.texto}</Aviso></div>
        <div className="acciones ancho"><button type="button" className="btn btn-secundario" onClick={onCerrar}>Cerrar</button><Boton type="submit" cargando={enviando}>Guardar</Boton></div>
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
      const { data } = await api.put('/perfil/password', form)
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
      <form className="formulario" onSubmit={guardar}>
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
export function Pie() {
  const { path } = useAppRoute()
  const [visitas, setVisitas] = useState(null)
  useEffect(() => {
    let vivo = true
    api.post('/visitas', { ruta: path }).then(({ data }) => vivo && setVisitas(data.visitas)).catch(() => vivo && setVisitas(null))
    return () => { vivo = false }
  }, [path])
  return (
    <footer className="pie">
      <span className="pie-texto">UNEXO · Grupo 05 SA · INF513 UAGRM</span>
      <span className="contador" aria-live="polite"><b>{visitas == null ? '—' : visitas.toLocaleString('es-BO')}</b> visitas a esta página</span>
    </footer>
  )
}

export { nombre }
