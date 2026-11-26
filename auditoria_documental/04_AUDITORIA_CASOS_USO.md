# Auditoría de actores y casos de uso

Commit auditado: `5bf47b2e863631908e37718fb343fd776003fb5b`. Fecha: 26/11/2026 (America/La_Paz). Solo lectura de originales.


| Actor documentado | Responsabilidad real | Cuenta/rol |
| --- | --- | --- |
| Administrador | Gestiona usuarios y toda la operación comercial. | administrador |
| Coordinador | Asigna interesados, valida pagos y supervisa vendedores. | coordinador |
| Vendedor | Da seguimiento a los interesados asignados. | vendedor |
| Visitante | Consulta el catálogo público de programas y módulos y registra su interés sin iniciar sesión. | Sin sesión |

Hay4 actores humanos documentados y3 roles autenticados. En implementación participan además el pagador sin sesión, Stripe y transporte SMTP. El catálogo externo es simulado por NCatalogoExterno; no hay prueba de integración real con Grupo06. Scheduler es un proceso interno/operativo y no se inventa como rol humano. El sistema SIS recibe exportación CSV gestionada; no se demostró integración HTTP automática.

## Nombres e identificadores completos

| Código | Nombre en lista/alcance | Nombre en especificación | Actor iniciador | Soporte |
| --- | --- | --- | --- | --- |
| CU1 | Gestión de Usuarios (Propietario, Clientes) | Gestionar Usuarios | Administrador | Implementación estática presente; diferencias por flujo |
| CU2 | Gestión de Captar, Consumir Oferta | Gestionar Captación de la Oferta | Visitante | Implementación estática presente; diferencias por flujo |
| CU3 | Gestión de Asignar Prospectos (Leads) | Gestionar Asignación de Prospectos | Coordinador | Implementación estática presente; diferencias por flujo |
| CU4 | Gestión de Embudo de Ventas en Tablero Kanban | Gestionar Embudo de Ventas | Vendedor | Implementación estática presente; diferencias por flujo |
| CU5 | Gestión de Pérdida de Prospectos y Clasificación de Motivos | Gestionar Pérdida y Motivos | Vendedor | Implementación estática presente; diferencias por flujo |
| CU6 | Gestión de Validar Datos y Procesar Conversión a Matrícula | Gestionar Conversión a Matrícula | Vendedor | Implementación estática presente; diferencias por flujo |
| CU7 | Gestión de Bitácora, Interacciones y Recordatorios | Gestionar Seguimiento del Prospecto | Vendedor | Implementación estática presente; diferencias por flujo |
| CU8 | Reportes y Estadísticas | Gestionar Reportes y Estadísticas | Coordinador | Implementación estática presente; diferencias por flujo |
## CU1. Gestión de Usuarios (Propietario, Clientes)

Página 24, sección4.4. Actores: Administrador, Coordinador, Vendedor. Iniciador: Administrador. Objetivo: Administrar las cuentas de usuario, su rol, vigencia y permisos, y controlar el acceso al sistema.

Descripción: El usuario inicia sesión con su correo y contraseña y el sistema arma su menú desde la matriz de acceso. El Administrador registra, modifica y cambia el estado de los usuarios, asigna permisos en la matriz y consulta la bitácora de accesos.

Precondición: El usuario tiene una cuenta activa y vigente; para gestionar usuarios, matriz y bitácora tiene permiso sobre esos recursos.

Flujo principal:

1. El usuario ingresa su correo y contraseña en Iniciar Sesión.
2. El sistema valida la credencial y su vigencia, registra el acceso en la bitácora y muestra el menú de su rol.
3. El Administrador abre Usuarios y registra o edita un usuario con nombre, correo, rol, vigencia y foto.
4. El sistema valida los datos y guarda el usuario.
5. El Administrador asigna permisos de lectura, modificación o eliminación en la Matriz de Acceso.
6. El Administrador consulta la Bitácora de Accesos filtrando por evento, usuario, IP y fechas.

Alternativos explícitos: No hay campo separado en la fuente de especificación; excepciones listadas no sustituyen flujos alternativos.

Excepciones documentadas:

- Credencial incorrecta: "Correo o contraseña incorrectos."
- Cuenta inactiva o vencida: "Su cuenta está inactiva o fuera de vigencia."
- Sin permiso sobre el recurso: "No tiene permiso para realizar esta acción."
- Último administrador: "Debe conservar al menos un administrador activo."
- Matriz del administrador: "El administrador debe conservar acceso total a Usuarios y Matriz de acceso."
- Foto demasiado grande: "La foto no debe superar 2 MB."
- Sin conexión o base de datos no disponible: la operación no se guarda y la interfaz muestra el error.

Postcondición documental: El usuario queda registrado o actualizado, sus permisos definen su menú y cada acceso queda en la bitácora.

Pantallas y módulos P: api/auth.js, servicios/auth.js, AppShell.jsx, Shell.jsx, PLogin.jsx, PUsuarios.jsx, PMatriz.jsx, api/sitio.js, api/usuarios.js, PAsignacion.jsx, PEmbudo.jsx, PReportes.jsx, api/seguridad.js, PBitacora.jsx.

Clases N: NAuth, NAcceso, NSitio, NFoto, NUsuario, NSeguridad. Clases D/modelos: DAuth, Usuario, DBitacora, Bitacora, ApiToken, DAcceso, LoginRequest, DSitio, VisitaRequest, DAlcance, Interes, ConsultaRequest, ActualizarPerfilRequest, CambiarPasswordRequest, DUsuario, Programa, ProgramaResponsable, UsuarioRequest, CambiarEstadoUsuarioRequest, DSeguridad, AsignarPermisoRequest, BitacoraRequest.


| Endpoint | N | D alcanzables estáticamente | Tablas candidatas | Estado |
| --- | --- | --- | --- | --- |
| POST /api/login | NAuth::login | DAcceso::menuPorRol; DAuth::crearToken; DAuth::usuarioPorCorreo; DBitacora::registrar | api_tokens; bitacora; usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/visitas | NSitio::visita | DAuth::tokenPorPlano; DBitacora::registrar; DSitio::recursoPorRuta; DSitio::visitas | api_tokens; bitacora; permisos; recursos | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/buscar | NSitio::buscar | DAlcance::codigosModuloCoordinador; DAuth::tokenPorPlano; DSitio::buscarCatalogo; DSitio::buscarIntereses; DSitio::buscarPaginas; DSitio::buscarUsuarios | api_tokens; intereses; permisos; usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/fotos/{archivo} | NSitio::foto |  |  | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/me | NAuth::me | DAcceso::menuPorRol |  | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PUT /api/perfil | NAuth::actualizarPerfil | DAuth::actualizarUsuario |  | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PUT /api/perfil/password | NAuth::cambiarPassword | DAuth::actualizarUsuario; DAuth::revocarOtrosTokens |  | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/logout | NAuth::logout | DAuth::eliminarToken; DBitacora::registrar | bitacora | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/usuarios | NUsuario::index | DAlcance::escaparLike; DUsuario::listar | programas; roles; usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/usuarios | NUsuario::store | DUsuario::actualizar; DUsuario::asignarProgramas; DUsuario::crear; DUsuario::fresco; DUsuario::quitarProgramas; DUsuario::transaccion | programas_responsables; usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PUT /api/usuarios/{usuario} | NUsuario::update | DUsuario::actualizar; DUsuario::asignarProgramas; DUsuario::bloquearAdministradoresActivos; DUsuario::existeOtroAdministradorActivo; DUsuario::fresco; DUsuario::obtener; DUsuario::quitarProgramas; DUsuario::revocarTokens; DUsuario::transaccion | programas_responsables; usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PATCH /api/usuarios/{usuario}/estado | NUsuario::cambiarEstado | DUsuario::actualizar; DUsuario::bloquearAdministradoresActivos; DUsuario::existeOtroAdministradorActivo; DUsuario::fresco; DUsuario::obtener; DUsuario::revocarTokens; DUsuario::transaccion | usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| DELETE /api/usuarios/{usuario}/foto | NUsuario::foto | DUsuario::actualizar; DUsuario::obtener | usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/vendedores | NUsuario::vendedores | DUsuario::vendedores | usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/matriz | NSeguridad::matriz | DSeguridad::matriz | permisos; recursos; roles | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PUT /api/matriz | NSeguridad::asignar | DSeguridad::guardarPermiso | permisos | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/bitacora | NSeguridad::bitacora | DAlcance::escaparLike; DSeguridad::bitacora |  | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/bitacora/resumen | NSeguridad::resumen | DSeguridad::resumen | bitacora; recursos | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |

Diagramas: uc-cu1, cls-cu1, com-cu1, sd-cu1; navegación según actor. Pruebas: ver pruebas_inventario.json y las PRUEBAS_BLANCA/NEGRA relacionadas; no ejecutadas aquí. Hallazgos: CU-001; ARQ-001.

## CU2. Gestión de Captar, Consumir Oferta

Página 25, sección4.4. Actores: Administrador, Coordinador, Visitante. Iniciador: Visitante. Objetivo: Captar prospectos desde el catálogo público de programas y módulos.

Descripción: El visitante consulta el catálogo por área y programa, busca módulos y registra su interés con sus datos; el registro crea el prospecto y su interés. En el panel, el Administrador y el Coordinador consultan la oferta académica y la sincronizan desde el catálogo del Grupo 06 (simulado).

Precondición: El catálogo tiene programas y módulos abiertos.

Flujo principal:

1. El visitante abre el Catálogo de Programas.
2. El sistema lista los programas y módulos abiertos y cuenta la visita.
3. El visitante elige un programa o un módulo y presiona Me interesa.
4. El visitante ingresa nombre, apellido, documento, teléfono, correo, profesión y ubicación.
5. El sistema valida los datos y registra el prospecto y su interés.
6. El sistema muestra el mensaje de registro exitoso.

Alternativos explícitos: No hay campo separado en la fuente de especificación; excepciones listadas no sustituyen flujos alternativos.

Excepciones documentadas:

- Módulos de varios programas: "Seleccione módulos de un solo programa por registro."
- Módulo cerrado: "Uno o más módulos seleccionados ya no están disponibles. Revise la selección."
- Datos de otra persona: "Ese correo o carnet ya está registrado con otros datos. Comuníquese con coordinación."
- Sin conexión o base de datos no disponible: la operación no se guarda y la interfaz muestra el error.

Postcondición documental: El prospecto y su interés quedan registrados, listos para asignarse a un vendedor.

Pantallas y módulos P: api/catalogo.js, FormularioOrdenPago.jsx, PCatalogo.jsx, PProspectos.jsx.

Clases N: NCatalogo, NCatalogoExterno, NProspecto. Clases D/modelos: DCatalogo, Programa, ConsultaRequest, DProspecto, Prospecto, CatalogoCache, Interes, RegistrarInteresRequest.


| Endpoint | N | D alcanzables estáticamente | Tablas candidatas | Estado |
| --- | --- | --- | --- | --- |
| GET /api/catalogo | NCatalogo::programas | DCatalogo::programasAbiertos | programas | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/registro-interes | NProspecto::registrarInteres | DProspecto::crear; DProspecto::crearInteres; DProspecto::encontrarPorDocumentoOCorreoBloqueado; DProspecto::modulosSolicitados; DProspecto::transaccion; DProspecto::vendedorExistente | catalogo_cache; intereses; prospectos | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/catalogo/sincronizar | NCatalogo::sincronizar | DCatalogo::sincronizar | catalogo_cache; programas | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |

Diagramas: uc-cu2, cls-cu2, com-cu2, sd-cu2; navegación según actor. Pruebas: ver pruebas_inventario.json y las PRUEBAS_BLANCA/NEGRA relacionadas; no ejecutadas aquí. Hallazgos: CU-003.

## CU3. Gestión de Asignar Prospectos (Leads)

Página 26, sección4.4. Actores: Administrador, Coordinador, Vendedor. Iniciador: Coordinador. Objetivo: Registrar prospectos y repartirlos entre los vendedores.

Descripción: El Coordinador o el Administrador registran prospectos a mano o por CSV con su origen y los asignan a un vendedor de forma manual o por reparto Round-Robin; cada vendedor ve su cartera.

Precondición: El usuario tiene permiso de modificación sobre Asignación de prospectos y hay vendedores activos.

Flujo principal:

1. El Coordinador abre Prospectos y registra un prospecto o importa un archivo CSV.
2. El sistema valida cada fila y registra los prospectos con su interés.
3. El Coordinador abre Asignación de Prospectos y filtra las tarjetas sin asignar.
4. El Coordinador asigna una tarjeta a un vendedor o reparte las pendientes por Round-Robin.
5. El sistema guarda la asignación y la tarjeta aparece en la cartera del vendedor.

Alternativos explícitos: No hay campo separado en la fuente de especificación; excepciones listadas no sustituyen flujos alternativos.

Excepciones documentadas:

- Registro por un vendedor: "Solo coordinación registra e importa prospectos."
- CSV con errores: "El archivo tiene errores; no se cargó ningún prospecto."
- CSV con columnas repetidas: "El archivo tiene columnas repetidas."
- Usuario que no es vendedor: "El usuario seleccionado no es vendedor."
- Sin vendedores: "No hay vendedores activos para repartir."
- Nada que repartir: "No había prospectos sin asignar."
- Sin conexión o base de datos no disponible: la operación no se guarda y la interfaz muestra el error.

Postcondición documental: Cada prospecto asignado queda en la cartera de su vendedor.

Pantallas y módulos P: api/prospectos.js, PProspectos.jsx, PAgenda.jsx, api/intereses.js, PAsignacion.jsx.

Clases N: NProspecto, NAcceso, NInteres, NAlcance. Clases D/modelos: DProspecto, DAlcance, Usuario, Prospecto, ConsultaRequest, Interes, CatalogoCache, StoreProspectoRequest, ImportarCsvRequest, UpdateProspectoRequest, CrearInteresRequest, DInteres, AsignarInteresRequest.


| Endpoint | N | D alcanzables estáticamente | Tablas candidatas | Estado |
| --- | --- | --- | --- | --- |
| GET /api/prospectos | NProspecto::index | DAlcance::escaparLike; DAlcance::intereses; DAlcance::prospectos; DProspecto::buscar | prospectos | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/prospectos | NProspecto::store | DProspecto::conIntereses; DProspecto::crear; DProspecto::crearInteres; DProspecto::modulosSolicitados; DProspecto::transaccion; DProspecto::vendedorExistente | catalogo_cache; intereses; permisos; prospectos | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/prospectos/importar | NProspecto::importarCSV | DProspecto::crear; DProspecto::crearInteres; DProspecto::existeDocumentoOCorreo; DProspecto::modulosSolicitados; DProspecto::transaccion; DProspecto::vendedorExistente | catalogo_cache; intereses; permisos; prospectos | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PUT /api/prospectos/{prospecto} | NProspecto::update | DAlcance::prospectos; DProspecto::actualizado; DProspecto::actualizar; DProspecto::estaDentroDeCartera; DProspecto::obtener | prospectos | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/prospectos/{prospecto}/intereses | NProspecto::crearInteres | DAlcance::prospectos; DProspecto::crearInteres; DProspecto::estaDentroDeCartera; DProspecto::modulosSolicitados; DProspecto::obtener; DProspecto::transaccion; DProspecto::vendedorExistente | catalogo_cache; intereses; prospectos | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PATCH /api/intereses/{interes}/asignar | NInteres::asignar | DInteres::actualizarRecordatoriosPendientes; DInteres::guardar; DInteres::obtener; DInteres::refrescarDetalle; DInteres::registrarInteraccion; DInteres::transaccion; DInteres::vendedor; DInteres::vendedorAsignado | intereses; usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/intereses/distribuir | NInteres::distribuir | DAlcance::codigosModuloCoordinador; DInteres::actualizarRecordatoriosPendientes; DInteres::cargaPorVendedor; DInteres::consultaAlcance; DInteres::guardar; DInteres::pendientesSinAsignar; DInteres::registrarInteraccion; DInteres::transaccion; DInteres::vendedorAsignado; DInteres::vendedorExistenteParaDocumento; DInteres::vendedoresVigentes | intereses; usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |

Diagramas: uc-cu3, cls-cu3, com-cu3, sd-cu3; navegación según actor. Pruebas: ver pruebas_inventario.json y las PRUEBAS_BLANCA/NEGRA relacionadas; no ejecutadas aquí. Hallazgos: CU-003.

Round-Robin real: agrupa pendientes por documento; reutiliza vendedor previo elegible cuando existe y, si no, elige la menor carga, resolviendo empates por el primer correo del orden disponible. Aumenta carga por cada tarjeta. No es una rotación circular estricta. Fuente: NInteres::distribuir y DInteres::cargaPorVendedor.

## CU4. Gestión de Embudo de Ventas en Tablero Kanban

Página 27, sección4.4. Actores: Administrador, Coordinador, Vendedor. Iniciador: Vendedor. Objetivo: Llevar cada prospecto por las etapas del embudo de ventas.

Descripción: El usuario ve las tarjetas de su alcance en un tablero Kanban de seis columnas y las mueve arrastrándolas o con la opción Mover a…; el sistema valida cada cambio de estado.

Precondición: El usuario tiene permiso de modificación sobre Embudo de ventas y la tarjeta está en su alcance (cartera del vendedor o programas del coordinador).

Flujo principal:

1. El usuario abre Embudo de Ventas.
2. El sistema muestra las tarjetas por estado: Nuevo, En Contacto, Seguimiento, Promesa de Pago, Convertido y Perdido.
3. El usuario arrastra una tarjeta o elige Mover a… y el estado de destino.
4. El sistema valida la regla del estado de destino y guarda el cambio.
5. El tablero muestra la tarjeta en su nueva columna.

Alternativos explícitos: No hay campo separado en la fuente de especificación; excepciones listadas no sustituyen flujos alternativos.

Excepciones documentadas:

- Tarjeta fuera de su cartera: "Este prospecto no está dentro de su cartera."
- Tarjeta convertida: "Una tarjeta convertida ya tiene matrícula: no se puede mover."
- Tarjeta cerrada: "La tarjeta ya está cerrada."
- Tarjeta sin vendedor: "La tarjeta no tiene vendedor asignado."
- Sin conexión o base de datos no disponible: la operación no se guarda y la interfaz muestra el error.

Postcondición documental: La tarjeta queda en el nuevo estado del embudo.

Pantallas y módulos P: api/intereses.js, PAgenda.jsx, PAsignacion.jsx, PEmbudo.jsx.

Clases N: NInteres, NAlcance, NConversion. Clases D/modelos: DInteres, DAlcance, Interes, Usuario, MotivoPerdida, ConsultaRequest, MoverInteresRequest.


| Endpoint | N | D alcanzables estáticamente | Tablas candidatas | Estado |
| --- | --- | --- | --- | --- |
| GET /api/intereses | NInteres::index | DAlcance::codigosModuloCoordinador; DAlcance::escaparLike; DInteres::consultaAlcance; DInteres::listar; DInteres::motivos | intereses; motivos_perdida | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/intereses/{interes} | NInteres::show | DInteres::detalle | intereses | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PATCH /api/intereses/{interes}/estado | NInteres::mover | DInteres::actualizarEstadoProspecto; DInteres::bloquear; DInteres::guardar; DInteres::obtener; DInteres::refrescarDetalle; DInteres::registrarInteraccion; DInteres::transaccion | intereses | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |

Diagramas: uc-cu4, cls-cu4, com-cu4, sd-cu4; navegación según actor. Pruebas: ver pruebas_inventario.json y las PRUEBAS_BLANCA/NEGRA relacionadas; no ejecutadas aquí. Hallazgos: SEC-001.

## CU5. Gestión de Pérdida de Prospectos y Clasificación de Motivos

Página 28, sección4.4. Actores: Administrador, Coordinador, Vendedor. Iniciador: Vendedor. Objetivo: Registrar por qué se pierde un prospecto, con un motivo clasificado.

Descripción: Al pasar una tarjeta a Perdido, el usuario elige un motivo de la lista clasificada por categoría y puede añadir una observación. El Administrador y el Coordinador registran, modifican y eliminan los motivos.

Precondición: Existen motivos de pérdida registrados y el usuario tiene permiso de modificación sobre Embudo de ventas (o sobre Motivos de pérdida para gestionarlos).

Flujo principal:

1. El usuario elige Perdido para una tarjeta del Embudo de Ventas.
2. El sistema muestra el formulario Marcar como Perdido con los motivos agrupados por categoría.
3. El usuario elige el motivo y escribe una observación.
4. El sistema guarda el estado Perdido con su motivo.
5. El Administrador o el Coordinador gestionan la lista en Motivos de Pérdida.

Alternativos explícitos: No hay campo separado en la fuente de especificación; excepciones listadas no sustituyen flujos alternativos.

Excepciones documentadas:

- Perdido sin motivo: el sistema rechaza el cambio y pide el motivo.
- Motivo repetido: "El motivo ya está registrado."
- Motivo en uso: "No se puede eliminar: hay prospectos perdidos con este motivo."
- Motivo del sistema: "Este motivo lo usa el sistema y no se puede cambiar ni eliminar."
- Sin conexión o base de datos no disponible: la operación no se guarda y la interfaz muestra el error.

Postcondición documental: La tarjeta queda en Perdido con su motivo.

Pantallas y módulos P: api/motivos.js, PMotivos.jsx.

Clases N: NMotivo. Clases D/modelos: DMotivo, Interes, MotivoPerdida, MotivoRequest.


| Endpoint | N | D alcanzables estáticamente | Tablas candidatas | Estado |
| --- | --- | --- | --- | --- |
| GET /api/motivos | NMotivo::index | DMotivo::listarConUsos | intereses; motivos_perdida | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/motivos | NMotivo::store | DMotivo::crear; DMotivo::existeNombre | motivos_perdida | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PUT /api/motivos/{motivo} | NMotivo::update | DMotivo::actualizar; DMotivo::existeNombre; DMotivo::obtener | motivos_perdida | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| DELETE /api/motivos/{motivo} | NMotivo::destroy | DMotivo::eliminar; DMotivo::estaEnUso; DMotivo::obtener | intereses; motivos_perdida | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |

Diagramas: uc-cu5, cls-cu5, com-cu5, sd-cu5; navegación según actor. Pruebas: ver pruebas_inventario.json y las PRUEBAS_BLANCA/NEGRA relacionadas; no ejecutadas aquí. Hallazgos: CL-002; SEC-001.

## CU6. Gestión de Validar Datos y Procesar Conversión a Matrícula

Página 29, sección4.4. Actores: Administrador, Coordinador, Vendedor. Iniciador: Vendedor. Objetivo: Cobrar al prospecto y convertirlo en alumno matriculado con sus datos validados.

Descripción: Desde la ficha del prospecto, el Vendedor crea una orden de pago único o en cuotas. Para una cuota pendiente puede iniciar Stripe Checkout Sandbox o registrar un comprobante de pago manual. Stripe confirma el pago mediante consulta de la sesión o webhook firmado; los comprobantes manuales son revisados por el Coordinador o Administrador. La primera cuota aprobada y los datos completos permiten convertir el interés, registrar inscripción y comisión y exportar la matrícula al SIS.

Precondición: El prospecto está en la cartera del vendedor y tiene un interés abierto.

Flujo principal:

1. El Vendedor abre la ficha del prospecto y genera una orden con módulos, descuentos y cuotas.
2. El Vendedor selecciona una cuota pendiente e inicia Stripe Checkout Sandbox.
3. El sistema valida la orden y el importe en BOB, registra la sesión y redirige a Stripe.
4. Tras el pago, el sistema consulta la sesión de retorno o procesa el webhook firmado y verifica su importe.
5. El sistema registra la transacción y marca la cuota como Pago aprobado de forma idempotente.
6. Si es la primera cuota y los datos están completos, el sistema convierte el interés y registra la inscripción y la comisión.
7. El Coordinador exporta las matrículas pendientes al SIS y registra el resultado.

Alternativos explícitos: A1. Pago manual: el Vendedor registra un método QR o transferencia y sube el comprobante; la cuota queda En revisión hasta que el Coordinador o Administrador la apruebe o rechace. / A2. Registro previo de tarjeta: el Vendedor inicia Stripe Setup; el sistema consulta la sesión de retorno y, si Stripe la confirma, asocia el método al prospecto. / A3. Checkout cancelado: el sistema consulta la sesión, conserva la cuota pendiente si no hubo confirmación y permite volver a intentar el pago. / A4. Anulación de orden: el Vendedor indica el motivo; el sistema solo anula una orden sin cuotas pagadas o en revisión ni pagos Stripe confirmados.

Excepciones documentadas:

- Orden de otro vendedor: "Solo el vendedor asignado genera la orden de pago."
- Total inválido: "El total de la orden debe ser mayor a cero."
- Orden anulada: "La orden de pago fue anulada y no admite cobros."
- Cuota ya pagada: "Esta cuota ya fue pagada."
- Cuota en revisión manual: "Esta cuota tiene un comprobante manual en revisión."
- Confirmación manual indebida: "Las cuotas procesadas por Stripe solo se confirman mediante la pasarela oficial."
- Comprobante repetido: "Ya hay un comprobante en revisión para esta cuota."
- Aprobación fuera de revisión: "Solo se aprueba una cuota en revisión."
- Conversión sin pago: "La primera cuota de una orden de pago todavía no está aprobada."
- Exportación vacía: "No hay matrículas pendientes de enviar."
- Sin conexión o base de datos no disponible: la operación no se guarda y la interfaz muestra el error.

Postcondición documental: El prospecto queda convertido en alumno, con su inscripción, comisión y exportación registradas.

Pantallas y módulos P: api/pagos.js, PPagoCuota.jsx, PPagoConfirmacion.jsx, PPagoCancelado.jsx, FormularioOrdenPago.jsx, ModalCompartirPago.jsx, MetodosPago.jsx, PlanPagos.jsx, PValidacionPagos.jsx, api/seguimiento.js, PMatriculas.jsx, api/exportaciones.js.

Clases N: NPago, NStripe, NNotificacion, Notificacion, NConversion, NAlcance, NSeguimiento, NExportacion. Clases D/modelos: DPago, Cuota, DStripe, OrdenPago, TransaccionStripe, Interes, MetodoPago, DNotificacion, DAlcance, Prospecto, ConsultaRequest, Usuario, Descuento, CrearSetupTarjetaRequest, CambiarEstadoMetodoRequest, CatalogoCache, Pago, CrearOrdenRequest, ConfigurarEnvioOrdenRequest, AnularOrdenRequest, CrearCheckoutRequest, ComprobantePago, AprobarCuotaRequest, RechazarCuotaRequest, DSeguimiento, InscripcionComercial, DExportacion, Exportacion, RegistrarResultadoRequest.


| Endpoint | N | D alcanzables estáticamente | Tablas candidatas | Estado |
| --- | --- | --- | --- | --- |
| POST /api/stripe/webhook | NPago::webhook | DAlcance::escaparLike; DAlcance::prospectos; DNotificacion::crear; DNotificacion::existeNotificacionEnviada; DPago::actualizarInteres; DPago::interesBloqueado; DPago::montoCuotasEnEstado; DPago::prospecto; DPago::prospectoEnCartera; DPago::registrarInteraccion; DStripe::actualizarTransaccion; DStripe::cuotaBloqueada; DStripe::eventoWebhook; DStripe::ordenConDetalle; DStripe::registrarEventoWebhook; DStripe::registrarMetodoStripe; DStripe::transaccion; DStripe::transaccionAbiertaPorCuota; DStripe::transaccionPorPaymentIntent; DStripe::transaccionPorSesion; DStripe::transaccionPorSesionBloqueada; DStripe::vencimientoMetodoStripe | cuotas; intereses; metodos_pago; notificaciones; ordenes_pago; prospectos; transacciones_stripe; webhook_eventos_stripe | DESACTUALIZADO |
| GET /api/pagos/publico/cuotas/{token} | NPago::abrirEnlaceCuotaPublico | DAlcance::escaparLike; DNotificacion::crear; DNotificacion::existeNotificacionEnviada; DPago::actualizarInteres; DPago::asegurarTokenCuota; DPago::cuotaPorToken; DPago::interesBloqueado; DPago::montoCuotasEnEstado; DPago::registrarInteraccion; DStripe::actualizarTransaccion; DStripe::contarIntentosCuota; DStripe::crearTransaccion; DStripe::cuotaBloqueada; DStripe::guardarClienteProspecto; DStripe::ordenConDetalle; DStripe::prospectoBloqueado; DStripe::registrarMetodoStripe; DStripe::transaccion; DStripe::transaccionAbiertaPorCuota; DStripe::transaccionPorSesion; DStripe::transaccionPorSesionBloqueada | cuotas; intereses; metodos_pago; notificaciones; ordenes_pago; prospectos; transacciones_stripe | DESACTUALIZADO |
| GET /api/pagos/publico/sesiones/{sessionId} | NPago::consultarRetornoPublico | DAlcance::escaparLike; DAlcance::prospectos; DNotificacion::crear; DNotificacion::existeNotificacionEnviada; DPago::actualizarInteres; DPago::interesBloqueado; DPago::montoCuotasEnEstado; DPago::prospecto; DPago::prospectoEnCartera; DPago::registrarInteraccion; DStripe::actualizarTransaccion; DStripe::cuotaBloqueada; DStripe::ordenConDetalle; DStripe::registrarMetodoStripe; DStripe::transaccion; DStripe::transaccionPorSesion; DStripe::transaccionPorSesionBloqueada; DStripe::vencimientoMetodoStripe | cuotas; intereses; metodos_pago; notificaciones; ordenes_pago; prospectos; transacciones_stripe | DESACTUALIZADO |
| POST /api/pagos/publico/sesiones/{sessionId}/cancelar | NPago::cancelarRetornoPublico | DAlcance::escaparLike; DNotificacion::crear; DNotificacion::existeNotificacionEnviada; DPago::actualizarInteres; DPago::interesBloqueado; DPago::montoCuotasEnEstado; DPago::prospecto; DPago::registrarInteraccion; DStripe::actualizarTransaccion; DStripe::cuotaBloqueada; DStripe::ordenConDetalle; DStripe::registrarMetodoStripe; DStripe::transaccion; DStripe::transaccionPorSesion; DStripe::transaccionPorSesionBloqueada; DStripe::vencimientoMetodoStripe | cuotas; intereses; metodos_pago; notificaciones; ordenes_pago; prospectos; transacciones_stripe | DESACTUALIZADO |
| GET /api/descuentos | NPago::descuentos | DPago::descuentos | descuentos | DESACTUALIZADO |
| GET /api/prospectos/{prospecto}/metodos-pago | NPago::metodos | DAlcance::prospectos; DPago::metodos; DPago::prospecto; DPago::prospectoEnCartera | prospectos | DESACTUALIZADO |
| POST /api/prospectos/{prospecto}/metodos-pago | NPago::registrarMetodo | DAlcance::prospectos; DPago::prospecto; DPago::prospectoEnCartera | prospectos | DESACTUALIZADO |
| POST /api/prospectos/{prospecto}/metodos-pago/stripe-setup | NPago::crearSetupTarjeta | DAlcance::prospectos; DPago::prospecto; DPago::prospectoEnCartera; DStripe::actualizarTransaccion; DStripe::crearTransaccion; DStripe::guardarClienteProspecto; DStripe::prospectoBloqueado; DStripe::registrarMetodoStripe; DStripe::transaccion; DStripe::transaccionPorSesion; DStripe::transaccionPorSesionBloqueada; DStripe::transaccionSetupAbierta; DStripe::vencimientoMetodoStripe | metodos_pago; prospectos; transacciones_stripe | DESACTUALIZADO |
| PATCH /api/metodos-pago/{metodo}/estado | NPago::cambiarEstadoMetodo | DAlcance::prospectos; DPago::actualizarMetodo; DPago::metodo; DPago::metodoConProspecto; DPago::prospectoEnCartera | metodos_pago; prospectos | DESACTUALIZADO |
| GET /api/ordenes-pago | NPago::ordenes | DAlcance::intereses; DPago::ordenes | ordenes_pago | DESACTUALIZADO |
| POST /api/intereses/{interes}/ordenes-pago | NPago::crearOrden | DNotificacion::crear; DPago::actualizarInteres; DPago::cantidadModulosAbiertos; DPago::crearOrden; DPago::crearPago; DPago::descuentosPorCodigo; DPago::insertarCuotas; DPago::insertarDescuentosOrden; DPago::insertarItems; DPago::interes; DPago::interesBloqueado; DPago::marcarEnvioCuota; DPago::modulos; DPago::ordenAbierta; DPago::ordenCompleta; DPago::registrarInteraccion; DPago::transaccion | catalogo_cache; cuotas; descuentos; intereses; notificaciones; orden_pago_descuentos; ordenes_pago; pagos | DESACTUALIZADO |
| PATCH /api/ordenes-pago/{orden}/envio-automatico | NPago::configurarEnvioAutomatico | DPago::actualizarOrden; DPago::interesDeOrden; DPago::orden; DPago::ordenCompleta | ordenes_pago | DESACTUALIZADO |
| PATCH /api/ordenes-pago/{orden}/anular | NPago::anularOrden | DAlcance::escaparLike; DNotificacion::crear; DNotificacion::existeNotificacionEnviada; DPago::actualizarInteres; DPago::actualizarOrden; DPago::hayCuotasEnEstados; DPago::interesBloqueado; DPago::montoCuotasEnEstado; DPago::registrarInteraccion; DStripe::actualizarTransaccion; DStripe::cuotaBloqueada; DStripe::hayTransaccionesEnEstado; DStripe::ordenBloqueada; DStripe::ordenConDetalle; DStripe::registrarMetodoStripe; DStripe::transaccion; DStripe::transaccionPorSesion; DStripe::transaccionPorSesionBloqueada; DStripe::transaccionesPendientesDeOrden | cuotas; intereses; metodos_pago; notificaciones; ordenes_pago; transacciones_stripe | DESACTUALIZADO |
| POST /api/ordenes-pago/{orden}/cuotas/{cuota}/comprobante | NPago::registrarComprobante | DPago::interesDeOrden; DPago::orden | ordenes_pago | DESACTUALIZADO |
| POST /api/ordenes-pago/{orden}/cuotas/{cuota}/checkout | NPago::crearCheckout | DAlcance::escaparLike; DNotificacion::crear; DNotificacion::existeNotificacionEnviada; DPago::actualizarInteres; DPago::asegurarTokenCuota; DPago::interesBloqueado; DPago::montoCuotasEnEstado; DPago::registrarInteraccion; DStripe::actualizarTransaccion; DStripe::contarIntentosCuota; DStripe::crearTransaccion; DStripe::cuotaBloqueada; DStripe::guardarClienteProspecto; DStripe::ordenConDetalle; DStripe::prospectoBloqueado; DStripe::registrarMetodoStripe; DStripe::transaccion; DStripe::transaccionAbiertaPorCuota; DStripe::transaccionPorSesion; DStripe::transaccionPorSesionBloqueada | cuotas; intereses; metodos_pago; notificaciones; ordenes_pago; prospectos; transacciones_stripe | DESACTUALIZADO |
| GET /api/pagos/stripe/sesiones/{sessionId} | NPago::confirmarCheckout | DAlcance::escaparLike; DAlcance::prospectos; DNotificacion::crear; DNotificacion::existeNotificacionEnviada; DPago::actualizarInteres; DPago::interesBloqueado; DPago::montoCuotasEnEstado; DPago::prospecto; DPago::prospectoEnCartera; DPago::registrarInteraccion; DStripe::actualizarTransaccion; DStripe::cuotaBloqueada; DStripe::ordenConDetalle; DStripe::registrarMetodoStripe; DStripe::transaccion; DStripe::transaccionPorSesion; DStripe::transaccionPorSesionBloqueada; DStripe::vencimientoMetodoStripe | cuotas; intereses; metodos_pago; notificaciones; ordenes_pago; prospectos; transacciones_stripe | DESACTUALIZADO |
| POST /api/pagos/stripe/sesiones/{sessionId}/cancelar | NPago::cancelarCheckout | DAlcance::escaparLike; DAlcance::prospectos; DNotificacion::crear; DNotificacion::existeNotificacionEnviada; DPago::actualizarInteres; DPago::interesBloqueado; DPago::montoCuotasEnEstado; DPago::prospecto; DPago::prospectoEnCartera; DPago::registrarInteraccion; DStripe::actualizarTransaccion; DStripe::cuotaBloqueada; DStripe::ordenConDetalle; DStripe::registrarMetodoStripe; DStripe::transaccion; DStripe::transaccionPorSesion; DStripe::transaccionPorSesionBloqueada | cuotas; intereses; metodos_pago; notificaciones; ordenes_pago; prospectos; transacciones_stripe | DESACTUALIZADO |
| GET /api/cuotas | NPago::cuotas | DAlcance::intereses; DPago::cuotas | comprobantes_pago; cuotas | DESACTUALIZADO |
| PATCH /api/ordenes-pago/{orden}/cuotas/{cuota}/aprobar | NPago::aprobar | DPago::actualizarComprobantes; DPago::cuotaBloqueada; DPago::interesBloqueado; DPago::interesDeOrden; DPago::orden; DPago::registrarInteraccion; DPago::transaccion | comprobantes_pago; cuotas; intereses; ordenes_pago | DESACTUALIZADO |
| PATCH /api/ordenes-pago/{orden}/cuotas/{cuota}/rechazar | NPago::rechazar | DPago::actualizarComprobantes; DPago::cuotaBloqueada; DPago::interesDeOrden; DPago::orden; DPago::transaccion | comprobantes_pago; cuotas; ordenes_pago | DESACTUALIZADO |
| GET /api/comprobantes/{comprobante} | NPago::comprobante | DPago::comprobante; DPago::ordenDeComprobante | comprobantes_pago; ordenes_pago | DESACTUALIZADO |
| GET /api/inscripciones | NSeguimiento::inscripciones | DAlcance::intereses; DSeguimiento::inscripciones | inscripciones_comerciales | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/exportaciones/pendientes | NExportacion::pendientes | DAlcance::codigosModuloCoordinador; DExportacion::consultaExportables; DExportacion::exportables | inscripciones_comerciales | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/exportaciones | NExportacion::exportar | DAlcance::codigosModuloCoordinador; DExportacion::consultaExportables; DExportacion::exportarPendientes | exportaciones; inscripciones_comerciales | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/exportaciones | NExportacion::historial | DAlcance::codigosModuloCoordinador; DExportacion::historial | exportaciones | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PATCH /api/exportaciones/{exportacion} | NExportacion::registrarResultado | DAlcance::codigosModuloCoordinador; DExportacion::historial; DExportacion::registrarResultado | exportaciones | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |

Diagramas: uc-cu6, cls-cu6, com-cu6, sd-cu6; navegación según actor. Pruebas: ver pruebas_inventario.json y las PRUEBAS_BLANCA/NEGRA relacionadas; no ejecutadas aquí. Hallazgos: PAG-001; CU-002; CU-004; BD-001; SEC-002.

Estado por subflujo: orden/cuotas/Checkout/Setup/anulación/exportación tienen soporte; nuevos QR/transferencia/comprobantes están expresamente bloqueados. Histórico manual es consultable. El nombre del CU no queda completamente satisfecho por la figura de secuencia porque no muestra NConversion. La comisión nace al convertir por cada solicitud, no al cobrar todo el plan.

## CU7. Gestión de Bitácora, Interacciones y Recordatorios

Página 31, sección4.4. Actores: Administrador, Coordinador, Vendedor. Iniciador: Vendedor. Objetivo: Registrar el seguimiento de cada prospecto para que ningún contacto se olvide.

Descripción: En la ficha del prospecto el usuario ve el historial cronológico de la tarjeta, registra interacciones y notas y agenda recordatorios; en Mi Día ve su agenda y marca los recordatorios realizados. Las notificaciones internas avisan de las novedades.

Precondición: La tarjeta está en el alcance del usuario.

Flujo principal:

1. El Vendedor abre Seguimiento y Agenda y elige una tarjeta.
2. El sistema muestra la ficha con el historial cronológico, los recordatorios y las órdenes de pago.
3. El Vendedor registra una interacción con su tipo, descripción y resultado.
4. El Vendedor agenda un recordatorio con fecha, hora y descripción.
5. En Mi Día, el Vendedor marca el recordatorio como realizado con su resultado, o lo cancela.
6. El usuario consulta sus notificaciones y las marca como leídas.

Alternativos explícitos: No hay campo separado en la fuente de especificación; excepciones listadas no sustituyen flujos alternativos.

Excepciones documentadas:

- Fecha pasada: "La actividad debe programarse para una fecha y hora futura."
- Actividad cerrada: "La actividad ya fue realizada o cancelada."
- Notificación a un prospecto ajeno: "Solo puede escribir a prospectos de su cartera."
- Sin conexión o base de datos no disponible: la operación no se guarda y la interfaz muestra el error.

Postcondición documental: La interacción y el recordatorio quedan en el historial de la tarjeta.

Pantallas y módulos P: api/seguimiento.js, PAgenda.jsx, PMiDia.jsx, api/notificaciones.js, PNotificaciones.jsx, ModalCompartirPago.jsx.

Clases N: NSeguimiento, NAlcance, NNotificacion, Notificacion. Clases D/modelos: DSeguimiento, Interes, Interaccion, RegistrarInteraccionRequest, CrearRecordatorioRequest, DAlcance, Usuario, Recordatorio, ConsultaRequest, CompletarRecordatorioRequest, DNotificacion, Prospecto, EnviarNotificacionRequest.


| Endpoint | N | D alcanzables estáticamente | Tablas candidatas | Estado |
| --- | --- | --- | --- | --- |
| POST /api/intereses/{interes}/interacciones | NSeguimiento::registrarInteraccion | DSeguimiento::actualizarInteres; DSeguimiento::cargarInteraccion; DSeguimiento::interes; DSeguimiento::registrarInteraccion; DSeguimiento::transaccion | intereses | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/intereses/{interes}/recordatorios | NSeguimiento::crearRecordatorio | DSeguimiento::actualizarInteres; DSeguimiento::crearRecordatorio; DSeguimiento::interes; DSeguimiento::transaccion | intereses | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/recordatorios | NSeguimiento::recordatorios | DAlcance::intereses; DSeguimiento::listarRecordatorios | recordatorios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PATCH /api/recordatorios/{recordatorio}/completar | NSeguimiento::completarRecordatorio | DSeguimiento::actualizarInteres; DSeguimiento::buscarRecordatorioBloqueado; DSeguimiento::cargarInteresRecordatorio; DSeguimiento::insertarInteraccion; DSeguimiento::obtenerRecordatorio; DSeguimiento::recordatorio; DSeguimiento::transaccion | interacciones; recordatorios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PATCH /api/recordatorios/{recordatorio}/cancelar | NSeguimiento::cancelarRecordatorio | DSeguimiento::cargarInteresRecordatorio; DSeguimiento::obtenerRecordatorio; DSeguimiento::recordatorio | recordatorios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/notificaciones | NNotificacion::index | DNotificacion::listar | notificaciones | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| POST /api/notificaciones | NNotificacion::enviar | DNotificacion::crear; DNotificacion::prospectoAsignadoA | notificaciones; prospectos | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PATCH /api/notificaciones/{notificacion}/leida | NNotificacion::marcarLeida | DNotificacion::marcarLeida; DNotificacion::obtener | notificaciones | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |

Diagramas: uc-cu7, cls-cu7, com-cu7, sd-cu7; navegación según actor. Pruebas: ver pruebas_inventario.json y las PRUEBAS_BLANCA/NEGRA relacionadas; no ejecutadas aquí. Hallazgos: CU-001; NOT-001.

## CU8. Reportes y Estadísticas

Página 32, sección4.4. Actores: Administrador, Coordinador, Vendedor. Iniciador: Coordinador. Objetivo: Medir el avance comercial y el uso del sistema.

Descripción: El usuario consulta el dashboard con indicadores y gráficos, los reportes como listados filtrados por fechas, estado y vendedor, y las estadísticas porcentuales del embudo; en Ventas y Comisiones se consultan y pagan las comisiones de los vendedores.

Precondición: El usuario tiene permiso de lectura sobre Dashboard, Reportes y estadísticas o Ventas y comisiones.

Flujo principal:

1. El usuario abre el Dashboard y ve los indicadores y gráficos de su alcance.
2. El usuario abre Reportes y Estadísticas y filtra por fechas, estado y vendedor.
3. El sistema muestra el listado y las estadísticas porcentuales.
4. El usuario descarga el listado en CSV.
5. En Ventas y Comisiones, el usuario con permiso de modificación consulta el resumen y paga las comisiones; solo el Administrador cambia el porcentaje de comisión.

Alternativos explícitos: No hay campo separado en la fuente de especificación; excepciones listadas no sustituyen flujos alternativos.

Excepciones documentadas:

- Porcentaje de comisión: "Solo el administrador cambia el porcentaje de comisión."
- Sin permiso: "No tiene permiso para realizar esta acción."
- Sin conexión o base de datos no disponible: la operación no se guarda y la interfaz muestra el error.

Postcondición documental: El usuario obtiene los reportes y estadísticas de su alcance; las comisiones pagadas quedan registradas.

Pantallas y módulos P: api/seguimiento.js, PComisiones.jsx, api/reportes.js, PDashboard.jsx, PMiDia.jsx, PReportes.jsx.

Clases N: NSeguimiento, NReporte, NAcceso. Clases D/modelos: DSeguimiento, DAlcance, Usuario, Comision, ConsultaRequest, ActualizarComisionRequest, DReporte, Interes, ListadoRequest.


| Endpoint | N | D alcanzables estáticamente | Tablas candidatas | Estado |
| --- | --- | --- | --- | --- |
| GET /api/comisiones | NSeguimiento::comisiones | DAlcance::intereses; DSeguimiento::comisiones; DSeguimiento::porcentajeComision | comisiones | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/comisiones/resumen | NSeguimiento::resumenComisiones | DAlcance::intereses; DSeguimiento::comisiones; DSeguimiento::resumenComisiones | comisiones; usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PATCH /api/comisiones/vendedores/{vendedor}/pagar | NSeguimiento::pagarComisiones | DAlcance::intereses; DSeguimiento::pagarComisiones; DSeguimiento::usuario | comisiones; usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/configuracion/comision | NSeguimiento::configuracionComision | DSeguimiento::porcentajeComision | comisiones | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| PUT /api/configuracion/comision | NSeguimiento::actualizarConfiguracionComision | DSeguimiento::actualizarPorcentajeComision; DSeguimiento::porcentajeComision | comisiones; configuraciones | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/dashboard | NReporte::dashboard | DAlcance::codigosModuloCoordinador; DReporte::dashboard; DReporte::tarjetas | bitacora; intereses; permisos; recursos | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/estadisticas/vendedor | NReporte::estadisticasVendedor | DReporte::estadisticasVendedor | comisiones; interacciones; intereses; recordatorios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/reportes/estadisticas | NReporte::estadisticas | DAlcance::codigosModuloCoordinador; DAlcance::escaparLike; DReporte::estadisticas; DReporte::filtrar; DReporte::tarjetas | intereses | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |
| GET /api/reportes/listado | NReporte::listado | DAlcance::codigosModuloCoordinador; DAlcance::escaparLike; DReporte::filtrar; DReporte::listado; DReporte::tarjetas; DReporte::vendedores | intereses; usuarios | TRAZA ESTÁTICA; tablas candidatas, relaciones Eloquent dinámicas requieren revisión |

Diagramas: uc-cu8, cls-cu8, com-cu8, sd-cu8; navegación según actor. Pruebas: ver pruebas_inventario.json y las PRUEBAS_BLANCA/NEGRA relacionadas; no ejecutadas aquí. Hallazgos: PAG-002; QA-001.

## Clasificación y propuestas justificadas

A: Los 8 CU macro tienen código. B: No se demostró un CU macro totalmente inexistente; sí las operaciones nuevas manuales de CU6 están bloqueadas. C/H: Hay objetivos públicos y de registro de tarjeta insuficientemente descritos. D: CU1/CU6/CU7 requieren actualización de nombres o alcance. E: No se localizaron IDs macro duplicados; CU01/CU1 son representaciones del mismo identificador. F: CU4 y CU5 comparten mover; se recomienda conservar IDs y documentar pérdida como especialización/subflujo. G: CU6 conviene descomponer en subobjetivos sin renumerar los ocho CU.


| ID propuesto | Nombre | Actor/objetivo | Justificación y código existente | Diagramas y relación |
| --- | --- | --- | --- | --- |
| CU6.1 (propuesto) | Pagar una cuota mediante enlace público | Prospecto sin sesión: cancelar su cuota y consultar resultado | PPagoCuota/PPagoConfirmacion; NPago::abrirEnlaceCuotaPublico y consultarRetornoPublico; no rol Cliente autenticado | Especificación, asociación con Stripe, secuencia con token y estados; subobjetivo de CU6 |
| CU6.2 (propuesto) | Registrar tarjeta con Stripe Setup | Prospecto sin sesión: autorizar registro remoto sin cobro | NPago::crearSetupTarjeta, NStripe::iniciarSetupTarjeta; confirmado en retorno tipo setup | Especificación y secuencia separada por no equivaler a pago; extensión/alternativa deCU6 cuya relación UML final debe justificarse |

Correos, idempotencia, webhook y scheduler son operaciones de soporte a estos objetivos, no CU humanos adicionales por defecto. Gestionar preferencias de apariencia puede describirse como función transversal sin CU nuevo obligatorio. No se aplicó ninguna renumeración.
