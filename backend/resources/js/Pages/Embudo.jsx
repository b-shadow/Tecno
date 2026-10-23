import { useMemo, useState } from 'react'
import { CalendarClock, KanbanSquare, UserRound } from 'lucide-react'
import { api } from '../services/api'
import { go } from '../services/navigation'
import { puede, useAuth } from '../services/auth'
import { Aviso, CabeceraPagina, Campo, Cargando, Modal, Vacio, bs, fecha, nombre, useAviso, useDatos } from '../components/ui'

const COLOR = { 'Nuevo': 'nuevo', 'En Contacto': 'contacto', 'Seguimiento': 'seguimiento', 'Promesa de Pago': 'promesa', 'Convertido': 'convertido', 'Perdido': 'perdido' }

/**
 * CU4: embudo de ventas en tablero Kanban (RF3.1, RF3.2). Las tarjetas se arrastran entre columnas o se mueven con
 * "Mover a…" (teclado y celular). Perdido pide el motivo (CU5); Convertido valida los datos y matricula (CU6).
 */
export default function Embudo() {
  const sesion = useAuth()
  const esVendedor = sesion.usuario?.rol === 'vendedor'
  const editable = puede('embudo', 'modificacion', sesion)
  const [filtros, setFiltros] = useState({ buscar: '', vendedor: '' })
  const { datos, cargando, error, recargar } = useDatos(async () => (await api.get('/intereses', { params: { buscar: filtros.buscar || undefined, vendedor: filtros.vendedor || undefined } })).data, [filtros.buscar, filtros.vendedor])
  const vendedores = useDatos(async () => (esVendedor ? [] : (await api.get('/vendedores')).data.vendedores), [esVendedor])
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
      const { data } = await api.patch(`/intereses/${tarjeta.nro_tarjeta}/estado`, { estado, ...extra })
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
          <nav className="etapas" aria-label="Ir a una etapa">
            {(datos?.estados || []).map((estado) => (
              <button key={estado} type="button" style={{ '--c': `var(--etapa-${COLOR[estado]})` }}
                onClick={() => document.getElementById(`etapa-${COLOR[estado]}`)?.scrollIntoView({ behavior: 'smooth', inline: 'start', block: 'nearest' })}>
                {estado} <b>{porEstado[estado]?.length || 0}</b>
              </button>
            ))}
          </nav>
          <div className="kanban" aria-label="Tablero del embudo">
            {(datos?.estados || []).map((estado) => (
              <section key={estado} id={`etapa-${COLOR[estado]}`} className={`columna ${encima === estado ? 'encima' : ''}`} style={{ '--c': `var(--etapa-${COLOR[estado]})` }} aria-label={estado}
                onDragOver={(e) => { if (editable && arrastrada) { e.preventDefault(); setEncima(estado) } }}
                onDragLeave={() => setEncima(null)}
                onDrop={(e) => { e.preventDefault(); setEncima(null); mover(arrastrada, estado); setArrastrada(null) }}>
                <header className="columna-cabecera"><h3>{estado}</h3><span>{porEstado[estado]?.length || 0}</span></header>
                <div className="columna-lista">
                  {porEstado[estado]?.map((t) => (
                    <Tarjeta key={t.nro_tarjeta} t={t} estados={datos.estados} editable={editable && t.estado !== 'Convertido'} mostrarVendedor={!esVendedor}
                      onArrastrar={setArrastrada} onMover={(e) => mover(t, e)} />
                  ))}
                  {!porEstado[estado]?.length && <div className="columna-vacia">Sin tarjetas</div>}
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

function Tarjeta({ t, estados, editable, mostrarVendedor, onArrastrar, onMover }) {
  const [arrastrando, setArrastrando] = useState(false)
  const pendiente = t.ordenes_pago?.flatMap((o) => o.cuotas || []).find((c) => c.estado !== 'Pago aprobado')
  const vencido = t.proximo_contacto && new Date(t.proximo_contacto) < new Date() && !['Convertido', 'Perdido'].includes(t.estado)
  return (
    <article className="tarjeta" draggable={editable} aria-grabbed={arrastrando}
      onDragStart={(e) => { e.dataTransfer.effectAllowed = 'move'; setArrastrando(true); onArrastrar(t) }}
      onDragEnd={() => { setArrastrando(false) }}>
      <div className="tarjeta-cabeza">
        <strong><a href="#" onClick={(e) => { e.preventDefault(); go(`/agenda?interes=${t.nro_tarjeta}`) }}>{nombre(t.prospecto)}</a></strong>
        <span className="cifra">#{t.nro_tarjeta}</span>
      </div>
      <p>{t.modulo_nombre} · {t.programa_nombre}</p>
      {t.motivo_perdida && <p><b>Motivo:</b> {t.motivo_perdida}</p>}
      {pendiente && <p>Cuota {pendiente.nro_cuota}: {bs(pendiente.monto)} · {pendiente.estado}</p>}
      {vencido && <span className="alerta"><CalendarClock size={13} /> Contacto vencido ({fecha(t.proximo_contacto, true)})</span>}
      <div className="tarjeta-pie">
        {mostrarVendedor && <span className="tarjeta-vendedor"><UserRound size={13} />{t.vendedor ? nombre(t.vendedor) : 'Sin asignar'}</span>}
        {editable && (
          <select className="control" aria-label={`Mover la tarjeta ${t.nro_tarjeta} a otra etapa`} value="" onChange={(e) => onMover(e.target.value)}>
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
