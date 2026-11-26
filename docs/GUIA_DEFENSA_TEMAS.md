# Guía Práctica de Defensa — Temas Visuales UNEXO

Documento de referencia rápida para explicar y modificar en vivo los tres temas (**Niños**, **Jóvenes**, **Adultos**) en modo **Día / Noche**, accesibilidad y persistencia sin romper la arquitectura de 3 capas (P/N/D).

> **Cómo probar en vivo:** con `npm run dev` activo en `http://localhost:5173`, cualquier guardado en los `.css` o `.js/.jsx` se refleja al instante en el navegador gracias a Vite HMR.

---

## Mapa rápido de archivos (Capa de Presentación)

| Archivo | Qué controla |
| :--- | :--- |
| `presentacion/src/estilos/temas/niños.css` | Colores pastel, tipografía redondeada, radios grandes, sol, rayos, nubes, luna, estrellas y modo noche infantil. |
| `presentacion/src/estilos/temas/jovenes.css` | Colores violeta/cian/magenta, degradados, botones con gradiente y figuras geométricas (círculos, triángulo, rombo, líneas). |
| `presentacion/src/estilos/temas/adultos.css` | Identidad corporativa UNEXO (`#083456` / `#F4F7F9` de día y `#0B1F33` / `#2CCFD5` de noche). |
| `presentacion/src/estilos/tokens.css` | Escala global de tamaño de letra (`--paso-letra`), alto contraste prioritario (`data-contraste="alto"`) y ocultamiento de decoraciones en alto contraste. |
| `presentacion/src/estilos/app.css` | Importación de temas, `@theme inline` para Tailwind, base tipográfica y estilos compartidos (`.hoja`, `.btn`, `.cifras`, `.decoracion-tema`). |
| `presentacion/src/servicios/theme.js` | Horario automático de Bolivia (`UTC-4`), persistencia en `localStorage`, cambio en `<html>` (`dataset`) y `setInterval` cada minuto. |
| `presentacion/src/componentes/Shell.jsx` | Botón rápido Día/Noche (`BotonTema`) y panel `Apariencia` (público, modo, letra `A− / slider / A+ / Normal`, alto contraste). |
| `presentacion/src/paginas/PCatalogo.jsx` | Elemento `<DecoracionCatalogo />` con los `div`/`span` puros (sin imágenes ni SVG) para el catálogo público `/anuncios`. |
| `presentacion/src/main.jsx` | Carga local de las tipografías (`@fontsource-variable/*` y `@fontsource/atkinson-hyperlegible`). |

---

## 1. Cambiar el color del sol

- **Archivo exacto:** `presentacion/src/estilos/temas/niños.css`
- **Línea exacta:** **23** (variable) y **235** (uso en `.sol`; los `.rayo` heredan con `background-color: inherit`).
- **Código actual:**
```css
  --niños-sol: #ffd34d;
```
- **Código que debo modificar (ejemplo a naranja cálido):**
```css
  --niños-sol: #ff8c42;
```
- **Resultado visual esperado:** En `/anuncios` con tema **Niños · Día**, tanto el círculo central del sol como sus 4 rayos cambian inmediatamente a naranja cálido `#ff8c42`.

---

## 2. Cambiar el tamaño del sol

- **Archivo exacto:** `presentacion/src/estilos/temas/niños.css`
- **Línea exacta:** **228–238** (escritorio) y **358** (móvil `<= 720px`).
- **Código actual:**
```css
.sol {
  display: none;
  position: absolute;
  top: 12px;
  right: 30px;
  width: 68px;
  height: 68px;
  background-color: var(--niños-sol, #ffd34d);
  border-radius: 50%;
  box-shadow: 0 0 0 8px rgb(255 211 77 / 0.24);
}
```
- **Código que debo modificar (ejemplo sol más grande):**
```css
.sol {
  display: none;
  position: absolute;
  top: 12px;
  right: 30px;
  width: 96px;
  height: 96px;
  background-color: var(--niños-sol, #ffd34d);
  border-radius: 50%;
  box-shadow: 0 0 0 12px rgb(255 211 77 / 0.24);
}
```
- **Resultado visual esperado:** El sol pasa de `68×68 px` a `96×96 px` en el catálogo público **Niños · Día**. *(En pantalla móvil `< 720px`, ajustar también `width`/`height` de `.sol` en la línea **358**).*

---

## 3. Cambiar el color de las nubes

- **Archivo exacto:** `presentacion/src/estilos/temas/niños.css`
- **Línea exacta:** **24** (variable) y **263** (`.nube`; los bultos `::before` y `::after` heredan `background-color: inherit`).
- **Código actual:**
```css
  --niños-nube: #ffffff;
```
- **Código que debo modificar (ejemplo a azul celeste muy suave):**
```css
  --niños-nube: #e0f2fe;
```
- **Resultado visual esperado:** Todas las nubes flotantes en **Niños · Día** cambian de blanco puro a celeste suave manteniendo su forma redondeada.

---

## 4. Cambiar el color de la luna

- **Archivo exacto:** `presentacion/src/estilos/temas/niños.css`
- **Línea exacta:** **25** (variable) y **325** (`.luna` usa `currentColor` en `box-shadow: -14px 8px 0 0 currentColor` para formar la media luna).
- **Código actual:**
```css
  --niños-luna: #fde68a;
```
- **Código que debo modificar (ejemplo a blanco plateado):**
```css
  --niños-luna: #e2e8f0;
```
- **Resultado visual esperado:** Al cambiar a **Niños · Noche**, la media luna de la esquina superior derecha cambia de amarillo pastel a blanco lunar plateado.

---

## 5. Cambiar el tamaño de las estrellas

- **Archivo exacto:** `presentacion/src/estilos/temas/niños.css`
- **Línea exacta:** **27** (tamaño base en `:root`), **333–334** (`.estrella` base) y **350–353** (variantes `.estrella-2` a `.estrella-5`).
- **Código actual:**
```css
  --niños-estrella-tamano: 14px;
```
- **Código que debo modificar:**
```css
  --niños-estrella-tamano: 24px;
```
  *(Nota: `.estrella-1` toma directamente `--niños-estrella-tamano`. Si desea agrandar también las estrellas secundarias `.estrella-2` a `.estrella-5`, modificar sus `width`/`height` en las líneas **350–353**).*
- **Resultado visual esperado:** En **Niños · Noche**, la estrella principal crece de `14 px` a `24 px` sin distorsionar su silueta de 8 puntas (formada por `.estrella` + `.estrella::after` rotada `45deg`).

---

## 6. Cambiar el fondo de Niños

- **Archivo exacto:** `presentacion/src/estilos/temas/niños.css`
- **Línea exacta:** **14** (Modo Día) y **107** (Modo Noche). Ambos alimentan `--niebla-2` (líneas **38** y **116**), que es el fondo aplicado al `body`.
- **Código actual (Día, línea 14):**
```css
  --color-fondo: #fff6e0;
```
- **Código actual (Noche, línea 107):**
```css
  --color-fondo: #172554;
```
- **Código que debo modificar (ejemplo Día a menta pastel muy claro):**
```css
  --color-fondo: #ecfdf5;
```
- **Resultado visual esperado:** Todo el lienzo general de UNEXO (catálogo, dashboard, listas, formularios) cambia de fondo crema cálido `#fff6e0` a menta pastel `#ecfdf5`.

---

## 7. Cambiar el color de los botones de Jóvenes

- **Archivo exacto:** `presentacion/src/estilos/temas/jovenes.css`
- **Línea exacta:**
  - Color base del tema: línea **12** (Día) y **102** (Noche).
  - Botón primario con degradado y color sólido de respaldo: líneas **182–186**.
- **Código actual (líneas 182–186):**
```css
:root[data-audiencia='jovenes'] .btn-primario {
  background-color: #6d28d9;
  background-image: var(--jovenes-gradiente-btn);
  color: #ffffff;
}
```
- **Código que debo modificar (ejemplo a botón índigo/azul eléctrico):**
```css
:root[data-audiencia='jovenes'] .btn-primario {
  background-color: #0284c7;
  background-image: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
  color: #ffffff;
}
```
- **Resultado visual esperado:** Todos los botones `.btn-primario` del tema Jóvenes (`Iniciar sesión`, `Enviar interés`, acciones principales) cambian al instante manteniendo texto blanco legible.

---

## 8. Cambiar un degradado de Jóvenes

- **Archivo exacto:** `presentacion/src/estilos/temas/jovenes.css`
- **Línea exacta:**
  - **23–25** (Modo Día): `--jovenes-gradiente-fondo`, `--jovenes-gradiente-btn`, `--jovenes-gradiente-acento`.
  - **108–110** (Modo Noche): mismas 3 variables en versión oscura.
- **Código actual (Día, líneas 23–25):**
```css
  --jovenes-gradiente-fondo: linear-gradient(135deg, #f1edff 0%, #ebe5ff 55%, #fce7f3 100%);
  --jovenes-gradiente-btn: linear-gradient(135deg, #7c3aed 0%, #5427a5 100%);
  --jovenes-gradiente-acento: linear-gradient(135deg, #7c3aed 0%, #db2777 100%);
```
- **Código que debo modificar (ejemplo degradado de fondo hacia cian-lavanda):**
```css
  --jovenes-gradiente-fondo: linear-gradient(135deg, #ede9fe 0%, #e0f2fe 55%, #fce7f3 100%);
```
- **Resultado visual esperado:** El fondo diagonal de toda la aplicación en **Jóvenes · Día** pasa a mezclar violeta, celeste tecnológico y rosa sutil.

---

## 9. Cambiar el azul corporativo de Adultos

- **Archivo exacto:** `presentacion/src/estilos/temas/adultos.css`
- **Línea exacta:**
  - Modo Día: línea **10** (`--color-primario: #083456;`), heredada por `--navy` en la línea **16**.
  - Modo Noche: líneas **65–66** (`--color-superficie: #0b1f33;` y `--color-fondo: #0d2439;`).
- **Código actual (Día, línea 10):**
```css
  --color-primario: #083456;
```
- **Código que debo modificar (ejemplo azul acero más claro):**
```css
  --color-primario: #1e40af;
```
- **Resultado visual esperado:** En el tema **Adultos**, encabezados, botones primarios, barra inferior del catálogo y enlace principal toman el nuevo azul corporativo manteniendo sobriedad profesional.

---

## 10. Cambiar la tipografía de cada tema

Las fuentes vienen cargadas localmente desde npm en `presentacion/src/main.jsx` (líneas **1–7**), así que no dependen de Internet en la defensa:

```javascript
import '@fontsource-variable/source-serif-4/opsz.css'
import '@fontsource-variable/public-sans/wght.css'
import '@fontsource-variable/bricolage-grotesque/wght.css'
import '@fontsource-variable/fredoka/wght.css'
import '@fontsource-variable/nunito/wght.css'
import '@fontsource/atkinson-hyperlegible/400.css'
import '@fontsource/atkinson-hyperlegible/700.css'
```

Para cambiar la fuente de cada tema (ya cargada en `main.jsx`):

- **Niños** — `presentacion/src/estilos/temas/niños.css`, líneas **89–90**:
  - Actual: `--fuente-titulo: 'Fredoka Variable', 'Fredoka', 'Nunito Variable', sans-serif;` y `--fuente-ui: 'Nunito Variable', 'Nunito', 'Segoe UI', sans-serif;`
  - Ejemplo cambio rápido: sustituir `'Fredoka Variable'` por `'Source Serif 4 Variable'` o `'Public Sans Variable'`.
- **Jóvenes** — `presentacion/src/estilos/temas/jovenes.css`, líneas **86–87**:
  - Actual: `--fuente-titulo: 'Bricolage Grotesque Variable', 'Bricolage Grotesque', 'Public Sans Variable', sans-serif;` y `--fuente-ui: 'Public Sans Variable', 'Public Sans', system-ui, sans-serif;`
- **Adultos** — `presentacion/src/estilos/temas/adultos.css`, líneas **52–53** (y línea **126** para `[data-zona='oferta']`):
  - Actual: `--fuente-titulo: 'Source Serif 4 Variable', 'Source Serif 4', Georgia, serif;` y `--fuente-ui: 'Public Sans Variable', 'Public Sans', 'Segoe UI', system-ui, sans-serif;` *(En el catálogo público Adultos, la línea **126** fija `--fuente-titulo: var(--fuente-ui);` para mantener el diseño original de UNEXO).*

- **Resultado visual esperado:** Los títulos (`h1`–`h4`) y la interfaz general (`body`) cambian inmediatamente de familia tipográfica sin alterar el resto de temas.

---

## 11. Cambiar el tamaño de las letras

- **Archivo exacto:**
  - Escala CSS global: `presentacion/src/estilos/tokens.css`, líneas **121–125**.
  - Aplicación en raíz `html`: `presentacion/src/estilos/app.css`, línea **116**.
  - Controles en pantalla: `presentacion/src/componentes/Shell.jsx`, líneas **141–147**.
- **Código actual (`tokens.css` líneas 121–125):**
```css
:root[data-letra='-1'] { --paso-letra: 0.9; }
:root[data-letra='0']  { --paso-letra: 1; }
:root[data-letra='1']  { --paso-letra: 1.12; }
:root[data-letra='2']  { --paso-letra: 1.25; }
:root[data-letra='3']  { --paso-letra: 1.4; }
```
- **Código que debo modificar (ejemplo hacer el nivel máximo `3` igual a `150%`):**
```css
:root[data-letra='3']  { --paso-letra: 1.5; }
```
- **Resultado visual esperado:** Como `app.css` línea **116** define `html { font-size: calc(100% * var(--escala) * var(--paso-letra, 1)); }` y las utilidades usan `rem`, toda la tipografía de la interfaz escala de manera proporcional. El usuario puede subir (`A+`), bajar (`A−`), deslizar o volver con `Normal` en el botón de paleta.

---

## 12. Cambiar los bordes de las tarjetas

Hay dos niveles: el **radio de redondeo** por tema (`--radio`, `--radio-grande`) y el **grosor/color de borde** compartido.

- **Radios por tema:**
  - **Niños** (`presentacion/src/estilos/temas/niños.css`, líneas **92–93**): `--radio: 18px;` y `--radio-grande: 26px;` (más `border-width: 2px;` en `.hoja, .tabla-marco, .cifras` en líneas **169–175**).
  - **Jóvenes** (`presentacion/src/estilos/temas/jovenes.css`, líneas **89–90**): `--radio: 12px;` y `--radio-grande: 18px;`.
  - **Adultos** (`presentacion/src/estilos/temas/adultos.css`, líneas **55–56**): `--radio: 4px;` y `--radio-grande: 6px;`.
- **Tarjetas base compartidas:** `presentacion/src/estilos/app.css`, línea **201**:
```css
  .hoja { @apply rounded-hoja border border-filete bg-papel; }
```
- **Código que debo modificar (ejemplo tarjetas mucho más cuadradas en Jóvenes, líneas 89–90 de `jovenes.css`):**
```css
  --radio: 6px;
  --radio-grande: 8px;
```
- **Resultado visual esperado:** Cambia al instante el redondeo de tarjetas `.hoja`, tablas `.tabla-marco`, barras de métricas `.cifras`, botones y cajas de formulario únicamente en ese tema.

---

## 13. Cambiar los horarios automáticos

- **Archivo exacto:** `presentacion/src/servicios/theme.js`
- **Línea exacta:** **8–9** (umbrales) y **33–46** (cálculo con zona horaria de Bolivia). *(El texto descriptivo visible al usuario está en `presentacion/src/componentes/Shell.jsx`, línea **138**).*
- **Código actual (`theme.js`, líneas 8–9):**
```javascript
export const DIA_DESDE = 7
export const NOCHE_DESDE = 19
```
- **Código que debo modificar (ejemplo para demostrar en vivo cambio inmediato a Noche si son las 18:00 o similar):**
```javascript
export const DIA_DESDE = 6
export const NOCHE_DESDE = 18
```
- **Resultado visual esperado:** Si el modo está en **"Según la hora"** y la hora actual en `America/La_Paz` (`UTC-4`) cae fuera del nuevo rango `[DIA_DESDE, NOCHE_DESDE)`, UNEXO cambia automáticamente entre modo Día (`light`) y modo Noche (`dark`) al guardar o en el siguiente ciclo del temporizador.

---

## 14. Explicar cómo funciona el selector de temas

- **Archivo exacto:** `presentacion/src/componentes/Shell.jsx`
- **Línea exacta:** **97–106** (`BotonTema` rápido) y **109–154** (`Apariencia` completo).
- **Flujo concreto:**
  1. En el encabezado (`AppShell.jsx`), se muestran el botón de luna/sol (`BotonTema`) y el botón con ícono de paleta (`Apariencia`).
  2. `Apariencia` lee el estado global con `useApariencia()` (línea **110**, basado en `useSyncExternalStore` de `theme.js` líneas **77–82**).
  3. El helper `seg(campo, valor, texto)` (líneas **120–122**) renderiza los botones segmentados de público (`niños`, `jovenes`, `adultos`) y modo (`auto`, `light`, `dark`).
  4. Al hacer clic en cualquier opción, ejecuta `cambiar({ [campo]: valor })`, lo que actualiza la preferencia en memoria, la guarda en `localStorage`, reescribe los atributos de `<html>` y notifica a los componentes suscritos sin desmontar React ni recargar la página.

---

## 15. Explicar cómo se guardan las preferencias

- **Archivo exacto:** `presentacion/src/servicios/theme.js`
- **Línea exacta:** **7** (`CLAVE`), **17–18** (carga inicial), **21–30** (`leer`) y **66–75** (`cambiar`).
- **Flujo concreto:**
  1. Todo se guarda en un solo objeto JSON bajo `localStorage` con la clave `'crm_apariencia'` (por defecto `{ modo: 'auto', audiencia: 'adultos', letra: 0, contraste: 'normal' }`).
  2. Al arrancar la app (`theme.js` línea **18** y **85**), `leer()` recupera la preferencia antes del render de React (con compatibilidad por si existía la clave antigua `'crm_theme'`).
  3. Al llamar `cambiar(...)`, se fusionan los cambios, se escribe en `localStorage.setItem(CLAVE, JSON.stringify(preferencias))` y se vuelve a aplicar en `<html>`.
  4. Por eso las preferencias sobreviven al cambiar entre rutas públicas (`/anuncios`), iniciar sesión, navegar en el panel interno, recargar con `F5` y cerrar sesión.

---

## 16. Explicar cómo funciona el modo automático

- **Archivo exacto:** `presentacion/src/servicios/theme.js`
- **Línea exacta:** **33–46** (`horaEnBolivia` y `temaPorHora`), **48–50** (`temaEfectivo`) y **85–91** (`setInterval`).
- **Flujo concreto:**
  1. `horaEnBolivia()` (líneas **33–40**) utiliza `Intl.DateTimeFormat('en-US', { timeZone: 'America/La_Paz', hour: 'numeric', hourCycle: 'h23' })`, por lo que siempre evalúa la hora oficial de Bolivia (`UTC-4`) aunque el navegador del cliente esté en otra zona horaria.
  2. `temaPorHora()` devuelve `'light'` si `hora >= DIA_DESDE && hora < NOCHE_DESDE` (de `07:00` a `18:59`), y `'dark'` desde las `19:00` hasta las `06:59`.
  3. `temaEfectivo()` consulta `temaPorHora()` únicamente cuando `preferencias.modo === 'auto'`; si el usuario eligió `'light'` o `'dark'` manualmente, respeta esa elección.
  4. Al pie del módulo (líneas **86–91**), un `setInterval` cada `60_000` ms (`1 minuto`) vuelve a llamar `aplicar()` y notifica a los oyentes si está activo el modo automático, permitiendo transición en vivo al llegar las 07:00 o las 19:00 sin recargar.

---

## 17. Explicar cómo funciona el alto contraste

- **Archivos exactos:**
  - Control UI: `presentacion/src/componentes/Shell.jsx`, línea **149**.
  - Atributo en `<html>`: `presentacion/src/servicios/theme.js`, líneas **59–60**.
  - Reglas CSS prioritarias: `presentacion/src/estilos/tokens.css`, líneas **128–222** (`html:root[data-contraste='alto']`).
- **Flujo concreto:**
  1. Al marcar la casilla **Alto contraste**, se llama `cambiar({ contraste: 'alto' })` y `theme.js` coloca `data-contraste="alto"` en `<html>`.
  2. En CSS, el selector `html:root[data-contraste='alto']` tiene **mayor especificidad** que `:root[data-audiencia='niños']`, `:root[data-audiencia='jovenes']` o `:root[data-audiencia='adultos']`.
  3. Gracias a esa mayor especificidad y a la variante `@custom-variant contraste` en `app.css` línea **17**, se sobrescriben todas las variables de colores a pares de altísimo contraste (`#ffffff` / `#000000`, azul enlace `#00338d` o cian `#72f2eb` en noche, bordes marcados), se apagan sombras y degradados (`líneas 217–222`) y se ocultan las decoraciones temáticas `.decoracion-tema { display: none !important; }` (líneas **214–216**) para garantizar legibilidad sin distracciones.

---

## 18. Explicar cómo React aplica las clases y atributos utilizados por CSS

- **Archivos exactos:**
  - `presentacion/src/servicios/theme.js`, líneas **52–64** (`aplicar()`).
  - `presentacion/src/estilos/app.css`, líneas **16–91** (`@custom-variant` y `@theme inline`).
  - `presentacion/src/componentes/Shell.jsx` y `presentacion/src/plantilla/AppShell.jsx` (`bg-header-bg`, `bg-riel`, `text-riel-tinta`, `bg-footer-bg`).
- **Flujo concreto:**
  1. React **no inyecta estilos inline** ni vuelve a montar componentes al cambiar de tema: delega la aplicación visual a atributos HTML en la etiqueta raíz (`document.documentElement`) dentro de `aplicar()` (`theme.js` líneas **56–60**):
     - `data-audiencia="niños" | "jovenes" | "adultos"`
     - `data-theme="light" | "dark"`
     - `data-letra="-1" | "0" | "1" | "2" | "3"`
     - `data-contraste="alto"` (presente solo cuando está activado)
  2. Cada hoja temática (`niños.css`, `jovenes.css`, `adultos.css`) redefine variables semánticas (`--color-primario`, `--color-fondo`, `--color-superficie`, `--navy`, `--papel`, `--fuente-titulo`, `--radio`, `--header-bg`, `--riel`, etc.) para esos selectores de atributo.
  3. En `app.css`, el bloque `@theme inline` (líneas **22–91**) conecta las utilidades de Tailwind CSS v4 (`bg-papel`, `bg-niebla-2`, `text-tinta`, `bg-navy`, `rounded-hoja`, `font-titulo`, `bg-header-bg`, `bg-riel`, etc.) directamente con esas variables CSS vivas (`--color-papel: var(--papel);`).
  4. Por eso todos los componentes React (`Dashboard`, `PCatalogo`, `Embudo`, `Pagos`, `Shell`) cambian de colores, fuentes, bordes, cabecera y menú lateral instantáneamente usando las **mismas clases**, sin duplicar pantallas ni provocar errores de hooks (`useState`) al alternar temas.
