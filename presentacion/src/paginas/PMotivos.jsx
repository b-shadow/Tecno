import { useState } from 'react'
import { Pencil, Plus, Trash2 } from 'lucide-react'
import { puede, useAuth } from '../servicios/auth'
import { Aviso, Barras, CabeceraPagina, Campo, Cargando, Modal, erroresDe, useAviso, useDatos } from '../componentes/ui'
import { apiErrorMessage } from '../servicios/errors'
import * as motivosApi from '../api/motivos'

/** CU5: motivos de pérdida y su clasificación por categoría (RF3.3), con cuántas tarjetas usan cada uno. */
export default function PMotivos() {
  const sesion = useAuth()
  const editable = puede('motivos', 'modificacion', sesion)
  const borrable = puede('motivos', 'eliminacion', sesion)
  const { datos, cargando, error, recargar } = useDatos(async () => (await motivosApi.index()).data)
  const [editando, setEditando] = useState(null)
  const aviso = useAviso()
  if (cargando && !datos) return <Cargando />
  if (error) return <Aviso tipo="error">{error}</Aviso>
  const porCategoria = datos.categorias.map((c) => ({ etiqueta: c, total: datos.motivos.filter((m) => m.categoria === c).reduce((s, m) => s + m.usos, 0) }))
  const suma = porCategoria.reduce((s, c) => s + c.total, 0) || 1

  return (
    <>
      <CabeceraPagina titulo="Motivos de pérdida" acciones={editable && <button type="button" className="btn btn-primario" onClick={() => setEditando({ nombre: '', categoria: 'Económico', nuevo: true })}><Plus size={16} /> Nuevo motivo</button>}>
        Al marcar una tarjeta como Perdida se elige uno de estos motivos. La categoría agrupa las estadísticas.
      </CabeceraPagina>
      <div className="grid grid-cols-[minmax(0,3fr)_minmax(0,2fr)] gap-6 max-movil:grid-cols-1">
        <div className="tabla-marco">
          <table className="tabla">
            <thead><tr><th>Motivo</th><th>Categoría</th><th className="num">Tarjetas</th><th /></tr></thead>
            <tbody>
              {datos.motivos.map((m) => (
                <tr key={m.nombre}>
                  <td>{m.nombre}</td><td>{m.categoria}</td><td className="num">{m.usos}</td>
                  <td className="acciones">
                    {editable && m.nombre !== 'Sin clasificar (web)' && <button type="button" className="btn btn-texto btn-icono" aria-label={`Editar ${m.nombre}`} onClick={() => setEditando({ ...m, original: m.nombre })}><Pencil size={16} /></button>}
                    {borrable && m.nombre !== 'Sin clasificar (web)' && !m.usos && <button type="button" className="btn btn-texto btn-icono" aria-label={`Eliminar ${m.nombre}`} onClick={async () => { try { aviso.ok((await motivosApi.destroy(m.nombre)).data.mensaje); recargar() } catch (e) { aviso.error(e) } }}><Trash2 size={16} /></button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <section className="hoja"><header className="hoja-titulo"><h3>Pérdidas por categoría</h3></header>
          <div className="hoja-cuerpo"><Barras datos={porCategoria.map((c) => ({ ...c, porcentaje: Math.round((c.total * 1000) / suma) / 10 }))} tono="perdido" /></div></section>
      </div>
      {editando && <EditarMotivo motivo={editando} categorias={datos.categorias} onCerrar={() => setEditando(null)} onListo={(m) => { aviso.ok(m); setEditando(null); recargar() }} />}
      {aviso.nodo}
    </>
  )
}

function EditarMotivo({ motivo, categorias, onCerrar, onListo }) {
  const [form, setForm] = useState({ nombre: motivo.nombre, categoria: motivo.categoria })
  const [errores, setErrores] = useState({})
  async function guardar(e) {
    e.preventDefault()
    try {
      const { data } = motivo.nuevo ? await motivosApi.store(form) : await motivosApi.update(motivo.original, form)
      onListo(data.mensaje)
    } catch (err) { setErrores({ ...erroresDe(err), general: apiErrorMessage(err) }) }
  }
  return (
    <Modal titulo={motivo.nuevo ? 'Nuevo motivo' : 'Editar motivo'} onCerrar={onCerrar}>
      <form className="grid gap-4" onSubmit={guardar}>
        <Campo etiqueta="Motivo" requerido error={errores.nombre}><input required maxLength={80} value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></Campo>
        <Campo etiqueta="Categoría" requerido><select value={form.categoria} onChange={(e) => setForm({ ...form, categoria: e.target.value })}>{categorias.map((c) => <option key={c}>{c}</option>)}</select></Campo>
        {errores.general && <Aviso tipo="error">{errores.general}</Aviso>}
        <div className="acciones"><button type="button" className="btn btn-secundario" onClick={onCerrar}>Cancelar</button><button type="submit" className="btn btn-primario">Guardar</button></div>
      </form>
    </Modal>
  )
}
