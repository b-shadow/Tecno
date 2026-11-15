import './style.css'
import './services/validation'

import { createApp, h } from 'vue'
import { createInertiaApp } from '@inertiajs/vue3'
import { resolvePageComponent } from 'laravel-vite-plugin/inertia-helpers'
import AppShell from './layouts/AppShell.vue'

createInertiaApp({
  title: (title) => (title ? `${title} - CRM Comercial Educativo` : 'CRM Comercial Educativo'),
  resolve: async (name) => {
    const page = await resolvePageComponent(`./Pages/${name}.vue`, import.meta.glob('./Pages/**/*.vue'))
    // Layout persistente: elige el layout publico o interno y aplica las reglas de acceso.
    page.default.layout ??= AppShell
    return page
  },
  setup({ el, App, props, plugin }) {
    createApp({ render: () => h(App, props) })
      .use(plugin)
      .mount(el)
  },
  progress: {
    color: '#10aeb5',
  },
})
