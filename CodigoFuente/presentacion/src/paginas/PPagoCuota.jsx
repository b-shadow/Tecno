import { useEffect, useState } from 'react'
import { CheckCircle2, ExternalLink, XCircle } from 'lucide-react'
import { Aviso, CabeceraPagina, Cargando, Etiqueta, bs, fecha } from '../componentes/ui'
import { apiErrorMessage } from '../servicios/errors'
import { go, useAppRoute } from '../servicios/navigation'
import * as pagosApi from '../api/pagos'

/**
 * CU6: enlace público seguro por cuota enviado por correo electrónico.
 * Verifica en tiempo real el estado en PostgreSQL, recupera o regenera la sesión de Stripe y redirige al cliente.
 */
export default function PPagoCuota() {
  const { query } = useAppRoute()
  const token = query.token || ''
  const [estado, setEstado] = useState({ cargando: true, datos: null, error: null })

  useEffect(() => {
    let activo = true
    if (!token) {
      setEstado({ cargando: false, datos: null, error: 'Falta el token de verificación de la cuota.' })
      return () => { activo = false }
    }
    ;(async () => {
      try {
        const { data } = await pagosApi.abrirEnlaceCuotaPublico(token)
        if (!activo) return
        setEstado({ cargando: false, datos: data, error: null })
        if (data.estado_link === 'pendiente' && data.url_checkout && !query.sin_redirigir) {
          window.location.assign(data.url_checkout)
        }
      } catch (err) {
        if (activo) {
          setEstado({ cargando: false, datos: null, error: apiErrorMessage(err) })
        }
      }
    })()
    return () => { activo = false }
  }, [token, query.sin_redirigir])

  if (estado.cargando) {
    return (
      <div className="mx-auto w-full max-w-[820px] px-4 py-6">
        <CabeceraPagina titulo="Preparando enlace seguro de pago">Verificando cuota pendiente en UNEXO y conectando con Stripe Sandbox…</CabeceraPagina>
        <section className="hoja hoja-cuerpo"><Cargando filas={4} /></section>
      </div>
    )
  }

  if (estado.error) {
    return (
      <div className="mx-auto w-full max-w-[820px] px-4 py-6">
        <CabeceraPagina titulo="Enlace no disponible">No se pudo iniciar la sesión de pago solicitada.</CabeceraPagina>
        <section className="hoja hoja-cuerpo grid gap-4">
          <Aviso tipo="error">{estado.error}</Aviso>
          <div className="acciones justify-start">
            <button type="button" className="btn btn-primario" onClick={() => go('/anuncios')}>Volver al catálogo</button>
          </div>
        </section>
      </div>
    )
  }

  const d = estado.datos
  const pagada = d.estado_link === 'pagada'
  const pendiente = d.estado_link === 'pendiente'
  const Icono = pagada ? CheckCircle2 : XCircle

  return (
    <div className="mx-auto w-full max-w-[820px] px-4 py-6">
      <CabeceraPagina titulo={pendiente ? 'Redirigiendo a Stripe Checkout' : pagada ? 'Cuota ya pagada' : 'Solicitud no disponible'}>
        {d.aviso_sandbox}
      </CabeceraPagina>

      <section className="hoja">
        <header className="hoja-titulo flex-wrap gap-2">
          <div className="flex items-center gap-3">
            {!pendiente && <Icono size={24} className={pagada ? 'text-acento-texto' : 'text-tinta-suave'} aria-hidden="true" />}
            <div>
              <h2>{d.programa}</h2>
              {d.modulo && <p className="text-sm text-tinta-suave">{d.modulo}</p>}
            </div>
          </div>
          <Etiqueta estado={pagada ? 'Pago aprobado' : pendiente ? 'Pendiente de pago' : 'Perdido'}>
            {pagada ? 'Pagada' : pendiente ? 'Pendiente de pago' : 'No disponible'}
          </Etiqueta>
        </header>

        <div className="hoja-cuerpo grid gap-4">
          <dl className="cifras">
            <div><dt>Importe ({d.moneda})</dt><dd className="tabular-nums">{bs(d.importe)}</dd></div>
            <div><dt>Cuota</dt><dd className="tabular-nums">{d.nro_cuota} de {d.total_cuotas}</dd></div>
            <div><dt>Vencimiento</dt><dd className="tabular-nums">{fecha(d.fecha_vencimiento)}</dd></div>
          </dl>

          {!pendiente && <Aviso tipo={pagada ? 'ok' : 'error'}>{d.mensaje}</Aviso>}

          <div className="acciones justify-start flex-wrap">
            {pendiente && d.url_checkout && (
              <button type="button" className="btn btn-primario" onClick={() => window.location.assign(d.url_checkout)}>
                <ExternalLink size={16} /> Ir a pagar en Stripe
              </button>
            )}
            <button type="button" className="btn btn-secundario" onClick={() => go('/anuncios')}>Volver al catálogo</button>
          </div>
        </div>
      </section>
    </div>
  )
}
