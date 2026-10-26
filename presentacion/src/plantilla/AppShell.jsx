import { useEffect, useState } from 'react'
import { Link, Outlet, ScrollRestoration } from 'react-router-dom'
import {
  BadgeDollarSign, BarChart3, CalendarDays, Circle, CircleSlash, CreditCard, GraduationCap, KanbanSquare, LayoutDashboard,
  Mail, Megaphone, Menu, NotebookTabs, School, ScrollText, ShieldCheck, Shuffle, UserRound, Users,
} from 'lucide-react'
import logo from '../assets/unexo-marca.png'
import { go, useAppRoute, useRecursoActual } from '../servicios/navigation'
import { refreshSession, useAuth } from '../servicios/auth'
import { redirectFor } from '../servicios/access'
import { Apariencia, BotonTema, Buscador, Perfil, Pie } from '../componentes/Shell'

// Íconos que la tabla recursos puede nombrar (columna icono).
const ICONOS = { BadgeDollarSign, BarChart3, CalendarDays, CircleSlash, CreditCard, GraduationCap, KanbanSquare, LayoutDashboard, Mail, Megaphone, NotebookTabs, School, ScrollText, ShieldCheck, Shuffle, UserRound, Users }
const GRUPOS = { 1: 'Inicio', 2: 'Gestión comercial', 3: 'Pagos y matrícula', 4: 'Análisis y comunicación', 5: 'Administración' }

/** Layout persistente: elige público o interno y aplica el acceso según el menú del rol (leído de la BD). */
export default function AppShell() {
  const ruta = useAppRoute()
  const sesion = useAuth()
  const redirigir = redirectFor(ruta, sesion)

  useEffect(() => {
    if (redirigir) go(redirigir, { replace: true })
  }, [ruta.fullPath, redirigir])

  useEffect(() => {
    refreshSession().catch(() => {})
  }, [])

  const recurso = useRecursoActual()
  const actual = sesion.menu?.find((m) => m.ruta === ruta.path)
  const interno = Boolean(sesion.usuario && actual)
  const Layout = interno ? Interno : Publico
  const titulo = actual?.nombre || { '/login': 'Iniciar sesión', '/error': 'Página no encontrada' }[recurso] || 'Programas y módulos'
  useEffect(() => { document.title = `${titulo} · UNEXO` }, [titulo])
  return (
    <Layout actual={actual}>
      {!redirigir && <Outlet />}
      <ScrollRestoration />
    </Layout>
  )
}

function Marca({ href = '/anuncios' }) {
  return (
    <Link to={href} className="marca" aria-label="UNEXO, ir al inicio">
      <img src={logo} alt="" width="34" height="34" />
      <span className="marca-texto"><strong>U<span>NEXO</span></strong><small>CRM Comercial Educativo</small></span>
    </Link>
  )
}

function Publico({ children }) {
  const { path } = useAppRoute()
  const { usuario, menu } = useAuth()
  return (
    <div className="publico">
      <a className="saltar" href="#contenido">Saltar al contenido</a>
      <header className="encabezado">
        <Marca />
        {/* El login es solo el formulario: la búsqueda va en el encabezado del catálogo y del panel. */}
        {path !== '/login' && <Buscador placeholder="Buscar programa o módulo…" />}
        <div className="encabezado-acciones">
          <BotonTema />
          <Apariencia />
          {usuario
            ? <Link className="btn btn-primario" to={menu?.[0]?.ruta || '/anuncios'}>Ir al panel</Link>
            : path !== '/login' && <Link className="btn btn-primario" to="/login">Iniciar sesión</Link>}
        </div>
      </header>
      <main id="contenido">{children}</main>
      <Pie />
    </div>
  )
}

function Interno({ children, actual }) {
  const { menu } = useAuth()
  const [cerrado, setCerrado] = useState(() => {
    try { return localStorage.getItem('crm_sidebar_collapsed') === '1' } catch { return false }
  })
  const [movil, setMovil] = useState(false)
  const { path } = useAppRoute()
  useEffect(() => setMovil(false), [path])

  function alternar() {
    if (window.matchMedia('(max-width: 960px)').matches) return setMovil(!movil)
    setCerrado(!cerrado)
    try { localStorage.setItem('crm_sidebar_collapsed', cerrado ? '0' : '1') } catch { /* preferencia opcional */ }
  }

  let grupoPrevio = null
  return (
    <div className={`shell ${cerrado ? 'riel-cerrado' : ''}`}>
      <a className="saltar" href="#contenido">Saltar al contenido</a>
      <aside className={`riel ${movil ? 'abierto' : ''}`} aria-label="Menú principal">
        <Link to={menu?.[0]?.ruta || '/anuncios'} className="riel-marca"><img src={logo} alt="" width="34" height="34" /><strong>U<span>NEXO</span></strong></Link>
        <nav aria-label="Módulos">
          {menu.map((item) => {
            const grupo = GRUPOS[Math.floor(item.orden / 10)] || null
            const titulo = grupo !== grupoPrevio ? grupo : null
            grupoPrevio = grupo
            const Icono = ICONOS[item.icono] || Circle
            return (
              <div key={item.codigo} style={{ display: 'contents' }}>
                {titulo && <div className="riel-grupo">{titulo}</div>}
                <Link to={item.ruta} className={item.ruta === path ? 'router-link-active' : ''} aria-current={item.ruta === path ? 'page' : undefined} title={cerrado ? item.nombre : undefined}>
                  <Icono size={19} aria-hidden="true" /><span>{item.nombre}</span>
                </Link>
              </div>
            )
          })}
        </nav>
        <div className="riel-pie">Menú según su rol · matriz de acceso</div>
      </aside>
      {movil && <div className="velo" onClick={() => setMovil(false)} aria-hidden="true" />}
      <div className="shell-principal">
        <header className="encabezado">
          <button type="button" className="btn btn-texto btn-icono" onClick={alternar} aria-label="Mostrar u ocultar el menú" title="Menú"><Menu size={22} /></button>
          <div className="encabezado-titulo"><h1 title={actual ? `Caso de uso ${actual.caso_uso}` : undefined}>{actual?.nombre}</h1></div>
          <Buscador />
          <div className="encabezado-acciones"><BotonTema /><Apariencia /><Perfil /></div>
        </header>
        <main id="contenido" className="contenido"><div className="contenido-ancho">{children}</div></main>
        <Pie />
      </div>
    </div>
  )
}
