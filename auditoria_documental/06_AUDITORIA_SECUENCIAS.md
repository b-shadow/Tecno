# Auditoría de secuencias y comunicación

Commit auditado: `5bf47b2e863631908e37718fb343fd776003fb5b`. Fecha: 26/11/2026 (America/La_Paz). Solo lectura de originales.

Hay8 secuencias y8 comunicaciones. No hay diagramas de actividades/estados en el modelo actual. Se analizaron todos los mensajes EA y se inspeccionaron globalmente todas sus imágenes. Las secuencias usan26 fragmentos opt; no desarrollan alternativas de error con alt. Los métodos N/D nombrados existen, lo que no certifica el orden completo ni las condiciones. Los parámetros aparecen vacíos en mensajes aunque las operaciones tienen firmas.

## EA-99 — CU1. Gestión de Usuarios (Propietario, Clientes): Comunicación (recorridos principales) (p.37)

Login real consulta usuario, verifica hash/vigencia, registra fallo o éxito y crea token. El diagrama desarrolla éxito y gestión de usuario/matriz pero no fallos, revocación de sesiones ni bitácora. El primer D de comunicación es usuarioPorCorreo; secuencia añade crearToken. Representación parcial coherente de éxito.

Participantes EA: Administrador, DAuth, DSeguridad, DUsuario, NAuth, NSeguridad, NUsuario, PLogin.jsx, PMatriz.jsx, PUsuarios.jsx, api/auth.js, api/seguridad.js, api/usuarios.js.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PLogin.jsx | Administrador → PLogin.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | login() | PLogin.jsx → api/auth.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | POST /login | api/auth.js → NAuth | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | usuarioPorCorreo() | NAuth → DAuth | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | abrir PUsuarios.jsx | Administrador → PUsuarios.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | store() | PUsuarios.jsx → api/usuarios.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | POST /usuarios | api/usuarios.js → NUsuario | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | transaccion() | NUsuario → DUsuario | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 9 | abrir PMatriz.jsx | Administrador → PMatriz.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 10 | asignar() | PMatriz.jsx → api/seguridad.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 11 | PUT /matriz | api/seguridad.js → NSeguridad | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 12 | guardarPermiso() | NSeguridad → DSeguridad | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-100 — CU2. Gestión de Captar, Consumir Oferta: Comunicación (recorridos principales) (p.38)

Catalogo lista módulos abiertos. Registrar interés real tiene transacción, reutilización de persona, control de programa único, creación firstOrCreate y errores por todos repetidos. Mensaje DProspecto::crear no debe leerse como creación incondicional de persona. Falta alternativa persona existente.

Participantes EA: DCatalogo, DProspecto, NCatalogo, NProspecto, PCatalogo.jsx, Visitante, api/catalogo.js.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PCatalogo.jsx | Visitante → PCatalogo.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | programas() | PCatalogo.jsx → api/catalogo.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | GET /catalogo | api/catalogo.js → NCatalogo | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | programasAbiertos() | NCatalogo → DCatalogo | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | abrir PCatalogo.jsx | Visitante → PCatalogo.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | registrarInteres() | PCatalogo.jsx → api/catalogo.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | POST /registro-interes | api/catalogo.js → NProspecto | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | transaccion() | NProspecto → DProspecto | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-101 — CU3. Gestión de Asignar Prospectos (Leads): Comunicación (recorridos principales) (p.38)

Registrar y asignar son dos recorridos. Asignar obtiene/bloquea y valida alcance/vendedor; guardar ocurre dentro de transacción y refrescar después. Comunicación se detiene en obtener/transaccion y no demuestra asignación completa. El reparto por menor carga no está modelado.

Participantes EA: Coordinador, DInteres, DProspecto, NInteres, NProspecto, PAsignacion.jsx, PProspectos.jsx, api/intereses.js, api/prospectos.js.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PProspectos.jsx | Coordinador → PProspectos.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | store() | PProspectos.jsx → api/prospectos.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | POST /prospectos | api/prospectos.js → NProspecto | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | transaccion() | NProspecto → DProspecto | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | abrir PAsignacion.jsx | Coordinador → PAsignacion.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | asignar() | PAsignacion.jsx → api/intereses.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | PATCH /intereses/{interes}/asignar | api/intereses.js → NInteres | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | obtener() | NInteres → DInteres | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-102 — CU4. Gestión de Embudo de Ventas en Tablero Kanban: Comunicación (recorridos principales) (p.38)

mover valida cartera, impide mover Convertido, hace transacción y bloqueo; Convertido deriva a NConversion y el resto guarda/actualiza prospecto. Diagrama solo representa el camino guardar→actualizar; no la alternativa Convertido ni motivo Perdido.

Participantes EA: DInteres, NInteres, PEmbudo.jsx, Vendedor, api/intereses.js.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PEmbudo.jsx | Vendedor → PEmbudo.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | mover() | PEmbudo.jsx → api/intereses.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | PATCH /intereses/{interes}/estado | api/intereses.js → NInteres | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | obtener() | NInteres → DInteres | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-103 — CU5. Gestión de Pérdida de Prospectos y Clasificación de Motivos: Comunicación (recorridos principales) (p.38)

Perdido añade registro de interacción y trigger clasifica/historial. Su comunicación/secuencia muestra NInteres y también gestión de motivos, pero la vista de clases solo gestiona motivos. Omitida interacción de pérdida y condición motivo obligatorio.

Participantes EA: Administrador, DInteres, DMotivo, NInteres, NMotivo, PEmbudo.jsx, PMotivos.jsx, Vendedor, api/intereses.js, api/motivos.js.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PEmbudo.jsx | Vendedor → PEmbudo.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | mover() | PEmbudo.jsx → api/intereses.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | PATCH /intereses/{interes}/estado... | api/intereses.js → NInteres | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | obtener() | NInteres → DInteres | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | abrir PMotivos.jsx | Administrador → PMotivos.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | store() | PMotivos.jsx → api/motivos.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | POST /motivos | api/motivos.js → NMotivo | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | crear() | NMotivo → DMotivo | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-124 — CU1. Gestión de Usuarios (Propietario, Clientes): Secuencia (recorridos principales) (p.69)

Login real consulta usuario, verifica hash/vigencia, registra fallo o éxito y crea token. El diagrama desarrolla éxito y gestión de usuario/matriz pero no fallos, revocación de sesiones ni bitácora. El primer D de comunicación es usuarioPorCorreo; secuencia añade crearToken. Representación parcial coherente de éxito.

Participantes EA: Administrador, Cliente HTTP, Datos PostgreSQL, Negocio Laravel, Pantalla React.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PLogin.jsx | Administrador → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | auth.js::login() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | NAuth::login() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NAuth.php:27 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | DAuth::usuarioPorCorreo() | Negocio Laravel → Datos PostgreSQL | datos/src/DAuth.php:12 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | ?Usuario | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | DAuth::crearToken() | Negocio Laravel → Datos PostgreSQL | datos/src/DAuth.php:33 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | void | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 9 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 10 | resultado mostrado | Pantalla React → Administrador | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 11 | abrir PUsuarios.jsx | Administrador → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 12 | usuarios.js::store() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 13 | NUsuario::store() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NUsuario.php:31 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 14 | DUsuario::crear() | Negocio Laravel → Datos PostgreSQL | datos/src/DUsuario.php:46 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 15 | Usuario | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 16 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 17 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 18 | resultado mostrado | Pantalla React → Administrador | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 19 | abrir PMatriz.jsx | Administrador → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 20 | seguridad.js::asignar() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 21 | NSeguridad::asignar() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NSeguridad.php:25 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 22 | DSeguridad::guardarPermiso() | Negocio Laravel → Datos PostgreSQL | datos/src/DSeguridad.php:22 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 23 | void | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 24 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 25 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 26 | resultado mostrado | Pantalla React → Administrador | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-125 — CU2. Gestión de Captar, Consumir Oferta: Secuencia (recorridos principales) (p.70)

Catalogo lista módulos abiertos. Registrar interés real tiene transacción, reutilización de persona, control de programa único, creación firstOrCreate y errores por todos repetidos. Mensaje DProspecto::crear no debe leerse como creación incondicional de persona. Falta alternativa persona existente.

Participantes EA: Cliente HTTP, Datos PostgreSQL, Negocio Laravel, Pantalla React, Visitante.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PCatalogo.jsx | Visitante → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | catalogo.js::programas() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | NCatalogo::programas() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NCatalogo.php:20 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | DCatalogo::programasAbiertos() | Negocio Laravel → Datos PostgreSQL | datos/src/DCatalogo.php:13 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | Collection | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | resultado mostrado | Pantalla React → Visitante | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 9 | abrir PCatalogo.jsx | Visitante → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 10 | catalogo.js::registrarInteres() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 11 | NProspecto::registrarInteres() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NProspecto.php:58 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 12 | DProspecto::crear() | Negocio Laravel → Datos PostgreSQL | datos/src/DProspecto.php:49 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 13 | Prospecto | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 14 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 15 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 16 | resultado mostrado | Pantalla React → Visitante | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-126 — CU3. Gestión de Asignar Prospectos (Leads): Secuencia (recorridos principales) (p.71)

Registrar y asignar son dos recorridos. Asignar obtiene/bloquea y valida alcance/vendedor; guardar ocurre dentro de transacción y refrescar después. Comunicación se detiene en obtener/transaccion y no demuestra asignación completa. El reparto por menor carga no está modelado.

Participantes EA: Cliente HTTP, Coordinador, Datos PostgreSQL, Negocio Laravel, Pantalla React.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PProspectos.jsx | Coordinador → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | prospectos.js::store() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | NProspecto::store() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NProspecto.php:114 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | DProspecto::crear() | Negocio Laravel → Datos PostgreSQL | datos/src/DProspecto.php:49 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | Prospecto | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | resultado mostrado | Pantalla React → Coordinador | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 9 | abrir PAsignacion.jsx | Coordinador → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 10 | intereses.js::asignar() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 11 | NInteres::asignar() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NInteres.php:82 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 12 | DInteres::transaccion() | Negocio Laravel → Datos PostgreSQL | datos/src/DInteres.php:67 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 13 | mixed | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 14 | DInteres::refrescarDetalle() | Negocio Laravel → Datos PostgreSQL | datos/src/DInteres.php:130 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 15 | Interes | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 16 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 17 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 18 | resultado mostrado | Pantalla React → Coordinador | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-127 — CU4. Gestión de Embudo de Ventas en Tablero Kanban: Secuencia (recorridos principales) (p.72)

mover valida cartera, impide mover Convertido, hace transacción y bloqueo; Convertido deriva a NConversion y el resto guarda/actualiza prospecto. Diagrama solo representa el camino guardar→actualizar; no la alternativa Convertido ni motivo Perdido.

Participantes EA: Cliente HTTP, Datos PostgreSQL, Negocio Laravel, Pantalla React, Vendedor.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PEmbudo.jsx | Vendedor → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | intereses.js::mover() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | NInteres::mover() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NInteres.php:38 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | DInteres::guardar() | Negocio Laravel → Datos PostgreSQL | datos/src/DInteres.php:77 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | void | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | DInteres::actualizarEstadoProspecto() | Negocio Laravel → Datos PostgreSQL | datos/src/DInteres.php:82 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | void | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 9 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 10 | resultado mostrado | Pantalla React → Vendedor | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-128 — CU5. Gestión de Pérdida de Prospectos y Clasificación de Motivos: Secuencia (recorridos principales) (p.73)

Perdido añade registro de interacción y trigger clasifica/historial. Su comunicación/secuencia muestra NInteres y también gestión de motivos, pero la vista de clases solo gestiona motivos. Omitida interacción de pérdida y condición motivo obligatorio.

Participantes EA: Administrador, Cliente HTTP, Datos PostgreSQL, Negocio Laravel, Pantalla React, Vendedor.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PEmbudo.jsx | Vendedor → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | intereses.js::mover() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | NInteres::mover() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NInteres.php:38 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | DInteres::guardar() | Negocio Laravel → Datos PostgreSQL | datos/src/DInteres.php:77 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | void | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | DInteres::actualizarEstadoProspecto() | Negocio Laravel → Datos PostgreSQL | datos/src/DInteres.php:82 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | void | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 9 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 10 | resultado mostrado | Pantalla React → Vendedor | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 11 | abrir PMotivos.jsx | Administrador → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 12 | motivos.js::store() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 13 | NMotivo::store() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NMotivo.php:25 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 14 | DMotivo::crear() | Negocio Laravel → Datos PostgreSQL | datos/src/DMotivo.php:37 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 15 | MotivoPerdida | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 16 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 17 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 18 | resultado mostrado | Pantalla React → Administrador | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-141 — CU6. Gestión de Validar Datos y Procesar Conversión a Matrícula: Comunicación (recorridos principales) (p.39)

Orden guarda cuotas; Checkout obtiene orden, llama a Stripe y registra transacción. Orden de llamadas principales concuerda con el camino resumido. Retorno ilustrado solo muestra transaccionPorSesion/retrieve, sin confirmar cuota, NConversion, inscripción, comisión o SMTP. El actor de retorno es Vendedor y falta el pagador público. No se representa webhook, Setup o conciliación duplicada. SEC-002.

Participantes EA: Coordinador, DExportacion, DPago, DStripe, NExportacion, NPago, NStripe, PAgenda.jsx, PMatriculas.jsx, PPagoConfirmacion.jsx, StripeClient, Vendedor, api/exportaciones.js, api/pagos.js.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PAgenda.jsx | Vendedor → PAgenda.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | crearOrden() | PAgenda.jsx → api/pagos.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | POST /intereses/{interes}/ordenes... | api/pagos.js → NPago | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | crearOrden() | NPago → DPago | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | insertarCuotas() | NPago → DPago | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | abrir PAgenda.jsx | Vendedor → PAgenda.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | crearCheckout() | PAgenda.jsx → api/pagos.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | POST /ordenes-pago/{orden}/cuotas... | api/pagos.js → NPago | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 9 | iniciarCheckoutCuota() | NPago → NStripe | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 10 | ordenConDetalle() | NStripe → DStripe | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 11 | checkout.sessions.create() | NStripe → StripeClient | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 12 | crearTransaccion() | NStripe → DStripe | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 13 | abrir PPagoConfirmacion.jsx | Vendedor → PPagoConfirmacion.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 14 | confirmarCheckout() | PPagoConfirmacion.jsx → api/pagos.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 15 | GET /pagos/stripe/sesiones/{sessi... | api/pagos.js → NPago | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 16 | verificarSesion() | NPago → NStripe | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 17 | transaccionPorSesion() | NStripe → DStripe | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 18 | checkout.sessions.retrieve() | NStripe → StripeClient | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 19 | abrir PMatriculas.jsx | Coordinador → PMatriculas.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 20 | exportar() | PMatriculas.jsx → api/exportaciones.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 21 | POST /exportaciones | api/exportaciones.js → NExportacion | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 22 | exportarPendientes() | NExportacion → DExportacion | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-142 — CU6. Gestión de Validar Datos y Procesar Conversión a Matrícula: Secuencia (recorridos principales) (p.74)

Orden guarda cuotas; Checkout obtiene orden, llama a Stripe y registra transacción. Orden de llamadas principales concuerda con el camino resumido. Retorno ilustrado solo muestra transaccionPorSesion/retrieve, sin confirmar cuota, NConversion, inscripción, comisión o SMTP. El actor de retorno es Vendedor y falta el pagador público. No se representa webhook, Setup o conciliación duplicada. SEC-002.

Participantes EA: Cliente HTTP, Coordinador, Datos PostgreSQL, Negocio Laravel, Pantalla React, Pasarela Stripe, Vendedor.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PAgenda.jsx | Vendedor → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | pagos.js::crearOrden() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | NPago::crearOrden() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NPago.php:115 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | DPago::crearOrden() | Negocio Laravel → Datos PostgreSQL | datos/src/DPago.php:46 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | OrdenPago | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | DPago::insertarCuotas() | Negocio Laravel → Datos PostgreSQL | datos/src/DPago.php:50 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | void | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 9 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 10 | resultado mostrado | Pantalla React → Vendedor | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 11 | abrir PAgenda.jsx | Vendedor → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 12 | pagos.js::crearCheckout() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 13 | NPago::crearCheckout() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NPago.php:261 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 14 | NStripe::iniciarCheckoutCuota() | Negocio Laravel → Negocio Laravel | negocio/app/Negocio/NStripe.php:33 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 15 | DStripe::ordenConDetalle() | Negocio Laravel → Datos PostgreSQL | datos/src/DStripe.php:21 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 16 | OrdenPago | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 17 | checkout.sessions.create() | Negocio Laravel → Pasarela Stripe | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 18 | Checkout Session | Pasarela Stripe → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 19 | DStripe::crearTransaccion() | Negocio Laravel → Datos PostgreSQL | datos/src/DStripe.php:104 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 20 | TransaccionStripe | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 21 | array | Negocio Laravel → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 22 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 23 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 24 | resultado mostrado | Pantalla React → Vendedor | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 25 | abrir PPagoConfirmacion.jsx | Vendedor → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 26 | pagos.js::confirmarCheckout() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 27 | NPago::confirmarCheckout() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NPago.php:270 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 28 | NStripe::verificarSesion() | Negocio Laravel → Negocio Laravel | negocio/app/Negocio/NStripe.php:379 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 29 | DStripe::transaccionPorSesion() | Negocio Laravel → Datos PostgreSQL | datos/src/DStripe.php:48 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 30 | ?TransaccionStripe | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 31 | checkout.sessions.retrieve() | Negocio Laravel → Pasarela Stripe | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 32 | Checkout Session | Pasarela Stripe → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 33 | array | Negocio Laravel → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 34 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 35 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 36 | resultado mostrado | Pantalla React → Vendedor | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 37 | abrir PMatriculas.jsx | Coordinador → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 38 | exportaciones.js::exportar() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 39 | NExportacion::exportar() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NExportacion.php:28 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 40 | DExportacion::exportarPendientes() | Negocio Laravel → Datos PostgreSQL | datos/src/DExportacion.php:20 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 41 | array | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 42 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 43 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 44 | resultado mostrado | Pantalla React → Coordinador | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-105 — CU7. Gestión de Bitácora, Interacciones y Recordatorios: Comunicación (recorridos principales) (p.39)

Interacción y recordatorio son objetivos distintos de notificación SMTP. El diagrama lista notificaciones y muestra crearRecordatorio, pero no enviarCorreo, fechas futuras, completar/cancelar, ni programación de avisos de cobro. Recordatorio de contacto no equivale a recordatorio de cuota.

Participantes EA: DNotificacion, DSeguimiento, NNotificacion, NSeguimiento, PAgenda.jsx, PNotificaciones.jsx, Vendedor, api/notificaciones.js, api/seguimiento.js.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PAgenda.jsx | Vendedor → PAgenda.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | registrarInteraccion() | PAgenda.jsx → api/seguimiento.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | POST /intereses/{interes}/interac... | api/seguimiento.js → NSeguimiento | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | interes() | NSeguimiento → DSeguimiento | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | abrir PAgenda.jsx | Vendedor → PAgenda.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | crearRecordatorio() | PAgenda.jsx → api/seguimiento.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | POST /intereses/{interes}/recorda... | api/seguimiento.js → NSeguimiento | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | interes() | NSeguimiento → DSeguimiento | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 9 | abrir PNotificaciones.jsx | Vendedor → PNotificaciones.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 10 | index() | PNotificaciones.jsx → api/notificaciones.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 11 | GET /notificaciones | api/notificaciones.js → NNotificacion | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 12 | listar() | NNotificacion → DNotificacion | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-106 — CU8. Reportes y Estadísticas: Comunicación (recorridos principales) (p.40)

Estadísticas y resumenComisiones tienen soporte N/D. Pagar comisiones y cambiar porcentaje requieren más permisos; el diagrama no los desarrolla. No implica que todo usuario con lectura pueda pagarlas.

Participantes EA: Coordinador, DReporte, DSeguimiento, NReporte, NSeguimiento, PComisiones.jsx, PReportes.jsx, api/reportes.js, api/seguimiento.js.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PReportes.jsx | Coordinador → PReportes.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | estadisticas() | PReportes.jsx → api/reportes.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | GET /reportes/estadisticas | api/reportes.js → NReporte | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | estadisticas() | NReporte → DReporte | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | abrir PComisiones.jsx | Coordinador → PComisiones.jsx | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | resumenComisiones() | PComisiones.jsx → api/seguimiento.js | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | GET /comisiones/resumen | api/seguimiento.js → NSeguimiento | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | resumenComisiones() | NSeguimiento → DSeguimiento | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-130 — CU7. Gestión de Bitácora, Interacciones y Recordatorios: Secuencia (recorridos principales) (p.75)

Interacción y recordatorio son objetivos distintos de notificación SMTP. El diagrama lista notificaciones y muestra crearRecordatorio, pero no enviarCorreo, fechas futuras, completar/cancelar, ni programación de avisos de cobro. Recordatorio de contacto no equivale a recordatorio de cuota.

Participantes EA: Cliente HTTP, Datos PostgreSQL, Negocio Laravel, Pantalla React, Vendedor.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PAgenda.jsx | Vendedor → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | seguimiento.js::registrarInteraccion() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | NSeguimiento::registrarInteraccion() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NSeguimiento.php:27 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | DSeguimiento::registrarInteraccion() | Negocio Laravel → Datos PostgreSQL | datos/src/DSeguimiento.php:39 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | Interaccion | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | resultado mostrado | Pantalla React → Vendedor | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 9 | abrir PAgenda.jsx | Vendedor → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 10 | seguimiento.js::crearRecordatorio() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 11 | NSeguimiento::crearRecordatorio() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NSeguimiento.php:59 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 12 | DSeguimiento::crearRecordatorio() | Negocio Laravel → Datos PostgreSQL | datos/src/DSeguimiento.php:68 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 13 | resultado | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 14 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 15 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 16 | resultado mostrado | Pantalla React → Vendedor | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 17 | abrir PNotificaciones.jsx | Vendedor → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 18 | notificaciones.js::index() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 19 | NNotificacion::index() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NNotificacion.php:189 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 20 | DNotificacion::listar() | Negocio Laravel → Datos PostgreSQL | datos/src/DNotificacion.php:37 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 21 | Collection | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 22 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 23 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 24 | resultado mostrado | Pantalla React → Vendedor | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## EA-131 — CU8. Reportes y Estadísticas: Secuencia (recorridos principales) (p.76)

Estadísticas y resumenComisiones tienen soporte N/D. Pagar comisiones y cambiar porcentaje requieren más permisos; el diagrama no los desarrolla. No implica que todo usuario con lectura pueda pagarlas.

Participantes EA: Cliente HTTP, Coordinador, Datos PostgreSQL, Negocio Laravel, Pantalla React.


| N.º | Mensaje UML | Origen → destino | Método real y evidencia | Coincidencia | Corrección propuesta |
| --- | --- | --- | --- | --- | --- |
| 1 | abrir PReportes.jsx | Coordinador → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 2 | reportes.js::estadisticas() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 3 | NReporte::estadisticas() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NReporte.php:40 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 4 | DReporte::estadisticas() | Negocio Laravel → Datos PostgreSQL | datos/src/DReporte.php:60 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 5 | array | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 6 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 7 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 8 | resultado mostrado | Pantalla React → Coordinador | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 9 | abrir PComisiones.jsx | Coordinador → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 10 | seguimiento.js::resumenComisiones() | Pantalla React → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 11 | NSeguimiento::resumenComisiones() | Cliente HTTP → Negocio Laravel | negocio/app/Negocio/NSeguimiento.php:125 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 12 | DSeguimiento::resumenComisiones() | Negocio Laravel → Datos PostgreSQL | datos/src/DSeguimiento.php:102 | EXISTE; orden y flujo requieren revisión semántica | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 13 | Collection | Datos PostgreSQL → Negocio Laravel | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 14 | JsonResponse | Negocio Laravel → Cliente HTTP | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 15 | respuesta JSON | Cliente HTTP → Pantalla React | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |
| 16 | resultado mostrado | Pantalla React → Coordinador | Interfaz/retorno/SDK; verificar cliente/ruta | Mensaje de interfaz, HTTP, retorno o infraestructura | Completar argumentos/condiciones según SEC-001; revisar recorrido completo, no agregar infraestructura irrelevante |

Cómo leer: en secuencia el tiempo baja, una activación indica ejecución y una línea discontinua retorno. En comunicación el número ordena los mensajes entre objetos; la numeración continua1,2,3 representa el recorrido seleccionado, pero no sustituye la relación de llamadas anidadas1.1/1.2 cuando sea necesaria para explicar anidamiento. Un retorno JsonResponse describe tipo PHP, mientras el navegador recibe JSON/estado HTTP.

## Estados y transiciones inferidos del código, sin crear diagramas originales

Interés: seis estados (Nuevo, En Contacto, Seguimiento, Promesa de Pago, Convertido, Perdido). El código impide mover Convertido; Perdido exige motivo vía Request y los triggers conservan historial. No hay un grafo completo de adyacencias que autorice solo una etapa siguiente: se valida estado destino/reglas, no se presupone un flujo lineal estricto. Orden: Activa/Anulada; no admite anular con cuotas pagadas/en revisión o pago Stripe confirmado. Cuota: Pendiente de pago/En revision/Pago aprobado/Pago rechazado; la revisión corresponde a datos manuales históricos. Sesión/transacción: pendiente, confirmado, cancelado, expirado, rechazado y reconciliacion_duplicada, con valores completos en CHECK de07. Recordatorio de contacto: estados en modelo/Request; no confundir con marcas temporales de aviso de cuota.

No se afirma que estados de Stripe y estados de cuota sean equivalentes uno a uno. Un pago confirmado no garantiza datos completos para convertir. Cualquier futura figura debe respetar esta distinción.

Corrección del inventario de estados de contacto: además de Pendiente, Realizada y Cancelada, existe Atrasada. DSeguimiento::listarRecordatorios la asigna tras 24 h de vencimiento al consultar agenda, antes del filtro de cartera. Es una transición automática por GET que falta en las figuras: API-001.
