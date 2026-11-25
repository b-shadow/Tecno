import { useMemo, useState } from 'react'
import { CalendarClock, KanbanSquare, UserRound } from 'lucide-react'
import { go } from '../servicios/navigation'
import { puede, useAuth } from '../servicios/auth'
import { Aviso, CabeceraPagina, Campo, Cargando, Modal, Vacio, bs, fecha, nombre, useAviso, useDatos } from '../componentes/ui'
import * as interesesApi from '../api/intereses'
import * as usuariosApi from '../api/usuarios'
import { ETAPA, TONO } from '../componentes/tonos'


/**
 * CU4: embudo de ventas en tablero Kanban (RF3.1, RF3.2). Las tarjetas se arrastran entre columnas o se mueven con
 * "Mover a…" (teclado y celular). Perdido pide el motivo (CU5); Convertido valida los datos y matricula (CU6).
 */
export default function PEmbudo() {
  const sesion = useAuth()
  const esVendedor = sesion.usuario?.rol === 'vendedor'
  const editable = puede('embudo', 'modificacion', sesion)
  const [filtros, setFiltros] = useState({ buscar: '', vendedor: '' })
  const { datos, cargando, error, recargar } = useDatos(async () => (await interesesApi.index({ buscar: filtros.buscar || undefined, vendedor: filtros.vendedor || undefined })).data, [filtros.buscar, filtros.vendedor])
  const vendedores = useDatos(async () => (esVendedor ? [] : (await usuariosApi.vendedores()).data.vendedores), [esVendedor])
  const [arrastrada, setArrastrada] = useState(null)
  const [encima, setEncima] = useState(null)
  const [perdida, setPerdida] = useState(null)
  const [faltantes, setFaltantes] = useState(null)
  const aviso = useAviso()

  const porEstado = useMemo(() => {
    const grupos = Object.fromEntries((datos?.estados || []).map((e) => [e, []]))
    for (const t of datos?.intereses || []) grupos[t.estado]?.push(t)
    return grupos
  }, [datos])

  async function mover(tarjeta, estado, extra = {}) {
    if (!tarjeta || tarjeta.estado === estado) return
    if (estado === 'Perdido' && !extra.motivo_perdida) return setPerdida({ tarjeta, motivo: '', observacion: '' })
    try {
      const { data } = await interesesApi.mover(tarjeta.nro_tarjeta, { estado, ...extra })
      aviso.ok(data.mensaje)
      setPerdida(null)
      recargar()
    } catch (e) {
      if (e.response?.data?.faltantes) setFaltantes({ tarjeta, lista: e.response.data.faltantes })
      else aviso.error(e)
    }
  }

  return (
    <>
      <CabeceraPagina titulo="Embudo de ventas" acciones={<button type="button" className="btn btn-secundario" onClick={recargar}>Actualizar</button>}>
        {esVendedor ? 'Su cartera, de la primera conversación a la matrícula.' : 'Tarjetas de los programas a su cargo. Arrastre una tarjeta o use “Mover a…”.'}
      </CabeceraPagina>

      <div className="barra-filtros">
        <Campo etiqueta="Buscar"><input type="search" placeholder="Prospecto, CI, módulo…" value={filtros.buscar} onChange={(e) => setFiltros({ ...filtros, buscar: e.target.value })} /></Campo>
        {!esVendedor && (
          <Campo etiqueta="Vendedor">
            <select value={filtros.vendedor} onChange={(e) => setFiltros({ ...filtros, vendedor: e.target.value })}>
              <option value="">Todos</option>
              {(vendedores.datos || []).map((v) => <option key={v.correo} value={v.correo}>{nombre(v)}</option>)}
            </select>
          </Campo>
        )}
      </div>

      {error && <Aviso tipo="error">{error}</Aviso>}
      {cargando && !datos ? <Cargando filas={5} /> : (
        datos?.intereses?.length === 0 && !filtros.buscar ? <Vacio titulo="Todavía no hay tarjetas" icono={KanbanSquare}>{esVendedor ? 'Cuando coordinación le asigne prospectos aparecerán aquí.' : 'Registre prospectos o espere los registros del catálogo.'}</Vacio> : (
          <>
          <nav className="mb-3 flex flex-wrap gap-1.5" aria-label="Ir a una etapa">
            {(datos?.estados || []).map((estado) => (
              <button key={estado} type="button" className={`inline-flex items-center gap-2 rounded-full border border-filete bg-papel px-3 py-1.5 text-sm font-[650] before:size-2 before:rounded-full before:bg-c before:content-[''] ${TONO[ETAPA[estado]]}`}
                onClick={() => document.getElementById(`etapa-${ETAPA[estado]}`)?.scrollIntoView({ behavior: 'smooth', inline: 'start', block: 'nearest' })}>
                {estado} <b className="text-tinta-suave tabular-nums">{porEstado[estado]?.length || 0}</b>
              </button>
            ))}
          </nav>
          <div aria-label="Tablero del embudo" className="grid snap-x snap-proximity auto-cols-[minmax(272px,1fr)] grid-flow-col items-start gap-3 overflow-x-auto pr-7 pb-3 [mask-image:linear-gradient(90deg,#000_calc(100%-20px),transparent)] max-movil:auto-cols-[86vw]">
            {(datos?.estados || []).map((estado) => (
              <section key={estado} id={`etapa-${ETAPA[estado]}`} className={`flex max-h-[calc(100dvh-310px)] min-h-60 snap-start flex-col rounded-hoja shadow-[inset_0_4px_0_var(--c)] outline-2 -outline-offset-2 outline-dashed transition-[background-color,outline-color] duration-150 ease-curva max-movil:max-h-none ${TONO[ETAPA[estado]]} ${encima === estado ? 'bg-acento-suave outline-c' : 'bg-niebla outline-transparent'}`} aria-label={estado}
                onDragOver={(e) => { if (editable && arrastrada) { e.preventDefault(); setEncima(estado) } }}
                onDragLeave={() => setEncima(null)}
                onDrop={(e) => { e.preventDefault(); setEncima(null); mover(arrastrada, estado); setArrastrada(null) }}>
                <header className="flex items-center justify-between gap-2 px-3.5 pt-3.5 pb-2.5">
                  <h3 className="font-ui text-sm font-[750] text-c claro:text-[color-mix(in_srgb,var(--c)_85%,#000)]">{estado}</h3>
                  <span className="rounded-full bg-papel px-2 py-px text-xs font-bold text-tinta-suave tabular-nums">{porEstado[estado]?.length || 0}</span>
                </header>
                <div className="grid gap-2 overflow-y-auto px-2.5 pb-3">
                  {porEstado[estado]?.map((t) => (
                    <Tarjeta key={t.nro_tarjeta} t={t} estados={datos.estados} editable={editable && t.estado !== 'Convertido'} mostrarVendedor={!esVendedor}
                      onArrastrar={setArrastrada} onMover={(e) => mover(t, e)} />
                  ))}
                  {!porEstado[estado]?.length && <div className="rounded-ui border border-dashed border-filete-fuerte px-3 py-[18px] text-center text-xs text-tinta-suave">Sin tarjetas</div>}
                </div>
              </section>
            ))}
          </div>
          </>
        )
      )}

      {perdida && (
        <Modal titulo="Marcar como perdido" descripcion={`${nombre(perdida.tarjeta.prospecto)} · ${perdida.tarjeta.modulo_nombre}`} onCerrar={() => setPerdida(null)}
          pie={<div className="acciones"><button type="button" className="btn btn-secundario" onClick={() => setPerdida(null)}>Cancelar</button><button type="button" className="btn btn-peligro" disabled={!perdida.motivo} onClick={() => mover(perdida.tarjeta, 'Perdido', { motivo_perdida: perdida.motivo, observacion: perdida.observacion || undefined })}>Marcar como perdido</button></div>}>
          <Campo etiqueta="Motivo de la pérdida" requerido ayuda="Obligatorio (RF3.3). Se usa en las estadísticas de pérdidas.">
            <select value={perdida.motivo} required onChange={(e) => setPerdida({ ...perdida, motivo: e.target.value })}>
              <option value="">Elija el motivo…</option>
              {Object.entries(agrupar(datos.motivos.filter((m) => m.nombre !== 'Sin clasificar (web)'), 'categoria')).map(([cat, lista]) => (
                <optgroup key={cat} label={cat}>{lista.map((m) => <option key={m.nombre} value={m.nombre}>{m.nombre}</option>)}</optgroup>
              ))}
            </select>
          </Campo>
          <Campo etiqueta="Observación (opcional)"><textarea maxLength={2000} value={perdida.observacion} onChange={(e) => setPerdida({ ...perdida, observacion: e.target.value })} placeholder="Detalle lo que dijo el prospecto." /></Campo>
        </Modal>
      )}

      {faltantes && (
        <Modal titulo="Todavía no se puede convertir" descripcion="Para matricular se validan los datos (RF3.4). Falta:" onCerrar={() => setFaltantes(null)}
          pie={<div className="acciones"><button type="button" className="btn btn-secundario" onClick={() => setFaltantes(null)}>Cerrar</button><button type="button" className="btn btn-primario" onClick={() => go(`/agenda?interes=${faltantes.tarjeta.nro_tarjeta}`)}>Abrir la ficha</button></div>}>
          <Aviso tipo="error"><ul>{faltantes.lista.map((f) => <li key={f}>{f}</li>)}</ul></Aviso>
        </Modal>
      )}
      {aviso.nodo}
    </>
  )
}

const DETALLE = 'text-xs leading-[1.4] text-tinta-suave'

function Tarjeta({ t, estados, editable, mostrarVendedor, onArrastrar, onMover }) {
  const [arrastrando, setArrastrando] = useState(false)
  const pendiente = t.ordenes_pago?.flatMap((o) => o.cuotas || []).find((c) => c.estado !== 'Pago aprobado')
  const vencido = t.proximo_contacto && new Date(t.proximo_contacto) < new Date() && !['Convertido', 'Perdido'].includes(t.estado)
  return (
    <article draggable={editable} aria-grabbed={arrastrando}
      className="grid cursor-grab gap-1.5 rounded-ui border border-filete bg-papel p-3 shadow-hoja transition-[transform,box-shadow] duration-150 ease-curva hover:border-filete-fuerte aria-[grabbed=true]:rotate-[1.5deg] aria-[grabbed=true]:opacity-55"
      onDragStart={(e) => { e.dataTransfer.effectAllowed = 'move'; setArrastrando(true); onArrastrar(t) }}
      onDragEnd={() => { setArrastrando(false) }}>
      <div className="flex items-baseline justify-between gap-2">
        <strong className="leading-tight font-bold"><a className="text-inherit no-underline hover:underline focus-visible:underline" href="#" onClick={(e) => { e.preventDefault(); go(`/agenda?interes=${t.nro_tarjeta}`) }}>{nombre(t.prospecto)}</a></strong>
        <span className="text-xs text-tinta-suave tabular-nums">#{t.nro_tarjeta}</span>
      </div>
      <p className={DETALLE}>{t.modulo_nombre} · {t.programa_nombre}</p>
      {t.motivo_perdida && <p className={DETALLE}><b>Motivo:</b> {t.motivo_perdida}</p>}
      {pendiente && <p className={DETALLE}>Cuota {pendiente.nro_cuota}: {bs(pendiente.monto)} · {pendiente.estado}</p>}
      {vencido && <span className="inline-flex items-center gap-1 text-xs font-[650] text-aviso"><CalendarClock size={13} /> Contacto vencido ({fecha(t.proximo_contacto, true)})</span>}
      <div className="flex flex-wrap items-center justify-between gap-1.5">
        {mostrarVendedor && <span className="inline-flex items-center gap-1 text-xs text-tinta-suave"><UserRound size={13} />{t.vendedor ? nombre(t.vendedor) : 'Sin asignar'}</span>}
        {editable && (
          <select className="control min-h-8 max-w-[160px] px-2 py-1 text-xs" aria-label={`Mover la tarjeta ${t.nro_tarjeta} a otra etapa`} value="" onChange={(e) => onMover(e.target.value)}>
            <option value="">Mover a…</option>
            {estados.filter((e) => e !== t.estado).map((e) => <option key={e} value={e}>{e}</option>)}
          </select>
        )}
      </div>
    </article>
  )
}

function agrupar(lista, campo) {
  return lista.reduce((g, x) => ({ ...g, [x[campo]]: [...(g[x[campo]] || []), x] }), {})
}
