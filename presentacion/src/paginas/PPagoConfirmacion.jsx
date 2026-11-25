import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle2, Clock, CreditCard, ExternalLink, Printer, XCircle } from 'lucide-react'
import { Aviso, CabeceraPagina, Cargando, Etiqueta, bs, fecha } from '../componentes/ui'
import { apiErrorMessage } from '../servicios/errors'
import { go, useAppRoute } from '../servicios/navigation'
import * as pagosApi from '../api/pagos'

/** CU6: pantalla de retorno oficial tras Stripe Checkout (payment o setup). Verifica siempre con Stripe vía Laravel. */
export default function PPagoConfirmacion() {
  const { query } = useAppRoute()
  const sessionId = query.session_id || ''
  const [estado, setEstado] = useState({ cargando: true, datos: null, error: null, codigo: null })

  useEffect(() => {
    let activo = true
    if (!sessionId) {
      setEstado({ cargando: false, datos: null, error: 'Falta el identificador de sesión de Stripe.', codigo: 400 })
      return () => { activo = false }
    }
    ;(async () => {
      try {
        const { data } = await pagosApi.confirmarCheckout(sessionId)
        if (activo) setEstado({ cargando: false, datos: data, error: null, codigo: 200 })
      } catch (err) {
        if (activo) {
          setEstado({
            cargando: false,
            datos: null,
            error: apiErrorMessage(err),
            codigo: err?.response?.status || 500,
          })
        }
      }
    })()
    return () => { activo = false }
  }, [sessionId])

  if (estado.cargando) {
    return (
      <>
        <CabeceraPagina titulo="Verificando pago con Stripe">Consultando el estado real de la operación en Stripe Sandbox…</CabeceraPagina>
        <section className="hoja hoja-cuerpo"><Cargando filas={5} /></section>
      </>
    )
  }

  if (estado.error) {
    const tituloError = estado.codigo === 404
      ? 'Sesión inexistente'
      : estado.codigo === 401 || estado.codigo === 403
        ? 'Usuario no autorizado'
        : 'No se pudo verificar la operación'
    return (
      <>
        <CabeceraPagina titulo={tituloError}>La confirmación solo se valida directamente con Stripe desde el servidor.</CabeceraPagina>
        <section className="hoja hoja-cuerpo grid gap-4">
          <Aviso tipo="error">{estado.error}</Aviso>
          <div className="acciones justify-start">
            <button type="button" className="btn btn-primario" onClick={() => go('/agenda')}>Volver a Agenda</button>
          </div>
        </section>
      </>
    )
  }

  const d = estado.datos
  const confirmado = d.estado_interno === 'confirmado'
  const duplicado = d.estado_interno === 'reconciliacion_duplicada'
  const rechazado = d.estado_interno === 'rechazado'
  const expirado = d.estado_interno === 'expirado'
  const Icono = confirmado ? CheckCircle2 : (rechazado || expirado || duplicado) ? XCircle : Clock

  return (
    <>
      <CabeceraPagina titulo={d.titulo || 'Resultado del pago'}>
        {d.tipo === 'setup'
          ? 'Registro oficial de tarjeta mediante Stripe Sandbox.'
          : 'Resultado verificado directamente contra la sesión de Stripe Sandbox.'}
      </CabeceraPagina>

      <section className="hoja">
        <header className="hoja-titulo">
          <div className="flex items-center gap-3">
            <Icono size={26} className={confirmado ? 'text-acento-texto' : 'text-tinta-suave'} aria-hidden="true" />
            <div>
              <h2>{confirmado ? (d.tipo === 'setup' ? '¡Tarjeta registrada en Stripe Sandbox!' : '¡Pago confirmado por Stripe Sandbox!') : d.titulo}</h2>
              <p className="text-sm text-tinta-suave">
                {confirmado
                  ? 'La transacción fue comprobada en el servidor con livemode=false (entorno de pruebas).'
                  : d.detalle_error || 'La operación aún no figura como pagada.'}
              </p>
            </div>
          </div>
          <Etiqueta estado={confirmado ? 'Pago aprobado' : rechazado ? 'Pago rechazado' : 'Pendiente de pago'} />
        </header>

        <div className="hoja-cuerpo grid gap-5">
          {duplicado && (
            <Aviso tipo="error">
              <AlertTriangle size={16} className="inline mr-1" />
              Se detectó un cobro adicional sobre una cuota que ya estaba liquidada. Quedó registrado para reconciliación sin duplicar el saldo ni la matrícula.
            </Aviso>
          )}

          {d.tipo === 'payment' && d.faltantes_conversion?.length > 0 && confirmado && (
            <Aviso>
              <strong>Pago confirmado por Stripe · Validación comercial pendiente:</strong> para completar la matrícula falta: {d.faltantes_conversion.join(' ')}
            </Aviso>
          )}

          {d.tipo === 'setup' ? (
            <dl className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-4">
              <div><dt className="text-xs text-tinta-suave">Prospecto</dt><dd className="font-semibold">{d.prospecto || '—'}</dd></div>
              <div><dt className="text-xs text-tinta-suave">Tarjeta</dt><dd className="font-semibold">{d.marca_tarjeta ? `${d.marca_tarjeta} •••• ${d.ultimos_digitos}` : 'Pendiente'}</dd></div>
              <div><dt className="text-xs text-tinta-suave">Cliente Stripe</dt><dd className="font-mono text-xs">{d.stripe_cliente || '—'}</dd></div>
              <div><dt className="text-xs text-tinta-suave">PaymentMethod Stripe</dt><dd className="font-mono text-xs">{d.stripe_metodo || '—'}</dd></div>
              <div><dt className="text-xs text-tinta-suave">Sesión Stripe</dt><dd className="font-mono text-xs break-all">{d.stripe_sesion}</dd></div>
              <div><dt className="text-xs text-tinta-suave">Fecha</dt><dd className="tabular-nums">{fecha(d.fecha_confirmacion, true)}</dd></div>
            </dl>
          ) : (
            <>
              <dl className="cifras">
                <div><dt>Monto ({d.moneda || 'BOB'})</dt><dd className="tabular-nums">{bs(d.monto)}</dd></div>
                <div><dt>Orden · cuota</dt><dd className="tabular-nums">#{d.nro_orden} · {d.nro_cuota} de {d.total_cuotas}</dd></div>
                <div><dt>Saldo pendiente</dt><dd className="tabular-nums">{bs(d.saldo_pendiente)}</dd></div>
                <div><dt>Estado interno</dt><dd>{d.estado_cuota || d.estado_interno}</dd></div>
              </dl>

              <dl className="grid grid-cols-[repeat(auto-fit,minmax(210px,1fr))] gap-4 border-t border-filete pt-4">
                <div><dt className="text-xs text-tinta-suave">Prospecto</dt><dd className="font-semibold">{d.prospecto || '—'}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Programa · módulo</dt><dd>{d.programa} · {d.modulo}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Método</dt><dd><CreditCard size={14} className="inline mr-1" />{d.marca_tarjeta ? `${d.marca_tarjeta} •••• ${d.ultimos_digitos}` : 'Tarjeta Stripe Sandbox'}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Estado en Stripe</dt><dd>{d.estado_pago} ({d.estado_sesion}) · Sandbox</dd></div>
                <div><dt className="text-xs text-tinta-suave">Estado comercial</dt><dd>{d.estado_comercial || '—'}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Fecha y hora</dt><dd className="tabular-nums">{fecha(d.fecha_confirmacion, true)}</dd></div>
                <div><dt className="text-xs text-tinta-suave">PaymentIntent Stripe</dt><dd className="font-mono text-xs break-all">{d.stripe_pago_intent || '—'}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Checkout Session Stripe</dt><dd className="font-mono text-xs break-all">{d.stripe_sesion}</dd></div>
              </dl>

              <p className="rounded-ui border border-filete bg-niebla-2 px-3 py-2 text-xs text-tinta-suave">
                Comprobante interno de prueba generado con <b>Stripe Sandbox</b> (moneda BOB, sin movimiento real de dinero ni valor fiscal).
              </p>
            </>
          )}

          <div className="acciones justify-start flex-wrap">
            {d.nro_tarjeta
              ? <button type="button" className="btn btn-primario" onClick={() => go(`/agenda?interes=${d.nro_tarjeta}`)}>Ver orden en Agenda</button>
              : <button type="button" className="btn btn-primario" onClick={() => go('/agenda')}>Volver a Agenda</button>}
            {d.url_checkout && !confirmado && !expirado && (
              <button type="button" className="btn btn-acento" onClick={() => window.location.assign(d.url_checkout)}>Completar pago en Stripe</button>
            )}
            {confirmado && d.tipo === 'payment' && (
              <button type="button" className="btn btn-secundario" onClick={() => window.print()}><Printer size={16} /> Imprimir comprobante interno</button>
            )}
            {d.receipt_url && (
              <a className="btn btn-texto" href={d.receipt_url} target="_blank" rel="noreferrer"><ExternalLink size={16} /> Recibo de prueba Stripe</a>
            )}
          </div>
        </div>
      </section>
    </>
  )
}
