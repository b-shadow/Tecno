import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import { login } from '../servicios/auth'
import { go, useAppRoute } from '../servicios/navigation'
import { inicio } from '../servicios/access'
import { Aviso, Boton } from '../componentes/ui'
import { apiErrorMessage } from '../servicios/errors'
import logo from '../assets/unexo-logo.png'
import logoNoche from '../assets/unexo-logo-noche.png'

/** CU1: acceso con credenciales (RF1.1). Cada intento, aceptado o fallido, queda en la bitácora con la IP. */
export default function Login() {
  const { query } = useAppRoute()
  const [form, setForm] = useState({ correo: '', password: '' })
  const [recordar, setRecordar] = useState(true)
  const [ver, setVer] = useState(false)
  const [error, setError] = useState(null)
  const [ayuda, setAyuda] = useState(false)
  const [enviando, setEnviando] = useState(false)

  async function entrar(e) {
    e.preventDefault()
    setEnviando(true)
    setError(null)
    try {
      const data = await login({ correo: form.correo.trim(), password: form.password }, recordar)
      const destino = query.redirect?.startsWith('/') && !query.redirect.startsWith('/login') && !query.redirect.startsWith('//') ? query.redirect : inicio(data)
      go(destino, { replace: true })
    } catch (err) {
      setError(apiErrorMessage(err, 'No se pudo iniciar sesión.'))
      setEnviando(false)
    }
  }

  return (
    <section className="acceso">
      <div className="acceso-form">
        <img className="acceso-logo logo-dia" src={logo} alt="UNEXO" width="220" height="221" />
        <img className="acceso-logo logo-noche" src={logoNoche} alt="UNEXO" width="220" height="221" />
        <form className="hoja hoja-cuerpo" onSubmit={entrar}>
          <div className="acceso-titulo">
            <h1>Iniciar sesión</h1>
            <p>Administración, coordinación y vendedores.</p>
          </div>
          <label className="campo"><span>Correo</span>
            <input type="email" autoComplete="username" required maxLength={160} value={form.correo} onChange={(e) => setForm({ ...form, correo: e.target.value })} />
          </label>
          <label className="campo campo-clave"><span>Contraseña</span>
            <input type={ver ? 'text' : 'password'} autoComplete="current-password" required maxLength={120} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <button type="button" className="btn btn-texto btn-icono" aria-label={ver ? 'Ocultar contraseña' : 'Mostrar contraseña'} onClick={() => setVer(!ver)}>{ver ? <EyeOff size={18} /> : <Eye size={18} />}</button>
          </label>
          <div className="acceso-opciones">
            <label className="check"><input type="checkbox" checked={recordar} onChange={(e) => setRecordar(e.target.checked)} /> Recordarme</label>
            <button type="button" className="btn btn-texto" onClick={() => setAyuda(!ayuda)}>¿Olvidó su contraseña?</button>
          </div>
          {ayuda && <Aviso>Solicite al administrador que restablezca su contraseña desde Usuarios.</Aviso>}
          <Aviso tipo="error">{error}</Aviso>
          <Boton type="submit" className="btn-primario btn-grande btn-bloque" cargando={enviando}>Ingresar</Boton>
        </form>
      </div>
    </section>
  )
}
