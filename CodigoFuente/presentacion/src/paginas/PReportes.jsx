import { useState } from 'react'
import { Download } from 'lucide-react'
import { descargarCsv } from '../servicios/archivos'
import { useAuth } from '../servicios/auth'
import { Aviso, Barras, CabeceraPagina, Campo, Cargando, Vacio, bs, nombre, useDatos } from '../componentes/ui'
import * as reportesApi from '../api/reportes'
import * as usuariosApi from '../api/usuarios'
import { ETAPA } from '../componentes/tonos'

const TIPOS = { tarjetas: 'Embudo de ventas', pagos: 'Cuotas y pagos', matriculas: 'Matrículas', comisiones: 'Comisiones', perdidas: 'Pérdidas y motivos', vendedores: 'Cartera por vendedor' }
const MONEDA = ['monto', 'precio']

/** CU8. Docente: "reporte es un listado, estadística es la representación porcentual". Aquí están los dos. */
export default function PReportes() {
  const { usuario } = useAuth()
  const [vista, setVista] = useState('estadisticas')
  const [f, setF] = useState({ tipo: 'tarjetas', desde: '', hasta: '', vendedor: '', estado: '', buscar: '' })
  const params = Object.fromEntries(Object.entries(f).filter(([, v]) => v))
  const est = useDatos(async () => (await reportesApi.estadisticas(params)).data, [f.desde, f.hasta, f.vendedor])
  const rep = useDatos(async () => (vista === 'listado' ? (await reportesApi.listado(params)).data : null), [vista, f.tipo, f.desde, f.hasta, f.vendedor, f.estado, f.buscar])
  const vendedores = useDatos(async () => (usuario?.rol === 'vendedor' ? [] : (await usuariosApi.vendedores()).data.vendedores), [usuario?.rol])
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })

  return (
    <>
      <CabeceraPagina titulo="Reportes y estadísticas">{usuario?.rol === 'vendedor' ? 'Sus cifras.' : 'Filtre por fechas y vendedor para ver cuántos leads tiene cada uno y cuántos concretó.'}</CabeceraPagina>
      <div className="pestanas mb-4" role="tablist">
        <button type="button" role="tab" aria-selected={vista === 'estadisticas'} onClick={() => setVista('estadisticas')}>Estadísticas (%)</button>
        <button type="button" role="tab" aria-selected={vista === 'listado'} onClick={() => setVista('listado')}>Reportes (listados)</button>
      </div>
      <div className="barra-filtros">
        {vista === 'listado' && <Campo etiqueta="Reporte"><select value={f.tipo} onChange={set('tipo')}>{Object.entries(TIPOS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></Campo>}
        <Campo etiqueta="Desde"><input type="date" value={f.desde} onChange={set('desde')} /></Campo>
        <Campo etiqueta="Hasta"><input type="date" value={f.hasta} min={f.desde || undefined} onChange={set('hasta')} /></Campo>
        {usuario?.rol !== 'vendedor' && <Campo etiqueta="Vendedor"><select value={f.vendedor} onChange={set('vendedor')}><option value="">Todos</option>{(vendedores.datos || []).map((v) => <option key={v.correo} value={v.correo}>{nombre(v)}</option>)}</select></Campo>}
        {vista === 'listado' && <Campo etiqueta="Buscar"><input type="search" value={f.buscar} onChange={set('buscar')} placeholder="Prospecto, CI o módulo" /></Campo>}
      </div>

      {vista === 'estadisticas' && (est.error ? <Aviso tipo="error">{est.error}</Aviso> : est.cargando && !est.datos ? <Cargando /> : (
        <>
          <div className="grid grid-cols-2 gap-6 max-movil:grid-cols-1 mb-6">
            <section className="hoja"><header className="hoja-titulo"><h3>Embudo por etapa</h3></header><div className="hoja-cuerpo"><Barras datos={est.datos.embudo.map((e) => ({ ...e, tono: ETAPA[e.etiqueta] }))} /></div></section>
            <section className="hoja"><header className="hoja-titulo"><h3>Origen de los leads</h3></header><div className="hoja-cuerpo"><Barras datos={est.datos.origen_de_leads} tono="seguimiento" /></div></section>
          </div>
          <div className="grid grid-cols-2 gap-6 max-movil:grid-cols-1 mb-6">
            <section className="hoja"><header className="hoja-titulo"><h3>Pérdidas por categoría (CU5)</h3></header><div className="hoja-cuerpo"><Barras datos={est.datos.perdidas_por_categoria} tono="perdido" /></div></section>
            <section className="hoja"><header className="hoja-titulo"><h3>Pérdidas por motivo</h3></header><div className="hoja-cuerpo"><Barras datos={est.datos.perdidas_por_motivo} tono="perdido" /></div></section>
          </div>
          <section className="hoja"><header className="hoja-titulo"><h3>Conversión por vendedor</h3></header>
            {!est.datos.conversion_por_vendedor.length ? <Vacio titulo="Sin datos de vendedores" /> : (
              <div className="tabla-marco rounded-none border-0"><table className="tabla"><thead><tr><th>Vendedor</th><th className="num">Tarjetas</th><th className="num">Concretadas</th><th className="num">Perdidas</th><th className="num">Conversión</th></tr></thead>
                <tbody>{est.datos.conversion_por_vendedor.map((v) => <tr key={v.vendedor}><td>{v.vendedor}</td><td className="num">{v.total}</td><td className="num">{v.convertidos}</td><td className="num">{v.perdidos}</td><td className="num">{Number(v.tasa_conversion).toLocaleString('es-BO')} %</td></tr>)}</tbody></table></div>
            )}
          </section>
        </>
      ))}

      {vista === 'listado' && (rep.error ? <Aviso tipo="error">{rep.error}</Aviso> : rep.cargando && !rep.datos ? <Cargando /> : rep.datos && (
        <section className="hoja">
          <header className="hoja-titulo"><h3>{rep.datos.titulo} · {rep.datos.filas.length} fila(s)</h3>
            <button type="button" className="btn btn-secundario" disabled={!rep.datos.filas.length} onClick={() => descargarCsv(`reporte_${f.tipo}.csv`, rep.datos.filas)}><Download size={16} /> Exportar CSV</button></header>
          {!rep.datos.filas.length ? <Vacio titulo="Sin resultados con esos filtros" /> : (
            <div className="tabla-marco rounded-none border-0"><table className="tabla">
              <thead><tr>{rep.datos.columnas.map((c) => <th key={c.key} className={MONEDA.includes(c.key) ? 'num' : ''}>{c.label}</th>)}</tr></thead>
              <tbody>{rep.datos.filas.map((fila, i) => <tr key={i}>{rep.datos.columnas.map((c) => <td key={c.key} className={MONEDA.includes(c.key) ? 'num' : ''}>{MONEDA.includes(c.key) ? bs(fila[c.key]) : fila[c.key] ?? '—'}</td>)}</tr>)}</tbody>
            </table></div>
          )}
        </section>
      ))}
    </>
  )
}
