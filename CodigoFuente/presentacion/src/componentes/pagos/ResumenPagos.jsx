import { Plus, RefreshCw } from 'lucide-react'

/** Formatea montos monetarios en bolivianos con dos decimales (ej. Bs 2.340,00). */
export const bsPago = (n) =>
  `Bs ${Number(n || 0).toLocaleString('es-BO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

/** Sección 1: Resumen financiero del prospecto con barra de progreso y acciones principales. */
export default function ResumenPagos({ totalContratado, totalPagado, saldoPendiente, cuotasPagadas, totalCuotas, tieneOrdenes, puedeGenerar, onGenerar, onActualizar, actualizando }) {
  return (
    <section className="hoja hoja-cuerpo grid gap-4" aria-label="Gestión de pagos">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h4 className="text-sm font-bold tracking-wide text-tinta-suave uppercase">Gestión de pagos</h4>
        </div>
        <div className="acciones flex-wrap">
          {tieneOrdenes && (
            <button type="button" className="btn btn-secundario" disabled={actualizando} onClick={onActualizar}>
              <RefreshCw size={15} className={actualizando ? 'animate-girar' : ''} /> Actualizar estado
            </button>
          )}
          {puedeGenerar && (
            <button type="button" className="btn btn-primario" onClick={onGenerar}>
              <Plus size={16} /> Generar orden de pago
            </button>
          )}
        </div>
      </div>

      <dl className="cifras pagos-cifras">
        <div>
          <dt>Total contratado</dt>
          <dd className="tabular-nums">{bsPago(totalContratado)}</dd>
        </div>
        <div>
          <dt>Total pagado</dt>
          <dd className="tabular-nums text-exito">{bsPago(totalPagado)}</dd>
        </div>
        <div>
          <dt>Saldo pendiente</dt>
          <dd className="tabular-nums">{bsPago(saldoPendiente)}</dd>
        </div>
      </dl>

      {totalCuotas > 0 && (
        <div className="grid gap-1.5">
          <progress
            className={`pagos-progreso ${cuotasPagadas === totalCuotas ? 'pagos-progreso-completa' : ''}`}
            value={cuotasPagadas}
            max={totalCuotas}
            aria-label="Progreso de cuotas pagadas"
          />
          <p className="text-sm font-semibold text-tinta-suave tabular-nums">
            {cuotasPagadas} de {totalCuotas} {totalCuotas === 1 ? 'cuota pagada' : 'cuotas pagadas'}
          </p>
        </div>
      )}
    </section>
  )
}
