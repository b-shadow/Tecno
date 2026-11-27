import { useEffect, useMemo, useRef, useState } from 'react'
import FormularioOrdenPago from './FormularioOrdenPago'
import HistorialPagos from './HistorialPagos'
import MetodosPago from './MetodosPago'
import ModalCompartirPago from './ModalCompartirPago'
import PlanPagos from './PlanPagos'
import ResumenPagos from './ResumenPagos'

/**
 * Orquestador principal de la pestaña Pagos en la ficha del prospecto.
 * Estructura visual en 4 bloques: Resumen -> Plan actual -> Métodos (contraído) -> Historial (contraído).
 */
export default function PagosProspecto({ t, esSuVendedor, editable, aviso, onCambio }) {
  const [modalOrden, setModalOrden] = useState(false)
  const [modalCompartir, setModalCompartir] = useState(null)
  const [actualizando, setActualizando] = useState(false)
  const timerRef = useRef(null)

  useEffect(() => () => {
    if (timerRef.current) clearTimeout(timerRef.current)
  }, [])

  const ordenes = t.ordenes_pago || []
  const metodos = t.prospecto?.metodos_pago || []

  const resumen = useMemo(() => {
    const vigentes = ordenes.filter((o) => o.estado !== 'Anulada')
    const totalContratado = vigentes.reduce((s, o) => s + Number(o.total || 0), 0)
    const todasCuotas = vigentes.flatMap((o) => o.cuotas || [])
    const pagadas = todasCuotas.filter((c) => c.estado === 'Pago aprobado')
    const totalPagado = pagadas.reduce((s, c) => s + Number(c.monto || 0), 0)
    const saldoPendiente = Math.max(Math.round((totalContratado - totalPagado) * 100) / 100, 0)
    const tieneOrdenAbierta = vigentes.some((o) => {
      const cuotas = o.cuotas || []
      return !(cuotas.length > 0 && cuotas.every((c) => c.estado === 'Pago aprobado'))
    })

    return {
      totalContratado,
      totalPagado,
      saldoPendiente,
      cuotasPagadas: pagadas.length,
      totalCuotas: todasCuotas.length,
      tieneOrdenAbierta,
    }
  }, [ordenes])

  const puedeGenerar = Boolean(editable && esSuVendedor && t.estado !== 'Convertido' && !resumen.tieneOrdenAbierta)

  async function refrescar() {
    setActualizando(true)
    try {
      await onCambio()
    } finally {
      if (timerRef.current) clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => setActualizando(false), 350)
    }
  }

  return (
    <div className="grid gap-5">
      <ResumenPagos
        totalContratado={resumen.totalContratado}
        totalPagado={resumen.totalPagado}
        saldoPendiente={resumen.saldoPendiente}
        cuotasPagadas={resumen.cuotasPagadas}
        totalCuotas={resumen.totalCuotas}
        tieneOrdenes={ordenes.length > 0}
        puedeGenerar={puedeGenerar}
        onGenerar={() => setModalOrden(true)}
        onActualizar={refrescar}
        actualizando={actualizando}
      />

      <PlanPagos
        t={t}
        ordenes={ordenes}
        editable={editable}
        puedeGenerar={puedeGenerar}
        onGenerar={() => setModalOrden(true)}
        onEnviarCuota={(orden, cuota) => setModalCompartir({ modo: 'cuota', orden, cuota })}
        aviso={aviso}
        onCambio={onCambio}
      />

      <MetodosPago
        metodos={metodos}
        editable={editable}
        onSolicitarRegistro={() => setModalCompartir({ modo: 'setup' })}
        onCambio={onCambio}
        aviso={aviso}
      />

      <HistorialPagos ordenes={ordenes} programaPorDefecto={t.programa_nombre} />

      {modalOrden && (
        <FormularioOrdenPago
          t={t}
          onCerrar={() => setModalOrden(false)}
          onListo={(mensaje) => {
            setModalOrden(false)
            aviso.ok(mensaje)
            onCambio()
          }}
        />
      )}

      {modalCompartir && (
        <ModalCompartirPago
          modo={modalCompartir.modo}
          t={t}
          orden={modalCompartir.orden || null}
          cuota={modalCompartir.cuota || null}
          onCerrar={() => setModalCompartir(null)}
          aviso={aviso}
          onCambio={onCambio}
        />
      )}
    </div>
  )
}
