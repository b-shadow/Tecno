import { useState } from 'react'
import { CreditCard } from 'lucide-react'
import { Etiqueta } from '../ui'
import * as pagosApi from '../../api/pagos'

/** Sección 3: Métodos de pago Stripe del prospecto, inicialmente contraída y sin QR/transferencia nuevos. */
export default function MetodosPago({ metodos = [], editable, onSolicitarRegistro, onCambio, aviso }) {
  const [mostrarInactivos, setMostrarInactivos] = useState(false)
  const [cambiando, setCambiando] = useState(null)

  const esTarjetaStripe = (m) => m.proveedor === 'stripe' || m.tipo === 'Tarjeta'
  const activosStripe = metodos.filter((m) => m.estado === 'activo' && esTarjetaStripe(m))
  const inactivosOHistoricos = metodos.filter((m) => !(m.estado === 'activo' && esTarjetaStripe(m)))
  const visibles = mostrarInactivos ? [...activosStripe, ...inactivosOHistoricos] : activosStripe

  async function cambiarEstado(m, nuevoEstado) {
    setCambiando(m.nro_metodo)
    try {
      const { data } = await pagosApi.cambiarEstadoMetodo(m.nro_metodo, nuevoEstado)
      aviso.ok(data.mensaje)
      onCambio()
    } catch (e) {
      aviso.error(e)
    } finally {
      setCambiando(null)
    }
  }

  return (
    <details className="hoja">
      <summary className="hoja-titulo cursor-pointer list-none select-none">
        <span className="flex flex-wrap items-center gap-2 font-semibold">
          <span>Métodos de pago del cliente</span>
          <span className="rounded-pill bg-niebla-2 px-2 py-0.5 text-xs font-bold tabular-nums text-tinta-suave">
            {activosStripe.length} {activosStripe.length === 1 ? 'tarjeta activa' : 'tarjetas activas'}
          </span>
        </span>
        <span className="text-xs text-tinta-suave">Desplegar</span>
      </summary>

      <div className="hoja-cuerpo grid gap-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <label className="check text-sm text-tinta-suave">
            <input
              type="checkbox"
              checked={mostrarInactivos}
              onChange={(e) => setMostrarInactivos(e.target.checked)}
            />
            Mostrar métodos inactivos e históricos
          </label>
          {editable && (
            <button type="button" className="btn btn-primario" onClick={onSolicitarRegistro}>
              <CreditCard size={16} /> Solicitar registro de tarjeta
            </button>
          )}
        </div>

        {!visibles.length ? (
          <p className="text-sm text-tinta-suave">
            No hay tarjetas activas registradas en Stripe. Puedes enviar al cliente un enlace seguro para registrar su tarjeta.
          </p>
        ) : (
          <div className="grid gap-2.5">
            {visibles.map((m) => {
              const stripe = esTarjetaStripe(m)
              const activa = m.estado === 'activo'
              const etiquetaEstado = stripe ? (activa ? 'Activa' : 'Inactiva') : 'Histórico'
              return (
                <div
                  key={m.nro_metodo}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-ui border border-filete bg-niebla-2 p-3"
                >
                  <div className="grid gap-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <strong className="text-sm">
                        {stripe
                          ? `${m.marca || 'Tarjeta'} terminada en ${m.ultimos_digitos || '••••'}`
                          : `${m.tipo} · Registro manual histórico`}
                      </strong>
                      <Etiqueta estado={activa && stripe ? 'Activo' : 'Inactivo'}>{etiquetaEstado}</Etiqueta>
                    </div>
                    <p className="text-xs text-tinta-suave">
                      {stripe
                        ? `Vence: ${m.vencimiento || '—'} · Titular: ${m.titular || 'Cliente Stripe'}`
                        : `Titular: ${m.titular || '—'} · Método anterior fuera de línea`}
                    </p>
                  </div>

                  {editable && stripe && (
                    <button
                      type="button"
                      className="btn btn-secundario"
                      disabled={cambiando === m.nro_metodo}
                      onClick={() => cambiarEstado(m, activa ? 'inactivo' : 'activo')}
                    >
                      {activa ? 'Desactivar' : 'Reactivar'}
                    </button>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </details>
  )
}
