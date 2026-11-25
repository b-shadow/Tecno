# Pendientes del documento P2 y del código (25/11/2026)

El documento habitual `documento/P2-INF513-GRUPO05SA.docx` ya integra la teoría y bibliografía investigadas. Su contenido fuente reside en `contenido.py` y sale en cada generación con `documento_p2.py`. Los pendientes de otros capítulos se mantienen. La reconstrucción completa del Word reemplaza las ediciones manuales posteriores; conservar una copia antes de ejecutarla.

## Hecho en este corte
- **Código en 3 capas estricto (P / N / D, como la Agenda 3C del docente):** `negocio/app/Negocio/N*.php` (antes
  Controller + Service fusionados, sin route-model binding), `datos/src/D*.php` (antes `*Repository`),
  `presentacion/src/paginas/P*.jsx`. `codigo.py` falla si vuelve un nombre MVC, si una N consulta la BD sin su D, si
  una D usa una N o si una página usa el cliente HTTP directo.
- **5.3.2:** un diagrama por CU (`cls-cuN.png`, como G07): una columna por área (página → api → N → D → tablas), cada «use» con los métodos.
- Pruebas: `scripts/verificar_p2.py` TODO OK; `verificar_navegadores.mjs` 321/321 en Chromium; `verificar_integridad.sql` OK.
- `scripts/qa_local.py` adaptado a las 3 carpetas; el seeder apuntaba a `App\Services\Conversion` (no existía): corregido.

## Falta en el documento
- **Cap. II completado el 25/11/2026:** 19 apartados investigados, citas en texto y 20 referencias primarias en la bibliografía. Todo queda integrado en `contenido.py` y en el DOCX habitual.
- **Cap. I y III:** antecedentes, planteamiento del problema y ubicación física exacta de UNEXO (datos reales de la clienta). El capítulo III incorpora contexto del campus virtual UNEXO documentado en la web institucional, sin atribuirle una dirección no verificada.
  Misión, visión, objetivo y organigrama son propuesta del grupo: confirmarlos y vaciar `contenido.POR_CONFIRMAR`.
- **Prioridad de los CU** (Alta/Media) en `contenido.PRIORIDAD`: decisión del grupo.
- **Diagramas en EA (completados el 25/11/2026):** actores, CU (8 + general), paquetes (6 + general),
  comunicación (8), secuencia (8) y despliegue. `ea/ea_faltantes.py` los guarda en `ea/crm-p2.eapx` y exporta
  PNG + EMF; `insertar_diagramas.py` sustituyó los 34 marcadores del DOCX conservando las ediciones manuales.
  Las secuencias muestran llamadas reales P→N→D, retornos con los tipos declarados en PHP y fragmentos `opt`;
  `actualizar_secuencias.py` reemplaza solo esas ocho imágenes en el Word existente.
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
