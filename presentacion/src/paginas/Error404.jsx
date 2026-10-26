import { Link } from 'react-router-dom'
import { CircleSlash } from 'lucide-react'
import { Vacio } from '../componentes/ui'

/** Página de error del diagrama de navegación: la dirección no existe. Su contador es el del recurso /error. */
export default function Error404() {
  return (
    <div className="contenido-ancho">
      <Vacio titulo="Página no encontrada" icono={CircleSlash}>
        La dirección que abrió no existe o cambió de lugar.
        {' '}<Link to="/anuncios">Ir al catálogo</Link>
      </Vacio>
    </div>
  )
}
