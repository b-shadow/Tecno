import { useEffect, useRef } from 'react'
import { BarController, BarElement, CategoryScale, Chart, Filler, Legend, LineController, LineElement, LinearScale, PointElement, Tooltip } from 'chart.js'
import { useApariencia } from '../servicios/theme'

Chart.register(BarController, BarElement, LineController, LineElement, PointElement, LinearScale, CategoryScale, Filler, Tooltip, Legend)

const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim()

/** Serie diaria (líneas) con colores tomados de los tokens del tema activo; se redibuja al cambiar de tema. */
export default function GraficoLineas({ etiquetas, series, formato = (v) => v, alto = 260, descripcion, tipo = 'line' }) {
  const lienzo = useRef(null)
  const apariencia = useApariencia()
  useEffect(() => {
    const tinta = css('--tinta-suave')
    const filete = css('--filete')
    const fuente = css('--fuente-ui')
    const grafico = new Chart(lienzo.current, {
      type: tipo,
      data: {
        labels: etiquetas,
        datasets: series.map((s) => ({
          label: s.nombre, data: s.datos, borderColor: css(s.color), backgroundColor: tipo === 'bar' ? css(s.color) : `${css(s.color)}22`, borderRadius: 3, maxBarThickness: 28,
          fill: s.relleno ?? false, tension: 0, pointRadius: 2, borderWidth: 2,
        })),
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 500 },
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: series.length > 1, labels: { color: tinta, font: { family: fuente }, boxWidth: 12 } },
          tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${formato(c.parsed.y)}` } },
        },
        scales: {
          x: { ticks: { color: tinta, font: { family: fuente } }, grid: { display: false } },
          y: { beginAtZero: true, ticks: { color: tinta, font: { family: fuente }, callback: (v) => formato(v), precision: 0 }, grid: { color: filete } },
        },
      },
    })
    return () => grafico.destroy()
  }, [etiquetas, series, formato, apariencia, tipo])
  return <div className="grafico" style={{ height: alto }}><canvas ref={lienzo} role="img" aria-label={descripcion} /></div>
}
