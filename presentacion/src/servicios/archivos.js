// Utilidades de archivos del navegador (sin HTTP).

/** Descarga un CSV con BOM (Excel) escapando celdas que empiezan como fórmula. */
export function descargarCsv(nombre, filas) {
  if (!filas.length) return
  const columnas = Object.keys(filas[0])
  const celda = (valor) => {
    let texto = valor == null ? '' : String(valor)
    if (/^[=+\-@\t\r]/.test(texto)) texto = `'${texto}`
    return `"${texto.replaceAll('"', '""')}"`
  }
  const contenido = [columnas.map(celda).join(','), ...filas.map((f) => columnas.map((c) => celda(f[c])).join(','))].join('\r\n')
  const enlace = document.createElement('a')
  enlace.href = URL.createObjectURL(new Blob(['﻿' + contenido], { type: 'text/csv;charset=utf-8' }))
  enlace.download = nombre
  document.body.appendChild(enlace)
  enlace.click()
  enlace.remove()
  setTimeout(() => URL.revokeObjectURL(enlace.href), 1000)
}

/** Lee un archivo del input como data URL (base64) para enviarlo a la API. */
export function leerArchivo(archivo) {
  return new Promise((resolve, reject) => {
    const lector = new FileReader()
    lector.onload = () => resolve(lector.result)
    lector.onerror = () => reject(new Error('No se pudo leer el archivo.'))
    lector.readAsDataURL(archivo)
  })
}
