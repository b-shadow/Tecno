import { Navigate, createBrowserRouter } from 'react-router-dom'
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
  children: [
    { path: '/', element: <Navigate to="/anuncios" replace /> },
    ...Object.entries(PAGINAS).map(([path, nombre]) => ({ path, lazy: pagina(nombre) })),
    // Ruta inexistente: página de error con el contador del recurso /error.
    { path: '*', lazy: pagina('PError404'), handle: { recurso: '/error' } },
  ],
}], { basename: import.meta.env.BASE_URL.replace(/\/$/, '') || '/' })

fijarRouter(router)
