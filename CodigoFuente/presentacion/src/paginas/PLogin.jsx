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
const LOGO = 'h-[clamp(56px,13vh,150px)] w-auto bajo:h-[clamp(44px,9vh,72px)]'

/** Cuentas de prueba por rol, visibles para la evaluación del docente. */
const DEMO = [
  { rol: 'Administrador', correo: 'pruebatecnoweb123+adminp2@gmail.com', password: 'P2Admin-6w7DBaCyTl4Fhtt1HVY' },
  { rol: 'Coordinador', correo: 'pruebatecnoweb123+coord@gmail.com', password: 'P2Coord-aWaiWoWEKSbvNk3kiqs' },
  { rol: 'Vendedor', correo: 'pruebatecnoweb123+vend1@gmail.com', password: 'P2Vend-tH3PA2eGzilY3q61v8I' },
]

export default function PLogin() {
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
    <section className="grid flex-1 place-items-center px-4 py-[clamp(12px,3.5vh,48px)] bajo:py-2">
      {/* El login entra entero en la pantalla: logo y espacios se achican con el alto (bajo: pantallas de 700 px o menos). */}
      <div className="grid w-[min(420px,100%)] justify-items-center gap-[clamp(12px,2.5vh,24px)]">
        <img className={`${LOGO} dark:hidden`} src={logo} alt="UNEXO" width="220" height="221" />
        <img className={`${LOGO} hidden dark:block`} src={logoNoche} alt="UNEXO" width="220" height="221" />
        <form className="hoja grid w-full gap-[clamp(10px,2vh,16px)] px-6 py-[clamp(16px,3vh,24px)] bajo:gap-2.5 bajo:py-3.5" onSubmit={entrar}>
          <div className="grid gap-1">
            <h1 className="text-2xl leading-[1.15]">Iniciar sesión</h1>
            <p className="text-sm text-tinta-suave bajo:hidden">Administración, coordinación y vendedores.</p>
          </div>
          <label className="campo bajo:gap-1"><span>Correo</span>
            <input type="email" autoComplete="username" required maxLength={160} value={form.correo} onChange={(e) => setForm({ ...form, correo: e.target.value })} />
          </label>
          <label className="campo relative bajo:gap-1"><span>Contraseña</span>
            <input className="pr-12" type={ver ? 'text' : 'password'} autoComplete="current-password" required maxLength={120} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <button type="button" className="btn btn-texto btn-icono absolute right-1 bottom-px" aria-label={ver ? 'Ocultar contraseña' : 'Mostrar contraseña'} onClick={() => setVer(!ver)}>{ver ? <EyeOff size={18} /> : <Eye size={18} />}</button>
          </label>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <label className="check"><input type="checkbox" checked={recordar} onChange={(e) => setRecordar(e.target.checked)} /> Recordarme</label>
            <button type="button" className="btn btn-texto" onClick={() => setAyuda(!ayuda)}>¿Olvidó su contraseña?</button>
          </div>
          {ayuda && <Aviso>Solicite al administrador que restablezca su contraseña desde Usuarios.</Aviso>}
          <Aviso tipo="error">{error}</Aviso>
          <Boton type="submit" className="btn-primario btn-grande w-full bajo:min-h-[46px]" cargando={enviando}>Ingresar</Boton>
        </form>
        <section className="hoja grid w-full gap-3 px-6 py-4 bajo:py-3" aria-labelledby="demo-titulo">
          <div className="grid gap-0.5">
            <h2 id="demo-titulo" className="text-base">Cuentas de prueba</h2>
            <p className="text-sm text-tinta-suave">Pulse «Usar» para llenar el formulario con la cuenta de ese rol.</p>
          </div>
          <ul className="grid divide-y divide-filete">
            {DEMO.map((c) => (
              <li key={c.rol} className="flex items-center justify-between gap-3 py-2.5 first:pt-0 last:pb-0">
                <div className="grid min-w-0 gap-0.5 text-sm">
                  <strong className="font-[650] text-tinta">{c.rol}</strong>
                  <span className="break-all text-tinta-suave select-all">{c.correo}</span>
                  <span className="text-tinta-suave select-all">{c.password}</span>
                </div>
                <button type="button" className="btn btn-secundario shrink-0" aria-label={`Usar cuenta de ${c.rol.toLowerCase()}`}
                  onClick={() => { setForm({ correo: c.correo, password: c.password }); setError(null) }}>Usar</button>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </section>
  )
}
