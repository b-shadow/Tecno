import { useEffect, useState } from 'react'
import { RotateCcw, XCircle } from 'lucide-react'
import { Aviso, Boton, CabeceraPagina, Cargando, bs } from '../componentes/ui'
import { apiErrorMessage } from '../servicios/errors'
import { go, useAppRoute } from '../servicios/navigation'
import * as pagosApi from '../api/pagos'

/** CU6: retorno cuando el usuario cancela o retrocede desde Stripe Checkout. */
export default function PPagoCancelado() {
  const { query } = useAppRoute()
  const sessionId = query.session_id || ''
  const [estado, setEstado] = useState({ cargando: Boolean(sessionId), datos: null, error: null })
  const [reintentando, setReintentando] = useState(false)

  useEffect(() => {
    let activo = true
    if (!sessionId) {
      setEstado({ cargando: false, datos: null, error: null })
      return () => { activo = false }
    }
    ;(async () => {
      try {
        const { data } = await pagosApi.cancelarCheckout(sessionId)
        if (activo) setEstado({ cargando: false, datos: data, error: null })
      } catch (err) {
        if (activo) setEstado({ cargando: false, datos: null, error: apiErrorMessage(err) })
      }
    })()
    return () => { activo = false }
  }, [sessionId])

  async function reintentarPago() {
    if (!estado.datos?.nro_orden || !estado.datos?.nro_cuota) return
    setReintentando(true)
    try {
      const { data } = await pagosApi.crearCheckout(estado.datos.nro_orden, estado.datos.nro_cuota)
      window.location.assign(data.url)
    } catch (err) {
      setEstado((prev) => ({ ...prev, error: apiErrorMessage(err) }))
      setReintentando(false)
    }
  }

  const d = estado.datos
  const pendiente = d && d.tipo === 'payment' && !['Pago aprobado', 'En revision'].includes(d.estado_cuota || '')

  return (
    <>
      <CabeceraPagina titulo="Pago no completado">
        La operación en Stripe Checkout fue cancelada o quedó inconclusa. No se registró ningún cobro en UNEXO.
      </CabeceraPagina>

      <section className="hoja hoja-cuerpo grid gap-4">
        {estado.cargando ? <Cargando filas={3} /> : (
          <>
            <div className="flex items-center gap-3">
              <XCircle size={24} className="text-tinta-suave" aria-hidden="true" />
              <div>
                <h2>{d?.estado_interno === 'confirmado' ? 'El pago ya figuraba confirmado' : 'Pago no completado'}</h2>
                <p className="text-sm text-tinta-suave">
                  {d?.estado_interno === 'confirmado'
                    ? 'Stripe confirmó esta transacción antes de regresar.'
                    : 'Puede volver a la orden de pago e intentarlo nuevamente mientras la cuota siga pendiente.'}
                </p>
              </div>
            </div>

            {estado.error && <Aviso tipo="error">{estado.error}</Aviso>}

            {d?.tipo === 'payment' && (
              <dl className="grid grid-cols-[repeat(auto-fit,minmax(190px,1fr))] gap-4 rounded-ui border border-filete p-4">
                <div><dt className="text-xs text-tinta-suave">Prospecto</dt><dd className="font-semibold">{d.prospecto || '—'}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Orden · cuota</dt><dd className="tabular-nums">#{d.nro_orden} · cuota {d.nro_cuota} de {d.total_cuotas}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Monto ({d.moneda || 'BOB'})</dt><dd className="tabular-nums">{bs(d.monto)}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Estado actual</dt><dd>{d.estado_cuota || d.estado_interno}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Saldo pendiente</dt><dd className="tabular-nums">{bs(d.saldo_pendiente)}</dd></div>
              </dl>
            )}

            <div className="acciones justify-start flex-wrap">
              <button type="button" className="btn btn-secundario" onClick={() => go(d?.nro_tarjeta ? `/agenda?interes=${d.nro_tarjeta}` : '/agenda')}>
                Volver a la orden
              </button>
              {pendiente && (
                <Boton cargando={reintentando} onClick={reintentarPago}>
                  <RotateCcw size={16} /> Intentar nuevamente
                </Boton>
              )}
              {d?.estado_interno === 'confirmado' && sessionId && (
                <button type="button" className="btn btn-primario" onClick={() => go(`/pagos/confirmacion?session_id=${encodeURIComponent(sessionId)}`)}>
                  Ver confirmación
                </button>
              )}
            </div>
          </>
        )}
      </section>
    </>
  )
}
