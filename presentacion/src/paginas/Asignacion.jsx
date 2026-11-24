import { useState } from 'react'
import { Shuffle } from 'lucide-react'
import { go } from '../servicios/navigation'
import { Aviso, Boton, CabeceraPagina, Campo, Cargando, Etiqueta, Vacio, fecha, nombre, useAviso, useDatos } from '../componentes/ui'
import * as interesesApi from '../api/intereses'
import * as usuariosApi from '../api/usuarios'

/**
 * CU3 / RF2.3: coordinación reparte prospectos a mano o por Round-Robin equitativo.
 * Reasignar conserva todo el historial y deja constancia de quién lo cambió.
 */
export default function Asignacion() {
  const [filtro, setFiltro] = useState({ buscar: '', vendedor: '', sin_asignar: true })
  const { datos, cargando, error, recargar } = useDatos(async () => (await interesesApi.index({ buscar: filtro.buscar || undefined, vendedor: filtro.vendedor || undefined, sin_asignar: filtro.sin_asignar ? 1 : undefined })).data, [filtro.buscar, filtro.vendedor, filtro.sin_asignar])
  const vendedores = useDatos(async () => (await usuariosApi.vendedores()).data.vendedores)
  const [repartiendo, setRepartiendo] = useState(false)
  const aviso = useAviso()

  async function asignar(t, correo) {
    if (!correo) return
    try {
      aviso.ok((await interesesApi.asignar(t.nro_tarjeta, correo)).data.mensaje)
      recargar()
    } catch (e) { aviso.error(e) }
  }

  const sinAsignar = (datos?.intereses || []).filter((t) => !t.vendedor_correo).length
  return (
    <>
      <CabeceraPagina titulo="Asignación de prospectos" acciones={
        <Boton className="btn-primario" cargando={repartiendo} onClick={async () => {
          setRepartiendo(true)
          try { aviso.ok((await interesesApi.distribuir()).data.mensaje); recargar() } catch (e) { aviso.error(e) } finally { setRepartiendo(false) }
        }}><Shuffle size={16} /> Repartir por turnos (Round-Robin)</Boton>
      }>
        El reparto automático da cada prospecto sin vendedor al vendedor activo con menos tarjetas abiertas; las tarjetas de un mismo prospecto van al mismo vendedor.
      </CabeceraPagina>
      <div className="barra-filtros">
        <Campo etiqueta="Buscar"><input type="search" placeholder="Prospecto, CI o módulo" value={filtro.buscar} onChange={(e) => setFiltro({ ...filtro, buscar: e.target.value })} /></Campo>
        <Campo etiqueta="Vendedor"><select value={filtro.vendedor} onChange={(e) => setFiltro({ ...filtro, vendedor: e.target.value, sin_asignar: false })}><option value="">Todos</option>{(vendedores.datos || []).map((v) => <option key={v.correo} value={v.correo}>{nombre(v)}</option>)}</select></Campo>
        <label className="check"><input type="checkbox" checked={filtro.sin_asignar} onChange={(e) => setFiltro({ ...filtro, sin_asignar: e.target.checked, vendedor: '' })} /> Solo sin asignar</label>
      </div>
      {error && <Aviso tipo="error">{error}</Aviso>}
      {cargando && !datos ? <Cargando /> : !datos?.intereses?.length ? <Vacio titulo={filtro.sin_asignar ? 'No hay prospectos pendientes de reparto' : 'Sin resultados'}>{filtro.sin_asignar ? 'Todos los prospectos tienen vendedor.' : 'Pruebe con otro filtro.'}</Vacio> : (
        <>
          {filtro.sin_asignar && <p className="nota tramo-s">{sinAsignar} tarjeta(s) esperan vendedor.</p>}
          <div className="tabla-marco">
            <table className="tabla">
              <thead><tr><th>Prospecto</th><th>Interés</th><th>Etapa</th><th>Registro</th><th>Vendedor</th></tr></thead>
              <tbody>
                {datos.intereses.map((t) => (
                  <tr key={t.nro_tarjeta}>
                    <td><a href="#" onClick={(e) => { e.preventDefault(); go(`/agenda?interes=${t.nro_tarjeta}`) }}><strong>{nombre(t.prospecto)}</strong></a><br /><small className="cifra">CI {t.documento}</small></td>
                    <td>{t.modulo_nombre}<br /><small className="nota">{t.programa_nombre}</small></td>
                    <td><Etiqueta estado={t.estado} /></td>
                    <td className="cifra">{fecha(t.fecha)}</td>
                    <td>
                      <select className="control" aria-label={`Vendedor de la tarjeta ${t.nro_tarjeta}`} value={t.vendedor_correo || ''} onChange={(e) => asignar(t, e.target.value)} disabled={['Convertido', 'Perdido'].includes(t.estado)}>
                        <option value="">Sin asignar</option>
                        {(vendedores.datos || []).map((v) => <option key={v.correo} value={v.correo}>{nombre(v)}</option>)}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
      {aviso.nodo}
    </>
  )
}
