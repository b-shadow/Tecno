import { Component } from 'react'
import { isRouteErrorResponse, useRouteError } from 'react-router-dom'

/**
 * Límite de error reutilizable para aislar fallos de renderizado en secciones específicas
 * sin derribar toda la interfaz. Siempre registra el error real en consola para diagnóstico.
 */
export class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error(`[UNEXO ErrorBoundary:${this.props.nombreSeccion || 'general'}]`, error, info?.componentStack || '')
  }

  render() {
    const { error } = this.state
    if (!error) return this.props.children

    const seccion = this.props.nombreSeccion || 'esta sección'
    return (
      <section className="hoja hoja-cuerpo grid gap-3" role="alert">
        <h3>No se pudo mostrar {seccion}</h3>
        <p className="text-sm text-tinta-suave">
          Ocurrió un error inesperado al renderizar este bloque. El resto del sistema sigue operativo.
        </p>
        {error?.message && (
          <details className="rounded-ui border border-filete bg-niebla-2 p-3 text-xs">
            <summary className="cursor-pointer font-semibold">Detalle técnico para diagnóstico</summary>
            <pre className="mt-2 overflow-auto whitespace-pre-wrap">{error.message}</pre>
          </details>
        )}
        <div className="acciones justify-start">
          <button
            type="button"
            className="btn btn-primario"
            onClick={() => this.setState({ error: null })}
          >
            Reintentar sección
          </button>
          <button
            type="button"
            className="btn btn-secundario"
            onClick={() => window.location.reload()}
          >
            Recargar navegador
          </button>
        </div>
      </section>
    )
  }
}

/** Captura errores a nivel de ruta de React Router manteniendo registro real y opción de recuperación. */
export function ErrorRuta() {
  const error = useRouteError()
  console.error('[UNEXO RouterError]', error)
  const detalle = isRouteErrorResponse(error)
    ? `${error.status} ${error.statusText}`
    : (error?.message || 'Error desconocido al cargar la ruta.')

  return (
    <main className="mx-auto my-8 w-full max-w-[720px] px-4">
      <section className="hoja hoja-cuerpo grid gap-3" role="alert">
        <h2>No se pudo cargar la pantalla</h2>
        <p className="text-sm text-tinta-suave">
          Se produjo un problema técnico en esta vista. Puedes reintentar o volver al inicio.
        </p>
        <details className="rounded-ui border border-filete bg-niebla-2 p-3 text-xs">
          <summary className="cursor-pointer font-semibold">Detalle técnico para diagnóstico</summary>
          <pre className="mt-2 overflow-auto whitespace-pre-wrap">{detalle}</pre>
        </details>
        <div className="acciones justify-start">
          <button type="button" className="btn btn-primario" onClick={() => window.location.reload()}>
            Recargar pantalla
          </button>
          <a className="btn btn-secundario" href="/anuncios">Ir al inicio</a>
        </div>
      </section>
    </main>
  )
}
