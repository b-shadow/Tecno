import { useState } from 'react'
import { ScrollText } from 'lucide-react'
import { Aviso, Barras, CabeceraPagina, Campo, Cargando, Etiqueta, Vacio, fecha, useDatos } from '../componentes/ui'
import * as seguridadApi from '../api/seguridad'

const EVENTOS = { login_exitoso: 'Inicio de sesión', login_fallido: 'Intento fallido', logout: 'Cierre de sesión', visita: 'Visita a página', acceso_denegado: 'Acceso denegado' }

/** Enunciado 4: bitácora de auditoría (logins aceptados y fallidos, IP, accesos denegados) y recursos más accedidos. */
export default function PBitacora() {
  const [f, setF] = useState({ evento: '', usuario: '', ip: '', desde: '', hasta: '', page: 1 })
  const params = Object.fromEntries(Object.entries(f).filter(([, v]) => v))
  const registros = useDatos(async () => (await seguridadApi.bitacora(params)).data.registros, [f.evento, f.usuario, f.ip, f.desde, f.hasta, f.page])
  const resumen = useDatos(async () => (await seguridadApi.resumen()).data)
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value, page: 1 })
  const r = resumen.datos

  return (
    <>
      <CabeceraPagina titulo="Bitácora de accesos">Registro persistente de cada inicio de sesión, intento fallido, acceso denegado y visita, con su IP.</CabeceraPagina>
      {r && (
        <>
          <dl className="cifras mb-6">
            {Object.entries(EVENTOS).map(([k, v]) => <div key={k}><dt>{v} (30 días)</dt><dd>{r.eventos[k] || 0}</dd></div>)}
          </dl>
          <div className="grid grid-cols-2 gap-6 max-movil:grid-cols-1 mb-6">
            <section className="hoja"><header className="hoja-titulo"><h3>Recursos más accedidos</h3></header>
              <div className="hoja-cuerpo"><Barras porcentaje={false} datos={r.recursos_mas_accedidos.map((x) => ({ etiqueta: x.nombre, total: x.visitas }))} tono="seguimiento" formato={(v) => v.toLocaleString('es-BO')} /></div></section>
            <section className="hoja"><header className="hoja-titulo"><h3>IPs con más intentos fallidos</h3></header>
              {!r.ips_con_fallos.length ? <Vacio titulo="Sin intentos fallidos" /> : (
                <div className="tabla-marco rounded-none border-0"><table className="tabla"><thead><tr><th>IP</th><th className="num">Intentos</th><th>Último</th></tr></thead>
                  <tbody>{r.ips_con_fallos.map((x) => <tr key={x.ip}><td className="tabular-nums">{x.ip}</td><td className="num">{x.total}</td><td className="tabular-nums">{fecha(x.ultimo, true)}</td></tr>)}</tbody></table></div>
              )}
            </section>
          </div>
        </>
      )}
      <div className="barra-filtros">
        <Campo etiqueta="Evento"><select value={f.evento} onChange={set('evento')}><option value="">Todos</option>{Object.entries(EVENTOS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></Campo>
        <Campo etiqueta="Usuario o correo"><input type="search" value={f.usuario} onChange={set('usuario')} /></Campo>
        <Campo etiqueta="IP"><input value={f.ip} onChange={set('ip')} inputMode="decimal" /></Campo>
        <Campo etiqueta="Desde"><input type="date" value={f.desde} onChange={set('desde')} /></Campo>
        <Campo etiqueta="Hasta"><input type="date" value={f.hasta} min={f.desde || undefined} onChange={set('hasta')} /></Campo>
      </div>
      {registros.error && <Aviso tipo="error">{registros.error}</Aviso>}
      {registros.cargando && !registros.datos ? <Cargando /> : !registros.datos?.data?.length ? <Vacio titulo="Sin registros con esos filtros" icono={ScrollText} /> : (
        <>
          <div className="tabla-marco">
            <table className="tabla">
              <thead><tr><th>Fecha</th><th>Evento</th><th>Usuario</th><th>Página</th><th>IP</th><th>Navegador</th></tr></thead>
              <tbody>{registros.datos.data.map((x) => (
                <tr key={x.nro_registro}>
                  <td className="tabular-nums">{fecha(x.fecha, true)}</td>
                  <td><Etiqueta estado={x.evento}>{EVENTOS[x.evento]}</Etiqueta></td>
                  <td>{x.usuario || x.correo_intentado || <span className="text-tinta-suave">Visitante</span>}</td>
                  <td>{x.recurso || '—'}</td>
                  <td className="tabular-nums">{x.ip}</td>
                  <td><small className="text-tinta-suave">{(x.navegador || '').slice(0, 48)}</small></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
          <div className="acciones mt-3">
            <span className="text-sm text-tinta-suave">Página {registros.datos.current_page} de {registros.datos.last_page} · {registros.datos.total} registros</span>
            <button type="button" className="btn btn-secundario" disabled={f.page <= 1} onClick={() => setF({ ...f, page: f.page - 1 })}>Anterior</button>
            <button type="button" className="btn btn-secundario" disabled={registros.datos.current_page>= registros.datos.last_page} onClick={() => setF({ ...f, page: f.page + 1 })}>Siguiente</button>
          </div>
        </>
      )}
    </>
  )
}
