import { useState } from 'react'
import { Mail } from 'lucide-react'
import { puede, useAuth } from '../servicios/auth'
import { Aviso, Boton, CabeceraPagina, Campo, Cargando, Etiqueta, Vacio, erroresDe, fecha, useAviso, useDatos } from '../componentes/ui'
import * as notificacionesApi from '../api/notificaciones'

/** CU7: avisos por correo a un prospecto de la cartera o al equipo, con el registro de cada envío. */
export default function PNotificaciones() {
  const sesion = useAuth()
  const puedeEnviar = puede('notificaciones', 'modificacion', sesion) || puede('agenda', 'modificacion', sesion)
  const { datos, cargando, error, recargar } = useDatos(async () => (await notificacionesApi.index()).data.notificaciones, [], { intervaloMs: 5000, refrescarAlEnfocar: true })
  const [form, setForm] = useState({ destinatario: '', tipo: '', mensaje: '' })
  const [errores, setErrores] = useState({})
  const [enviando, setEnviando] = useState(false)
  const aviso = useAviso()

  async function enviar(e) {
    e.preventDefault()
    setEnviando(true)
    try {
      aviso.ok((await notificacionesApi.enviar(form)).data.mensaje)
      setForm({ destinatario: '', tipo: '', mensaje: '' })
      setErrores({})
      recargar()
    } catch (err) { setErrores(erroresDe(err)); aviso.error(err) } finally { setEnviando(false) }
  }

  return (
    <>
      <CabeceraPagina titulo="Notificaciones">Correos enviados desde el CRM y su estado.</CabeceraPagina>
      <div className={puedeEnviar ? 'grid grid-cols-[minmax(0,3fr)_minmax(0,2fr)] items-start gap-6 max-movil:grid-cols-1' : ''}>
        {puedeEnviar && (
          <form className="hoja hoja-cuerpo grid gap-4" onSubmit={enviar}>
            <h3>Enviar correo</h3>
            <Campo etiqueta="Para" requerido error={errores.destinatario}><input type="email" required maxLength={160} value={form.destinatario} onChange={(e) => setForm({ ...form, destinatario: e.target.value })} placeholder="correo del prospecto" /></Campo>
            <Campo etiqueta="Asunto" requerido error={errores.tipo}><input required maxLength={120} value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })} /></Campo>
            <Campo etiqueta="Mensaje" requerido error={errores.mensaje}><textarea required minLength={3} maxLength={5000} value={form.mensaje} onChange={(e) => setForm({ ...form, mensaje: e.target.value })} /></Campo>
            <div className="acciones"><Boton type="submit" cargando={enviando}>Enviar</Boton></div>
          </form>
        )}
        <section className="hoja">
          <header className="hoja-titulo"><h3>Enviadas</h3></header>
          {error && <Aviso tipo="error">{error}</Aviso>}
          {cargando && !datos ? <div className="hoja-cuerpo"><Cargando /></div> : !datos?.length ? <Vacio titulo="Sin notificaciones" icono={Mail} /> : (
            <ul>{datos.map((n) => (
              <li key={n.nro_notificacion} className="grid gap-1 border-b border-filete px-3.5 py-3">
                <span className="flex justify-between gap-2"><strong>{n.tipo}</strong><Etiqueta estado={n.estado} /></span>
                <small className="text-tinta-suave">Para {n.destinatario} · {fecha(n.fecha_envio, true)}</small>
                <p className="text-sm">{n.mensaje}</p>
                {n.estado !== 'leida' && <button type="button" className="btn btn-texto justify-self-start" onClick={async () => { await notificacionesApi.marcarLeida(n.nro_notificacion); recargar() }}>Marcar como leída</button>}
              </li>
            ))}</ul>
          )}
        </section>
      </div>
      {aviso.nodo}
    </>
  )
}
