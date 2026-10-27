import { useEffect, useMemo, useRef, useState } from 'react'
import { ArrowLeft, Check, RefreshCw, SearchX } from 'lucide-react'
import { useAppRoute } from '../servicios/navigation'
import { puede, useAuth } from '../servicios/auth'
import { Aviso, Boton, Campo, Cargando, Vacio, bs, erroresDe, useAviso, useDatos } from '../componentes/ui'
import { apiErrorMessage } from '../servicios/errors'
import * as catalogoApi from '../api/catalogo'

const VACIO = { nombre: '', apellido: '', documento: '', telefono: '', correo: '', profesion: '', ubicacion: '' }

const horas = (modulos) => modulos.reduce((s, m) => s + (parseInt(m.duracion, 10) || 0), 0)
// Código corto de cada casilla: prefijo del programa + orden de cursado (DAT-1, CIB-3).
const sigla = (programa, i) => `${programa.codigo.split('-')[0].slice(0, 3).toUpperCase()}-${i + 1}`
// Imagen que envía la API del catálogo (decorativa: el nombre va al lado); si no carga, se oculta.
const Foto = ({ src, className }) => (src ? <img className={className} src={src} alt="" loading="lazy" decoding="async" onError={(e) => { e.currentTarget.hidden = true }} /> : null)
// Color estable por área: hash del nombre entre 4 tonos bien distintos (navy, turquesa, azul, índigo); si dos áreas
// chocan, la siguiente toma el próximo tono libre. Un área nueva no recolorea a las que ya tenían su tono.
function coloresDeAreas(areas) {
  const mapa = new Map()
  for (const a of areas) {
    let k = [...a].reduce((h, c) => (h * 31 + c.charCodeAt(0))>>> 0, 7) % 4
    for (let n = 0; n < 4 && [...mapa.values()].includes(k + 1); n++) k = (k + 1) % 4
    mapa.set(a, k + 1)
  }
  return mapa
}

/**
 * CU2: la oferta como malla curricular. Cada programa es una fila y sus módulos, casillas en orden de cursado,
 * agrupadas por área. Público en /anuncios (registro de interés); interno en /gestion-anuncios (consulta y sincronización, RNF2).
 */
export default function Catalogo() {
  const { path, query } = useAppRoute()
  const sesion = useAuth()
  const interno = path === '/gestion-anuncios'
  const { datos, cargando, error, recargar } = useDatos(async () => (await catalogoApi.programas()).data.programas)
  const [area, setArea] = useState('')
  const [eleccion, setEleccion] = useState(null)
  const [registrando, setRegistrando] = useState(false)

  const programas = useMemo(() => [...(datos || [])].sort((a, b) => a.area.localeCompare(b.area, 'es') || a.nombre.localeCompare(b.nombre, 'es')), [datos])
  const areas = useMemo(() => [...new Set(programas.map((p) => p.area))], [programas])
  const colores = useMemo(() => coloresDeAreas(areas), [areas])

  // Programa o módulo pedido por la URL (?programa= o ?modulo=, desde el buscador del encabezado).
  useEffect(() => {
    if (!programas.length) return
    const porModulo = query.modulo && programas.find((p) => p.modulos.some((m) => m.codigo === query.modulo))
    const programa = porModulo || programas.find((p) => p.codigo === query.programa)
    if (!programa) return
    setArea('')
    setRegistrando(false)
    setEleccion({ programa, modulo: porModulo ? programa.modulos.find((m) => m.codigo === query.modulo) : null, desdeUrl: true })
  }, [programas, query.modulo, query.programa])

  if (cargando) return <div className="oferta"><Cargando filas={6} /></div>
  if (error) return <div className="oferta"><Aviso tipo="error">{error}</Aviso><div className="acciones acciones-inicio"><button type="button" className="btn btn-secundario" onClick={recargar}>Reintentar</button></div></div>
  if (!programas.length) return <Vacio titulo="No hay programas abiertos" icono={SearchX}>La oferta se publicará pronto.</Vacio>

  if (registrando && eleccion) return <Registro eleccion={eleccion} onVolver={() => setRegistrando(false)} />

  const visibles = area ? programas.filter((p) => p.area === area) : programas
  const totalModulos = visibles.reduce((s, p) => s + p.modulos.length, 0)

  return (
    <>
      {interno && <BarraInterna onSincronizado={recargar} puedeSincronizar={puede('gestion-anuncios', 'modificacion', sesion)} />}
      <section className={`oferta ${interno ? 'oferta-interna' : ''}`} aria-labelledby="titulo-oferta">
        <header className="oferta-cabecera">
          <div>
            <h1 id="titulo-oferta">Malla de la oferta</h1>
            <p><span className="cifra">{visibles.length}</span> {visibles.length === 1 ? 'programa' : 'programas'} · <span className="cifra">{totalModulos}</span> módulos. Tome el programa completo o solo el módulo que necesita.</p>
          </div>
          <div className="areas" role="group" aria-label="Filtrar por área">
            <button type="button" className="area-filtro" aria-pressed={!area} onClick={() => setArea('')}>Todas</button>
            {areas.map((a) => (
              <button key={a} type="button" className={`area-filtro area-${colores.get(a)}`} aria-pressed={area === a} onClick={() => setArea(a)}>{a}</button>
            ))}
          </div>
        </header>

        <Malla areas={areas} colores={colores} visibles={visibles} eleccion={eleccion} onElegir={setEleccion} />

        {!interno && <BarraEleccion eleccion={eleccion} onContinuar={() => setRegistrando(true)} />}
      </section>
    </>
  )
}

/** La malla: una tabla por semántica (programa × orden de cursado), que en celular se pliega a bloques con cadena vertical. */
function Malla({ areas, colores, visibles, eleccion, onElegir }) {
  const columnas = Math.max(...visibles.map((p) => p.modulos.length))
  const fila = useRef(null)

  // Si la elección llega desde el buscador, la fila se lleva a la vista.
  useEffect(() => {
    if (eleccion?.desdeUrl) fila.current?.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }, [eleccion])

  const grupos = areas.map((a) => ({ area: a, color: colores.get(a), programas: visibles.filter((p) => p.area === a) })).filter((g) => g.programas.length)

  return (
    <div className="malla-marco">
      <table className="malla" data-columnas={Math.min(columnas, 10)}>
        <caption className="solo-lector">Programas por área con sus módulos en orden de cursado</caption>
        <colgroup><col className="malla-col-programa" />{Array.from({ length: columnas }, (_, i) => <col key={i} />)}</colgroup>
        <thead>
          <tr><th scope="col">Programa</th>{Array.from({ length: columnas }, (_, i) => <th key={i} scope="col">Módulo {i + 1}</th>)}</tr>
        </thead>
        {grupos.map((g) => (
          <tbody key={g.area} className={`area-${g.color}`}>
            <tr className="malla-area"><th colSpan={columnas + 1} scope="rowgroup">{g.area} <small>{g.programas.length} {g.programas.length === 1 ? 'programa' : 'programas'}</small></th></tr>
            {g.programas.map((p) => {
              const abierta = eleccion?.programa.codigo === p.codigo
              return (
                <tr key={p.codigo} ref={abierta ? fila : undefined} className={`malla-fila ${abierta ? 'abierta' : ''}`}>
                  <th scope="row">
                    <button type="button" className="programa-celda" aria-expanded={abierta} aria-pressed={abierta && !eleccion.modulo}
                      onClick={() => onElegir(abierta && !eleccion.modulo ? null : { programa: p, modulo: null })}>
                      <Foto src={p.imagen} className="programa-img" />
                      <strong>{p.nombre}</strong>
                      <small><span className="cifra">{bs(p.precio_total)}</span> · <span className="cifra">{horas(p.modulos)}</span> h · {p.modulos.length} módulos</small>
                      {!abierta && <span className="programa-siglas" aria-hidden="true">{p.modulos.map((m, i) => <i key={m.codigo}>{sigla(p, i)}</i>)}</span>}
                      {abierta && p.descripcion && <span className="programa-desc">{p.descripcion}</span>}
                    </button>
                  </th>
                  {Array.from({ length: columnas }, (_, i) => {
                    const m = p.modulos[i]
                    if (!m) return <td key={i} className="malla-vacia" aria-hidden="true" />
                    const elegida = abierta && eleccion.modulo?.codigo === m.codigo
                    return (
                      <td key={m.codigo} className={i === p.modulos.length - 1 ? 'ultima' : ''}>
                        <button type="button" className="materia" aria-pressed={elegida} aria-label={`${m.nombre}, módulo ${i + 1} de ${p.nombre}, ${bs(m.precio)}`}
                          onClick={() => onElegir(elegida ? { programa: p, modulo: null } : { programa: p, modulo: m })}>
                          {abierta && <Foto src={m.imagen} className="materia-img" />}
                          <b>{sigla(p, i)}</b>
                          <span>{m.nombre}</span>
                          <small><span className="cifra">{bs(m.precio)}</span>{m.duracion && ` · ${m.duracion}`}</small>
                          {abierta && m.descripcion && <span className="materia-desc">{m.descripcion}</span>}
                        </button>
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        ))}
      </table>
    </div>
  )
}

/** Barra fija con la elección actual y la única acción principal del catálogo. */
function BarraEleccion({ eleccion, onContinuar }) {
  if (!eleccion) {
    return <div className="eleccion vacia" role="status"><p>Toque un programa para verlo completo, o un módulo para tomarlo solo. Precios en bolivianos; el programa completo admite hasta 12 cuotas.</p></div>
  }
  const { programa, modulo } = eleccion
  return (
    <div className="eleccion" role="status">
      <p>
        <small>{modulo ? `Solo este módulo de ${programa.nombre}` : `Programa completo · ${programa.modulos.length} módulos`}</small>
        <strong>{modulo ? modulo.nombre : programa.nombre}</strong>
      </p>
      <b className="eleccion-precio cifra">{bs(modulo ? modulo.precio : programa.precio_total)}</b>
      <button type="button" className="btn btn-acento btn-grande" onClick={onContinuar}>{modulo ? 'Me interesa este módulo' : 'Me interesa el programa'}</button>
    </div>
  )
}

function BarraInterna({ onSincronizado, puedeSincronizar }) {
  const aviso = useAviso()
  const [enviando, setEnviando] = useState(false)
  return (
    <div className="cabecera-pagina">
      <div><h2>Oferta académica</h2><p>Réplica local del catálogo del sistema académico (Grupo 06). Es la misma oferta que ve el público en el catálogo.</p></div>
      {puedeSincronizar && (
        <Boton className="btn-secundario" cargando={enviando} onClick={async () => {
          setEnviando(true)
          try { aviso.ok((await catalogoApi.sincronizar()).data.mensaje); onSincronizado() } catch (e) { aviso.error(e) } finally { setEnviando(false) }
        }}><RefreshCw size={16} /> Sincronizar catálogo</Boton>
      )}
      {aviso.nodo}
    </div>
  )
}

/** Formulario de interés: datos básicos del prospecto (validados aquí y en el servidor). */
function Registro({ eleccion, onVolver }) {
  const [form, setForm] = useState(VACIO)
  const [errores, setErrores] = useState({})
  const [estado, setEstado] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const { programa, modulo } = eleccion
  const [modulosSeleccionados, setModulosSeleccionados] = useState(() => modulo ? [modulo.codigo] : programa.modulos.map((m) => m.codigo))
  const seleccionados = programa.modulos.filter((m) => modulosSeleccionados.includes(m.codigo))
  const total = seleccionados.reduce((s, m) => s + Number(m.precio), 0)
  const set = (campo) => (e) => setForm({ ...form, [campo]: e.target.value })

  function alternarModulo(codigo) {
    setModulosSeleccionados((actuales) => actuales.includes(codigo)
      ? actuales.filter((x) => x !== codigo)
      : [...actuales, codigo])
  }

  useEffect(() => { window.scrollTo({ top: 0 }) }, [])

  async function enviar(e) {
    e.preventDefault()
    setEnviando(true)
    setEstado(null)
    try {
      const { data } = await catalogoApi.registrarInteres({ ...form, modulo_codigos: modulosSeleccionados })
      setEstado({ tipo: 'ok', texto: `${data.mensaje} ${data.detalle || ''}` })
      setErrores({})
      setForm(VACIO)
    } catch (err) {
      setErrores(erroresDe(err))
      setEstado({ tipo: 'error', texto: apiErrorMessage(err, 'No se pudo registrar su interés.') })
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className="registro">
      <div className="registro-resumen">
        <button type="button" className="btn btn-texto btn-volver" onClick={onVolver}><ArrowLeft size={16} /> Volver a la malla</button>
        <Foto src={(modulo || programa).imagen} className="registro-img" />
        <h1>{programa.nombre}</h1>
        <p>{seleccionados.length === programa.modulos.length ? `Programa completo: ${programa.modulos.length} módulos` : `${seleccionados.length} de ${programa.modulos.length} módulos seleccionados`}</p>
        <ol className="cadena">
          {programa.modulos.map((m, i) => {
            const incluido = modulosSeleccionados.includes(m.codigo)
            return (
              <li key={m.codigo} className={`${incluido ? 'incluido' : ''} modulo-interes`}>
                <label>
                  <input type="checkbox" checked={incluido} onChange={() => alternarModulo(m.codigo)} />
                  <b>{sigla(programa, i)}</b><span>{m.nombre}</span>
                  <small className="cifra">{bs(m.precio)}</small>
                  {incluido && <Check size={16} aria-label="incluido" />}
                </label>
              </li>
            )
          })}
        </ol>
        <div className="total"><span className="cifra">{bs(total)}</span><small>{seleccionados.length === programa.modulos.length ? 'programa completo' : `${seleccionados.length} módulo(s) seleccionados`}</small></div>
      </div>
      <form className="formulario dos hoja hoja-cuerpo" onSubmit={enviar}>
        <h2 className="ancho">Deje sus datos y un asesor le escribe por WhatsApp</h2>
        <Campo etiqueta="Nombre *" error={errores.nombre}><input value={form.nombre} onChange={set('nombre')} required maxLength={120} autoComplete="given-name" pattern="[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .\-]+" title="Solo letras y espacios." aria-invalid={Boolean(errores.nombre)} /></Campo>
        <Campo etiqueta="Apellido *" error={errores.apellido}><input value={form.apellido} onChange={set('apellido')} required maxLength={120} autoComplete="family-name" pattern="[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .\-]+" title="Solo letras y espacios." aria-invalid={Boolean(errores.apellido)} /></Campo>
        <Campo etiqueta="Carnet de identidad *" error={errores.documento}><input value={form.documento} onChange={set('documento')} required maxLength={20} placeholder="Nro. de documento" pattern="[0-9A-Za-z\-]+" title="Números, letras y guion; por ejemplo 7845123-1A." aria-invalid={Boolean(errores.documento)} /></Campo>
        <Campo etiqueta="Teléfono (WhatsApp) *" error={errores.telefono}><input value={form.telefono} onChange={set('telefono')} required inputMode="tel" placeholder="Ej. 71234567" pattern="\+?[0-9 ]{7,20}" title="Entre 7 y 20 dígitos." autoComplete="tel" aria-invalid={Boolean(errores.telefono)} /></Campo>
        <Campo etiqueta="Correo *" error={errores.correo}><input type="email" value={form.correo} onChange={set('correo')} required maxLength={160} placeholder="usted@correo.com" autoComplete="email" aria-invalid={Boolean(errores.correo)} /></Campo>
        <Campo etiqueta="Profesión u ocupación" error={errores.profesion}><input value={form.profesion} onChange={set('profesion')} maxLength={120} placeholder="Ej. Ingeniero de sistemas" /></Campo>
        <Campo etiqueta="Ciudad" error={errores.ubicacion}><input value={form.ubicacion} onChange={set('ubicacion')} maxLength={160} placeholder="Ej. Santa Cruz" autoComplete="address-level2" /></Campo>
        <div className="ancho"><Aviso tipo={estado?.tipo}>{estado?.texto}</Aviso></div>
        <div className="acciones ancho"><Boton type="submit" className="btn-primario btn-grande" cargando={enviando} disabled={!modulosSeleccionados.length} aria-label="Enviar interés">Enviar interés ({modulosSeleccionados.length})</Boton></div>
      </form>
    </section>
  )
}
