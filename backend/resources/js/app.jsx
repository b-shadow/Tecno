import '@fontsource-variable/source-serif-4/opsz.css'
import '@fontsource-variable/public-sans/wght.css'
import '@fontsource-variable/bricolage-grotesque/wght.css'
import '@fontsource-variable/fredoka/wght.css'
import '@fontsource-variable/nunito/wght.css'
import '@fontsource/atkinson-hyperlegible/400.css'
import '@fontsource/atkinson-hyperlegible/700.css'
import './styles/tokens.css'
import './styles/base.css'
import './styles/layout.css'
import './styles/components.css'
import './styles/catalogo.css'
import './styles/panel.css'
import './services/validation'
import './services/theme'

import { createRoot } from 'react-dom/client'
import { createInertiaApp } from '@inertiajs/react'
import { resolvePageComponent } from 'laravel-vite-plugin/inertia-helpers'
import AppShell from './layouts/AppShell'

// Capa de presentación (React). Laravel sirve la plantilla con Inertia; los datos vienen de la API REST.
createInertiaApp({
  title: (title) => (title ? `${title} · UNEXO` : 'UNEXO · CRM Comercial Educativo'),
  resolve: async (name) => {
    const page = await resolvePageComponent(`./Pages/${name}.jsx`, import.meta.glob('./Pages/**/*.jsx'))
    page.default.layout ??= (contenido) => <AppShell>{contenido}</AppShell>
    return page
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />)
  },
  progress: { color: '#10aeb5' },
})
