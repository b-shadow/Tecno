---
name: UNEXO
description: Malla de la oferta para el catálogo público y el login; prospecto de admisión sobrio para el panel CRM de UNEXO.
colors:
  navy: "#083456"
  navy-700: "#0b4268"
  navy-950: "#041d31"
  turquesa: "#10aeb5"
  turquesa-700: "#0a7c82"
  turquesa-100: "#dcf4f4"
  papel: "#ffffff"
  niebla: "#e9eef2"
  niebla-2: "#f4f7f9"
  tinta: "#1d2733"
  tinta-suave: "#4e5d6b"
  filete: "#cfd9e0"
  filete-fuerte: "#9fb1bf"
  portada-suave: "#c7d6e3"
  exito: "#1d7547"
  exito-suave: "#e1f3e8"
  aviso: "#94540a"
  aviso-suave: "#fcefd9"
  peligro: "#b42318"
  peligro-suave: "#fde8e6"
  etapa-nuevo: "#52677a"
  etapa-contacto: "#0a7c82"
  etapa-seguimiento: "#2f5d9c"
  etapa-promesa: "#94540a"
  etapa-convertido: "#1d7547"
  etapa-perdido: "#b42318"
  programa-1: "#083456"
  programa-2: "#0a7c82"
  programa-3: "#2f5d9c"
  programa-4: "#43407f"
  programa-5: "#2d5f5a"
  acento-2-jovenes: "#ff6b57"
  acento-2-jovenes-texto: "#c33a28"
  acento-2-ninos: "#ffb703"
  acento-2-ninos-texto: "#8a5a00"
  noche-papel: "#0b1f33"
  noche-niebla: "#102a42"
  noche-tinta: "#e6eef4"
  noche-portada: "#0f3a5f"
  noche-acento: "#2ccfd5"
  noche-acento-texto: "#5fe0e4"
typography:
  display-publico:
    fontFamily: "'Public Sans Variable', 'Public Sans', 'Segoe UI', system-ui, sans-serif"
    fontSize: "clamp(2.25rem, 1.5rem + 2.4vw, 3.5rem)"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.03em"
  headline-publico:
    fontFamily: "'Public Sans Variable', 'Public Sans', 'Segoe UI', system-ui, sans-serif"
    fontSize: "clamp(1.9rem, 1.4rem + 1.6vw, 2.6rem)"
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "'Source Serif 4 Variable', 'Source Serif 4', Georgia, serif"
    fontSize: "2.375rem"
    fontWeight: 650
    lineHeight: 1.12
    letterSpacing: "-0.015em"
    fontVariation: "'opsz' 60"
  title:
    fontFamily: "'Source Serif 4 Variable', 'Source Serif 4', Georgia, serif"
    fontSize: "1.75rem"
    fontWeight: 650
    lineHeight: 1.12
    letterSpacing: "-0.015em"
  codigo:
    fontFamily: "'Public Sans Variable', 'Public Sans', 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 800
    letterSpacing: "0.06em"
    fontFeature: "'tnum'"
  body:
    fontFamily: "'Public Sans Variable', 'Public Sans', 'Segoe UI', system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
    fontFeature: "'lnum'"
  label:
    fontFamily: "'Public Sans Variable', 'Public Sans', 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 650
    lineHeight: 1.2
rounded:
  radio: "4px"
  radio-grande: "6px"
  radio-jovenes: "10px"
  radio-grande-jovenes: "16px"
  radio-ninos: "16px"
  radio-grande-ninos: "24px"
  pastilla: "999px"
spacing:
  e-1: "4px"
  e-2: "8px"
  e-3: "12px"
  e-4: "16px"
  e-5: "24px"
  e-6: "32px"
  e-7: "48px"
  e-8: "64px"
components:
  button-primary:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.papel}"
    typography: "{typography.label}"
    rounded: "{rounded.radio}"
    padding: "8px 16px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "{colors.navy-700}"
  button-accent:
    backgroundColor: "{colors.turquesa}"
    textColor: "{colors.navy-950}"
    typography: "{typography.label}"
    rounded: "{rounded.radio}"
    padding: "8px 16px"
    height: "40px"
  button-secondary:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.tinta}"
    typography: "{typography.label}"
    rounded: "{rounded.radio}"
    padding: "8px 16px"
    height: "40px"
  button-large:
    padding: "12px 22px"
    height: "52px"
  input:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.radio}"
    padding: "9px 12px"
    height: "42px"
  status-tag:
    backgroundColor: "{colors.papel}"
    rounded: "{rounded.pastilla}"
    padding: "2px 10px"
  ficha-portada:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.papel}"
    typography: "{typography.headline}"
  riel:
    backgroundColor: "{colors.navy-950}"
    width: "264px"
  riel-item-active:
    backgroundColor: "{colors.turquesa}"
    textColor: "{colors.navy-950}"
    rounded: "{rounded.radio}"
    padding: "10px 12px"
  kanban-column:
    backgroundColor: "{colors.niebla}"
    rounded: "{rounded.radio-grande}"
    width: "272px"
  kanban-card:
    backgroundColor: "{colors.papel}"
    rounded: "{rounded.radio}"
    padding: "12px"
  area-filter:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.tinta}"
    typography: "{typography.label}"
    rounded: "{rounded.pastilla}"
    padding: "8px 16px"
    height: "40px"
  area-filter-active:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.papel}"
  malla-hoja:
    backgroundColor: "{colors.papel}"
    rounded: "{rounded.radio-grande}"
  malla-programa:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.navy}"
    rounded: "{rounded.radio}"
    padding: "10px 12px"
    width: "280px"
    height: "92px"
  malla-casilla:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.tinta}"
    typography: "{typography.codigo}"
    rounded: "{rounded.radio}"
    padding: "10px 12px"
    height: "92px"
  malla-casilla-elegida:
    backgroundColor: "{colors.programa-1}"
    textColor: "{colors.papel}"
  barra-eleccion:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.papel}"
    padding: "12px 40px"
  login-logo:
    width: "176px"
---

# Design System: UNEXO

## Overview

**Creative North Star: "Malla de la oferta / Prospecto de admisión"**

El sitio tiene dos superficies con mundos distintos sobre los mismos tokens. **El catálogo público y el login** (`/anuncios`, `/login`, y la misma malla dentro del panel en `/gestion-anuncios`) viven en la **Malla de la oferta**: toda la oferta en una malla curricular. Cada programa es una fila; sus módulos son casillas codificadas (DAT-1, CIB-3) unidas por líneas de correlatividad en orden de cursado, agrupadas por área y filtradas con píldoras. Elegir un programa abre su fila en el lugar y muestra la descripción de cada módulo; elegir una casilla la rellena con el color del área. Una barra navy al pie resume la elección con su precio y lleva al formulario corto con el botón turquesa "Me interesa". El login es solo el logo completo de UNEXO sobre el formulario.

**El panel interno** (riel, Kanban, ficha, tablas, agenda) sigue en el **Prospecto de admisión** en versión sobria: el prospecto impreso que una institución entrega en admisiones, con columnas del Kanban con pestaña de color por etapa y la ficha del prospecto como capítulo con portada navy e historial convertido en índice numerado.

Las dos superficies comparten papel blanco y gris azulado muy claro, el navy como tinta y tapa, y el turquesa como relleno y filete, nunca letra sobre claro. Ninguna usa sombras decorativas. La densidad del panel es de documento (filetes de 1px, cifras tabulares en lugar de íconos); la del catálogo es de malla (bordes de 2px del color del área, columnas iguales, códigos cortos).

El mundo tiene cuatro ejes que se aplican como atributos de `<html>` y cambian tokens, no componentes: `data-theme` (día/noche, automático por el reloj del cliente entre 07:00 y 19:00, con elección manual), `data-audiencia` (adultos, jóvenes, niños: tipografía, radios, densidad y acento secundario completos), `data-letra` (-1 a 3, escala de letra) y `data-contraste="alto"` (paleta AAA y Atkinson Hyperlegible). Todo valor visual pasa por variables, así que cualquier pantalla nueva hereda los cuatro ejes sin código propio.

Las imágenes de programas y módulos de la malla, del formulario de interés y sus miniaturas en celular son **contenido externo**: llegan del campo `imagen` de la API del catálogo del sistema académico (hoy rellenos de demostración del Grupo 06), no son assets del build. Son decorativas (`alt=""`, el nombre va al lado) y se ocultan si no cargan. Los únicos rasters propios son los logos (`resources/assets/unexo-logo.png` y su variante `unexo-logo-noche.png`).

**Key Characteristics:**
- Dos superficies: Malla de la oferta (catálogo público y login) y Prospecto de admisión sobrio (panel).
- Malla = tabla programa × Módulo 1..N, columnas iguales, casillas con borde de 2px del color del área unidas por líneas de correlatividad.
- Color de área estable por hash entre 4 tonos, siempre acompañado del nombre del área.
- Títulos públicos de adultos en Public Sans 800; el panel conserva la serif de títulos.
- Filetes de 1px y superficies planas en el panel; la sombra solo en capas flotantes y tarjetas arrastrables.
- Cuatro ejes de tema en `<html>`; ningún componente fija un color o una fuente fuera de las variables.

## Colors

Paleta de marca de dos colores (navy y turquesa del logo UNEXO) sobre neutros gris azulados, con familias de color funcionales para estados, etapas y áreas.

### Primary
- **Navy UNEXO** (navy): tinta de marca, título "Malla de la oferta" y nombres de programa, barra de elección del catálogo, píldora de área activa, botón primario, portada de la ficha del panel (`--portada`), día de hoy del calendario. Su tono profundo (navy-950) es el riel lateral del panel y el texto sobre turquesa; navy-700 es el hover del primario y el color de enlace.

### Secondary
- **Turquesa UNEXO** (turquesa): relleno y filete. Botón "Me interesa" de la barra de elección (acento con texto navy-950), ítem activo del riel, selección de texto, marcas del calendario, anillo de foco de los campos (mezclado al 30–35%). Nunca como texto sobre papel.
- **Turquesa de lectura** (turquesa-700): la versión del turquesa que sí puede ser texto sobre claro (`--acento-texto`), los módulos incluidos de la cadena del formulario de interés y el color del foco (`--foco`).
- **Turquesa velo** (turquesa-100): fondo de fila o ítem seleccionado y de avisos informativos (`--acento-suave`).

### Tertiary
- **Acento secundario por audiencia** (`--acento-2`): turquesa en adultos, coral (acento-2-jovenes) en jóvenes y ámbar (acento-2-ninos) en niños. Sus variantes `-texto` colorean las cifras del historial y de las cuotas del panel.

### Neutral
- **Papel** (papel): superficie de la hoja de la malla, casillas, hojas, tablas y encabezado.
- **Niebla** (niebla): separadores, columnas del Kanban, pistas de barras, fondo de imagen mientras carga.
- **Niebla clara** (niebla-2): fondo del sitio público y del cuerpo del panel, cabeceras de tabla.
- **Tinta** (tinta) y **Tinta suave** (tinta-suave): texto principal y secundario (cabeceras "Módulo n", precio y horas de las casillas, descripciones).
- **Filete** (filete) y **Filete fuerte** (filete-fuerte): bordes de 1px; el fuerte para campos, botones secundarios, píldoras de área y la cadena de módulos no incluidos.
- **Gris de portada** (portada-suave): texto secundario sobre navy (barra de elección, portada de la ficha).

### Estados, etapas y áreas
- **Estados**: éxito, aviso y peligro, cada uno con su fondo `-suave`. Siempre acompañados de texto o ícono.
- **Etapas del embudo (RF3.2)**: Nuevo (etapa-nuevo), En contacto (etapa-contacto), Seguimiento (etapa-seguimiento), Promesa de pago (etapa-promesa), Convertido (etapa-convertido), Perdido (etapa-perdido). Pintan la pestaña de la columna, el título de columna y la etiqueta de estado.
- **Áreas** (programa-1 a programa-4; programa-5 queda definido sin uso): cada área toma uno de los cuatro tonos (navy, turquesa de lectura, azul, índigo) por hash de su nombre; si dos áreas chocan, la segunda toma el siguiente tono libre, así un área nueva no recolorea a las que ya tenían el suyo. El tono pinta el punto de la píldora de área, el filete de 2px bajo el nombre del área, el borde de 2px de las casillas, sus códigos, las líneas de correlatividad y el relleno de la casilla elegida (con texto blanco). Programa, casilla y fila abierta usan mezclas del tono sobre papel (6%, 8–9%, 16% en hover).

### Noche y alto contraste
En `data-theme="dark"` el papel pasa a noche-papel, la tinta a noche-tinta, la portada a noche-portada y el acento a noche-acento; el botón primario y la píldora de área activa se vuelven turquesa con texto oscuro, los títulos públicos pasan de navy a tinta, y etapas y áreas tienen versiones claras propias definidas en `tokens.css` (sobre ellas el texto de la casilla elegida es `--sobre-acento`). En `data-contraste="alto"` el papel es #ffffff y la tinta #000000 (o al revés de noche), los filetes son negros (o blancos), el foco es magenta #c4005a (amarillo #ffff00 de noche), la casilla elegida suma un contorno de 3px en tinta y la barra de elección un filete superior de 3px.

### Named Rules
**La Regla del Turquesa Mudo.** El turquesa #10aeb5 nunca es texto sobre fondo claro. Cuando el turquesa tiene que leerse, se usa `--acento-texto` (turquesa-700).

**La Regla de las Variables.** Ningún componente escribe un hex propio para algo que cambia con tema, audiencia o contraste; usa los tokens semánticos (`--papel`, `--tinta`, `--acento`, `--portada`, `--etapa-*`, `--programa-*`). El área llega a sus piezas como `--c` desde la clase `area-n` del grupo.

**La Regla del Color con Palabra.** Un estado, una etapa o un área nunca se comunica solo por color: la etiqueta lleva texto y punto, la columna lleva su nombre, el grupo de la malla lleva el nombre del área y su conteo.

**La Regla del Tono Estable.** El color de un área sale del hash de su nombre, no del orden de llegada. Agregar o quitar un área nunca cambia el color de las demás.

## Typography

**Display Font (panel):** Source Serif 4 Variable (con Georgia, serif), eje óptico `opsz` 60
**Display Font (público adultos):** Public Sans Variable a 800
**Body Font:** Public Sans Variable (con Segoe UI, system-ui, sans-serif)

**Character:** En el panel, serif editorial de prospecto para títulos y cifras con sans pública sobria para la interfaz. En el catálogo y el login de adultos, una sola familia: Public Sans muy pesada en navy para títulos, regular para el resto (`--fuente-titulo` pasa a `--fuente-ui` y `--titulo-peso` a 800 dentro de `.publico` y `.oferta`). Por audiencia, en ambas superficies: jóvenes cambia los títulos a Bricolage Grotesque Variable (peso 760); niños usa Fredoka Variable para títulos (peso 620) y Nunito Variable para interfaz, con escala 1.08; alto contraste cambia la interfaz a Atkinson Hyperlegible.

### Hierarchy
- **Display público** (display-publico): "Malla de la oferta", en navy.
- **Headline público** (headline-publico): nombre del programa o módulo en el formulario de interés.
- **Headline** (h1 del panel, 2.375rem): títulos de página y portada de la ficha.
- **Title** (h2, 1.75rem; h3 1.375rem; h4 1.125rem): títulos de hoja y ficha; el login usa 1.75rem a 800 en Public Sans.
- **Código** (codigo): códigos de casilla DAT-n en el color del área; en celular, la tira de códigos del programa plegado.
- **Body**: texto corrido, máximo 70ch en descripciones de página, 44ch en el conteo de la malla y 24ch en la descripción de una casilla.
- **Label**: botones, nombres de campo, píldoras de área. Las etiquetas pequeñas usan 0.75rem a 700–750; nombres de casilla 0.875rem a 700 y de programa 1rem a 800.
- **Cifras grandes**: precio de la barra de elección 1.75rem a 800 y total del formulario 2.375rem a 800, ambos tabulares; las cifras del historial (1.75rem, 700), cuotas y tablero de cifras del panel (`clamp(1.6rem, 1.1rem + 1vw, 2.375rem)`) usan la serif tabular.

La escala es fija en rem (0.75, 0.875, 1, 1.125, 1.375, 1.75, 2.375 y los títulos fluidos) y el `html` la multiplica por `--escala` y `--paso-letra` (0.9, 1.12, 1.25, 1.4), así que el tamaño de letra elegido mueve todo el sistema.

### Named Rules
**La Regla de la Cifra Tabular.** Todo número que se compara (precio, horas, contador, paso, cantidad por columna) va con `tabular-nums`; en el panel, los que identifican (paso, cuota) van además en la serif de títulos.

**La Regla del Título sin Sombrero.** Ningún título lleva un rótulo pequeño encima. La jerarquía la dan el tamaño, el peso y el filete. El código DAT-n de una casilla no es un rótulo: es el identificador del módulo y va dentro de la casilla, no encima de un título de sección.

## Layout

- **Catálogo público**: encabezado fijo de 68px (marca, buscador predictivo de hasta 560px al centro, tema, Apariencia e Iniciar sesión). Debajo, la cabecera de la oferta: título y conteo de programas y módulos a la izquierda, píldoras de área a la derecha ("Todas" primero, hasta el 64% del ancho). Luego la hoja de la malla con márgenes laterales `clamp(16px, 3vw, 40px)` y al pie la barra de elección, fija abajo al desplazar y empujada al fondo de la pantalla cuando la malla es corta.
- **Malla**: tabla con columna de programa de 280px (fija a la izquierda al desplazar hacia los lados) y columnas Módulo 1..N de ancho igual; separación de 16px entre columnas y 10px entre filas. Un grupo por área con su nombre y conteo sobre un filete de 2px del color del área. Las celdas de una fila tienen la misma altura (mínimo 92px). Con 6 a 10 módulos la malla tiene ancho mínimo (1340px a 2060px, +180px por columna) y se desplaza hacia los lados; con 3 a 5, entre 721px y 1240px, mínimo 1160px.
- **Celular (≤720px)**: la malla se pliega a bloques por programa, sin hoja alrededor. Cada programa plegado muestra nombre, precio y horas, la tira de códigos y una miniatura de 84px a la derecha; al tocarlo se despliega su cadena vertical de módulos, unida por una línea de 2px del color del área a 10px del borde izquierdo y sangrada 22px, cada casilla con miniatura de 72px. Las píldoras de área pasan a una sola fila con desplazamiento horizontal a sangre. La barra de elección vacía deja de ser fija y el botón "Me interesa" ocupa todo el ancho. A ≤380px la marca muestra solo el ícono.
- **Formulario de interés**: resumen 4fr / formulario 7fr, máximo 1200px, una columna por debajo de 961px.
- **Login**: centrado en la pantalla, columna de hasta 420px con el logo (132–176px de ancho) sobre la hoja del formulario.
- **Panel**: riel lateral navy de 264px (76px plegado) más contenido con padding `clamp(16px, 2.4vw, 32px)` y ancho máximo de 1440px. Por debajo de 961px el riel es un cajón deslizable de hasta 300px con velo.
- **Rejillas del panel**: 2 columnas iguales, 3fr/2fr, 2fr/1fr y 3 columnas, todas a una columna por debajo de 721px. La agenda es lista (280–360px) + ficha, apilada por debajo de 1101px.
- **Ritmo**: múltiplos de 4px (`--e-1` a `--e-8`) multiplicados por `--densidad` (1 en adultos y jóvenes, 1.2 en niños).
- **Kanban**: columnas de mínimo 272px en scroll horizontal con encaje, fundido en el borde derecho para avisar que hay más; en celular cada columna ocupa 86vw.

## Elevation & Depth

Plano por defecto: la profundidad la dan los filetes, el cambio entre papel y niebla, los bordes de color de la malla y las superficies navy (barra de elección, portada de la ficha). Hay solo dos sombras de elevación, ambas tintadas con navy-950. En la malla, el `box-shadow` de la columna de programa (`-16px 0 0` en papel) y el anillo blanco de 2px del punto de la píldora activa son máscaras y anillos, no elevación.

### Shadow Vocabulary
- **Sombra** (`box-shadow: 0 1px 2px rgb(4 29 49 / 0.06), 0 8px 24px -12px rgb(4 29 49 / 0.18)`): tarjetas del Kanban, que se arrastran.
- **Sombra de capa** (`box-shadow: 0 2px 6px rgb(4 29 49 / 0.08), 0 24px 48px -16px rgb(4 29 49 / 0.32)`): lo que flota sobre la página: menú y lista del buscador, panel de Apariencia, menú de perfil, notificaciones, modales y riel abierto en celular.

### Named Rules
**La Regla de la Hoja Plana.** Hojas, la malla y sus casillas, tablas, tablero de cifras, columnas y la barra de elección no llevan sombra. Una sombra significa "esto se mueve o flota".

## Shapes

Esquinas apenas suavizadas en adultos (radio 4px, radio-grande 6px), más redondas en jóvenes (10/16px) y en niños (16/24px). El radio pequeño va en controles, casillas, celdas de programa, tarjetas y filas; el grande en la hoja de la malla, hojas, tablas, columnas, menús, modales y la imagen del formulario de interés. Las imágenes dentro de una casilla van a 16:9 con el radio pequeño menos 1px. La pastilla (999px) se reserva para píldoras de área, etiquetas de estado, contadores, filtros de etapa, chip de perfil y barras.

Los bordes del panel son de 1px y sus acentos de forma son franjas superiores de 4px (columnas del Kanban), nunca laterales. La malla habla en 2px: borde de casilla y de celda de programa, filete bajo el nombre del área, líneas de correlatividad (16×2px entre casillas, a 46px del borde superior) y la cadena vertical en celular; la cadena del formulario de interés usa 2px discontinuo en los módulos no incluidos y 2px continuo en turquesa de lectura en los incluidos.

## Components

### Buttons
- **Forma:** radio de la audiencia, alto mínimo 40px (52px en el grande, 40×40 el de ícono), peso 650.
- **Primario:** navy con texto blanco; hover navy-700. De noche pasa a turquesa con texto oscuro.
- **Acento:** turquesa con texto navy-950; hover con brillo 1.06. En el catálogo es solo el "Me interesa" grande de la barra de elección.
- **Secundario:** papel, texto tinta, borde filete-fuerte; hover borde tinta-suave y fondo niebla clara.
- **Texto, peligro y peligro suave** completan la familia. Al presionar baja 1px; deshabilitado al 55% de opacidad. Transiciones de 160ms con `cubic-bezier(0.16, 1, 0.3, 1)`.

### Chips
- **Píldora de área:** pastilla de papel con borde filete-fuerte, texto tinta a 700 y punto de 10px del color del área ("Todas" sin punto). Hover con borde tinta-suave. Activa (`aria-pressed`): relleno navy, texto blanco y anillo blanco de 2px alrededor del punto; de noche, relleno turquesa con texto oscuro.
- **Etiqueta de estado:** pastilla de papel con borde y texto del color de la etapa o estado y un punto de 7px; texto 0.75rem a 700.
- **Filtros de etapa:** pastillas de papel con punto de 8px del color de la etapa y su cantidad tabular.

### Cards / Containers
- **Hoja:** papel, borde filete, radio grande, padding 24px, título con filete inferior. Nunca se anida otra hoja dentro.
- **Tablero de cifras:** una sola fila de valores separados por filetes verticales, sin tarjetas por cifra.
- **Tabla:** marco de radio grande, cabecera fija en niebla clara, filas con filete y hover en niebla clara; selección en turquesa velo.

### Inputs / Fields
- **Estilo:** papel, borde filete-fuerte, radio de la audiencia, alto 42px; nombre del campo arriba en 0.875rem a 650, ayuda y error en 0.75rem.
- **Foco:** borde turquesa-700 y anillo de 3px del acento al 35%. Foco de teclado general: contorno de 3px en `--foco` con separación de 2px.
- **Error:** borde peligro y mensaje en peligro a 600. El campo de contraseña lleva el botón de ícono para mostrarla dentro, a la derecha.

### Navigation
- **Riel del panel:** fondo navy-950, enlaces en #dbe7f0 a 550, agrupados con rótulos de grupo en #8fa9bd; hover blanco al 7%; activo con relleno turquesa y texto navy-950.
- **Encabezado:** papel con filete inferior; marca con el ícono del logo de 34px y "UNEXO" en Public Sans 800 con la segunda parte en turquesa de lectura.
- **Pestañas de página del panel:** subrayado de 3px en acento al seleccionar.
- **Pie:** contador de visitas en cifra tabular dentro de un recuadro de radio pequeño.

### Malla de la oferta (firma del catálogo)
Hoja de papel con filete y radio grande sobre el fondo niebla clara. Cabecera de columnas "Programa" y "Módulo 1..N" en 0.75rem a 700 tinta suave. Por área, una fila de grupo con el nombre a 800 y su conteo, sobre un filete de 2px del color del área.
- **Celda de programa:** botón con borde de 2px del área sobre papel mezclado al 9% (16% en hover); nombre a 800 en navy, precio total, horas y cantidad de módulos en 0.75rem. Plegada en celular muestra la tira de códigos (cada código con borde de 1px del área y radio de 3px).
- **Casilla de módulo:** botón con borde de 2px del área sobre papel; código DAT-n arriba (codigo, color del área), nombre a 700 y precio con duración. Hover: mezcla del área al 8%. Una línea de 2px del área une el programa con su Módulo 1 y cada casilla con la siguiente; la última casilla no lleva línea.
- **Fila abierta:** al elegir un programa su fila se abre en el lugar: la celda de programa muestra su imagen 16:9 y su descripción; cada casilla, su imagen 16:9 y su descripción (hasta 24ch), con fondo del área al 6%. Las imágenes son contenido externo de la API del catálogo. Todo lo que aparece entra con `abrir` (260ms, de -4px y opacidad 0).
- **Casilla elegida:** relleno del color del área con todo el texto en blanco (en noche, `--sobre-acento`); el programa elegido completo se rellena igual. En alto contraste suma un contorno de 3px en tinta.
- **Transiciones:** fondo, borde y color a 180ms con la curva del sistema.

### Barra de elección (firma del catálogo)
Franja navy de lado a lado al pie de la oferta, fija al desplazar. Sin elección, una línea de ayuda en gris de portada. Con elección: el nombre del programa o módulo a 800 (1.125rem), el precio a 800 (1.75rem) tabular y el botón de acento grande "Me interesa el programa" o "Me interesa este módulo", que lleva al formulario de interés. El formulario repite la elección: imagen externa, título headline-publico, la cadena de módulos con sus códigos (incluidos en turquesa de lectura con check) y el total sobre un filete de 2px navy.

### Login
El logo completo de UNEXO (`unexo-logo.png`; de noche `unexo-logo-noche.png`, alternado por `data-theme`) centrado sobre la hoja del formulario: título "Iniciar sesión" a 800, una línea de quién entra, correo, contraseña con botón para mostrarla, "Recordarme", ayuda de contraseña y el botón primario grande a todo el ancho. Sin portada ni ilustración.

### Columna del Kanban y ficha (firma del panel)
Cada columna es niebla con radio grande y una franja superior de 4px del color de la etapa; el título de columna va en Public Sans 750 del color de la etapa (oscurecido al 85% en día). Al arrastrar encima, la columna pasa a turquesa velo con contorno punteado de la etapa. La ficha del prospecto abre con una portada navy (título 2.375rem) y su historial es un índice numerado: pasos 01, 02… en serif 1.75rem del acento secundario de lectura, con tipo, texto y fecha.

## Do's and Don'ts

### Do:
- **Do** poner cada valor visual detrás de un token de `tokens.css` para que tema, audiencia, letra y contraste lo cambien;
  Tailwind lo lee desde `@theme inline` de `estilos/app.css` (`bg-papel`, `text-tinta-suave`, `rounded-hoja`, `font-titulo`…).
- **Do** usar `--acento-texto` (#0a7c82 de día) cuando el turquesa tenga que leerse como texto.
- **Do** mostrar la oferta como malla: un programa por fila, sus módulos como casillas de borde 2px del color del área en columnas Módulo 1..N iguales, unidas por líneas de correlatividad.
- **Do** asignar el color de área por hash de su nombre entre programa-1 y programa-4, y escribir siempre el nombre del área junto al color.
- **Do** dejar una sola acción principal en el catálogo: el botón turquesa "Me interesa" de la barra navy de elección.
- **Do** tratar las imágenes de programas y módulos como contenido externo de la API: `alt=""`, 16:9, y ocultarlas si no cargan.
- **Do** numerar con cifras tabulares lo que tiene orden o se compara y separar filas del panel con filetes de 1px.
- **Do** marcar etapas del panel con una franja superior de 4px de su color y su nombre escrito.
- **Do** reservar `--sombra` para lo arrastrable y `--sombra-capa` para lo que flota.
- **Do** respetar `prefers-reduced-motion`: las animaciones y transiciones bajan a 0.001ms.

### Don't:
- **Don't** usar turquesa #10aeb5 como texto sobre papel o niebla.
- **Don't** poner etiquetas pequeñas o rótulos encima de los títulos.
- **Don't** usar franjas laterales de color en filas, tarjetas o avisos (la línea de correlatividad en celular es una cadena entre casillas, no una franja de tarjeta).
- **Don't** anidar hojas o tarjetas dentro de otras hojas.
- **Don't** usar texto con degradado ni sombras decorativas en superficies que no se mueven.
- **Don't** volver al catálogo con pestañas por programa, una portada gigante de un solo programa o una grilla de tarjetas iguales con imagen y botón.
- **Don't** usar la serif de títulos en el catálogo ni en el login de adultos.
