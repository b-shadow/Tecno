import { useMemo, useState } from 'react'
import { Aviso, Boton, Campo, Cargando, Modal, fecha, hoyLocal, nombre, useDatos } from '../ui'
import { apiErrorMessage } from '../../servicios/errors'
import { bsPago } from './ResumenPagos'
import * as catalogoApi from '../../api/catalogo'
import * as pagosApi from '../../api/pagos'

// Parámetros configurables del formulario (fáciles de ajustar durante la defensa).
const MIN_MODULOS_DESCUENTO = 3
const OPCIONES_CUOTAS = [2, 3, 4, 5, 6, 8, 10, 12]

function sumarMesesSinDesborde(fechaIso, meses) {
  const [anio, mes, dia] = fechaIso.split('-').map(Number)
  const destino = new Date(anio, mes - 1 + meses, 1, 12, 0, 0)
  const ultimoDia = new Date(destino.getFullYear(), destino.getMonth() + 1, 0, 12, 0, 0).getDate()
  destino.setDate(Math.min(dia, ultimoDia))
  return `${destino.getFullYear()}-${String(destino.getMonth() + 1).padStart(2, '0')}-${String(destino.getDate()).padStart(2, '0')}`
}

function esCorreoValido(correo) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(correo || '').trim())
}

/** Modal limpio y organizado para configurar módulos, descuentos, plan de cuotas y envíos automáticos. */
export default function FormularioOrdenPago({ t, onCerrar, onListo }) {
  const catalogo = useDatos(async () => (await catalogoApi.programas()).data.programas)
  const descuentos = useDatos(async () => (await pagosApi.descuentos()).data.descuentos)
  const programa = catalogo.datos?.find((p) => p.modulos.some((m) => m.codigo === t.modulo_codigo))

  const correoProspecto = String(t.prospecto?.correo || '').trim()
  const tieneCorreoValido = esCorreoValido(correoProspecto)

  const [modulos, setModulos] = useState([t.modulo_codigo])
  const [dctos, setDctos] = useState([])
  const [formaPago, setFormaPago] = useState('unico')
  const [cuotas, setCuotas] = useState(3)
  const [vence, setVence] = useState(() => hoyLocal(1))
  const [envioAutomatico, setEnvioAutomatico] = useState(tieneCorreoValido)
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  const totalModulosPrograma = programa?.modulos?.length || 0
  const cumpleTresModulos = modulos.length >= MIN_MODULOS_DESCUENTO
  const cumpleProgramaCompleto = totalModulosPrograma > 0 && modulos.length === totalModulosPrograma

  function actualizarModulos(siguiente) {
    setModulos(siguiente)
    const cumpleTres = siguiente.length >= MIN_MODULOS_DESCUENTO
    const cumpleComp = totalModulosPrograma > 0 && siguiente.length === totalModulosPrograma
    // Depura de forma síncrona los descuentos incompatibles con la nueva selección de módulos.
    setDctos((prev) => prev.filter((codigo) => {
      if (codigo === '3_MAS_MODULOS' && !cumpleTres) return false
      if (codigo === 'PROGRAMA_COMPLETO' && !cumpleComp) return false
      return true
    }))
  }

  function seleccionarModulo(codigo) {
    actualizarModulos(modulos.includes(codigo) ? modulos.filter((x) => x !== codigo) : [...modulos, codigo])
  }

  function alternarProgramaCompleto(marcado) {
    if (!programa) return
    actualizarModulos(marcado ? programa.modulos.map((m) => m.codigo) : [])
  }

  function alternarDescuento(codigo) {
    setDctos((prev) => (prev.includes(codigo) ? prev.filter((x) => x !== codigo) : [...prev, codigo]))
  }

  const subtotal = useMemo(
    () => (programa?.modulos || []).filter((m) => modulos.includes(m.codigo)).reduce((s, m) => s + Number(m.precio), 0),
    [programa, modulos],
  )

  const descuentosAplicados = useMemo(
    () => (descuentos.datos || []).filter((d) => dctos.includes(d.codigo)),
    [descuentos.datos, dctos],
  )

  // Conserva exactamente la fórmula de acumulación del backend (cada descuento redondeado a 2 decimales sobre el subtotal).
  const importeDescontado = useMemo(
    () => descuentosAplicados.reduce((s, d) => s + Math.round(subtotal * Number(d.porcentaje)) / 100, 0),
    [descuentosAplicados, subtotal],
  )

  const total = Math.max(Math.round((subtotal - importeDescontado) * 100) / 100, 0)
  const cantidadCuotas = formaPago === 'unico' ? 1 : cuotas

  const vistaCuotas = useMemo(() => {
    if (total <= 0 || !vence) return []
    const base = Math.floor((total / cantidadCuotas) * 100) / 100
    return Array.from({ length: cantidadCuotas }, (_, idx) => {
      const nro = idx + 1
      const importe = nro === cantidadCuotas ? Math.round((total - base * (cantidadCuotas - 1)) * 100) / 100 : base
      return { nro, fecha: sumarMesesSinDesborde(vence, idx), importe }
    })
  }, [total, cantidadCuotas, vence])

  async function generarOrden(e) {
    e.preventDefault()
    if (!modulos.length || enviando) return
    setEnviando(true)
    setError(null)
    try {
      const { data } = await pagosApi.crearOrden(t.nro_tarjeta, {
        modulos,
        descuentos: dctos,
        cuotas: cantidadCuotas,
        primer_vencimiento: vence,
        envio_automatico: tieneCorreoValido ? envioAutomatico : false,
      })
      onListo(data.mensaje, data.aviso_correo)
    } catch (err) {
      setError(apiErrorMessage(err))
      setEnviando(false)
    }
  }

  return (
    <Modal ancho titulo="Generar orden de pago" descripcion="Configura módulos, descuentos, forma de pago y recordatorios." onCerrar={onCerrar}>
      {!programa ? <Cargando /> : (
        <form className="grid gap-5" onSubmit={generarOrden}>
          {/* A. Información comercial */}
          <section className="grid grid-cols-2 gap-3 rounded-ui border border-filete bg-niebla-2 p-3.5 max-movil:grid-cols-1">
            <div>
              <span className="text-xs text-tinta-suave">Prospecto</span>
              <strong className="block">{nombre(t.prospecto)}</strong>
            </div>
            <div>
              <span className="text-xs text-tinta-suave">Programa educativo</span>
              <strong className="block">{programa.nombre}</strong>
            </div>
          </section>

          {/* B. Selección de módulos */}
          <fieldset className="grid gap-2.5 min-w-0">
            <legend className="mb-1 font-bold">Módulos contratados</legend>
            <label className="check font-semibold">
              <input
                type="checkbox"
                checked={cumpleProgramaCompleto}
                onChange={(e) => alternarProgramaCompleto(e.target.checked)}
              />
              Seleccionar programa completo ({totalModulosPrograma} módulos)
            </label>
            <div className="grid gap-2 rounded-ui border border-filete p-3">
              {programa.modulos.map((m, i) => (
                <label key={m.codigo} className="check justify-between gap-2">
                  <span className="flex items-center gap-2.5">
                    <input
                      type="checkbox"
                      checked={modulos.includes(m.codigo)}
                      onChange={() => seleccionarModulo(m.codigo)}
                    />
                    <span>{String(i + 1).padStart(2, '0')} · {m.nombre}</span>
                  </span>
                  <b className="text-sm tabular-nums">{bsPago(m.precio)}</b>
                </label>
              ))}
            </div>
            <div className="flex flex-wrap justify-between gap-2 text-sm text-tinta-suave">
              <span>{modulos.length} {modulos.length === 1 ? 'módulo seleccionado' : 'módulos seleccionados'}</span>
              <span>Subtotal: <b className="text-tinta tabular-nums">{bsPago(subtotal)}</b></span>
            </div>
          </fieldset>

          {/* C. Descuentos */}
          <fieldset className="grid gap-2.5 min-w-0">
            <legend className="mb-1 font-bold">Descuentos</legend>
            <div className="grid gap-2 rounded-ui border border-filete p-3">
              {(descuentos.datos || []).map((d) => {
                const esTres = d.codigo === '3_MAS_MODULOS'
                const esCompleto = d.codigo === 'PROGRAMA_COMPLETO'
                const deshabilitado = (esTres && !cumpleTresModulos) || (esCompleto && !cumpleProgramaCompleto)
                const ayudaRegla = esTres && !cumpleTresModulos
                  ? 'Selecciona al menos tres módulos para aplicar este descuento.'
                  : esCompleto && !cumpleProgramaCompleto
                    ? 'Selecciona todos los módulos para aplicar este descuento.'
                    : null
                return (
                  <div key={d.codigo} className="grid gap-0.5">
                    <label className={`check ${deshabilitado ? 'opacity-60' : ''}`}>
                      <input
                        type="checkbox"
                        disabled={deshabilitado}
                        checked={dctos.includes(d.codigo)}
                        onChange={() => alternarDescuento(d.codigo)}
                      />
                      <span>{d.nombre} — <b>{Number(d.porcentaje)}%</b></span>
                    </label>
                    {ayudaRegla && <small className="pl-7 text-xs text-tinta-suave">{ayudaRegla}</small>}
                  </div>
                )
              })}
            </div>
          </fieldset>

          {/* D/E. Resumen económico */}
          <section className="rounded-ui border border-filete bg-niebla-2 p-4 grid gap-1.5 text-sm">
            <div className="flex justify-between gap-2">
              <span className="text-tinta-suave">Subtotal</span>
              <span className="tabular-nums">{bsPago(subtotal)}</span>
            </div>
            <div className="flex justify-between gap-2">
              <span className="text-tinta-suave">
                Descuentos ({descuentosAplicados.length ? descuentosAplicados.map((d) => `${d.nombre} ${Number(d.porcentaje)}%`).join(' + ') : 'Ninguno'})
              </span>
              <span className="tabular-nums text-exito">- {bsPago(importeDescontado)}</span>
            </div>
            <div className="mt-1 flex justify-between gap-2 border-t border-filete pt-2 text-base font-bold">
              <span>Total final</span>
              <span className="text-lg tabular-nums text-acento-texto">{bsPago(total)}</span>
            </div>
          </section>

          {/* F. Forma de pago */}
          <div className="grid grid-cols-3 gap-4 max-movil:grid-cols-1">
            <Campo etiqueta="Forma de pago" requerido>
              <select value={formaPago} onChange={(e) => setFormaPago(e.target.value)}>
                <option value="unico">Pago único</option>
                <option value="cuotas">Pago en cuotas</option>
              </select>
            </Campo>
            {formaPago === 'cuotas' && (
              <Campo etiqueta="Cantidad de cuotas" requerido>
                <select value={cuotas} onChange={(e) => setCuotas(Number(e.target.value))}>
                  {OPCIONES_CUOTAS.map((n) => (
                    <option key={n} value={n}>Plan de {n} cuotas</option>
                  ))}
                </select>
              </Campo>
            )}
            <Campo etiqueta={formaPago === 'unico' ? 'Vencimiento' : 'Primer vencimiento'} requerido>
              <input type="date" min={hoyLocal()} required value={vence} onChange={(e) => setVence(e.target.value)} />
            </Campo>
          </div>

          {/* G. Vista previa de cuotas */}
          {formaPago === 'cuotas' && vistaCuotas.length > 0 && (
            <div className="grid gap-1.5">
              <strong className="text-sm">Vista previa del plan</strong>
              <div className="tabla-marco">
                <table className="tabla">
                  <thead>
                    <tr>
                      <th>Cuota</th>
                      <th>Vencimiento</th>
                      <th className="num">Importe</th>
                    </tr>
                  </thead>
                  <tbody>
                    {vistaCuotas.map((c) => (
                      <tr key={c.nro}>
                        <td className="tabular-nums">{c.nro} de {cantidadCuotas}</td>
                        <td className="tabular-nums">{fecha(c.fecha)}</td>
                        <td className="num">{bsPago(c.importe)}</td>
                      </tr>
                    ))}
                    <tr className="font-bold">
                      <td colSpan={2}>Total</td>
                      <td className="num">{bsPago(total)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* H. Envío automático */}
          <section className="rounded-ui border border-filete p-3.5 grid gap-1">
            <label className={`check font-semibold ${!tieneCorreoValido ? 'opacity-60' : ''}`}>
              <input
                type="checkbox"
                disabled={!tieneCorreoValido}
                checked={tieneCorreoValido && envioAutomatico}
                onChange={(e) => setEnvioAutomatico(e.target.checked)}
              />
              Enviar solicitudes y recordatorios automáticamente por correo electrónico
            </label>
            <small className="pl-7 text-xs text-tinta-suave">
              {tieneCorreoValido
                ? 'UNEXO enviará automáticamente las solicitudes según los vencimientos. También podrás enviar cualquier cuota manualmente.'
                : 'El cliente no tiene un correo válido registrado. Puedes crear la orden y compartir los enlaces por WhatsApp o copia manual.'}
            </small>
          </section>

          {!modulos.length && <Aviso tipo="error">Selecciona al menos un módulo para generar la orden.</Aviso>}
          <Aviso tipo="error">{error}</Aviso>

          {/* I. Botones finales */}
          <div className="acciones">
            <button type="button" className="btn btn-secundario" disabled={enviando} onClick={onCerrar}>Cancelar</button>
            <Boton type="submit" className="btn-primario" cargando={enviando} disabled={!modulos.length || total <= 0}>
              {enviando ? 'Generando orden...' : 'Confirmar orden de pago'}
            </Boton>
          </div>
        </form>
      )}
    </Modal>
  )
}
