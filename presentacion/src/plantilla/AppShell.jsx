import { Fragment, useEffect, useState } from 'react'
import { Link, Outlet, ScrollRestoration } from 'react-router-dom'
import {
  BadgeDollarSign, BarChart3, CalendarDays, Circle, CircleSlash, CreditCard, GraduationCap, KanbanSquare, LayoutDashboard,
  Mail, Megaphone, Menu, NotebookTabs, School, ScrollText, ShieldCheck, Shuffle, UserRound, Users,
} from 'lucide-react'
import logo from '../assets/unexo-marca.png'
import { go, useAppRoute, useRecursoActual } from '../servicios/navigation'
import { refreshSession, useAuth } from '../servicios/auth'
import { redirectFor } from '../servicios/access'
import { ErrorBoundary } from '../componentes/ErrorBoundary'
import { Apariencia, BotonTema, Buscador, Perfil, Pie } from '../componentes/Shell'

// Íconos que la tabla recursos puede nombrar (columna icono).
const ICONOS = { BadgeDollarSign, BarChart3, CalendarDays, CircleSlash, CreditCard, GraduationCap, KanbanSquare, LayoutDashboard, Mail, Megaphone, NotebookTabs, School, ScrollText, ShieldCheck, Shuffle, UserRound, Users }
const GRUPOS = { 1: 'Inicio', 2: 'Gestión comercial', 3: 'Pagos y matrícula', 4: 'Análisis y comunicación', 5: 'Administración' }

// Piezas comunes a la plantilla pública y la interna.
const ENCABEZADO = 'app-encabezado sticky top-0 z-30 flex min-h-[68px] items-center justify-between gap-4 border-b border-header-borde bg-header-bg px-[clamp(16px,3vw,40px)] max-tableta:min-h-[60px] max-tableta:gap-2 max-movil:flex-wrap max-movil:py-2'
const ACCIONES = 'ml-auto flex shrink-0 items-center gap-2'
const BUSCADOR = 'mx-auto min-w-0 max-w-[560px] flex-1 max-movil:order-3 max-movil:max-w-none max-movil:basis-full'
const SALTAR = 'absolute top-0 left-3 z-100 -translate-y-[120%] rounded-ui bg-navy px-3.5 py-2.5 text-white focus:translate-y-3'

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
  const actual = sesion.menu?.find((m) => m.ruta === recurso)
  const interno = Boolean(sesion.usuario && actual)
  const Layout = interno ? Interno : Publico
  const titulo = {
    '/pagos/confirmacion': 'Confirmación de pago',
    '/pagos/cancelado': 'Pago cancelado',
    '/login': 'Iniciar sesión',
    '/error': 'Página no encontrada',
  }[ruta.path] || actual?.nombre || 'Programas y módulos'
  useEffect(() => { document.title = `${titulo} · UNEXO` }, [titulo])
  return (
    <Layout actual={actual}>
      {!redirigir && (
        <ErrorBoundary key={ruta.path} nombreSeccion={titulo}>
          <Outlet />
        </ErrorBoundary>
      )}
      <ScrollRestoration />
    </Layout>
  )
}

function Marca({ href = '/anuncios' }) {
  return (
    <Link to={href} className="app-marca inline-flex shrink-0 items-center gap-2.5 text-navy no-underline dark:text-white" aria-label="UNEXO, ir al inicio">
      <img src={logo} alt="" width="34" height="34" className="size-[34px] object-contain" />
      {/* A 320 px el encabezado público cabe en dos filas: solo el ícono de la marca. */}
      <span className="flex flex-col leading-none max-mini:hidden">
        <strong className="font-ui text-[1.2rem] font-extrabold tracking-[0.02em]">U<span className="text-acento-texto">NEXO</span></strong>
        <small className="mt-[3px] text-xs text-tinta-suave max-tableta:hidden">CRM Comercial Educativo</small>
      </span>
    </Link>
  )
}

function Publico({ children }) {
  const { path } = useAppRoute()
  const { usuario, menu } = useAuth()
  const enRetornoPago = path.startsWith('/pagos/')
  return (
    <div data-zona="oferta" className="flex min-h-dvh flex-col">
      <a className={SALTAR} href="#contenido">Saltar al contenido</a>
      <header className={ENCABEZADO}>
        <Marca />
        {/* El login y el retorno de pago mantienen el encabezado limpio sin buscador interno. */}
        {path !== '/login' && !enRetornoPago && <Buscador className={BUSCADOR} placeholder="Buscar programa o módulo…" />}
        <div className={ACCIONES}>
          <BotonTema />
          <Apariencia />
          {!enRetornoPago && (usuario
            ? <Link className="btn btn-primario" to={menu?.[0]?.ruta || '/anuncios'}>Ir al panel</Link>
            : path !== '/login' && <Link className="btn btn-primario" to="/login">Iniciar sesión</Link>)}
        </div>
      </header>
      <main id="contenido" className="flex flex-1 flex-col *:shrink-0">{children}</main>
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
  // Riel cerrado (solo en escritorio): quedan los íconos; en celular el riel es un cajón que se abre encima.
  const oculto = cerrado ? 'tableta:hidden' : ''
  return (
    <div className={`grid min-h-dvh grid-cols-[minmax(0,1fr)] ${cerrado ? 'tableta:grid-cols-[76px_minmax(0,1fr)]' : 'tableta:grid-cols-[264px_minmax(0,1fr)]'}`}>
      <a className={SALTAR} href="#contenido">Saltar al contenido</a>
      <aside aria-label="Menú principal" className={`app-riel flex h-dvh flex-col overflow-y-auto bg-riel text-riel-tinta contraste:bg-black
        tableta:sticky tableta:top-0 max-tableta:fixed max-tableta:inset-y-0 max-tableta:left-0 max-tableta:z-60 max-tableta:w-[min(300px,86vw)]
        max-tableta:transition-transform max-tableta:duration-[260ms] max-tableta:ease-curva ${movil ? 'max-tableta:shadow-capa' : 'max-tableta:-translate-x-[102%]'}`}>
        <Link to={menu?.[0]?.ruta || '/anuncios'} className="flex min-h-[68px] items-center gap-2.5 border-b border-riel-borde px-[18px] text-riel-marca no-underline">
          <img src={logo} alt="" width="34" height="34" className="size-[34px] rounded-ui bg-white p-[3px]" />
          <strong className={`text-[1.15rem] font-extrabold tracking-[0.02em] ${oculto}`}>U<span className="text-turquesa">NEXO</span></strong>
        </Link>
        <nav aria-label="Módulos" className="flex flex-col gap-0.5 px-2 py-3">
          {menu.map((item) => {
            const grupo = GRUPOS[Math.floor(item.orden / 10)] || null
            const titulo = grupo !== grupoPrevio ? grupo : null
            grupoPrevio = grupo
            const Icono = ICONOS[item.icono] || Circle
            return (
              <Fragment key={item.codigo}>
                {titulo && <div className={`mx-3 mt-4 mb-1 text-xs font-bold text-riel-suave ${oculto}`}>{titulo}</div>}
                <Link to={item.ruta} aria-current={item.ruta === path ? 'page' : undefined} title={cerrado ? item.nombre : undefined}
                  className={`flex items-center gap-3 rounded-ui px-3 py-2.5 font-[550] text-riel-tinta no-underline transition-colors duration-150 ease-curva
                    hover:bg-riel-hover hover:text-riel-tinta aria-[current=page]:bg-riel-activo aria-[current=page]:text-riel-activo-tinta ${cerrado ? 'tableta:justify-center' : ''}`}>
                  <Icono size={19} aria-hidden="true" className={`shrink-0 ${item.ruta === path ? '' : 'opacity-85'}`} /><span className={oculto}>{item.nombre}</span>
                </Link>
              </Fragment>
            )
          })}
        </nav>
        <div className={`mt-auto border-t border-riel-borde px-[18px] py-4 text-xs text-riel-suave ${oculto}`}>Menú según su rol · matriz de acceso</div>
      </aside>
      {movil && <div className="fixed inset-0 z-55 bg-[rgb(4_29_49/0.5)] tableta:hidden" onClick={() => setMovil(false)} aria-hidden="true" />}
      <div className="flex min-w-0 flex-col">
        <header className={ENCABEZADO}>
          <button type="button" className="btn btn-texto btn-icono" onClick={alternar} aria-label="Mostrar u ocultar el menú" title="Menú"><Menu size={22} /></button>
          <div className="min-w-0 max-movil:flex-1"><h1 className="truncate text-xl" title={actual ? `Caso de uso ${actual.caso_uso}` : undefined}>{actual?.nombre}</h1></div>
          <Buscador className={BUSCADOR} />
          <div className={ACCIONES}><BotonTema /><Apariencia /><Perfil /></div>
        </header>
        <main id="contenido" className="min-w-0 flex-1 p-[clamp(16px,2.4vw,32px)]"><div className="mx-auto w-full max-w-[1440px]">{children}</div></main>
        <Pie />
      </div>
    </div>
  )
}
