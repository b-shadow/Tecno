import { Navigate, createBrowserRouter } from 'react-router-dom'
import { ErrorRuta } from './componentes/ErrorBoundary'
import AppShell from './plantilla/AppShell'
import { fijarRouter } from './servicios/navigation'

// Una ruta por página del diagrama de navegación. El acceso real lo decide el menú del rol (BD) en AppShell
// y la API vuelve a validarlo en cada llamada (middleware acceso:).
const pagina = (nombre) => () => import(`./paginas/${nombre}.jsx`).then((m) => ({ Component: m.default }))

const PAGINAS = {
  '/anuncios': 'PCatalogo', '/gestion-anuncios': 'PCatalogo', '/login': 'PLogin',
  '/dashboard': 'PDashboard', '/inicio-vendedor': 'PMiDia', '/embudo': 'PEmbudo',
  '/prospectos': 'PProspectos', '/interesados': 'PAsignacion', '/agenda': 'PAgenda', '/motivos-perdida': 'PMotivos',
  '/validacion-pagos': 'PValidacionPagos', '/alumnos': 'PMatriculas', '/seguimiento': 'PComisiones',
  '/reportes': 'PReportes', '/notificaciones': 'PNotificaciones',
  '/usuarios': 'PUsuarios', '/matriz-acceso': 'PMatriz', '/bitacora': 'PBitacora',
}

export const router = createBrowserRouter([{
  element: <AppShell />,
  errorElement: <ErrorRuta />,
  children: [
    { path: '/', element: <Navigate to="/anuncios" replace /> },
    ...Object.entries(PAGINAS).map(([path, nombre]) => ({ path, lazy: pagina(nombre), errorElement: <ErrorRuta /> })),
    { path: '/pagos/cuota', lazy: pagina('PPagoCuota'), handle: { recurso: '/anuncios' }, errorElement: <ErrorRuta /> },
    { path: '/pagos/confirmacion', lazy: pagina('PPagoConfirmacion'), handle: { recurso: '/anuncios' }, errorElement: <ErrorRuta /> },
    { path: '/pagos/cancelado', lazy: pagina('PPagoCancelado'), handle: { recurso: '/anuncios' }, errorElement: <ErrorRuta /> },
    // Ruta inexistente: página de error con el contador del recurso /error.
    { path: '*', lazy: pagina('PError404'), handle: { recurso: '/error' }, errorElement: <ErrorRuta /> },
  ],
}], { basename: import.meta.env.BASE_URL.replace(/\/$/, '') || '/' })

fijarRouter(router)
