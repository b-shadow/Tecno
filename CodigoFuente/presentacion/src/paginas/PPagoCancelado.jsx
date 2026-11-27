import { useEffect, useState } from 'react'
import { RotateCcw, XCircle } from 'lucide-react'
import { Aviso, CabeceraPagina, Cargando, bs } from '../componentes/ui'
import { apiErrorMessage } from '../servicios/errors'
import { useAuth } from '../servicios/auth'
import { go, useAppRoute } from '../servicios/navigation'
import * as pagosApi from '../api/pagos'

/** CU6: retorno seguro cuando el cliente cancela o retrocede desde Stripe Checkout. */
export default function PPagoCancelado() {
  const { query } = useAppRoute()
  const sesion = useAuth()
  const sessionId = query.session_id || ''
  const token = query.token || ''
  const [estado, setEstado] = useState({ cargando: Boolean(sessionId), datos: null, error: null })
  const esVistaPublica = Boolean(token) || !sesion.usuario

  useEffect(() => {
    let activo = true
    if (!sessionId) {
      setEstado({ cargando: false, datos: null, error: null })
      return () => { activo = false }
    }
    if (!token && !sesion.token) {
      setEstado({ cargando: false, datos: null, error: 'El enlace de retorno requiere un token de verificación válido.' })
      return () => { activo = false }
    }
    ;(async () => {
      try {
        const { data } = token
          ? await pagosApi.cancelarRetornoPublico(sessionId, token)
          : await pagosApi.cancelarCheckout(sessionId)
        if (activo) setEstado({ cargando: false, datos: data, error: null })
      } catch (err) {
        if (activo) setEstado({ cargando: false, datos: null, error: apiErrorMessage(err) })
      }
    })()
    return () => { activo = false }
  }, [sessionId, token, sesion.token])

  const d = estado.datos
  const esSetup = d?.tipo === 'setup'
  const pendiente = d && d.estado_interno !== 'confirmado' && d.estado_interno !== 'expirado'
  const monto = d?.importe ?? d?.monto ?? 0
  const rutaConfirmacion = token
    ? `/pagos/confirmacion?session_id=${encodeURIComponent(sessionId)}&token=${encodeURIComponent(token)}`
    : `/pagos/confirmacion?session_id=${encodeURIComponent(sessionId)}`

  return (
    <div className="mx-auto w-full max-w-[920px] px-4 py-6">
      <CabeceraPagina titulo={esSetup ? 'Registro de tarjeta no completado' : 'Pago no completado'}>
        {esSetup
          ? 'El registro de tarjeta en Stripe Checkout fue cancelado o quedó inconcluso. No se ha realizado ningún cobro.'
          : 'La operación en Stripe Checkout fue cancelada o quedó inconclusa. No se registró ningún cobro en UNEXO y tu orden continúa activa.'}
      </CabeceraPagina>

      <section className="hoja hoja-cuerpo grid gap-4">
        {estado.cargando ? <Cargando filas={3} /> : (
          <>
            <div className="flex items-center gap-3">
              <XCircle size={24} className="text-tinta-suave" aria-hidden="true" />
              <div>
                <h2>
                  {d?.estado_interno === 'confirmado'
                    ? (esSetup ? 'La tarjeta ya figuraba registrada' : 'El pago ya figuraba confirmado')
                    : (esSetup ? 'Registro de tarjeta no completado' : 'Pago no completado')}
                </h2>
                <p className="text-sm text-tinta-suave">
                  {d?.estado_interno === 'confirmado'
                    ? 'Stripe confirmó esta operación antes de regresar.'
                    : d?.estado_interno === 'expirado'
                      ? 'Esta sesión expiró. Solicita un nuevo enlace a tu asesor en UNEXO.'
                      : 'No se ha realizado ningún cobro. Puedes continuar utilizando el mismo enlace mientras la sesión siga vigente.'}
                </p>
              </div>
            </div>

            {estado.error && <Aviso tipo="error">{estado.error}</Aviso>}

            {d?.tipo === 'payment' && (
              <dl className="grid grid-cols-[repeat(auto-fit,minmax(190px,1fr))] gap-4 rounded-ui border border-filete p-4">
                <div><dt className="text-xs text-tinta-suave">Programa educativo</dt><dd className="font-semibold">{d.programa || '—'}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Cuota</dt><dd className="tabular-nums">{d.nro_cuota} de {d.total_cuotas}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Importe ({d.moneda || 'BOB'})</dt><dd className="tabular-nums">{bs(monto)}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Estado actual</dt><dd>{d.estado_cuota || d.estado_interno}</dd></div>
              </dl>
            )}

            <p className="rounded-ui border border-filete bg-niebla-2 px-3 py-2 text-xs text-tinta-suave">
              {d?.aviso_sandbox || 'Operación de demostración mediante Stripe Sandbox (moneda BOB, sin movimiento real de dinero).'}
            </p>

            <div className="acciones justify-start flex-wrap">
              {esVistaPublica
                ? <button type="button" className="btn btn-secundario" onClick={() => go('/anuncios')}>Volver al sitio web</button>
                : <button type="button" className="btn btn-secundario" onClick={() => go(d?.nro_tarjeta ? `/agenda?interes=${d.nro_tarjeta}` : '/agenda')}>Volver a la orden</button>}

              {pendiente && d?.url_checkout && (
                <button type="button" className="btn btn-primario" onClick={() => window.location.assign(d.url_checkout)}>
                  <RotateCcw size={16} /> {esSetup ? 'Continuar registro en Stripe' : 'Continuar pago en Stripe'}
                </button>
              )}
              {d?.estado_interno === 'confirmado' && sessionId && (
                <button type="button" className="btn btn-primario" onClick={() => go(rutaConfirmacion)}>
                  Ver confirmación
                </button>
              )}
            </div>
          </>
        )}
      </section>
    </div>
  )
}
