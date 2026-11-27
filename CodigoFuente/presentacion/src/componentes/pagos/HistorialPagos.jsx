import { useMemo, useState } from 'react'
import { ExternalLink, Info } from 'lucide-react'
import { Etiqueta, Modal, fecha } from '../ui'
import { bsPago } from './ResumenPagos'

function clasificarCuota(o, c) {
  const esStripe = c.proveedor === 'stripe' || Boolean(c.stripe_pago_intent)
  const tieneComprobante = Boolean(o.pago?.comprobantes?.some((cp) => (cp.nro_cuota ?? 1) === c.nro_cuota))

  if (o.estado === 'Anulada') {
    return {
      estadoTexto: 'Orden anulada',
      badge: 'Perdido',
      metodoTexto: 'Sin cobro vigente',
      origenTexto: 'Orden anulada',
    }
  }
  if (c.estado === 'Pago aprobado') {
    return esStripe
      ? {
          estadoTexto: 'Pago confirmado por Stripe',
          badge: 'Pago aprobado',
          metodoTexto: c.metodo?.ultimos_digitos
            ? `${c.metodo.marca || 'Tarjeta'} •••• ${c.metodo.ultimos_digitos}`
            : 'Tarjeta Stripe',
          origenTexto: 'Stripe Checkout Sandbox',
        }
      : {
          estadoTexto: 'Pago manual histórico',
          badge: 'Pago aprobado',
          metodoTexto: c.metodo?.tipo || (tieneComprobante ? 'Comprobante revisado' : 'Registro histórico'),
          origenTexto: 'Registro administrativo anterior',
        }
  }
  if (c.estado === 'Pago rechazado') {
    return {
      estadoTexto: 'Pago rechazado',
      badge: 'Pago rechazado',
      metodoTexto: c.metodo?.tipo || 'Revisión comercial',
      origenTexto: 'Pago rechazado',
    }
  }
  if (c.estado === 'En revision') {
    return {
      estadoTexto: 'En revisión',
      badge: 'En revision',
      metodoTexto: c.metodo?.tipo || 'Comprobante histórico',
      origenTexto: 'Pendiente de revisión histórica',
    }
  }
  return {
    estadoTexto: 'Pago pendiente',
    badge: 'Pendiente de pago',
    metodoTexto: 'Por pagar en Stripe',
    origenTexto: 'Stripe Checkout Sandbox',
  }
}

/** Sección 4: Historial cronológico compacto de cuotas y cobros, inicialmente contraído. */
export default function HistorialPagos({ ordenes = [], programaPorDefecto = 'Programa educativo' }) {
  const [detalle, setDetalle] = useState(null)

  const filas = useMemo(() => {
    const lista = []
    ordenes.forEach((o) => {
      const programa = o.items?.[0]?.programa_nombre || programaPorDefecto
      const totalCuotas = o.cuotas?.length || 1
      ;(o.cuotas || []).forEach((c) => {
        const meta = clasificarCuota(o, c)
        lista.push({
          id: `${o.nro_orden}-${c.nro_cuota}`,
          orden: o,
          cuota: c,
          programa,
          totalCuotas,
          fechaMostrar: c.fecha_pago || c.fecha_vencimiento || o.fecha_generacion,
          ...meta,
        })
      })
    })
    return lista.sort((a, b) => {
      if (a.orden.nro_orden !== b.orden.nro_orden) return b.orden.nro_orden - a.orden.nro_orden
      return a.cuota.nro_cuota - b.cuota.nro_cuota
    })
  }, [ordenes, programaPorDefecto])

  return (
    <details className="hoja">
      <summary className="hoja-titulo cursor-pointer list-none select-none">
        <span className="flex flex-wrap items-center gap-2 font-semibold">
          <span>Historial de pagos</span>
          <span className="rounded-pill bg-niebla-2 px-2 py-0.5 text-xs font-bold tabular-nums text-tinta-suave">
            {filas.length} {filas.length === 1 ? 'movimiento' : 'movimientos'}
          </span>
        </span>
        <span className="text-xs text-tinta-suave">Desplegar</span>
      </summary>

      <div className="hoja-cuerpo grid gap-3">
        {!filas.length ? (
          <p className="text-sm text-tinta-suave">Aún no existen movimientos de pago registrados.</p>
        ) : (
          <div className="tabla-marco">
            <table className="tabla pagos-tabla">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Programa</th>
                  <th>Cuota</th>
                  <th>Importe</th>
                  <th>Método</th>
                  <th>Estado</th>
                  <th>Detalles</th>
                </tr>
              </thead>
              <tbody>
                {filas.map((f) => (
                  <tr key={f.id}>
                    <td className="tabular-nums whitespace-nowrap">{fecha(f.fechaMostrar, Boolean(f.cuota.fecha_pago))}</td>
                    <td>{f.programa}</td>
                    <td className="tabular-nums whitespace-nowrap">
                      #{f.orden.nro_orden} · {f.cuota.nro_cuota}/{f.totalCuotas}
                    </td>
                    <td className="tabular-nums font-semibold whitespace-nowrap">{bsPago(f.cuota.monto)}</td>
                    <td>{f.metodoTexto}</td>
                    <td><Etiqueta estado={f.badge}>{f.estadoTexto}</Etiqueta></td>
                    <td>
                      <button type="button" className="btn btn-texto" onClick={() => setDetalle(f)}>
                        <Info size={14} /> Ver detalles
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {detalle && (
        <Modal
          titulo={`Detalle · Orden #${detalle.orden.nro_orden} · Cuota ${detalle.cuota.nro_cuota} de ${detalle.totalCuotas}`}
          descripcion={`${detalle.programa} · ${bsPago(detalle.cuota.monto)}`}
          onCerrar={() => setDetalle(null)}
        >
          <dl className="grid gap-3 text-sm">
            <div><dt className="text-xs text-tinta-suave">Estado</dt><dd className="font-semibold">{detalle.estadoTexto}</dd></div>
            <div><dt className="text-xs text-tinta-suave">Origen / Pasarela</dt><dd>{detalle.origenTexto}</dd></div>
            <div><dt className="text-xs text-tinta-suave">Método</dt><dd>{detalle.metodoTexto}</dd></div>
            <div><dt className="text-xs text-tinta-suave">Vencimiento</dt><dd className="tabular-nums">{fecha(detalle.cuota.fecha_vencimiento)}</dd></div>
            {detalle.cuota.fecha_pago && (
              <div><dt className="text-xs text-tinta-suave">Fecha de confirmación</dt><dd className="tabular-nums">{fecha(detalle.cuota.fecha_pago, true)}</dd></div>
            )}
            {detalle.cuota.stripe_pago_intent && (
              <div>
                <dt className="text-xs text-tinta-suave">Referencia de pago Stripe</dt>
                <dd className="font-mono text-xs wrap-anywhere">{detalle.cuota.stripe_pago_intent}</dd>
              </div>
            )}
            {detalle.cuota.stripe_recibo_url && (
              <div>
                <a className="btn btn-secundario inline-flex" href={detalle.cuota.stripe_recibo_url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink size={15} /> Abrir comprobante Stripe
                </a>
              </div>
            )}
            {detalle.cuota.observacion && (
              <div><dt className="text-xs text-tinta-suave">Observación</dt><dd className="wrap-anywhere">{detalle.cuota.observacion}</dd></div>
            )}
            {detalle.orden.motivo_anulacion && (
              <div><dt className="text-xs text-tinta-suave">Motivo de anulación</dt><dd className="wrap-anywhere">{detalle.orden.motivo_anulacion}</dd></div>
            )}
          </dl>
          <div className="acciones mt-4">
            <button type="button" className="btn btn-primario" onClick={() => setDetalle(null)}>Cerrar</button>
          </div>
        </Modal>
      )}
    </details>
  )
}
