import { useState } from 'react'
import { BadgeDollarSign } from 'lucide-react'
import { puede, useAuth } from '../servicios/auth'
import { Aviso, CabeceraPagina, Campo, Cargando, Etiqueta, Vacio, bs, fecha, nombre, useAviso, useDatos } from '../componentes/ui'
import * as seguimientoApi from '../api/seguimiento'

/** CU8: ventas concretadas y comisiones de cada vendedor; coordinación fija el porcentaje y registra los pagos. */
export default function PComisiones() {
  const sesion = useAuth()
  const gestiona = puede('seguimiento', 'modificacion', sesion)
  const comisiones = useDatos(async () => (await seguimientoApi.comisiones()).data, [], { intervaloMs: 5000, refrescarAlEnfocar: true })
  const resumen = useDatos(async () => (gestiona ? (await seguimientoApi.resumenComisiones()).data.vendedores : []), [gestiona], { intervaloMs: 5000, refrescarAlEnfocar: true })
  const [porcentaje, setPorcentaje] = useState('')
  const aviso = useAviso()
  const recargar = () => { comisiones.recargar(); resumen.recargar() }

  if (comisiones.cargando && !comisiones.datos) return <Cargando />
  if (comisiones.error) return <Aviso tipo="error">{comisiones.error}</Aviso>
  const lista = comisiones.datos.comisiones
  const pendiente = lista.filter((c) => c.estado === 'Pendiente').reduce((s, c) => s + Number(c.monto), 0)

  return (
    <>
      <CabeceraPagina titulo="Ventas y comisiones">Cada módulo matriculado genera la comisión del vendedor que hizo la venta, con el porcentaje vigente en ese momento.</CabeceraPagina>
      <dl className="cifras mb-6">
        <div><dt>Ventas concretadas</dt><dd>{lista.length}</dd></div>
        <div><dt>Comisión pendiente</dt><dd className="tabular-nums">{bs(pendiente)}</dd></div>
        <div><dt>Porcentaje vigente</dt><dd>{Number(comisiones.datos.porcentaje)}%</dd></div>
      </dl>
      {gestiona && (
        <div className="grid grid-cols-[minmax(0,2fr)_minmax(0,1fr)] gap-6 max-movil:grid-cols-1 mb-6">
          <section className="hoja"><header className="hoja-titulo"><h3>Por vendedor</h3></header>
            <div className="tabla-marco rounded-none border-0"><table className="tabla">
              <thead><tr><th>Vendedor</th><th className="num">Cursos</th><th className="num">Total</th><th className="num">Pendiente</th><th /></tr></thead>
              <tbody>{(resumen.datos || []).map((v) => (
                <tr key={v.correo}><td>{nombre(v)}</td><td className="num">{v.cursos_vendidos}</td><td className="num">{bs(v.comision_total)}</td><td className="num">{bs(v.comision_pendiente)}</td>
                  <td>{Number(v.comision_pendiente)> 0 && <button type="button" className="btn btn-secundario" onClick={async () => { try { aviso.ok((await seguimientoApi.pagarComisiones(v.correo)).data.mensaje); recargar() } catch (e) { aviso.error(e) } }}>Registrar pago</button>}</td></tr>
              ))}</tbody>
            </table></div>
          </section>
          {sesion.usuario?.rol === 'administrador' && <form className="hoja hoja-cuerpo grid gap-4" onSubmit={async (e) => { e.preventDefault(); try { aviso.ok((await seguimientoApi.actualizarConfiguracionComision(porcentaje)).data.mensaje); setPorcentaje(''); recargar() } catch (err) { aviso.error(err) } }}>
            <h3>Porcentaje de comisión</h3>
            <p className="text-sm text-tinta-suave">Se aplica a las ventas que se matriculen desde ahora.</p>
            <Campo etiqueta="Nuevo porcentaje (0 a 50)" requerido><input type="number" min={0} max={50} step="0.5" required value={porcentaje} onChange={(e) => setPorcentaje(e.target.value)} /></Campo>
            <div className="acciones"><button type="submit" className="btn btn-primario">Guardar</button></div>
          </form>}
        </div>
      )}
      {!lista.length ? <Vacio titulo="Todavía no hay ventas concretadas" icono={BadgeDollarSign} /> : (
        <div className="tabla-marco"><table className="tabla">
          <thead><tr><th>Alumno</th><th>Módulo</th><th>Vendedor</th><th className="num">%</th><th className="num">Comisión</th><th>Estado</th><th>Fecha</th></tr></thead>
          <tbody>{lista.map((c) => (
            <tr key={c.nro_solicitud}><td>{nombre(c.venta?.orden_pago?.interes?.prospecto)}</td><td>{c.venta?.modulo_nombre}</td><td>{nombre(c.vendedor)}</td>
              <td className="num">{Number(c.porcentaje)}</td><td className="num">{bs(c.monto)}</td><td><Etiqueta estado={c.estado} /></td><td className="tabular-nums">{fecha(c.created_at)}</td></tr>
          ))}</tbody>
        </table></div>
      )}
      {aviso.nodo}
    </>
  )
}
