import { useState } from 'react'
import { Ban, CheckCircle2, ExternalLink, Info, Plus, Send } from 'lucide-react'
import { Aviso, Boton, Campo, Etiqueta, Modal, fecha, hoyLocal } from '../ui'
import { apiErrorMessage } from '../../servicios/errors'
import { bsPago } from './ResumenPagos'
import * as pagosApi from '../../api/pagos'

const DIAS_PREVIO = 3
const DIAS_DESPUES = 3

function sumarDias(fechaIso, dias) {
  const [a, m, d] = String(fechaIso).slice(0, 10).split('-').map(Number)
  const dt = new Date(a, m - 1, d + dias, 12, 0, 0)
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
}

function proximoRecordatorio(c, envioAutomatico) {
  if (!envioAutomatico || c.estado !== 'Pendiente de pago') return null
  const hoy = hoyLocal()
  const previo = sumarDias(c.fecha_vencimiento, -DIAS_PREVIO)
  const dia = String(c.fecha_vencimiento).slice(0, 10)
  const mora = sumarDias(c.fecha_vencimiento, DIAS_DESPUES)

  if (!c.recordatorio_previo_en && previo > hoy) return previo
  if (!c.recordatorio_vencimiento_en && dia >= hoy) return dia
  if (!c.recordatorio_mora_en && mora >= hoy) return mora
  return null
}

/** Sección 2: Órdenes activas como elemento principal, cuotas limpias y órdenes liquidadas/anuladas contraídas. */
export default function PlanPagos({ t, ordenes, editable, puedeGenerar, onGenerar, onEnviarCuota, aviso, onCambio }) {
  const [detalleOrden, setDetalleOrden] = useState(null)
  const [detalleCuota, setDetalleCuota] = useState(null)
  const [anularOrdenModal, setAnularOrdenModal] = useState(null)

  const ordenesActivas = ordenes.filter((o) => {
    if (o.estado === 'Anulada') return false
    const total = o.cuotas.length
    const pagadas = o.cuotas.filter((c) => c.estado === 'Pago aprobado').length
    return !(total > 0 && pagadas === total)
  })
  const ordenesCerradas = ordenes.filter((o) => !ordenesActivas.includes(o))

  if (!ordenes.length || (!ordenesActivas.length && !ordenesCerradas.length)) {
    return (
      <section className="hoja hoja-cuerpo grid justify-items-start gap-2.5">
        <h4>Sin órdenes de pago</h4>
        <p className="text-sm text-tinta-suave">Configura los módulos, descuentos y condiciones comerciales para generar una orden.</p>
        {puedeGenerar && (
          <button type="button" className="btn btn-primario" onClick={onGenerar}>
            <Plus size={16} /> Generar orden de pago
          </button>
        )}
      </section>
    )
  }

  return (
    <section className="grid gap-4">
      {!ordenesActivas.length && (
        <div className="hoja hoja-cuerpo flex flex-wrap items-center justify-between gap-3">
          <div>
            <h4>Sin órdenes pendientes activas</h4>
            <p className="text-sm text-tinta-suave">Las órdenes anteriores ya fueron liquidadas o anuladas.</p>
          </div>
          {puedeGenerar && (
            <button type="button" className="btn btn-primario" onClick={onGenerar}>
              <Plus size={16} /> Generar orden de pago
            </button>
          )}
        </div>
      )}

      {ordenesActivas.map((o) => (
        <TarjetaOrden
          key={o.nro_orden}
          o={o}
          t={t}
          editable={editable}
          onVerDetalles={() => setDetalleOrden(o)}
          onEnviarCuota={(c) => onEnviarCuota(o, c)}
          onVerCuota={(c) => setDetalleCuota({ orden: o, cuota: c })}
        />
      ))}

      {ordenesCerradas.length > 0 && (
        <details className="hoja">
          <summary className="hoja-titulo cursor-pointer list-none select-none">
            <span className="font-semibold">Órdenes liquidadas y anuladas ({ordenesCerradas.length})</span>
            <span className="text-xs text-tinta-suave">Desplegar</span>
          </summary>
          <div className="hoja-cuerpo grid gap-4">
            {ordenesCerradas.map((o) => (
              <TarjetaOrden
                key={o.nro_orden}
                o={o}
                t={t}
                editable={editable}
                onVerDetalles={() => setDetalleOrden(o)}
                onEnviarCuota={(c) => onEnviarCuota(o, c)}
                onVerCuota={(c) => setDetalleCuota({ orden: o, cuota: c })}
              />
            ))}
          </div>
        </details>
      )}

      {detalleOrden && (
        <ModalDetallesOrden
          orden={detalleOrden}
          editable={editable}
          onCerrar={() => setDetalleOrden(null)}
          onAnular={(o) => { setDetalleOrden(null); setAnularOrdenModal(o) }}
          onCambio={onCambio}
          aviso={aviso}
        />
      )}

      {detalleCuota && (
        <ModalDetalleCuota
          orden={detalleCuota.orden}
          cuota={detalleCuota.cuota}
          onCerrar={() => setDetalleCuota(null)}
        />
      )}

      {anularOrdenModal && (
        <ModalAnularOrden
          orden={anularOrdenModal}
          onCerrar={() => setAnularOrdenModal(null)}
          onListo={(m) => { aviso.ok(m); setAnularOrdenModal(null); onCambio() }}
        />
      )}
    </section>
  )
}

function TarjetaOrden({ o, t, editable, onVerDetalles, onEnviarCuota, onVerCuota }) {
  const anulada = o.estado === 'Anulada'
  const totalCuotas = o.cuotas.length
  const pagadas = o.cuotas.filter((c) => c.estado === 'Pago aprobado').length
  const liquidada = !anulada && totalCuotas > 0 && pagadas === totalCuotas
  const programa = o.items?.[0]?.programa_nombre || t.programa_nombre

  return (
    <article className="hoja">
      <header className="hoja-titulo flex-wrap gap-3">
        <div>
          <h4>Orden de pago #{o.nro_orden} · {programa}</h4>
          <p className="text-sm text-tinta-suave">
            {o.items.length} {o.items.length === 1 ? 'módulo contratado' : 'módulos contratados'}
            {' · '}Total: <b className="text-tinta tabular-nums">{bsPago(o.total)}</b>
            {!anulada && !liquidada && <> · Envíos automáticos: <b>{o.envio_automatico ? 'Activados' : 'Desactivados'}</b></>}
          </p>
        </div>
        <div className="acciones flex-wrap">
          {anulada
            ? <Etiqueta estado="Perdido">Anulada</Etiqueta>
            : <Etiqueta estado={liquidada ? 'Pago aprobado' : 'Pendiente de pago'}>{liquidada ? 'Liquidada' : 'Activa'}</Etiqueta>}
          <button type="button" className="btn btn-secundario" onClick={onVerDetalles}>
            <Info size={15} /> Detalles y opciones
          </button>
        </div>
      </header>

      {anulada && o.motivo_anulacion && (
        <div className="px-6 pt-3"><Aviso tipo="error">Orden anulada: {o.motivo_anulacion}</Aviso></div>
      )}

      <div className="hoja-cuerpo grid gap-2.5">
        {o.cuotas.map((c) => {
          const pagada = c.estado === 'Pago aprobado'
          const puedeEnviar = editable && !anulada && ['Pendiente de pago', 'Pago rechazado'].includes(c.estado)
          const proxRecordatorio = proximoRecordatorio(c, Boolean(o.envio_automatico && !anulada))
          return (
            <div key={c.nro_cuota} className="flex flex-wrap items-center justify-between gap-3 rounded-ui border border-filete px-4 py-3">
              <div className="grid gap-0.5">
                <strong className="text-sm">Cuota {c.nro_cuota} de {totalCuotas}</strong>
                <div className="text-xs text-tinta-suave">
                  Vencimiento: <span className="tabular-nums">{fecha(c.fecha_vencimiento)}</span>
                  {proxRecordatorio && <> · Próximo recordatorio: <span className="tabular-nums">{fecha(proxRecordatorio)}</span></>}
                </div>
                <div className="mt-0.5 flex flex-wrap items-center gap-2.5">
                  <strong className="text-base tabular-nums">{bsPago(c.monto)}</strong>
                  <Etiqueta estado={c.estado}>{pagada ? 'Pago confirmado' : c.estado}</Etiqueta>
                </div>
              </div>

              <div className="acciones">
                {puedeEnviar && (
                  <button type="button" className="btn btn-primario" onClick={() => onEnviarCuota(c)}>
                    <Send size={15} /> Enviar solicitud de pago
                  </button>
                )}
                {pagada && (
                  <button type="button" className="btn btn-secundario" onClick={() => onVerCuota(c)}>
                    <CheckCircle2 size={15} /> Ver detalles
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </article>
  )
}

function ModalDetallesOrden({ orden, editable, onCerrar, onAnular, onCambio, aviso }) {
  const [cambiandoAuto, setCambiandoAuto] = useState(false)
  const anulada = orden.estado === 'Anulada'
  const anulable = editable && !anulada && !orden.cuotas.some((c) => ['Pago aprobado', 'En revision'].includes(c.estado))

  async function alternarAuto(activar) {
    setCambiandoAuto(true)
    try {
      const { data } = await pagosApi.configurarEnvioAutomatico(orden.nro_orden, activar)
      aviso.ok(data.mensaje)
      onCambio()
      onCerrar()
    } catch (err) {
      aviso.error(err)
      setCambiandoAuto(false)
    }
  }

  return (
    <Modal ancho titulo={`Detalles de orden #${orden.nro_orden}`} descripcion={`Generada el ${fecha(orden.fecha_generacion, true)}`} onCerrar={onCerrar}>
      <div className="grid gap-4">
        <section className="grid gap-1.5">
          <strong className="text-sm">Módulos contratados</strong>
          <ul className="grid gap-1 rounded-ui border border-filete p-3 text-sm">
            {orden.items.map((i) => (
              <li key={i.nro_solicitud} className="flex justify-between gap-2">
                <span>{i.modulo_nombre}</span>
                <b className="tabular-nums">{bsPago(i.precio_acordado)}</b>
              </li>
            ))}
          </ul>
        </section>

        <section className="grid gap-1.5 text-sm">
          <div className="flex justify-between"><span>Subtotal</span><span className="tabular-nums">{bsPago(orden.subtotal)}</span></div>
          <div className="flex justify-between">
            <span>Descuentos ({orden.descuentos?.length ? orden.descuentos.map((d) => `${d.descuento?.nombre || d.descuento_codigo} (${Number(d.porcentaje)}%)`).join(', ') : 'Sin descuentos'})</span>
            <span className="tabular-nums text-exito">- {bsPago(orden.descuento_total)}</span>
          </div>
          <div className="flex justify-between font-bold border-t border-filete pt-2">
            <span>Total</span><span className="tabular-nums">{bsPago(orden.total)}</span>
          </div>
        </section>

        {!anulada && editable && (
          <section className="flex flex-wrap items-center justify-between gap-3 rounded-ui border border-filete bg-niebla-2 p-3 text-sm">
            <div>
              <strong>Envíos automáticos por correo</strong>
              <p className="text-xs text-tinta-suave">Estado actual: {orden.envio_automatico ? 'Activados' : 'Desactivados'}</p>
            </div>
            <Boton className="btn-secundario" cargando={cambiandoAuto} onClick={() => alternarAuto(!orden.envio_automatico)}>
              {orden.envio_automatico ? 'Desactivar envíos' : 'Activar envíos'}
            </Boton>
          </section>
        )}

        <div className="acciones justify-between flex-wrap">
          {anulable ? (
            <button type="button" className="btn btn-peligro-suave" onClick={() => onAnular(orden)}>
              <Ban size={15} /> Anular orden
            </button>
          ) : <span />}
          <button type="button" className="btn btn-primario" onClick={onCerrar}>Cerrar</button>
        </div>
      </div>
    </Modal>
  )
}

function ModalDetalleCuota({ orden, cuota, onCerrar }) {
  const metodoTxt = cuota.metodo
    ? (cuota.metodo.tipo === 'Tarjeta' ? `${cuota.metodo.marca} terminada en ${cuota.metodo.ultimos_digitos}` : cuota.metodo.tipo)
    : cuota.proveedor === 'stripe' ? 'Tarjeta en Stripe Sandbox' : 'Registro histórico'

  return (
    <Modal titulo={`Detalle · Cuota ${cuota.nro_cuota} (Orden #${orden.nro_orden})`} onCerrar={onCerrar}>
      <dl className="grid grid-cols-2 gap-3 text-sm max-movil:grid-cols-1">
        <div><dt className="text-xs text-tinta-suave">Importe</dt><dd className="font-bold tabular-nums">{bsPago(cuota.monto)} (BOB)</dd></div>
        <div><dt className="text-xs text-tinta-suave">Estado</dt><dd><Etiqueta estado={cuota.estado} /></dd></div>
        <div><dt className="text-xs text-tinta-suave">Fecha de pago</dt><dd className="tabular-nums">{fecha(cuota.fecha_pago, true)}</dd></div>
        <div><dt className="text-xs text-tinta-suave">Método</dt><dd>{metodoTxt}</dd></div>
        <div><dt className="text-xs text-tinta-suave">Pasarela</dt><dd>{cuota.proveedor === 'stripe' ? 'Stripe Checkout Sandbox' : 'Pago manual histórico'}</dd></div>
        {cuota.stripe_pago_intent && (
          <div className="col-span-full"><dt className="text-xs text-tinta-suave">Referencia Stripe</dt><dd className="font-mono text-xs break-all">{cuota.stripe_pago_intent}</dd></div>
        )}
        {!cuota.stripe_pago_intent && cuota.observacion && (
          <div className="col-span-full"><dt className="text-xs text-tinta-suave">Observación</dt><dd>{cuota.observacion}</dd></div>
        )}
      </dl>
      <div className="acciones justify-start">
        {cuota.stripe_recibo_url && (
          <a className="btn btn-secundario" href={cuota.stripe_recibo_url} target="_blank" rel="noreferrer"><ExternalLink size={15} /> Recibo Stripe</a>
        )}
        <button type="button" className="btn btn-primario" onClick={onCerrar}>Cerrar</button>
      </div>
    </Modal>
  )
}

function ModalAnularOrden({ orden, onCerrar, onListo }) {
  const [motivo, setMotivo] = useState('')
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  async function enviar(e) {
    e.preventDefault()
    setEnviando(true)
    try {
      onListo((await pagosApi.anularOrden(orden.nro_orden, motivo)).data.mensaje)
    } catch (err) {
      setError(apiErrorMessage(err))
      setEnviando(false)
    }
  }

  return (
    <Modal titulo={`Anular orden #${orden.nro_orden}`} descripcion={`Importe: ${bsPago(orden.total)}. Si tiene enlaces Stripe pendientes, quedarán deshabilitados.`} onCerrar={onCerrar}>
      <form className="grid gap-4" onSubmit={enviar}>
        <Campo etiqueta="Motivo de anulación" requerido ayuda="Mínimo 5 caracteres. Queda registrado en el historial.">
          <textarea required minLength={5} maxLength={500} value={motivo} onChange={(e) => setMotivo(e.target.value)} />
        </Campo>
        <Aviso tipo="error">{error}</Aviso>
        <div className="acciones">
          <button type="button" className="btn btn-secundario" onClick={onCerrar}>Cancelar</button>
          <Boton type="submit" className="btn-peligro-suave" cargando={enviando} disabled={motivo.trim().length < 5}>Confirmar anulación</Boton>
        </div>
      </form>
    </Modal>
  )
}
