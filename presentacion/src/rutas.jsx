import { Navigate, createBrowserRouter } from 'react-router-dom'
import AppShell from './plantilla/AppShell'
import { fijarRouter } from './servicios/navigation'

// Una ruta por página del diagrama de navegación. El acceso real lo decide el menú del rol (BD) en AppShell
// y la API vuelve a validarlo en cada llamada (middleware acceso:).
const pagina = (nombre) => () => import(`./paginas/${nombre}.jsx`).then((m) => ({ Component: m.default }))

const PAGINAS = {
  '/anuncios': 'Catalogo', '/gestion-anuncios': 'Catalogo', '/login': 'Login',
  '/dashboard': 'Dashboard', '/inicio-vendedor': 'MiDia', '/embudo': 'Embudo',
  '/prospectos': 'Prospectos', '/interesados': 'Asignacion', '/agenda': 'Agenda', '/motivos-perdida': 'Motivos',
  '/validacion-pagos': 'ValidacionPagos', '/alumnos': 'Matriculas', '/seguimiento': 'Comisiones',
  '/reportes': 'Reportes', '/notificaciones': 'Notificaciones',
  '/usuarios': 'Usuarios', '/matriz-acceso': 'Matriz', '/bitacora': 'Bitacora',
}

export const router = createBrowserRouter([{
  element: <AppShell />,
  children: [
    { path: '/', element: <Navigate to="/anuncios" replace /> },
    ...Object.entries(PAGINAS).map(([path, nombre]) => ({ path, lazy: pagina(nombre) })),
    // Ruta inexistente: página de error con el contador del recurso /error.
    { path: '*', lazy: pagina('Error404'), handle: { recurso: '/error' } },
  ],
}], { basename: import.meta.env.BASE_URL.replace(/\/$/, '') || '/' })

fijarRouter(router)
