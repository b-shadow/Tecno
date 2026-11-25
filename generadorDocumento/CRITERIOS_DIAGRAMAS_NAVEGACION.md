# Criterios de diseño de los diagramas de navegación

Guía para la sección 7.5 del P2. El docente y Conallen fijan la notación y el sentido de las relaciones. El G07 sirve de referencia para distribuir los flujos y continuarlos entre páginas. El diagrama del Administrador muestra cómo aplicamos esos criterios al CRM.

## Alcance y elementos

- Dibuja un diagrama por actor. Para los roles internos, parte de la autenticación, sigue con el menú y organiza los casos de uso según el recorrido y el orden de implementación. Para el Visitante, parte de las entradas públicas. Comprueba las pantallas y acciones contra la matriz de acceso y las condiciones de la interfaz.
- Representa cada pantalla o componente compartido una vez por actor. Conecta a esa misma caja los flujos que la usan. Comprueba los destinos contra el router y los parámetros reales.
- Una **página cliente** representa una pantalla o vista del frontend. Sus atributos reflejan el estado relevante y sus operaciones corresponden a funciones reales de la interfaz.
- Un **formulario** muestra los campos que captura para el envío. Las funciones JavaScript, como `guardar()`, pertenecen a la página que controla la interacción. En EA se mantiene la etiqueta visible `«Formulario»`.
- Una **página servidor**, identificada como `ps …`, representa el endpoint que procesa la solicitud. `ps Login` corresponde a `POST /api/login` y a `NAuth::login()`. Los atributos representan los datos que procesa el endpoint y la operación corresponde al método real. En el CRM, Laravel devuelve JSON y React actualiza o abre la vista.
- Una **tabla** se identifica como `BD: nombre_tabla`, con columnas reales y accesos que ejecuta el endpoint. Comprueba la cadena de llamadas hasta los métodos de datos. Si el diagrama muestra accesos representativos, conserva los nombres de las tablas efectivamente consultadas o escritas.
- Distingue las páginas externas, como Stripe Checkout, de las pantallas del CRM. Ubica los avisos donde realmente los muestra la interfaz.

## Relaciones, flechas y rombos

| Relación | Sentido y significado | Dibujo en el Administrador |
| --- | --- | --- |
| `«link»` | El actor entra a una página. Una página navega a otra, abre un diálogo o llama a un endpoint fuera del envío de un formulario. | Línea **discontinua** con flecha hacia el destino. Indica la ruta, los parámetros o la acción que origina el enlace. |
| `«submit»` | El formulario envía sus datos al endpoint que los procesa. | Línea **continua** con flecha del formulario a la página servidor. Conserva el método y la ruta reales en el modelo. |
| `«build»` | La respuesta del servidor permite mostrar una vista, actualizar su contenido o presentar un aviso. | Línea **continua** con flecha del servidor a la vista que consume la respuesta. Rotula el resultado cuando distingue una rama relevante. |
| `«access»` | Una página servidor consulta o escribe en una tabla real. | Línea **continua** con flecha hacia la tabla. Indica `SELECT`, `INSERT`, `UPDATE` o `DELETE` de acuerdo con el acceso. |
| Composición | Un formulario integrado forma parte de la pantalla que lo contiene. | Línea **continua** con rombo negro en el extremo de la pantalla. La flecha abierta hacia el formulario indica navegabilidad, como en la figura 5 de Conallen. |
| Agregación | El modelo declara una relación entre un todo y una parte compartida. | Línea **continua** con rombo vacío del lado del todo. Comprueba que la relación estructural esté justificada. |
| `«include»` | Una página servidor llama a una parte compartida del servidor. | Flecha hacia la parte incluida cuando se representa esa llamada. Conserva el estereotipo y el sentido del flujo. |

El **rombo** señala pertenencia. La **flecha abierta de una asociación** indica navegabilidad. El **puente** señala un cruce de líneas que siguen su recorrido por separado. La línea discontinua del `«link»` distingue el tipo de relación.

### Formularios integrados y diálogos

- **Formulario integrado.** En `Login`, el rombo negro va del lado de la pantalla y la flecha apunta a `Iniciar sesión`. El formulario apunta con `«submit»` a `ps Login`. En el Administrador, los formularios de contacto, agenda y correo integrados en sus vistas también usan composición.
- **Diálogo que abre una acción.** Usa `«link»` desde la pantalla y rotula la acción, como `Mi perfil`, `Importar CSV` o `Editar`. El diálogo conserva sus propias relaciones de envío y respuesta.
- **Varios controles en un diálogo.** El docente enseña un `«submit»` por formulario. Identifica cada envío y su receptor. Revisa qué llamada ejecuta cada botón y distingue el envío del formulario de las acciones auxiliares.

## Distribución y lectura

1. **Acomoda por flujo.** Agrupa las pantallas, los formularios, los endpoints y las tablas que participan en una misma operación. Favorece recorridos de izquierda a derecha dentro de cada grupo. Ubica el menú y la ficha donde sus ramas puedan salir con claridad. Define las posiciones por el recorrido, con libertad para mezclar tipos de cajas.
2. **Diseña a escala de hoja.** Parte de un lienzo continuo. Ajusta su ancho para que el texto pueda leerse en carta apaisada. Distribuye los grupos en altura para aprovechar cada hoja. Mantén espacio entre cajas y suficiente margen para rótulos y puntas de flecha.
3. **Traza líneas fáciles de seguir.** Usa recorridos cortos y rectos. Aprovecha las diagonales que despejen el camino y usa quiebres para rodear obstáculos. Asigna puntos de entrada y salida distintos a las cajas con muchas conexiones. Comprueba que las líneas queden fuera de las cajas y que sus tramos se distingan en los cruces.
4. **Asocia cada rótulo con su conector.** Coloca el estereotipo y su detalle junto a un tramo claro de la línea. Pueden ir apilados o juntos en un renglón según el espacio. Revisa la cercanía a las líneas vecinas, sobre todo alrededor del menú y la ficha. Conserva la ruta completa y las condiciones en EA cuando abrevies el texto visible.
5. **Revisa el resultado exportado.** EA puede desplazar los rótulos de los conectores con varios quiebres. Comprueba el EMF real y revisa los extremos, los rombos, las flechas, los textos próximos a cortes y las parejas de ida y respuesta. Si el encargo es ajustar rótulos, conserva las posiciones, los trazados y los cortes aprobados.

## Franjas para Word y PDF

- Usa **franjas horizontales de ancho completo**, una por página, de arriba abajo. Mantén el ancho, la escala y la alineación horizontal en toda la secuencia. Los conectores continúan en la misma posición horizontal al pasar de página.
- Coloca el encabezado `7.5.n. Diagrama de Navegación del <Actor>` en la primera página. Las siguientes continúan con el dibujo. Reserva altura para los encabezados y aprovecha la caja útil de la hoja.
- Coloca los cortes entre cajas y rótulos. Prefiere los límites que interrumpen menos trazos y revisa ambos lados de cada corte.
- Inserta el **EMF vectorial** en Word. Usa el PNG para revisar el lienzo completo. Comprueba en el PDF la legibilidad, la altura utilizada y la nitidez al ampliar.
- El Administrador quedó en **seis franjas**, en las páginas **179 a 184** de la exportación de referencia. El número de franjas depende de las dimensiones del dibujo y se comprueba al exportar.

## Auditoría

- [ ] Cada caja existe en el sistema y corresponde al actor.
- [ ] Cada llamada coincide con el verbo, la ruta, el método y la ubicación de sus parámetros. Distingue parámetros de ruta, de consulta y del cuerpo.
- [ ] Las flechas apuntan al receptor correcto, los rombos están del lado del contenedor y los enlaces a diálogos se identifican con la acción que los abre.
- [ ] Las respuestas coinciden con el recorrido real. Comprueba los estados, las condiciones, los códigos de error y el destino de retorno.
- [ ] Los rótulos se leen y se asocian con sus conectores. Revisa el EMF para comprobar la separación entre textos, cajas y líneas.
- [ ] Cada caja y rótulo aparece completo en su página. Las franjas conservan la continuidad y la escala. Word y PDF muestran el mismo recorrido y el índice apunta a la sección correcta.

El verificador automático comprueba rutas, métodos, permisos, parámetros y referencias declaradas. Completa la auditoría leyendo los componentes y las ramas del código. En el Administrador se comprobó que Login presenta el aviso de `422` o `403` dentro de la pantalla, que `Pie` solicita y muestra las visitas y que el retorno de Stripe con token usa las rutas públicas y vuelve a `/anuncios`.

## Regeneración

Desde `crm-web/generadorDocumento/`, respalda el proyecto EA y el Word maestro. Cierra el proyecto en EA antes de ejecutar la automatización.

```powershell
python -c "import navegacion as n; errores = n.verificar(); assert not errores, errores"
python ea/navegacion_hojas.py Administrador --simular
python ea/navegacion_hojas.py Administrador
python insertar_navegacion.py --administrador
.\exportar.ps1
```

`navegacion.py` define el modelo. `ea/navegacion_administrador.py` define el acomodo y los rótulos. `ea/navegacion_hojas.py` actualiza el proyecto editable de Enterprise Architect y exporta EMF y PNG. `insertar_navegacion.py --administrador` reemplaza 7.5.1 en el Word maestro. `exportar.ps1` actualiza los índices y produce DOCX, DOC y PDF. Haz la comprobación final sobre las páginas renderizadas del PDF.

`ea/navegacion_roles.py` define la distribución de Coordinador, Vendedor y Visitante y reutiliza el trazado y los rótulos del Administrador. Para regenerar esos tres diagramas juntos, pasa `Coordinador Vendedor Visitante` a `ea/navegacion_hojas.py` y después ejecuta `python insertar_navegacion.py --actor Coordinador --actor Vendedor --actor Visitante`.

## Referencias

- [Clases del docente, reglas de navegación](referencias/CLASES_DOCENTE.md).
- [Conallen, material del tema 2, figura 5 y sección de formularios](../../referencias/T2.3-Modeling-Web-Application-Architectures-UML.pdf#page=10).
- [UML 2.5.1, asociaciones y agregación](https://www.omg.org/spec/UML/2.5.1/PDF).
- [Documento aprobado G07, navegación del Propietario, páginas 95 a 97](referencias/G07-documento-aprobado.pdf#page=95).
- [Reglas generales del documento P2](REGLAS_DOCUMENTO_P2.md).
