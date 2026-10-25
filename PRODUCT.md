# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Vendedores** (asesores comerciales): trabajan desde el celular, entre llamadas y mensajes de WhatsApp. Abren su
  cartera, mueven tarjetas del embudo, registran lo que pasó en cada contacto, agendan el próximo y cobran.
- **Coordinación**: en escritorio. Reparte prospectos (manual o Round-Robin), valida comprobantes de pago, sigue a cada
  vendedor y revisa reportes de los programas a su cargo.
- **Administración**: ocasional. Usuarios, vigencia de credenciales, matriz de acceso y bitácora de auditoría.
- **Prospectos** (público): personas interesadas en un programa o módulo; llegan al catálogo desde el celular por redes
  sociales y dejan sus datos.
- **El docente de la materia** evalúa el sistema en vivo, proyectado, con cuentas de cada rol.

## Product Purpose

CRM comercial para una institución educativa que vende programas de formación (programas de 5–6 módulos y módulos
sueltos). Capta prospectos desde un catálogo público, los reparte entre vendedores, los lleva por un embudo Kanban
(Nuevo → En Contacto → Seguimiento → Promesa de Pago → Convertido / Perdido), cobra con pago único o plan de cuotas y
envía los alumnos matriculados al sistema académico (SIS) del Grupo 06. Éxito: más prospectos convertidos en matrícula,
ninguno olvidado, y la coordinación sabiendo en todo momento qué pasa con cada uno y por qué se pierden.

## Positioning

El embudo es la unidad de trabajo: cada interés de un prospecto por un módulo es una tarjeta con su historial completo
(movimientos, contactos, recordatorios, pagos). Perder exige un motivo clasificado; convertir exige datos completos y la
primera cuota aprobada. La matrícula sale del CRM ya validada hacia el sistema académico.

## Operating Context

- Proyecto 2 de INF513 Tecnología Web (UAGRM, FICCT), Grupo 05 SA. Arquitectura de 3 capas: React (cliente) + Laravel
  API REST + PostgreSQL compartido con el P1 (sistema vía correo sobre la misma base).
- Despliegue en `https://www.tecnoweb.org.bo/inf513/grupo05sa/proyecto2` (Apache + PHP de la facultad, sin SSH, sin
  depender de CDNs en tiempo de ejecución).
- Una clienta real (la institución) validó el flujo comercial en noviembre de 2026.
- Bolivia: moneda Bs, hora America/La_Paz, español.

## Capabilities and Constraints

- Roles: administrador, coordinador, vendedor. Menú dinámico leído de la BD según la matriz rol × recurso
  (lectura / modificación / eliminación). Vendedor: solo su cartera. Coordinador: solo sus programas.
- Exigencias del enunciado que la interfaz debe mostrar: barra de navegación según permisos; **3 temas por público
  (niños, jóvenes, adultos) que cambian el carácter completo** (tipografía, radios, densidad, acento secundario,
  ilustración e íconos), combinados con **día/noche automático según la hora del cliente** y manual; **accesibilidad**:
  tamaño de letra (deslizador o botones) y alto contraste (WCAG); **búsqueda global en el encabezado** de la página
  principal; **contador de visitas en el pie de cada página**; dashboard con estadísticas del negocio y de accesos;
  validación en español en cliente y servidor.
- Estilo único en CSS propio, en archivos aparte (regla del docente). React con `@inertiajs/react`, Vite, Chart.js,
  `lucide-react`.
- Pagos simulados: tarjeta (solo marca, últimos 4 y vencimiento), QR y transferencia; pasarela simulada.

## Brand Commitments

- Nombre: **UNEXO** (el logo es una U con un nodo y debajo "NEXO"; se lee UNEXO). Descriptor: "CRM Comercial Educativo".
- Logo: `backend/resources/assets/UNEXO.png`. Colores del logo, obligatorios: navy `#083456` (U y "NE") y teal
  `#10aeb5` (nodo y "XO").

## Evidence on Hand

- Catálogo simulado: 5 programas y 25 módulos con ilustraciones SVG en `backend/public/catalogo-demo/` (placeholder
  hasta la API real del Grupo 06).
- Datos de demostración ficticios (seeder). No hay testimonios, cifras de ventas reales ni fotos de alumnos: no inventarlos.

## Product Principles

1. La tarjeta del prospecto es el centro: todo (contacto, agenda, pago, pérdida, matrícula) se hace desde ella o la lleva a ella.
2. Celular primero para el vendedor; escritorio denso para coordinación. Una misma pantalla debe servir a ambos.
3. Nada se pierde en silencio: cada movimiento deja rastro con quién, cuándo y por qué.
4. Lo que el docente revisa tiene que verse: menú por rol, temas, accesibilidad, contador, búsqueda, bitácora.

## Accessibility & Inclusion

WCAG 2.1 AA como base y modo de alto contraste; tamaño de letra ajustable por el usuario; foco visible y navegación por
teclado (incluido mover tarjetas del Kanban sin arrastrar); `prefers-reduced-motion` respetado; textos en español.
