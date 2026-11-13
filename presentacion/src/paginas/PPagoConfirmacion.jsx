import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle2, Clock, CreditCard, ExternalLink, Printer, XCircle } from 'lucide-react'
import { Aviso, CabeceraPagina, Cargando, Etiqueta, bs, fecha } from '../componentes/ui'
import { apiErrorMessage } from '../servicios/errors'
import { useAuth } from '../servicios/auth'
import { go, useAppRoute } from '../servicios/navigation'
import * as pagosApi from '../api/pagos'

/** CU6: pantalla de retorno oficial tras Stripe Checkout (payment o setup). Verifica siempre con Stripe vía Laravel. */
export default function PPagoConfirmacion() {
  const { query } = useAppRoute()
  const sesion = useAuth()
  const sessionId = query.session_id || ''
  const token = query.token || ''
  const [estado, setEstado] = useState({ cargando: true, datos: null, error: null, codigo: null })

  useEffect(() => {
    let activo = true
    if (!sessionId) {
      setEstado({ cargando: false, datos: null, error: 'Falta el identificador de sesión de Stripe.', codigo: 400 })
      return () => { activo = false }
    }
    if (!token && !sesion.token) {
      setEstado({ cargando: false, datos: null, error: 'El enlace de confirmación requiere un token de verificación válido.', codigo: 403 })
      return () => { activo = false }
    }
    ;(async () => {
      try {
        const { data } = token
          ? await pagosApi.consultarRetornoPublico(sessionId, token)
          : await pagosApi.confirmarCheckout(sessionId)
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
  }, [sessionId, token, sesion.token])

  const esVistaPublica = Boolean(token) || !sesion.usuario
  const accionVolver = () => (esVistaPublica
    ? <button type="button" className="btn btn-primario" onClick={() => go('/anuncios')}>Volver al sitio web</button>
    : <button type="button" className="btn btn-primario" onClick={() => go('/agenda')}>Volver a Agenda</button>)

  if (estado.cargando) {
    return (
      <div className="mx-auto w-full max-w-[920px] px-4 py-6">
        <CabeceraPagina titulo="Verificando operación con Stripe">Consultando el estado real directamente con Stripe Sandbox…</CabeceraPagina>
        <section className="hoja hoja-cuerpo"><Cargando filas={5} /></section>
      </div>
    )
  }

  if (estado.error || !estado.datos) {
    const tituloError = estado.codigo === 404
      ? 'Sesión inexistente'
      : estado.codigo === 401 || estado.codigo === 403
        ? 'Enlace no autorizado'
        : estado.codigo === 410
          ? 'Enlace caducado'
          : 'No se pudo verificar la operación'
    return (
      <div className="mx-auto w-full max-w-[920px] px-4 py-6">
        <CabeceraPagina titulo={tituloError}>La confirmación solo se valida directamente con Stripe desde el servidor.</CabeceraPagina>
        <section className="hoja hoja-cuerpo grid gap-4">
          <Aviso tipo="error">{estado.error || 'No se recibió información de confirmación desde el servidor.'}</Aviso>
          <div className="acciones justify-start">{accionVolver()}</div>
        </section>
      </div>
    )
  }

  const d = estado.datos
  const esSetup = d.tipo === 'setup'
  const confirmado = d.estado_interno === 'confirmado'
  const duplicado = d.estado_interno === 'reconciliacion_duplicada'
  const rechazado = d.estado_interno === 'rechazado'
  const expirado = d.estado_interno === 'expirado'
  const Icono = confirmado ? CheckCircle2 : (rechazado || expirado || duplicado) ? XCircle : Clock
  const monto = d.importe ?? d.monto ?? 0
  const referencia = d.referencia_pago || d.stripe_pago_intent || d.stripe_sesion || '—'

  return (
    <div className="mx-auto w-full max-w-[920px] px-4 py-6">
      <CabeceraPagina titulo={d.titulo || (esSetup ? 'Registro de tarjeta' : 'Resultado del pago')}>
        {esSetup
          ? 'Registro de tarjeta verificado mediante Stripe Sandbox.'
          : 'Resultado verificado directamente con Stripe Sandbox.'}
      </CabeceraPagina>

      <section className="hoja">
        <header className="hoja-titulo">
          <div className="flex items-center gap-3">
            <Icono size={28} className={confirmado ? 'text-acento-texto shrink-0' : 'text-tinta-suave shrink-0'} aria-hidden="true" />
            <div>
              <h2>
                {confirmado
                  ? (esSetup ? '¡Tarjeta registrada correctamente!' : '¡Pago confirmado por Stripe Sandbox!')
                  : (d.titulo || (esSetup ? 'Registro de tarjeta no completado' : 'Operación no completada'))}
              </h2>
              <p className="text-sm text-tinta-suave">
                {confirmado
                  ? (esSetup
                    ? 'No se ha realizado ningún cobro. La tarjeta quedó verificada en Stripe Sandbox.'
                    : 'La operación fue verificada en Stripe Sandbox (entorno de pruebas, sin cobro real).')
                  : d.detalle_error || (esSetup
                    ? 'El registro de la tarjeta aún no figura como completado en Stripe.'
                    : 'La operación aún no figura como pagada.')}
              </p>
            </div>
          </div>
          {esSetup ? (
            <Etiqueta estado={confirmado ? 'Activo' : expirado ? 'Inactivo' : 'Pendiente de pago'}>
              {confirmado ? 'Tarjeta registrada' : (expirado ? 'Expirado' : 'Pendiente')}
            </Etiqueta>
          ) : (
            <Etiqueta estado={confirmado ? 'Pago aprobado' : rechazado ? 'Pago rechazado' : 'Pendiente de pago'} />
          )}
        </header>

        <div className="hoja-cuerpo grid gap-5">
          {duplicado && (
            <Aviso tipo="error">
              <AlertTriangle size={16} className="inline mr-1" />
              Se detectó un pago adicional sobre una cuota que ya había sido liquidada. Contacte con UNEXO para su revisión.
            </Aviso>
          )}

          {!esVistaPublica && d.tipo === 'payment' && d.faltantes_conversion?.length > 0 && confirmado && (
            <Aviso>
              <strong>Pago confirmado por Stripe · Validación comercial pendiente:</strong> para completar la matrícula falta: {d.faltantes_conversion.join(' ')}
            </Aviso>
          )}

          {esSetup ? (
            <>
              <dl className="grid grid-cols-[repeat(auto-fit,minmax(180px,1fr))] gap-4">
                {!esVistaPublica && d.prospecto && <div><dt className="text-xs text-tinta-suave">Prospecto</dt><dd className="font-semibold">{d.prospecto}</dd></div>}
                <div><dt className="text-xs text-tinta-suave">Marca de la tarjeta</dt><dd className="font-semibold inline-flex items-center gap-1.5"><CreditCard size={15} aria-hidden="true" /> {d.marca_tarjeta || 'Pendiente'}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Últimos 4 dígitos</dt><dd className="font-semibold tabular-nums">{d.ultimos_digitos ? `•••• ${d.ultimos_digitos}` : '—'}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Fecha de vencimiento</dt><dd className="font-semibold tabular-nums">{d.vencimiento || '—'}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Fecha de registro</dt><dd className="tabular-nums">{fecha(d.fecha_confirmacion, true)}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Referencia Stripe</dt><dd className="font-mono text-xs break-all">{referencia}</dd></div>
              </dl>

              <p className="rounded-ui border border-filete bg-niebla-2 px-3 py-2.5 text-sm font-medium text-tinta">
                No se ha realizado ningún cobro. Tus datos de tarjeta se almacenan de forma segura en Stripe Sandbox.
              </p>
            </>
          ) : (
            <>
              <dl className="cifras">
                <div><dt>Importe ({d.moneda || 'BOB'})</dt><dd className="tabular-nums">{bs(monto)}</dd></div>
                <div><dt>Cuota</dt><dd className="tabular-nums">{d.nro_cuota} de {d.total_cuotas}</dd></div>
                <div><dt>Estado del pago</dt><dd>{confirmado ? 'Pago confirmado' : (d.estado_cuota || d.estado_interno)}</dd></div>
                {!esVistaPublica && <div><dt>Saldo pendiente</dt><dd className="tabular-nums">{bs(d.saldo_pendiente)}</dd></div>}
              </dl>

              <dl className="grid grid-cols-[repeat(auto-fit,minmax(210px,1fr))] gap-4 border-t border-filete pt-4">
                <div><dt className="text-xs text-tinta-suave">Programa educativo</dt><dd className="font-semibold">{d.programa || '—'}{d.modulo ? ` · ${d.modulo}` : ''}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Moneda</dt><dd>{d.moneda || 'BOB'} (Bolivianos)</dd></div>
                <div><dt className="text-xs text-tinta-suave">Referencia de pago</dt><dd className="font-mono text-xs break-all">{referencia}</dd></div>
                <div><dt className="text-xs text-tinta-suave">Fecha y hora</dt><dd className="tabular-nums">{fecha(d.fecha_confirmacion, true)}</dd></div>
                {!esVistaPublica && d.prospecto && <div><dt className="text-xs text-tinta-suave">Prospecto</dt><dd className="font-semibold">{d.prospecto}</dd></div>}
                {!esVistaPublica && d.estado_comercial && <div><dt className="text-xs text-tinta-suave">Estado comercial</dt><dd>{d.estado_comercial}</dd></div>}
              </dl>

              <p className="rounded-ui border border-filete bg-niebla-2 px-3 py-2 text-xs text-tinta-suave">
                {d.aviso_sandbox || 'Operación de demostración mediante Stripe Sandbox (moneda BOB, sin movimiento real de dinero ni valor fiscal).'}
              </p>
            </>
          )}

          <div className="acciones justify-start flex-wrap">
            {esVistaPublica ? (
              <button type="button" className="btn btn-primario" onClick={() => go('/anuncios')}>Volver al sitio web</button>
            ) : (
              d.nro_tarjeta
                ? <button type="button" className="btn btn-primario" onClick={() => go(`/agenda?interes=${d.nro_tarjeta}`)}>Ver orden en Agenda</button>
                : <button type="button" className="btn btn-primario" onClick={() => go('/agenda')}>Volver a Agenda</button>
            )}
            {d.url_checkout && !confirmado && !expirado && (
              <button type="button" className="btn btn-acento" onClick={() => window.location.assign(d.url_checkout)}>
                {esSetup ? 'Completar registro en Stripe' : 'Completar pago en Stripe'}
              </button>
            )}
            {confirmado && !esSetup && (
              <button type="button" className="btn btn-secundario" onClick={() => window.print()}><Printer size={16} /> Imprimir comprobante</button>
            )}
            {!esVistaPublica && d.receipt_url && (
              <a className="btn btn-texto" href={d.receipt_url} target="_blank" rel="noreferrer"><ExternalLink size={16} /> Recibo de prueba Stripe</a>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}
