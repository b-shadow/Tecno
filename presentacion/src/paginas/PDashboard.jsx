import { useMemo } from 'react'
import { useAuth } from '../servicios/auth'
import GraficoLineas from '../componentes/Grafico'
import { Aviso, Barras, CabeceraPagina, Cargando, bs, useDatos } from '../componentes/ui'
import * as reportesApi from '../api/reportes'
import { ETAPA } from '../componentes/tonos'

const moneda = (v) => bs(v)
const miles = (v) => v.toLocaleString('es-BO')
const dia = (d) => new Date(`${d}T12:00:00`).toLocaleDateString('es-BO', { day: '2-digit', month: 'short' })

/** CU8 / enunciado 8: panel analítico del negocio y del flujo de accesos del sitio. */
export default function PDashboard() {
  const { usuario } = useAuth()
  const { datos, cargando, error, recargar } = useDatos(async () => (await reportesApi.dashboard()).data, [], { intervaloMs: 10000, refrescarAlEnfocar: true })
  const ingresos = useMemo(() => datos && { etiquetas: datos.ingresos_por_dia.map((d) => dia(d.dia)), series: [{ nombre: 'Ingresos', datos: datos.ingresos_por_dia.map((d) => d.total), color: '--acento', relleno: true }] }, [datos])
  const accesos = useMemo(() => datos?.accesos && {
    etiquetas: datos.accesos.exitosos.map((d) => dia(d.dia)),
    series: [
      { nombre: 'Inicios de sesión', datos: datos.accesos.exitosos.map((d) => d.total), color: '--etapa-seguimiento' },
      { nombre: 'Intentos fallidos', datos: datos.accesos.fallidos.map((d) => d.total), color: '--peligro' },
    ],
  }, [datos])

  if (cargando && !datos) return <Cargando filas={8} />
  if (error) return <Aviso tipo="error">{error}</Aviso>
  const k = datos.indicadores
  return (
    <>
      <CabeceraPagina titulo={`Hola, ${usuario?.nombre}`} acciones={<button type="button" className="btn btn-secundario" onClick={recargar}>Actualizar</button>}>
        {usuario?.rol === 'coordinador' ? 'Resumen de los programas a su cargo.' : 'Resumen de toda la operación comercial.'}
      </CabeceraPagina>
      <dl className="cifras mb-6">
        <div><dt>Tarjetas abiertas</dt><dd>{k.tarjetas_abiertas}</dd></div>
        <div><dt>Sin asignar</dt><dd>{k.sin_asignar}</dd></div>
        <div><dt>Cuotas en revisión</dt><dd>{k.cuotas_en_revision}</dd></div>
        <div><dt>Cuotas vencidas</dt><dd>{k.cuotas_vencidas}</dd></div>
        <div><dt>Ingresos del mes</dt><dd className="tabular-nums">{bs(k.ingresos_mes)}</dd></div>
        <div><dt>Actividades hoy</dt><dd>{k.actividades_hoy}</dd></div>
      </dl>
      <div className="grid grid-cols-2 gap-6 max-movil:grid-cols-1 mb-6">
        <section className="hoja"><header className="hoja-titulo"><h3>Embudo por etapa</h3><small>{k.convertidos} convertidos · {k.perdidos} perdidos</small></header>
          <div className="hoja-cuerpo"><Barras datos={datos.embudo.map((e) => ({ ...e, tono: ETAPA[e.etiqueta] }))} /></div></section>
        <section className="hoja"><header className="hoja-titulo"><h3>Ingresos de los últimos 14 días</h3></header>
          <div className="hoja-cuerpo"><GraficoLineas {...ingresos} tipo="bar" formato={moneda} descripcion="Ingresos aprobados por día" /></div></section>
      </div>
      <div className="grid grid-cols-2 gap-6 max-movil:grid-cols-1">
        <section className="hoja"><header className="hoja-titulo"><h3>Matrículas por programa</h3></header>
          <div className="hoja-cuerpo"><Barras datos={datos.ventas_por_programa} /></div></section>
        <section className="hoja"><header className="hoja-titulo"><h3>Páginas más visitadas</h3></header>
          <div className="hoja-cuerpo"><Barras porcentaje={false} datos={datos.visitas_por_pagina.map((v) => ({ etiqueta: v.nombre, total: v.visitas }))} formato={miles} tono="seguimiento" /></div></section>
      </div>
      {accesos && (
        <section className="hoja mt-6">
          <header className="hoja-titulo"><h3>Accesos al sistema (14 días)</h3><small>{datos.accesos.denegados_semana} accesos denegados esta semana</small></header>
          <div className="hoja-cuerpo"><GraficoLineas {...accesos} descripcion="Inicios de sesión exitosos y fallidos por día" /></div>
        </section>
      )}
    </>
  )
}
