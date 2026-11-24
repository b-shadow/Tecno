import { useState } from 'react'
import { Download, FileUp, UserPlus, UsersRound } from 'lucide-react'
import { descargarCsv } from '../servicios/archivos'
import { go } from '../servicios/navigation'
import { puede, useAuth } from '../servicios/auth'
import { Aviso, CabeceraPagina, Campo, Cargando, Etiqueta, Modal, Persona, Vacio, erroresDe, fecha, nombre, useAviso, useDatos } from '../componentes/ui'
import { apiErrorMessage } from '../servicios/errors'
import * as catalogoApi from '../api/catalogo'
import * as prospectosApi from '../api/prospectos'

/** CU3 / RF2.1: prospectos registrados a mano, por CSV o desde el catálogo, con su origen. */
export default function Prospectos() {
  const sesion = useAuth()
  const puedeAlta = puede('interesados', 'modificacion', sesion)
  const [filtro, setFiltro] = useState({ buscar: '', origen: '' })
  const { datos, cargando, error, recargar } = useDatos(async () => (await prospectosApi.index({ buscar: filtro.buscar || undefined, origen: filtro.origen || undefined })).data, [filtro.buscar, filtro.origen])
  const [modal, setModal] = useState(null)
  const aviso = useAviso()

  return (
    <>
      <CabeceraPagina titulo="Prospectos" acciones={puedeAlta && <>
        <button type="button" className="btn btn-secundario" onClick={() => setModal('csv')}><FileUp size={16} /> Importar CSV</button>
        <button type="button" className="btn btn-primario" onClick={() => setModal('nuevo')}><UserPlus size={16} /> Registrar prospecto</button>
      </>}>
        {puedeAlta ? 'Registro manual o masivo. Los que llegan del catálogo aparecen con origen Web.' : 'Prospectos de su cartera.'}
      </CabeceraPagina>
      <div className="barra-filtros">
        <Campo etiqueta="Buscar"><input type="search" placeholder="Nombre, CI, correo o teléfono" value={filtro.buscar} onChange={(e) => setFiltro({ ...filtro, buscar: e.target.value })} /></Campo>
        <Campo etiqueta="Origen"><select value={filtro.origen} onChange={(e) => setFiltro({ ...filtro, origen: e.target.value })}><option value="">Todos</option>{(datos?.origenes || []).map((o) => <option key={o}>{o}</option>)}</select></Campo>
      </div>
      {error && <Aviso tipo="error">{error}</Aviso>}
      {cargando && !datos ? <Cargando /> : !datos?.prospectos?.length ? <Vacio titulo="No hay prospectos" icono={UsersRound}>{puedeAlta ? 'Registre el primero o importe un CSV.' : 'Cuando le asignen prospectos aparecerán aquí.'}</Vacio> : (
        <div className="tabla-marco">
          <table className="tabla">
            <thead><tr><th>Prospecto</th><th>CI</th><th>Teléfono</th><th>Origen</th><th>Intereses</th><th>Registro</th></tr></thead>
            <tbody>
              {datos.prospectos.map((p) => (
                <tr key={p.documento}>
                  <td><Persona usuario={p} detalle={p.correo} /></td>
                  <td className="tabular-nums">{p.documento}</td>
                  <td className="tabular-nums">{p.telefono}</td>
                  <td>{p.origen}</td>
                  <td>{p.intereses.length ? p.intereses.map((i) => (
                    <div key={i.nro_tarjeta} className="my-0.5 flex items-center gap-2">
                      <a href="#" onClick={(e) => { e.preventDefault(); go(`/agenda?interes=${i.nro_tarjeta}`) }}>{i.modulo_nombre}</a><Etiqueta estado={i.estado} />
                    </div>
                  )) : <small className="text-tinta-suave">Sin interés registrado</small>}</td>
                  <td className="tabular-nums">{fecha(p.fecha_registro)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {modal === 'nuevo' && <NuevoProspecto origenes={datos?.origenes || []} onCerrar={() => setModal(null)} onListo={(m) => { aviso.ok(m); setModal(null); recargar() }} />}
      {modal === 'csv' && <ImportarCsv onCerrar={() => setModal(null)} onListo={(m) => { aviso.ok(m); setModal(null); recargar() }} />}
      {aviso.nodo}
    </>
  )
}

function NuevoProspecto({ origenes, onCerrar, onListo }) {
  const catalogo = useDatos(async () => (await catalogoApi.programas()).data.programas)
  const [form, setForm] = useState({ documento: '', nombre: '', apellido: '', telefono: '', correo: '', origen: 'WhatsApp', profesion: '', ubicacion: '', interes: '' })
  const [errores, setErrores] = useState({})
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })
  async function guardar(e) {
    e.preventDefault()
    const [tipo, codigo] = form.interes.split(':')
    const { interes, ...datos } = form
    try {
      onListo((await prospectosApi.store({ ...datos, ...(tipo === 'p' ? { programa_codigo: codigo } : tipo === 'm' ? { modulo_codigo: codigo } : {}) })).data.mensaje)
    } catch (err) {
      setErrores({ ...erroresDe(err), general: apiErrorMessage(err) })
    }
  }
  return (
    <Modal ancho titulo="Registrar prospecto" descripcion="Datos básicos (RF2.1). Si elige un interés, se crea su tarjeta en el embudo." onCerrar={onCerrar}>
      <form className="grid gap-4 grid-cols-2 max-movil:grid-cols-1" onSubmit={guardar}>
        <Campo etiqueta="Carnet de identidad" requerido error={errores.documento}><input required maxLength={20} pattern="[0-9A-Za-z\-]+" title="Números, letras y guion." value={form.documento} onChange={set('documento')} /></Campo>
        <Campo etiqueta="Origen del contacto" requerido error={errores.origen}><select value={form.origen} onChange={set('origen')}>{origenes.map((o) => <option key={o}>{o}</option>)}</select></Campo>
        <Campo etiqueta="Nombre" requerido error={errores.nombre}><input required maxLength={120} value={form.nombre} onChange={set('nombre')} /></Campo>
        <Campo etiqueta="Apellido" requerido error={errores.apellido}><input required maxLength={120} value={form.apellido} onChange={set('apellido')} /></Campo>
        <Campo etiqueta="Teléfono" requerido error={errores.telefono}><input required inputMode="tel" pattern="\+?[0-9 ]{7,20}" title="Entre 7 y 20 dígitos." value={form.telefono} onChange={set('telefono')} /></Campo>
        <Campo etiqueta="Correo" requerido error={errores.correo}><input type="email" required maxLength={160} value={form.correo} onChange={set('correo')} /></Campo>
        <Campo etiqueta="Profesión" error={errores.profesion}><input maxLength={120} value={form.profesion} onChange={set('profesion')} /></Campo>
        <Campo etiqueta="Ciudad" error={errores.ubicacion}><input maxLength={160} value={form.ubicacion} onChange={set('ubicacion')} /></Campo>
        <div className="col-span-full">
          <Campo etiqueta="Interés (RF2.2)" ayuda="Programa completo o un módulo independiente." error={errores.modulo_codigo}>
            <select value={form.interes} onChange={set('interes')}>
              <option value="">Sin interés por ahora</option>
              {(catalogo.datos || []).map((p) => (
                <optgroup key={p.codigo} label={p.nombre}>
                  <option value={`p:${p.codigo}`}>Programa completo ({p.modulos.length} módulos)</option>
                  {p.modulos.map((m) => <option key={m.codigo} value={`m:${m.codigo}`}>{m.nombre}</option>)}
                </optgroup>
              ))}
            </select>
          </Campo>
        </div>
        {errores.general && <div className="col-span-full"><Aviso tipo="error">{errores.general}</Aviso></div>}
        <div className="acciones col-span-full"><button type="button" className="btn btn-secundario" onClick={onCerrar}>Cancelar</button><button type="submit" className="btn btn-primario">Registrar</button></div>
      </form>
    </Modal>
  )
}

function ImportarCsv({ onCerrar, onListo }) {
  const [archivo, setArchivo] = useState(null)
  const [resultado, setResultado] = useState(null)
  const [clave, setClave] = useState(0)
  async function importar() {
    try {
      const { data } = await prospectosApi.importarCSV(await archivo.text())
      onListo(data.mensaje)
    } catch (err) {
      setResultado({ mensaje: apiErrorMessage(err), errores: err.response?.data?.errores || [] })
      setArchivo(null)
      setClave(clave + 1)
    }
  }
  return (
    <Modal titulo="Importar prospectos desde CSV" descripcion="Columnas: documento, nombre, apellido, telefono, correo, origen. Opcionales: profesion, ubicacion y modulo_codigo o programa_codigo (con ellas el prospecto entra al embudo para el reparto). Si una fila tiene errores no se carga ninguna." onCerrar={onCerrar}
      pie={<div className="acciones"><button type="button" className="btn btn-texto" onClick={() => descargarCsv('plantilla_prospectos.csv', [{ documento: '7845123', nombre: 'Ana', apellido: 'Rojas', telefono: '71234567', correo: 'ana.rojas@correo.bo', origen: 'Facebook', profesion: 'Contadora', ubicacion: 'Santa Cruz', modulo_codigo: '', programa_codigo: '' }])}><Download size={16} /> Plantilla</button><button type="button" className="btn btn-secundario" onClick={onCerrar}>Cancelar</button><button type="button" className="btn btn-primario" disabled={!archivo} onClick={importar}>Importar</button></div>}>
      <Campo etiqueta="Archivo CSV" requerido><input key={clave} type="file" accept=".csv,text/csv" onChange={(e) => setArchivo(e.target.files[0] || null)} /></Campo>
      {resultado && (
        <Aviso tipo="error">
          {resultado.mensaje}
          {Array.isArray(resultado.errores) && resultado.errores.length> 0 && <ul>{resultado.errores.slice(0, 12).map((e, i) => <li key={i}>{e.fila ? `Fila ${e.fila}: ` : ''}{e.columna ? `${e.columna} — ` : ''}{e.error}</li>)}</ul>}
        </Aviso>
      )}
    </Modal>
  )
}
