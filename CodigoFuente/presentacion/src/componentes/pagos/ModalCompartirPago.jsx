import { useEffect, useRef, useState } from 'react'
import { Check, Copy, Mail, MessageCircle } from 'lucide-react'
import { Aviso, Boton, Campo, Cargando, Modal, fecha, nombre } from '../ui'
import { apiErrorMessage } from '../../servicios/errors'
import {
  copiarAlPortapapeles, mensajeWhatsAppPago, mensajeWhatsAppSetup, normalizarTelefonoBolivia,
  plantillaCorreoPago, plantillaCorreoSetup, urlWhatsApp,
} from '../../servicios/pagosCompartir'
import { bsPago } from './ResumenPagos'
import * as notificacionesApi from '../../api/notificaciones'
import * as pagosApi from '../../api/pagos'

/**
 * Modal único para compartir solicitudes de pago de cuotas o registro remoto de tarjeta (Stripe Setup).
 * Reutiliza la sesión vigente sin exponer URLs extensas ni detalles técnicos permanentes.
 */
export default function ModalCompartirPago({ modo, t, orden = null, cuota = null, onCerrar, aviso, onCambio }) {
  const [sesion, setSesion] = useState({ cargando: true, url: null, urlCorreo: null, error: null })
  const [vistaCorreo, setVistaCorreo] = useState(false)
  const [copiado, setCopiado] = useState(false)
  const [copiaManual, setCopiaManual] = useState(false)
  const [enviandoCorreo, setEnviandoCorreo] = useState(false)
  const [errorCorreo, setErrorCorreo] = useState(null)
  const inputManualRef = useRef(null)

  const prospectoNombre = nombre(t.prospecto)
  const programa = orden?.items?.[0]?.programa_nombre || t.programa_nombre
  const modulo = orden?.items?.map((i) => i.modulo_nombre).join(', ') || t.modulo_nombre
  const totalCuotas = orden?.cuotas?.length || 1

  const [correoForm, setCorreoForm] = useState({ destinatario: t.prospecto?.correo || '', tipo: '', mensaje: '' })

  useEffect(() => {
    let activo = true
    ;(async () => {
      try {
        const { data } = modo === 'setup'
          ? await pagosApi.crearSetupTarjeta(t.documento, t.nro_tarjeta)
          : await pagosApi.crearCheckout(orden.nro_orden, cuota.nro_cuota)
        if (!activo) return
        const urlStripe = data.url
        const urlEmail = data.url_cuota || data.url
        setSesion({ cargando: false, url: urlStripe, urlCorreo: urlEmail, error: null })

        const tpl = modo === 'setup'
          ? plantillaCorreoSetup({ prospectoNombre, programa, enlace: urlEmail })
          : plantillaCorreoPago({
              prospectoNombre,
              programa,
              modulo,
              ordenNro: orden.nro_orden,
              cuotaNro: cuota.nro_cuota,
              totalCuotas,
              monto: cuota.monto,
              vencimiento: fecha(cuota.fecha_vencimiento),
              enlace: urlEmail,
            })
        setCorreoForm({ destinatario: t.prospecto?.correo || '', tipo: tpl.asunto, mensaje: tpl.mensaje })
      } catch (err) {
        if (activo) setSesion({ cargando: false, url: null, urlCorreo: null, error: apiErrorMessage(err) })
      }
    })()
    return () => { activo = false }
  }, [modo, t.documento, t.nro_tarjeta, orden?.nro_orden, cuota?.nro_cuota])

  function compartirPorWhatsApp() {
    if (!sesion.url) return
    const tel = normalizarTelefonoBolivia(t.prospecto?.telefono)
    if (!tel.valido) {
      aviso.error(tel.error)
      return
    }
    const mensaje = modo === 'setup'
      ? mensajeWhatsAppSetup({ prospectoNombre, programa, enlace: sesion.url })
      : mensajeWhatsAppPago({
          prospectoNombre,
          programa,
          ordenNro: orden.nro_orden,
          cuotaNro: cuota.nro_cuota,
          totalCuotas,
          monto: cuota.monto,
          vencimiento: fecha(cuota.fecha_vencimiento),
          enlace: sesion.url,
        })
    window.open(urlWhatsApp(tel.telefono, mensaje), '_blank', 'noopener,noreferrer')
  }

  async function copiarEnlace() {
    if (!sesion.url) return
    const ok = await copiarAlPortapapeles(sesion.url)
    if (ok) {
      setCopiado(true)
      aviso.ok('Enlace copiado correctamente.')
      setTimeout(() => setCopiado(false), 2500)
    } else {
      setCopiaManual(true)
      setTimeout(() => inputManualRef.current?.select(), 50)
    }
  }

  async function enviarCorreo(e) {
    e.preventDefault()
    if (!sesion.urlCorreo || enviandoCorreo) return
    setEnviandoCorreo(true)
    setErrorCorreo(null)
    try {
      const { data } = await notificacionesApi.enviar({
        destinatario: correoForm.destinatario.trim(),
        tipo: correoForm.tipo.trim(),
        mensaje: correoForm.mensaje,
        enlace: sesion.urlCorreo,
        texto_boton: modo === 'setup' ? 'Registrar tarjeta' : 'Completar pago',
      })
      aviso.ok(data.mensaje)
      onCambio?.()
      onCerrar()
    } catch (err) {
      setErrorCorreo(apiErrorMessage(err, 'No se pudo enviar el correo por SMTP.'))
    } finally {
      setEnviandoCorreo(false)
    }
  }

  const titulo = modo === 'setup' ? 'Solicitar registro de tarjeta' : 'Enviar solicitud de pago'
  const descripcion = modo === 'setup'
    ? 'El cliente introducirá su tarjeta directamente en Stripe Sandbox.'
    : 'Comparte el enlace seguro para que el cliente realice el pago.'

  return (
    <Modal titulo={titulo} descripcion={descripcion} onCerrar={onCerrar}>
      <dl className="grid grid-cols-2 gap-3 rounded-ui border border-filete bg-niebla-2 p-3.5 text-sm max-movil:grid-cols-1">
        <div>
          <dt className="text-xs text-tinta-suave">Cliente</dt>
          <dd className="font-semibold">{prospectoNombre}</dd>
        </div>
        <div>
          <dt className="text-xs text-tinta-suave">Programa</dt>
          <dd className="font-semibold">{programa}</dd>
        </div>
        {modo === 'cuota' && (
          <>
            <div>
              <dt className="text-xs text-tinta-suave">Cuota</dt>
              <dd className="tabular-nums">{cuota.nro_cuota} de {totalCuotas}</dd>
            </div>
            <div>
              <dt className="text-xs text-tinta-suave">Vencimiento · Monto</dt>
              <dd className="font-semibold tabular-nums">{fecha(cuota.fecha_vencimiento)} · {bsPago(cuota.monto)}</dd>
            </div>
          </>
        )}
      </dl>

      {sesion.cargando ? (
        <Cargando filas={2} />
      ) : sesion.error ? (
        <Aviso tipo="error">{sesion.error}</Aviso>
      ) : (
        <>
          <div className="grid gap-2">
            <button type="button" className="btn btn-acento justify-start" onClick={compartirPorWhatsApp}>
              <MessageCircle size={17} /> Enviar por WhatsApp
            </button>
            <button type="button" className="btn btn-primario justify-start" onClick={() => setVistaCorreo((v) => !v)}>
              <Mail size={17} /> Enviar por correo electrónico
            </button>
            <button type="button" className="btn btn-secundario justify-start" onClick={copiarEnlace}>
              {copiado ? <Check size={17} /> : <Copy size={17} />} {copiado ? 'Enlace copiado correctamente' : 'Copiar enlace de pago'}
            </button>
          </div>

          {copiaManual && (
            <Campo etiqueta="Copia manual del enlace" ayuda="Selecciona y presiona Ctrl+C.">
              <input ref={inputManualRef} type="text" readOnly value={sesion.url} onFocus={(e) => e.target.select()} />
            </Campo>
          )}

          {vistaCorreo && (
            <form className="grid gap-3 border-t border-filete pt-4" onSubmit={enviarCorreo}>
              <Campo etiqueta="Destinatario" requerido>
                <input
                  type="email"
                  required
                  maxLength={160}
                  value={correoForm.destinatario}
                  onChange={(e) => setCorreoForm({ ...correoForm, destinatario: e.target.value })}
                />
              </Campo>
              <Campo etiqueta="Asunto" requerido>
                <input
                  required
                  maxLength={120}
                  value={correoForm.tipo}
                  onChange={(e) => setCorreoForm({ ...correoForm, tipo: e.target.value })}
                />
              </Campo>
              <Campo etiqueta="Mensaje" requerido>
                <textarea
                  rows={5}
                  required
                  minLength={3}
                  maxLength={5000}
                  value={correoForm.mensaje}
                  onChange={(e) => setCorreoForm({ ...correoForm, mensaje: e.target.value })}
                />
              </Campo>
              <Aviso tipo="error">{errorCorreo}</Aviso>
              <div className="acciones">
                <Boton type="submit" className="btn-primario" cargando={enviandoCorreo}>
                  <Mail size={15} /> {errorCorreo ? 'Reintentar envío' : 'Confirmar y enviar'}
                </Boton>
              </div>
            </form>
          )}
        </>
      )}

      <div className="acciones">
        <button type="button" className="btn btn-secundario" onClick={onCerrar}>Cancelar</button>
      </div>
    </Modal>
  )
}
