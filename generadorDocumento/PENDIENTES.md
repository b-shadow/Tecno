# Pendientes del documento P2 y del código (25/11/2026)

`python documento_p2.py` genera sin incoherencias y lista al final los 59 `[PENDIENTE]` del documento.

## Hecho en este corte
- **Código en 3 capas estricto (P / N / D, como la Agenda 3C del docente):** `negocio/app/Negocio/N*.php` (antes
  Controller + Service fusionados, sin route-model binding), `datos/src/D*.php` (antes `*Repository`),
  `presentacion/src/paginas/P*.jsx`. `codigo.py` falla si vuelve un nombre MVC, si una N consulta la BD sin su D, si
  una D usa una N o si una página usa el cliente HTTP directo.
- **5.3.2:** una figura por área del CU (`cls-cuN-k.png`): página → api → N → D → tablas, cada «use» con los métodos.
- Pruebas: `scripts/verificar_p2.py` TODO OK; `verificar_navegadores.mjs` 321/321 en Chromium; `verificar_integridad.sql` OK.
- `scripts/qa_local.py` adaptado a las 3 carpetas; el seeder apuntaba a `App\Services\Conversion` (no existía): corregido.

## Falta en el documento
- **Cap. II:** los 19 temas de teoría y la bibliografía (cada tema ya tiene su evidencia en `contenido.EVIDENCIA`).
- **Cap. I y III:** antecedentes, planteamiento del problema y ubicación de UNEXO (datos reales de la clienta).
  Misión, visión, objetivo y organigrama son propuesta del grupo: confirmarlos y vaciar `contenido.POR_CONFIRMAR`.
- **Prioridad de los CU** (Alta/Media) en `contenido.PRIORIDAD`: decisión del grupo.
- **Diagramas en EA:** actores, CU (8 + general), paquetes (6 + general), colaboración (8), secuencia (8), despliegue.
  La colaboración y la secuencia deben usar las clases P/N/D reales (`codigo.cadena(cu)` ya da la cadena y los mensajes).
- **7.6:** capturas de pantalla (`scripts/capturas_p2.mjs`) y **11. Conclusión** (una por objetivo, tras las pruebas finales).

## Falta en textos y scripts (quedaron con nombres viejos)
- `REGLAS_DOCUMENTO_P2.md` §6b y §4 (5.3.1, 7.4) todavía describen Controller/Service/Repository: pasar a N / D.
- Comentarios de `navegacion.py` (cabecera, `SitioController@buscar`, `InteresService::listar`) → `NSitio`, `NInteres`.
- `../P2_WEB.md` §3 (estructura de carpetas) y los README de `negocio/` y `datos/` si mencionan Controllers/Services.
- Scripts de prueba desactualizados respecto de la API actual (fallan antes del refactor también):
  `verificar_correcciones.py` (usa `/intereses/{id}/tomar` y `id`), `verificar_auditoria.py` (`usuario['id']`),
  `verificar_seguridad.py` (campo `pagos`), `verificar_administradores.py`, `verificar_reenvio_comprobante.py`,
  `verificar_sesion.mjs` (importa de `backend/`). El seeder no crea `vendedor.b@test.local`, que esos scripts usan.
- Rutas de la API que ninguna pantalla llama (aviso del generador): `crearInteres`, `metodos`, `ordenes`, `historial`,
  `configuracionComision`, `DELETE /usuarios/{u}/foto`: usarlas en la interfaz o borrarlas.
