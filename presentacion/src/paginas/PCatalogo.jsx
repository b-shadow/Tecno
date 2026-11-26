import { useEffect, useMemo, useRef, useState } from 'react'
import { ArrowLeft, Check, RefreshCw, SearchX } from 'lucide-react'
import { useAppRoute } from '../servicios/navigation'
import { puede, useAuth } from '../servicios/auth'
import { Aviso, Boton, CabeceraPagina, Campo, Cargando, Vacio, bs, erroresDe, useAviso, useDatos } from '../componentes/ui'
import { AREA } from '../componentes/tonos'
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
    let k = [...a].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7) % 4
    for (let n = 0; n < 4 && [...mapa.values()].includes(k + 1); n++) k = (k + 1) % 4
    mapa.set(a, k + 1)
  }
  return mapa
}

// Margen lateral del catálogo público (la barra de elección y la tira de áreas lo cruzan de borde a borde).
const MARGEN = 'px-[clamp(16px,3vw,40px)]'
const SANGRAR = '-mx-[clamp(16px,3vw,40px)]'
// Texto sobre una casilla elegida (fondo del color del área).
const SOBRE_COLOR = 'text-white dark:text-sobre-acento'
// Ancho mínimo de la malla en escritorio según la cantidad de módulos: con muchos, se desplaza hacia los lados.
const ANCHO_MALLA = {
  3: 'malla:max-amplio:min-w-[1160px]', 4: 'malla:max-amplio:min-w-[1160px]', 5: 'malla:max-amplio:min-w-[1160px]',
  6: 'malla:min-w-[1340px]', 7: 'malla:min-w-[1520px]', 8: 'malla:min-w-[1700px]', 9: 'malla:min-w-[1880px]', 10: 'malla:min-w-[2060px]',
}
// La columna del programa queda fija al desplazar la malla: su franja izquierda (::before) tapa lo que pasa por debajo.
// Trazo que une cada casilla con la siguiente (en escritorio, horizontal).
const CONECTOR = "after:absolute after:top-[46px] after:-right-4 after:h-0.5 after:w-4 after:bg-c after:content-[''] max-malla:after:hidden"
const CASILLA = 'grid h-full w-full min-w-0 min-h-[92px] content-start gap-1 rounded-ui border-2 border-c px-3 py-2.5 text-left transition-colors duration-180 ease-curva contraste:aria-pressed:outline-3 contraste:aria-pressed:outline-offset-2 contraste:aria-pressed:outline-tinta'
const IMAGEN = 'aspect-video w-full animate-abrir rounded-[calc(var(--radio)-1px)] bg-niebla object-cover'

/**
 * CU2: la oferta como malla curricular. Cada programa es una fila y sus módulos, casillas en orden de cursado,
 * agrupadas por área. Público en /anuncios (registro de interés); interno en /gestion-anuncios (consulta y sincronización, RNF2).
 */
export default function PCatalogo() {
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

  // data-zona="oferta": en el público adulto los títulos del catálogo van en grotesca pesada (tokens.css).
  const oferta = `flex flex-1 flex-col ${interno ? '' : `${MARGEN} pt-[clamp(20px,3vw,40px)]`}`
  if (cargando) return <div data-zona="oferta" className={oferta}><Cargando filas={6} /></div>
  if (error) return <div data-zona="oferta" className={oferta}><Aviso tipo="error">{error}</Aviso><div className="acciones mt-3 justify-start"><button type="button" className="btn btn-secundario" onClick={recargar}>Reintentar</button></div></div>
  if (!programas.length) return <Vacio titulo="No hay programas abiertos" icono={SearchX}>La oferta se publicará pronto.</Vacio>

  if (registrando && eleccion) return <Registro eleccion={eleccion} onVolver={() => setRegistrando(false)} />

  const visibles = area ? programas.filter((p) => p.area === area) : programas
  const totalModulos = visibles.reduce((s, p) => s + p.modulos.length, 0)

  return (
    <>
      {interno && <BarraInterna onSincronizado={recargar} puedeSincronizar={puede('gestion-anuncios', 'modificacion', sesion)} />}
      <section data-zona="oferta" className={`relative ${oferta}`} aria-labelledby="titulo-oferta">
        {!interno && <DecoracionCatalogo />}
        <header className="relative z-1 mb-6 flex flex-wrap items-end justify-between gap-x-8 gap-y-4">
          <div>
            <h1 id="titulo-oferta" className="text-[clamp(2.25rem,1.5rem+2.4vw,3.5rem)] leading-none tracking-[-0.03em] text-navy dark:text-tinta">Malla de la oferta</h1>
            <p className="mt-2 max-w-[44ch] text-tinta-suave">
              <span className="font-bold text-tinta tabular-nums">{visibles.length}</span> {visibles.length === 1 ? 'programa' : 'programas'} · <span className="font-bold text-tinta tabular-nums">{totalModulos}</span> módulos. Tome el programa completo o solo el módulo que necesita.
            </p>
          </div>
          <div role="group" aria-label="Filtrar por área"
            className={`flex flex-wrap gap-2 max-malla:flex-nowrap max-malla:overflow-x-auto max-malla:pt-0.5 max-malla:pb-1.5 max-malla:[scrollbar-width:none] ${interno ? '' : 'max-malla:-mx-[clamp(16px,3vw,40px)] max-malla:px-[clamp(16px,3vw,40px)]'}`}>
            <FiltroArea elegido={!area} onClick={() => setArea('')}>Todas</FiltroArea>
            {areas.map((a) => <FiltroArea key={a} color={colores.get(a)} elegido={area === a} onClick={() => setArea(a)}>{a}</FiltroArea>)}
          </div>
        </header>

        <div className="relative z-1">
          <Malla areas={areas} colores={colores} visibles={visibles} eleccion={eleccion} onElegir={setEleccion} />
        </div>

        {!interno && <BarraEleccion eleccion={eleccion} onContinuar={() => setRegistrando(true)} />}
      </section>
    </>
  )
}

/** Decoraciones en CSS puro para el catálogo público (visibles solo en temas Niños y Jóvenes). */
function DecoracionCatalogo() {
  return (
    <div className="decoracion-tema" aria-hidden="true">
      <div className="sol">
        <span className="rayo rayo-1" />
        <span className="rayo rayo-2" />
        <span className="rayo rayo-3" />
        <span className="rayo rayo-4" />
      </div>
      <div className="nube nube-1" />
      <div className="nube nube-2" />
      <div className="forma-pastel forma-pastel-1" />
      <div className="forma-pastel forma-pastel-2" />

      <div className="luna" />
      <span className="estrella estrella-1" />
      <span className="estrella estrella-2" />
      <span className="estrella estrella-3" />
      <span className="estrella estrella-4" />
      <span className="estrella estrella-5" />

      <div className="geo-circulo geo-circulo-1" />
      <div className="geo-circulo geo-circulo-2" />
      <div className="geo-triangulo" />
      <div className="geo-rombo" />
      <div className="geo-lineas" />
    </div>
  )
}

/** Botón de filtro por área: punto con el color del área (sin color en "Todas"). */
function FiltroArea({ color, elegido, onClick, children }) {
  const punto = color ? `${AREA[color]} before:size-2.5 before:rounded-full before:bg-c before:content-[''] ${elegido ? 'before:shadow-[0_0_0_2px_#fff]' : ''}` : ''
  const estado = elegido
    ? 'border-navy bg-navy text-white dark:border-acento dark:bg-acento dark:text-sobre-acento'
    : 'border-filete-fuerte bg-papel text-tinta hover:border-tinta-suave'
  return (
    <button type="button" aria-pressed={elegido} onClick={onClick}
      className={`inline-flex min-h-10 items-center gap-2 rounded-full border px-4 py-2 text-sm font-bold whitespace-nowrap transition-colors duration-150 ease-curva ${estado} ${punto}`}>
      {children}
    </button>
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
  // Celdas de la malla: en celular la tabla se vuelve bloques.
  const bloque = 'max-malla:block max-malla:w-full'

  return (
    <div className="mb-6 overflow-x-auto rounded-hoja border border-filete bg-papel max-malla:overflow-visible max-malla:border-0 max-malla:bg-transparent">
      <table className={`w-full table-fixed border-separate border-spacing-x-4 border-spacing-y-2.5 px-2 pb-2.5 max-malla:p-0 ${bloque} ${ANCHO_MALLA[Math.min(columnas, 10)] || ''}`}>
        <caption className="sr-only">Programas por área con sus módulos en orden de cursado</caption>
        <colgroup><col className="w-[280px]" />{Array.from({ length: columnas }, (_, i) => <col key={i} />)}</colgroup>
        <thead className="max-malla:hidden">
          <tr>
            <th scope="col" className="sticky left-0 z-2 bg-papel px-3.5 pt-3.5 text-left align-top text-xs font-bold whitespace-nowrap text-tinta-suave before:absolute before:inset-y-0 before:-left-4 before:w-4 before:bg-papel before:content-[''] max-malla:before:hidden">Programa</th>
            {Array.from({ length: columnas }, (_, i) => <th key={i} scope="col" className="px-3.5 pt-3.5 text-left align-top text-xs font-bold whitespace-nowrap text-tinta-suave">Módulo {i + 1}</th>)}
          </tr>
        </thead>
        {grupos.map((g, gi) => (
          <tbody key={g.area} className={`${AREA[g.color]} ${bloque} ${gi > 0 ? 'max-malla:mt-6' : ''}`}>
            <tr className={bloque}>
              <th colSpan={columnas + 1} scope="rowgroup" className={`border-b-2 border-c px-1 pt-3 pb-0.5 text-left align-top text-base font-extrabold text-tinta max-malla:mb-3 max-malla:p-0 max-malla:pb-1.5 ${bloque}`}>
                {g.area} <small className="ml-2 text-xs font-semibold text-tinta-suave">{g.programas.length} {g.programas.length === 1 ? 'programa' : 'programas'}</small>
              </th>
            </tr>
            {g.programas.map((p) => {
              const abierta = eleccion?.programa.codigo === p.codigo
              const programaElegido = abierta && !eleccion.modulo
              return (
                <tr key={p.codigo} ref={abierta ? fila : undefined} className={`max-malla:mb-3 ${bloque}`}>
                  <th scope="row" className={`sticky left-0 z-2 h-px bg-papel p-0 align-top before:absolute before:inset-y-0 before:-left-4 before:w-4 before:bg-papel before:content-[''] max-malla:before:hidden max-malla:static max-malla:h-auto ${bloque} ${CONECTOR}`}>
                    <button type="button" aria-expanded={abierta} aria-pressed={programaElegido}
                      onClick={() => onElegir(programaElegido ? null : { programa: p, modulo: null })}
                      className={`${CASILLA} max-malla:grid-cols-[minmax(0,1fr)_auto] max-malla:gap-x-3 ${programaElegido
                        ? `bg-c ${SOBRE_COLOR}`
                        : 'bg-[color-mix(in_srgb,var(--c)_9%,var(--papel))] text-tinta hover:bg-[color-mix(in_srgb,var(--c)_16%,var(--papel))]'}`}>
                      <Foto src={p.imagen} className={`${IMAGEN} mb-1.5 ${abierta ? 'block' : 'hidden'} max-malla:col-start-2 max-malla:row-span-3 max-malla:row-start-1 max-malla:m-0 max-malla:block max-malla:w-[84px]`} />
                      <strong className={`text-base leading-tight font-extrabold max-malla:col-start-1 ${programaElegido ? SOBRE_COLOR : 'text-navy dark:text-tinta'}`}>{p.nombre}</strong>
                      <small className={`text-xs max-malla:col-start-1 ${programaElegido ? SOBRE_COLOR : 'text-tinta-suave'}`}>
                        <span className="tabular-nums">{bs(p.precio_total)}</span> · <span className="tabular-nums">{horas(p.modulos)}</span> h · {p.modulos.length} módulos
                      </small>
                      {!abierta && (
                        <span className="hidden max-malla:col-start-1 max-malla:mt-1.5 max-malla:flex max-malla:flex-wrap max-malla:gap-1" aria-hidden="true">
                          {p.modulos.map((m, i) => <i key={m.codigo} className="rounded-[3px] border border-c px-[5px] py-px text-xs font-extrabold tracking-[0.04em] text-c not-italic tabular-nums">{sigla(p, i)}</i>)}
                        </span>
                      )}
                      {abierta && p.descripcion && <span className={`mt-1.5 block animate-abrir text-xs leading-[1.45] max-malla:col-start-1 ${programaElegido ? SOBRE_COLOR : 'text-tinta-suave'}`}>{p.descripcion}</span>}
                    </button>
                  </th>
                  {Array.from({ length: columnas }, (_, i) => {
                    const m = p.modulos[i]
                    if (!m) return <td key={i} className="p-0 max-malla:hidden" aria-hidden="true" />
                    const elegida = abierta && eleccion.modulo?.codigo === m.codigo
                    const ultima = i === p.modulos.length - 1
                    return (
                      <td key={m.codigo}
                        className={`relative h-px p-0 align-top ${ultima ? '' : CONECTOR} max-malla:h-auto max-malla:pt-2.5 max-malla:pl-[22px] ${bloque} ${abierta ? '' : 'max-malla:hidden'}
                          max-malla:before:absolute max-malla:before:top-0 max-malla:before:left-2.5 max-malla:before:w-0.5 max-malla:before:bg-c max-malla:before:content-[''] ${ultima ? 'max-malla:before:h-[34px]' : 'max-malla:before:bottom-0'}`}>
                        <button type="button" aria-pressed={elegida} aria-label={`${m.nombre}, módulo ${i + 1} de ${p.nombre}, ${bs(m.precio)}`}
                          onClick={() => onElegir(elegida ? { programa: p, modulo: null } : { programa: p, modulo: m })}
                          className={`${CASILLA} max-malla:min-h-0 max-malla:grid-cols-[auto_minmax(0,1fr)_auto] max-malla:gap-x-2.5 ${elegida
                            ? 'bg-c'
                            : abierta ? 'bg-[color-mix(in_srgb,var(--c)_6%,var(--papel))]' : 'bg-papel hover:bg-[color-mix(in_srgb,var(--c)_8%,var(--papel))]'} text-tinta`}>
                          {abierta && <Foto src={m.imagen} className={`${IMAGEN} mb-1.5 block max-malla:col-start-3 max-malla:row-span-2 max-malla:row-start-1 max-malla:m-0 max-malla:w-[72px]`} />}
                          <b className={`text-xs font-extrabold tracking-[0.06em] tabular-nums max-malla:row-span-2 max-malla:self-center ${elegida ? SOBRE_COLOR : 'text-c'}`}>{sigla(p, i)}</b>
                          <span className={`text-sm leading-tight font-bold ${elegida ? SOBRE_COLOR : ''}`}>{m.nombre}</span>
                          <small className={`text-xs max-malla:col-start-2 ${elegida ? SOBRE_COLOR : 'text-tinta-suave'}`}><span className="tabular-nums">{bs(m.precio)}</span>{m.duracion && ` · ${m.duracion}`}</small>
                          {abierta && m.descripcion && <span className={`mt-1.5 block max-w-[24ch] animate-abrir text-xs leading-[1.45] max-malla:col-span-full max-malla:max-w-none ${elegida ? SOBRE_COLOR : 'text-tinta-suave'}`}>{m.descripcion}</span>}
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
  const barra = `sticky bottom-0 z-25 ${SANGRAR} mt-auto flex flex-wrap items-center gap-x-6 gap-y-2 bg-navy ${MARGEN} py-3 text-white contraste:border-t-3 contraste:border-tinta contraste:bg-portada max-malla:gap-x-3`
  if (!eleccion) {
    return (
      <div className={`${barra} max-malla:static`} role="status">
        <p className="min-w-0 flex-1 text-sm text-portada-suave max-malla:text-xs">Toque un programa para verlo completo, o un módulo para tomarlo solo. Precios en bolivianos; el programa completo admite hasta 12 cuotas.</p>
      </div>
    )
  }
  const { programa, modulo } = eleccion
  return (
    <div className={barra} role="status">
      <p className="grid min-w-0 flex-1 gap-0.5">
        <small className="text-xs text-portada-suave max-malla:hidden">{modulo ? `Solo este módulo de ${programa.nombre}` : `Programa completo · ${programa.modulos.length} módulos`}</small>
        <strong className="text-lg leading-[1.2] font-extrabold max-malla:truncate max-malla:text-base">{modulo ? modulo.nombre : programa.nombre}</strong>
      </p>
      <b className="text-2xl font-extrabold tabular-nums max-malla:text-xl">{bs(modulo ? modulo.precio : programa.precio_total)}</b>
      <button type="button" className="btn btn-acento btn-grande max-malla:flex-[1_1_100%]" onClick={onContinuar}>{modulo ? 'Me interesa este módulo' : 'Me interesa el programa'}</button>
    </div>
  )
}

function BarraInterna({ onSincronizado, puedeSincronizar }) {
  const aviso = useAviso()
  const [enviando, setEnviando] = useState(false)
  return (
    <>
      <CabeceraPagina titulo="Oferta académica" acciones={puedeSincronizar && (
        <Boton className="btn-secundario" cargando={enviando} onClick={async () => {
          setEnviando(true)
          try { aviso.ok((await catalogoApi.sincronizar()).data.mensaje); onSincronizado() } catch (e) { aviso.error(e) } finally { setEnviando(false) }
        }}><RefreshCw size={16} /> Sincronizar catálogo</Boton>
      )}>
        Réplica local del catálogo del sistema académico (Grupo 06). Es la misma oferta que ve el público en el catálogo.
      </CabeceraPagina>
      {aviso.nodo}
    </>
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
    <section data-zona="oferta" className={`mx-auto grid w-full max-w-[1200px] grid-cols-[minmax(0,4fr)_minmax(0,7fr)] items-start gap-8 ${MARGEN} py-[clamp(24px,4vw,56px)] max-tableta:grid-cols-1`}>
      <div className="grid content-start gap-3">
        <button type="button" className="btn btn-texto -ml-2 justify-self-start" onClick={onVolver}><ArrowLeft size={16} /> Volver a la malla</button>
        <Foto src={(modulo || programa).imagen} className="aspect-video w-full rounded-hoja bg-niebla object-cover" />
        <h1 className="text-[clamp(1.9rem,1.4rem+1.6vw,2.6rem)] leading-[1.05] tracking-[-0.025em] text-navy dark:text-tinta">{programa.nombre}</h1>
        <p className="text-tinta-suave">{seleccionados.length === programa.modulos.length ? `Programa completo: ${programa.modulos.length} módulos` : `${seleccionados.length} de ${programa.modulos.length} módulos seleccionados`}</p>
        <ol className="mt-2 grid gap-2">
          {programa.modulos.map((m, i) => {
            const incluido = modulosSeleccionados.includes(m.codigo)
            return (
              <li key={m.codigo}
                className={`relative rounded-ui border-2 text-sm not-first:before:absolute not-first:before:-top-2.5 not-first:before:left-[2.2rem] not-first:before:h-2 not-first:before:w-0.5 not-first:before:bg-filete-fuerte not-first:before:content-['']
                  ${incluido ? 'border-solid border-acento-texto font-[650] text-tinta' : 'border-dashed border-filete-fuerte text-tinta-suave'}`}>
                <label className="grid cursor-pointer grid-cols-[auto_4.2rem_minmax(0,1fr)_auto_auto] items-center gap-2.5 px-3 py-2">
                  <input type="checkbox" className="size-[18px] accent-(--acento-texto)" checked={incluido} onChange={() => alternarModulo(m.codigo)} />
                  <b className={`text-xs tracking-[0.06em] tabular-nums ${incluido ? 'text-acento-texto' : ''}`}>{sigla(programa, i)}</b><span>{m.nombre}</span>
                  <small className="whitespace-nowrap text-tinta-suave tabular-nums">{bs(m.precio)}</small>
                  {incluido && <Check size={16} aria-label="incluido" className="text-acento-texto" />}
                </label>
              </li>
            )
          })}
        </ol>
        <div className="mt-3 grid gap-0.5 border-t-2 border-navy pt-3 dark:border-acento">
          <span className="text-3xl leading-[1.05] font-extrabold text-navy tabular-nums dark:text-tinta">{bs(total)}</span>
          <small className="text-sm text-tinta-suave">{seleccionados.length === programa.modulos.length ? 'programa completo' : `${seleccionados.length} módulo(s) seleccionados`}</small>
        </div>
      </div>
      <form className="hoja hoja-cuerpo grid grid-cols-2 gap-4 max-movil:grid-cols-1" onSubmit={enviar}>
        <h2 className="col-span-full text-xl">Deje sus datos y un asesor le escribe por WhatsApp</h2>
        <Campo etiqueta="Nombre *" error={errores.nombre}><input value={form.nombre} onChange={set('nombre')} required maxLength={120} autoComplete="given-name" pattern="[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .\-]+" title="Solo letras y espacios." aria-invalid={Boolean(errores.nombre)} /></Campo>
        <Campo etiqueta="Apellido *" error={errores.apellido}><input value={form.apellido} onChange={set('apellido')} required maxLength={120} autoComplete="family-name" pattern="[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .\-]+" title="Solo letras y espacios." aria-invalid={Boolean(errores.apellido)} /></Campo>
        <Campo etiqueta="Carnet de identidad *" error={errores.documento}><input value={form.documento} onChange={set('documento')} required maxLength={20} placeholder="Nro. de documento" pattern="[0-9A-Za-z\-]+" title="Números, letras y guion; por ejemplo 7845123-1A." aria-invalid={Boolean(errores.documento)} /></Campo>
        <Campo etiqueta="Teléfono (WhatsApp) *" error={errores.telefono}><input value={form.telefono} onChange={set('telefono')} required inputMode="tel" placeholder="Ej. 71234567" pattern="\+?[0-9 ]{7,20}" title="Entre 7 y 20 dígitos." autoComplete="tel" aria-invalid={Boolean(errores.telefono)} /></Campo>
        <Campo etiqueta="Correo *" error={errores.correo}><input type="email" value={form.correo} onChange={set('correo')} required maxLength={160} placeholder="usted@correo.com" autoComplete="email" aria-invalid={Boolean(errores.correo)} /></Campo>
        <Campo etiqueta="Profesión u ocupación" error={errores.profesion}><input value={form.profesion} onChange={set('profesion')} maxLength={120} placeholder="Ej. Ingeniero de sistemas" /></Campo>
        <Campo etiqueta="Ciudad" error={errores.ubicacion}><input value={form.ubicacion} onChange={set('ubicacion')} maxLength={160} placeholder="Ej. Santa Cruz" autoComplete="address-level2" /></Campo>
        <div className="col-span-full"><Aviso tipo={estado?.tipo}>{estado?.texto}</Aviso></div>
        <div className="acciones col-span-full"><Boton type="submit" className="btn-primario btn-grande" cargando={enviando} disabled={!modulosSeleccionados.length} aria-label="Enviar interés">Enviar interés ({modulosSeleccionados.length})</Boton></div>
      </form>
    </section>
  )
}
