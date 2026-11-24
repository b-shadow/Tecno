import { useState } from 'react'
import { FileSearch, ReceiptText } from 'lucide-react'
import { go } from '../servicios/navigation'
import { Aviso, CabeceraPagina, Campo, Cargando, Etiqueta, Modal, Vacio, bs, fecha, useAviso, useDatos } from '../componentes/ui'
import * as pagosApi from '../api/pagos'

const ESTADOS = ['En revision', 'Pendiente de pago', 'Pago aprobado', 'Pago rechazado']
const TEXTO = { 'En revision': 'En revisión' }

/** CU6: coordinación revisa los comprobantes de cada cuota. Aprobar la 1.ª cuota dispara la matrícula si los datos están completos. */
export default function ValidacionPagos() {
  const [estado, setEstado] = useState('En revision')
  const { datos, cargando, error, recargar } = useDatos(async () => (await pagosApi.cuotas({ estado: estado || undefined })).data.cuotas, [estado])
  const [revisar, setRevisar] = useState(null)
  const aviso = useAviso()

  return (
    <>
      <CabeceraPagina titulo="Validación de pagos">Revise el comprobante y apruebe o rechace la cuota. El vendedor ve el resultado en la ficha.</CabeceraPagina>
      <div className="barra-filtros">
        <div className="segmentos" role="group" aria-label="Estado de la cuota">
          {ESTADOS.map((e) => <button key={e} type="button" aria-pressed={estado === e} onClick={() => setEstado(e)}>{TEXTO[e] || e}</button>)}
          <button type="button" aria-pressed={!estado} onClick={() => setEstado('')}>Todas</button>
        </div>
      </div>
      {error && <Aviso tipo="error">{error}</Aviso>}
      {cargando && !datos ? <Cargando /> : !datos?.length ? <Vacio titulo={estado === 'En revision' ? 'No hay comprobantes por revisar' : 'Sin cuotas en este estado'} icono={ReceiptText} /> : (
        <div className="tabla-marco">
          <table className="tabla">
            <thead><tr><th>Prospecto</th><th>Orden · cuota</th><th className="num">Monto</th><th>Vence</th><th>Vendedor</th><th>Estado</th><th /></tr></thead>
            <tbody>
              {datos.map((c) => (
                <tr key={`${c.nro_orden}-${c.nro_cuota}`}>
                  <td><a href="#" onClick={(e) => { e.preventDefault(); go(`/agenda?interes=${c.nro_tarjeta}`) }}><strong>{c.prospecto}</strong></a><br /><small>{c.modulo_nombre}</small></td>
                  <td className="cifra">#{c.nro_orden} · {c.nro_cuota}</td>
                  <td className="num">{bs(c.monto)}</td>
                  <td className="cifra">{fecha(c.fecha_vencimiento)}</td>
                  <td>{c.vendedor}</td>
                  <td><Etiqueta estado={c.estado}>{TEXTO[c.estado] || c.estado}</Etiqueta></td>
                  <td>{(c.comprobantes.length> 0 || c.estado === 'En revision') && <button type="button" className="btn btn-secundario" onClick={() => setRevisar(c)}><FileSearch size={16} /> {c.estado === 'En revision' ? 'Revisar' : 'Ver'}</button>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {revisar && <Revision cuota={revisar} onCerrar={() => setRevisar(null)} onListo={(m) => { aviso.ok(m); setRevisar(null); recargar() }} aviso={aviso} />}
      {aviso.nodo}
    </>
  )
}

function Revision({ cuota, onCerrar, onListo, aviso }) {
  // Sin comprobante = cobro con tarjeta por la pasarela simulada: se valida con la transacción registrada.
  const comp = cuota.comprobantes[0]
  const archivo = useDatos(async () => (comp ? (await pagosApi.comprobante(comp.nro_comprobante)).data.comprobante : null), [comp?.nro_comprobante])
  const [observacion, setObservacion] = useState('')
  const enRevision = cuota.estado === 'En revision'
  async function decidir(accion) {
    try {
      const { data } = await pagosApi[accion](cuota.nro_orden, cuota.nro_cuota, observacion || undefined)
      onListo(data.faltantes_conversion?.length ? `${data.mensaje} Para matricular falta: ${data.faltantes_conversion.join(' ')}` : data.mensaje)
    } catch (e) { aviso.error(e) }
  }
  const a = archivo.datos
  return (
    <Modal ancho titulo={`${cuota.prospecto} · cuota ${cuota.nro_cuota} de la orden #${cuota.nro_orden}`} descripcion={comp ? `${bs(cuota.monto)} · ${comp.nombre_archivo || 'comprobante'} · enviado ${fecha(comp.fecha_envio, true)}` : `${bs(cuota.monto)} · cobro con tarjeta (pasarela simulada)`} onCerrar={onCerrar}
      pie={enRevision && <div className="acciones"><button type="button" className="btn btn-peligro-suave" disabled={!observacion.trim()} onClick={() => decidir('rechazar')}>Rechazar</button><button type="button" className="btn btn-primario" onClick={() => decidir('aprobar')}>Aprobar pago</button></div>}>
      {archivo.cargando ? <Cargando filas={3} /> : a?.mime === 'application/pdf'
        ? <iframe title="Comprobante" src={a.archivo} className="comprobante-pdf" />
        : a && <img src={a.archivo} alt={`Comprobante de ${cuota.prospecto}`} className="comprobante-img" />}
      {!comp && cuota.observacion && <p><b>Transacción:</b> {cuota.observacion}</p>}
      {comp?.remitente && <p><b>Enviado por:</b> {comp.remitente}{comp.hora_pago ? ` · pagado el ${fecha(comp.hora_pago, true)}` : ''}</p>}
      {comp?.observacion && <p><b>Observación:</b> {comp.observacion}</p>}
      {enRevision && <Campo etiqueta="Observación" ayuda="Obligatoria para rechazar: el vendedor la verá en la ficha."><textarea value={observacion} maxLength={1000} onChange={(e) => setObservacion(e.target.value)} /></Campo>}
    </Modal>
  )
}
