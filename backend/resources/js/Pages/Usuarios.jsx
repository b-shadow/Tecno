import { useState } from 'react'
import { UserPlus, Users } from 'lucide-react'
import { api, leerArchivo } from '../services/api'
import { useAppRoute } from '../services/navigation'
import { puede, useAuth } from '../services/auth'
import { Avatar, Aviso, Boton, CabeceraPagina, Campo, Cargando, Modal, Vacio, erroresDe, fecha, nombre, useAviso, useDatos } from '../components/ui'
import { apiErrorMessage } from '../services/errors'

const hoy = () => new Date().toISOString().slice(0, 10)
const enUnAnio = () => new Date(Date.now() + 365 * 86400000).toISOString().slice(0, 10)

/** CU1: usuarios con rol, vigencia de la credencial y foto con nombre legible. */
export default function Usuarios() {
  const { query } = useAppRoute()
  const sesion = useAuth()
  const [filtro, setFiltro] = useState({ buscar: query.buscar || '', rol: '', estado: '' })
  const { datos, cargando, error, recargar } = useDatos(async () => (await api.get('/usuarios', { params: Object.fromEntries(Object.entries(filtro).filter(([, v]) => v)) })).data, [filtro.buscar, filtro.rol, filtro.estado])
  const [editando, setEditando] = useState(null)
  const aviso = useAviso()
  const editable = puede('usuarios', 'modificacion', sesion)

  async function cambiarEstado(u) {
    try {
      aviso.ok((await api.patch(`/usuarios/${encodeURIComponent(u.correo)}/estado`, { estado: u.estado === 'activo' ? 'inactivo' : 'activo' })).data.mensaje)
      recargar()
    } catch (e) { aviso.error(e) }
  }

  return (
    <>
      <CabeceraPagina titulo="Usuarios" acciones={editable && <button type="button" className="btn btn-primario" onClick={() => setEditando({})}><UserPlus size={16} /> Nuevo usuario</button>}>
        Cada credencial tiene rol, estado y periodo de vigencia; fuera de ese periodo no puede ingresar.
      </CabeceraPagina>
      <div className="barra-filtros">
        <Campo etiqueta="Buscar"><input type="search" value={filtro.buscar} onChange={(e) => setFiltro({ ...filtro, buscar: e.target.value })} placeholder="Nombre o correo" /></Campo>
        <Campo etiqueta="Rol"><select value={filtro.rol} onChange={(e) => setFiltro({ ...filtro, rol: e.target.value })}><option value="">Todos</option>{(datos?.roles || []).map((r) => <option key={r.nombre}>{r.nombre}</option>)}</select></Campo>
        <Campo etiqueta="Estado"><select value={filtro.estado} onChange={(e) => setFiltro({ ...filtro, estado: e.target.value })}><option value="">Todos</option><option>activo</option><option>inactivo</option></select></Campo>
      </div>
      {error && <Aviso tipo="error">{error}</Aviso>}
      {cargando && !datos ? <Cargando /> : !datos?.usuarios?.length ? <Vacio titulo="Sin usuarios con ese filtro" icono={Users} /> : (
        <div className="tabla-marco">
          <table className="tabla">
            <thead><tr><th>Usuario</th><th>Rol</th><th>Vigencia</th><th>Estado</th><th /></tr></thead>
            <tbody>
              {datos.usuarios.map((u) => (
                <tr key={u.correo}>
                  <td><div className="persona"><Avatar usuario={u} /><div><strong>{nombre(u)}</strong><small>{u.correo}</small></div></div></td>
                  <td style={{ textTransform: 'capitalize' }}>{u.rol}{u.rol === 'coordinador' && <small style={{ display: 'block', color: 'var(--tinta-suave)' }}>{u.programas_a_cargo?.length || 0} programa(s)</small>}</td>
                  <td className="cifra">{fecha(u.fecha_inicio)} — {fecha(u.fecha_fin)}</td>
                  <td><span className={`status-pill etiqueta e-${u.estado}`}>{u.estado}</span></td>
                  <td className="acciones">{editable && <>
                    <button type="button" className="btn btn-texto" onClick={() => setEditando(u)}>Editar</button>
                    <button type="button" className="btn btn-secundario" onClick={() => cambiarEstado(u)}>{u.estado === 'activo' ? 'Desactivar' : 'Activar'}</button>
                  </>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {editando && <FormUsuario usuario={editando} roles={datos?.roles || []} programas={datos?.programas || []} onCerrar={() => setEditando(null)} onListo={(m) => { aviso.ok(m); setEditando(null); recargar() }} />}
      {aviso.nodo}
    </>
  )
}

function FormUsuario({ usuario, roles, programas, onCerrar, onListo }) {
  const nuevo = !usuario.correo
  const [form, setForm] = useState({
    nombre: usuario.nombre || '', apellido: usuario.apellido || '', correo: usuario.correo || '', telefono: usuario.telefono || '',
    password: '', rol: usuario.rol || 'vendedor', estado: usuario.estado || 'activo',
    fecha_inicio: usuario.fecha_inicio || hoy(), fecha_fin: usuario.fecha_fin || enUnAnio(),
    programas: (usuario.programas_a_cargo || []).map((p) => p.programa_codigo), foto: null,
  })
  const [errores, setErrores] = useState({})
  const [enviando, setEnviando] = useState(false)
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })
  async function guardar(e) {
    e.preventDefault()
    setEnviando(true)
    try {
      const datos = { ...form, password: form.password || undefined, foto: form.foto || undefined }
      const { data } = nuevo ? await api.post('/usuarios', datos) : await api.put(`/usuarios/${encodeURIComponent(usuario.correo)}`, datos)
      onListo(data.mensaje)
    } catch (err) {
      setErrores({ ...erroresDe(err), general: apiErrorMessage(err) })
      setEnviando(false)
    }
  }
  return (
    <Modal ancho titulo={nuevo ? 'Nuevo usuario' : `Editar ${nombre(usuario)}`} onCerrar={onCerrar}>
      {/* autoComplete="off" + nombres propios: el navegador no rellena la contraseña del administrador en este formulario. */}
      <form className="formulario dos" onSubmit={guardar} autoComplete="off">
        <Campo etiqueta="Nombre" requerido error={errores.nombre}><input name="usuario-nombre" required maxLength={120} value={form.nombre} onChange={set('nombre')} /></Campo>
        <Campo etiqueta="Apellido" requerido error={errores.apellido}><input name="usuario-apellido" required maxLength={120} value={form.apellido} onChange={set('apellido')} /></Campo>
        <Campo etiqueta="Correo" requerido error={errores.correo} ayuda={nuevo ? 'Será su usuario de acceso.' : 'Identifica al usuario: no se puede cambiar.'}><input name="usuario-correo" type="email" required maxLength={160} value={form.correo} onChange={set('correo')} readOnly={!nuevo} autoComplete="off" /></Campo>
        <Campo etiqueta="Teléfono" error={errores.telefono}><input name="usuario-telefono" inputMode="tel" pattern="\+?[0-9 ]{7,20}" title="Entre 7 y 20 dígitos." value={form.telefono} onChange={set('telefono')} /></Campo>
        <Campo etiqueta={nuevo ? 'Contraseña' : 'Nueva contraseña (opcional)'} requerido={nuevo} error={errores.password} ayuda="Mínimo 8 caracteres, con letras y números."><input name="usuario-clave-nueva" type="password" autoComplete="new-password" required={nuevo} minLength={8} pattern="(?=.*[A-Za-z])(?=.*\d).{8,}" title="Al menos 8 caracteres con letras y números." value={form.password} onChange={set('password')} /></Campo>
        <Campo etiqueta="Rol" requerido error={errores.rol}><select value={form.rol} onChange={set('rol')}>{roles.map((r) => <option key={r.nombre} value={r.nombre}>{r.nombre}</option>)}</select></Campo>
        <Campo etiqueta="Inicio de vigencia" requerido error={errores.fecha_inicio}><input type="date" required value={form.fecha_inicio} onChange={set('fecha_inicio')} /></Campo>
        <Campo etiqueta="Fin de vigencia" requerido error={errores.fecha_fin}><input type="date" required min={form.fecha_inicio} value={form.fecha_fin} onChange={set('fecha_fin')} /></Campo>
        <Campo etiqueta="Estado" requerido><select value={form.estado} onChange={set('estado')}><option>activo</option><option>inactivo</option></select></Campo>
        <Campo etiqueta="Foto" error={errores.foto} ayuda="Se guarda como apellido_nombre.jpg."><input type="file" accept="image/jpeg,image/png,image/webp" onChange={async (e) => { const f = e.target.files[0]; if (f) setForm({ ...form, foto: await leerArchivo(f) }) }} /></Campo>
        {form.rol === 'coordinador' && (
          <fieldset className="ancho" style={{ border: 0, padding: 0, margin: 0, display: 'grid', gap: 8 }}>
            <legend style={{ fontWeight: 700, marginBottom: 6 }}>Programas a su cargo (RF1.3)</legend>
            {programas.map((p) => <label key={p.codigo} className="check"><input type="checkbox" checked={form.programas.includes(p.codigo)} onChange={() => setForm({ ...form, programas: form.programas.includes(p.codigo) ? form.programas.filter((x) => x !== p.codigo) : [...form.programas, p.codigo] })} /> {p.nombre}</label>)}
          </fieldset>
        )}
        {errores.general && <div className="ancho"><Aviso tipo="error">{errores.general}</Aviso></div>}
        <div className="acciones ancho"><button type="button" className="btn btn-secundario" onClick={onCerrar}>Cancelar</button><Boton type="submit" cargando={enviando}>{nuevo ? 'Crear usuario' : 'Guardar cambios'}</Boton></div>
      </form>
    </Modal>
  )
}
