import '@fontsource-variable/source-serif-4/opsz.css'
import '@fontsource-variable/public-sans/wght.css'
import '@fontsource-variable/bricolage-grotesque/wght.css'
import '@fontsource-variable/fredoka/wght.css'
import '@fontsource-variable/nunito/wght.css'
import '@fontsource/atkinson-hyperlegible/400.css'
import '@fontsource/atkinson-hyperlegible/700.css'
import './estilos/tokens.css'
import './estilos/base.css'
import './estilos/layout.css'
import './estilos/components.css'
import './estilos/catalogo.css'
import './estilos/panel.css'
import './servicios/validation'
import './servicios/theme'

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { router } from './rutas'

// Capa 1 (presentación): SPA de React. Todos los datos llegan de la API REST de Laravel (capa 2) por api/.
createRoot(document.getElementById('app')).render(<StrictMode><RouterProvider router={router} /></StrictMode>)
