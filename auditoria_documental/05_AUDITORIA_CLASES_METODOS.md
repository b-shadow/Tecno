# Clases, métodos, atributos y relaciones P/N/D

Commit auditado: `5bf47b2e863631908e37718fb343fd776003fb5b`. Fecha: 26/11/2026 (America/La_Paz). Solo lectura de originales.

Inventario estático: 111 clases PHP y521 métodos declarados en negocio/app y datos/src.58 nombres PHP documentados en figuras de clase, con305 apariciones de operación PHP; todos esos nombres de clase y métodos existen.303 firmas coinciden en parámetros tipados/orden, retorno y visibilidad en la comparación automatizada; dos no coinciden (CL-001). Valores por defecto, referencias y variádicos no quedan certificados globalmente por el extractor. Este conteo no incluye métodos heredados del framework.

P*.jsx son componentes funcionales React; api/*.js son módulos, no clases PHP. Su representación UML es una abstracción válida si se indica boundary/module. Los modelos Eloquent heredan atributos de persistencia dinámicos: una columna no exige una propiedad PHP declarada con $. Las cajas de modelo que ocultan atributos no demuestran que esos atributos no existan. Las diferencias por columna están en07.


| Clase documentada | Archivo real | Capa | Diagramas EA | Responsabilidad |
| --- | --- | --- | --- | --- |
| ApiToken | datos/src/Modelos/ApiToken.php | D | 1 | Modelo Eloquent |
| Bitacora | datos/src/Modelos/Bitacora.php | D | 1 | Modelo Eloquent |
| CatalogoCache | datos/src/Modelos/CatalogoCache.php | D | 2, 3, 138 | Modelo Eloquent |
| Comision | datos/src/Modelos/Comision.php | D | 8 | Modelo Eloquent |
| ComprobantePago | datos/src/Modelos/ComprobantePago.php | D | 138 | Modelo Eloquent |
| Cuota | datos/src/Modelos/Cuota.php | D | 138 | Modelo Eloquent |
| DAcceso | datos/src/DAcceso.php | D | 1 | Persistencia |
| DAlcance | datos/src/DAlcance.php | D | 1, 3, 4, 7, 8, 138 | Persistencia |
| DAuth | datos/src/DAuth.php | D | 1 | Persistencia |
| DBitacora | datos/src/DBitacora.php | D | 1 | Persistencia |
| DCatalogo | datos/src/DCatalogo.php | D | 2 | Persistencia |
| DExportacion | datos/src/DExportacion.php | D | 138 | Persistencia |
| DInteres | datos/src/DInteres.php | D | 3, 4 | Persistencia |
| DMotivo | datos/src/DMotivo.php | D | 5 | Persistencia |
| DNotificacion | datos/src/DNotificacion.php | D | 7 | Persistencia |
| DPago | datos/src/DPago.php | D | 138 | Persistencia |
| DProspecto | datos/src/DProspecto.php | D | 2, 3 | Persistencia |
| DReporte | datos/src/DReporte.php | D | 8 | Persistencia |
| DSeguimiento | datos/src/DSeguimiento.php | D | 7, 8, 138 | Persistencia |
| DSeguridad | datos/src/DSeguridad.php | D | 1 | Persistencia |
| DSitio | datos/src/DSitio.php | D | 1 | Persistencia |
| DStripe | datos/src/DStripe.php | D | 138 | Persistencia |
| DUsuario | datos/src/DUsuario.php | D | 1 | Persistencia |
| Descuento | datos/src/Modelos/Descuento.php | D | 138 | Persistencia |
| Exportacion | datos/src/Modelos/Exportacion.php | D | 138 | Modelo Eloquent |
| InscripcionComercial | datos/src/Modelos/InscripcionComercial.php | D | 138 | Modelo Eloquent |
| Interaccion | datos/src/Modelos/Interaccion.php | D | 7 | Modelo Eloquent |
| Interes | datos/src/Modelos/Interes.php | D | 1, 2, 3, 4, 5, 7, 8, 138 | Modelo Eloquent |
| MetodoPago | datos/src/Modelos/MetodoPago.php | D | 138 | Modelo Eloquent |
| MotivoPerdida | datos/src/Modelos/MotivoPerdida.php | D | 4, 5 | Modelo Eloquent |
| NAcceso | negocio/app/Negocio/NAcceso.php | N | 1, 3, 8 | Reglas/API |
| NAlcance | negocio/app/Negocio/NAlcance.php | N | 3, 4, 7, 138 | Reglas/API |
| NAuth | negocio/app/Negocio/NAuth.php | N | 1 | Reglas/API |
| NCatalogo | negocio/app/Negocio/NCatalogo.php | N | 2 | Reglas/API |
| NCatalogoExterno | negocio/app/Negocio/NCatalogoExterno.php | N | 2 | Reglas/API |
| NConversion | negocio/app/Negocio/NConversion.php | N | 4, 138 | Reglas/API |
| NExportacion | negocio/app/Negocio/NExportacion.php | N | 138 | Reglas/API |
| NFoto | negocio/app/Negocio/NFoto.php | N | 1 | Reglas/API |
| NInteres | negocio/app/Negocio/NInteres.php | N | 3, 4 | Reglas/API |
| NMotivo | negocio/app/Negocio/NMotivo.php | N | 5 | Reglas/API |
| NNotificacion | negocio/app/Negocio/NNotificacion.php | N | 7 | Reglas/API |
| NPago | negocio/app/Negocio/NPago.php | N | 138 | Reglas/API |
| NProspecto | negocio/app/Negocio/NProspecto.php | N | 2, 3 | Reglas/API |
| NReporte | negocio/app/Negocio/NReporte.php | N | 8 | Reglas/API |
| NSeguimiento | negocio/app/Negocio/NSeguimiento.php | N | 7, 8, 138 | Reglas/API |
| NSeguridad | negocio/app/Negocio/NSeguridad.php | N | 1 | Reglas/API |
| NSitio | negocio/app/Negocio/NSitio.php | N | 1 | Reglas/API |
| NStripe | negocio/app/Negocio/NStripe.php | N | 138 | Reglas/API |
| NUsuario | negocio/app/Negocio/NUsuario.php | N | 1 | Reglas/API |
| Notificacion | datos/src/Modelos/Notificacion.php | D | 7 | Reglas/API |
| OrdenPago | datos/src/Modelos/OrdenPago.php | D | 138 | Modelo Eloquent |
| Pago | datos/src/Modelos/Pago.php | D | 138 | Modelo Eloquent |
| Programa | datos/src/Modelos/Programa.php | D | 1, 2 | Modelo Eloquent |
| ProgramaResponsable | datos/src/Modelos/ProgramaResponsable.php | D | 1 | Modelo Eloquent |
| Prospecto | datos/src/Modelos/Prospecto.php | D | 2, 3, 7, 138 | Modelo Eloquent |
| Recordatorio | datos/src/Modelos/Recordatorio.php | D | 7 | Modelo Eloquent |
| TransaccionStripe | datos/src/Modelos/TransaccionStripe.php | D | 138 | Modelo Eloquent |
| Usuario | datos/src/Modelos/Usuario.php | D | 1, 3, 4, 7, 8, 138 | Modelo Eloquent |

## Operaciones documentadas, parámetros, retorno y visibilidad

Cada fila es una aparición en una figura. La evidencia exacta con línea/firma real está en comparacion_metodos_ea.json; para no repetir el código completo se presenta la firma tipada resumida.

| Diagrama | Clase | Operación | Parámetros UML | Retorno UML | Visibilidad | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | NAuth | login | LoginRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NAuth | sesion | Usuario:usuario | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 1 | NAuth | usuarioOpcional | ?string:tokenPlano | ?Usuario | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NAuth | me | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NAuth | actualizarPerfil | ActualizarPerfilRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NAuth | cambiarPassword | CambiarPasswordRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NAuth | logout | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DAuth | usuarioPorCorreo | string:correo | ?Usuario | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DAuth | crearToken | string:correo, string:tokenPlano | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DAuth | tokenPorPlano | string:tokenPlano | ?ApiToken | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DAuth | actualizarUsuario | Usuario:usuario, array:datos | Usuario | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DAuth | revocarOtrosTokens | Usuario:usuario, string:tokenActual | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DAuth | eliminarToken | ?ApiToken:token | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DBitacora | registrar | string:evento, string:ip, ?string:navegador, ?string:usuario, ?string:recurso, ?string:correoIntentado | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NAcceso | menu | Usuario:usuario | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NAcceso | permite | ?Usuario:usuario, string:recurso, string:nivel | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NAcceso | olvidar |  | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DAcceso | menuPorRol | string:rol | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NSitio | visita | VisitaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NSitio | buscar | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DSitio | recursoPorRuta | string:ruta | ?object | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DSitio | visitas | string:codigo | int | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DSitio | buscarCatalogo | string:like | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DSitio | buscarIntereses | string:like, Usuario:usuario | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DSitio | buscarUsuarios | string:like | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DSitio | buscarPaginas | string:like, string:rol | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DAlcance | codigosModuloCoordinador | string:correo | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NFoto | guardar | string:dataUrl, string:apellido, string:nombre, ?string:anterior | string | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NUsuario | index | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NUsuario | store | UsuarioRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NUsuario | guardarExtras | Usuario:usuario, array:datos | void | Private | COINCIDE FIRMA (defaults no certificados) |
| 1 | NUsuario | update | UsuarioRequest:r, string:usuario | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NUsuario | conservarAdministrador | Usuario:usuario, array:datos | void | Private | COINCIDE FIRMA (defaults no certificados) |
| 1 | NUsuario | cambiarEstado | CambiarEstadoUsuarioRequest:r, string:usuario | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NUsuario | vendedores |  | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | listar | array:filtros | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | transaccion | callable:operacion | mixed | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | crear | array:datos | Usuario | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | fresco | Usuario:usuario, bool:conProgramas | Usuario | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | actualizar | Usuario:usuario, array:datos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | asignarProgramas | Usuario:usuario, array:codigos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | quitarProgramas | string:correo | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | bloquearAdministradoresActivos |  | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | obtener | string:correo | Usuario | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | revocarTokens | Usuario:usuario, ?string:excepto | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | existeOtroAdministradorActivo | string:correo | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DUsuario | vendedores |  | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NSeguridad | matriz |  | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NSeguridad | asignar | AsignarPermisoRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NSeguridad | bitacora | BitacoraRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | NSeguridad | resumen |  | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DSeguridad | matriz |  | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DSeguridad | guardarPermiso | array:clave, ?string:acceso | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DSeguridad | bitacora | array:filtros | LengthAwarePaginator | Public | COINCIDE FIRMA (defaults no certificados) |
| 1 | DSeguridad | resumen | Carbon:desde | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | NCatalogo | programas | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | NCatalogo | sincronizar |  | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | NCatalogoExterno | ofertas |  | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | NCatalogoExterno | programas |  | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 2 | NCatalogoExterno | modulo | string:nombre, int:precio, string:slug, string:descripcion | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 2 | DCatalogo | programasAbiertos |  | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | DCatalogo | sincronizar | Collection:ofertas | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | NProspecto | registrarInteres | RegistrarInteresRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | NProspecto | modulosSolicitados | array:datos | Collection | Private | COINCIDE FIRMA (defaults no certificados) |
| 2 | NProspecto | soloPersona | array:datos | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 2 | NProspecto | crearIntereses | Prospecto:prospecto, Collection:modulos, ?string:vendedor | Collection | Private | COINCIDE FIRMA (defaults no certificados) |
| 2 | DProspecto | transaccion | callable:operacion | mixed | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | DProspecto | encontrarPorDocumentoOCorreoBloqueado | string:documento, string:correo | ?Prospecto | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | DProspecto | crear | array:datos | Prospecto | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | DProspecto | modulosSolicitados | array:datos | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | DProspecto | vendedorExistente | Prospecto:prospecto | ?string | Public | COINCIDE FIRMA (defaults no certificados) |
| 2 | DProspecto | crearInteres | Prospecto:prospecto, CatalogoCache:modulo, ?string:vendedor | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | NProspecto | index | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | NProspecto | store | StoreProspectoRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | NProspecto | autorizarAlta | Usuario:usuario | void | Private | COINCIDE FIRMA (defaults no certificados) |
| 3 | NProspecto | soloPersona | array:datos | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 3 | NProspecto | crearIntereses | Prospecto:prospecto, Collection:modulos, ?string:vendedor | Collection | Private | COINCIDE FIRMA (defaults no certificados) |
| 3 | NProspecto | modulosSolicitados | array:datos | Collection | Private | COINCIDE FIRMA (defaults no certificados) |
| 3 | NProspecto | importarCSV | ImportarCsvRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | NProspecto | cargarCsv | Usuario:usuario, string:csv | int | Private | COINCIDE FIRMA (defaults no certificados) |
| 3 | NProspecto | leerCsv | string:texto | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 3 | NProspecto | update | UpdateProspectoRequest:r, string:prospecto | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | buscar | Usuario:usuario, string:texto, ?string:origen | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | transaccion | callable:operacion | mixed | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | crear | array:datos | Prospecto | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | conIntereses | Prospecto:prospecto | Prospecto | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | vendedorExistente | Prospecto:prospecto | ?string | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | crearInteres | Prospecto:prospecto, CatalogoCache:modulo, ?string:vendedor | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | modulosSolicitados | array:datos | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | existeDocumentoOCorreo | string:documento, string:correo | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | obtener | string:documento | Prospecto | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | estaDentroDeCartera | Prospecto:prospecto, Usuario:usuario | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | actualizar | Prospecto:prospecto, array:datos | Prospecto | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DProspecto | actualizado | Prospecto:prospecto | Prospecto | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DAlcance | prospectos | Builder:query, Usuario:usuario | Builder | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DAlcance | intereses | Builder:query, Usuario:usuario, string:tabla | Builder | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DAlcance | codigosModuloCoordinador | string:correo | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | NAcceso | permite | ?Usuario:usuario, string:recurso, string:nivel | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | NInteres | asignar | AsignarInteresRequest:r, int:interes | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | NInteres | asignarA | Interes:interes, Usuario:vendedor, Usuario:quien | void | Private | COINCIDE FIRMA (defaults no certificados) |
| 3 | NInteres | distribuir | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | obtener | int:numero | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | vendedor | string:correo | Usuario | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | transaccion | callable:operacion | mixed | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | refrescarDetalle | Interes:interes | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | vendedorAsignado | Interes:interes | ?Usuario | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | guardar | Interes:interes, array:datos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | actualizarRecordatoriosPendientes | Interes:interes, string:vendedor | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | registrarInteraccion | Interes:interes, array:datos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | vendedoresVigentes |  | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | cargaPorVendedor | array:correos | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | pendientesSinAsignar | Usuario:usuario | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | consultaAlcance | Usuario:usuario | No aplica | Private | COINCIDE FIRMA (defaults no certificados) |
| 3 | DInteres | vendedorExistenteParaDocumento | string:documento, array:correos | ?string | Public | COINCIDE FIRMA (defaults no certificados) |
| 3 | NAlcance | autorizarTarjeta | Usuario:usuario, object:interes | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | NAlcance | autorizarTarjeta | Usuario:usuario, object:interes | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | NConversion | faltantes | Interes:interes | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | NConversion | procesar | Interes:interes, Usuario:usuario | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | NInteres | index | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | NInteres | show | ConsultaRequest:r, int:interes | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | NInteres | mover | MoverInteresRequest:r, int:interes | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | DInteres | listar | Usuario:usuario, array:filtros | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | DInteres | consultaAlcance | Usuario:usuario | No aplica | Private | COINCIDE FIRMA (defaults no certificados) |
| 4 | DInteres | motivos |  | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | DInteres | detalle | int:numero | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | DInteres | obtener | int:numero | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | DInteres | transaccion | callable:operacion | mixed | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | DInteres | bloquear | int:numero | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | DInteres | guardar | Interes:interes, array:datos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | DInteres | actualizarEstadoProspecto | Interes:interes, string:estado | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | DInteres | registrarInteraccion | Interes:interes, array:datos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | DInteres | refrescarDetalle | Interes:interes | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 4 | DAlcance | codigosModuloCoordinador | string:correo | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 5 | NMotivo | index |  | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 5 | NMotivo | store | MotivoRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 5 | NMotivo | validarNombreUnico | string:nombre, ?string:excepto | void | Private | COINCIDE FIRMA (defaults no certificados) |
| 5 | NMotivo | update | MotivoRequest:r, string:motivo | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 5 | NMotivo | validarEditable | MotivoPerdida:motivo | void | Private | COINCIDE FIRMA (defaults no certificados) |
| 5 | NMotivo | destroy | string:motivo | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 5 | DMotivo | listarConUsos |  | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 5 | DMotivo | crear | array:datos | MotivoPerdida | Public | COINCIDE FIRMA (defaults no certificados) |
| 5 | DMotivo | existeNombre | string:nombre, ?string:excepto | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 5 | DMotivo | obtener | string:nombre | MotivoPerdida | Public | COINCIDE FIRMA (defaults no certificados) |
| 5 | DMotivo | actualizar | MotivoPerdida:motivo, array:datos | MotivoPerdida | Public | COINCIDE FIRMA (defaults no certificados) |
| 5 | DMotivo | estaEnUso | string:nombre | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 5 | DMotivo | eliminar | MotivoPerdida:motivo | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | NSeguimiento | registrarInteraccion | RegistrarInteraccionRequest:r, int:interes | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | NSeguimiento | crearRecordatorio | CrearRecordatorioRequest:r, int:interes | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | NSeguimiento | fechaNegocio | string:valor | CarbonImmutable | Private | COINCIDE FIRMA (defaults no certificados) |
| 7 | NSeguimiento | recordatorios | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | NSeguimiento | completarRecordatorio | CompletarRecordatorioRequest:r, int:recordatorio | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | NSeguimiento | exigirAbierto | Recordatorio:recordatorio | void | Private | COINCIDE FIRMA (defaults no certificados) |
| 7 | NSeguimiento | cancelarRecordatorio | ConsultaRequest:r, int:recordatorio | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | interes | int:numero | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | transaccion | callable:operacion | mixed | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | registrarInteraccion | Interes:interes, array:datos | Interaccion | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | actualizarInteres | Interes:interes, array:datos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | cargarInteraccion | Interaccion:interaccion | Interaccion | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | crearRecordatorio | Interes:interes, array:datos | No aplica | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | listarRecordatorios | Usuario:usuario, ?string:estado, :desde, :hasta | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | obtenerRecordatorio | int:numero | Recordatorio | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | cargarInteresRecordatorio | Recordatorio:recordatorio | Recordatorio | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | buscarRecordatorioBloqueado | int:numero | Recordatorio | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | recordatorio | Recordatorio:recordatorio, array:datos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DSeguimiento | insertarInteraccion | array:datos | Interaccion | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | NAlcance | autorizarTarjeta | Usuario:usuario, object:interes | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DAlcance | intereses | Builder:query, Usuario:usuario, string:tabla | Builder | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | NNotificacion | index | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | NNotificacion | enviar | EnviarNotificacionRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | NNotificacion | marcarLeida | ConsultaRequest:r, int:notificacion | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DNotificacion | listar | Usuario:usuario | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DNotificacion | prospectoAsignadoA | string:correo, string:vendedor | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DNotificacion | crear | array:datos | Notificacion | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DNotificacion | obtener | int:numero | Notificacion | Public | COINCIDE FIRMA (defaults no certificados) |
| 7 | DNotificacion | marcarLeida | Notificacion:notificacion | Notificacion | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | NSeguimiento | comisiones | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | NSeguimiento | resumenComisiones | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | NSeguimiento | pagarComisiones | ConsultaRequest:r, string:vendedor | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | NSeguimiento | actualizarConfiguracionComision | ActualizarComisionRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DSeguimiento | comisiones | Usuario:usuario | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DSeguimiento | porcentajeComision |  | float | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DSeguimiento | resumenComisiones | Usuario:usuario | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DSeguimiento | usuario | string:correo | Usuario | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DSeguimiento | pagarComisiones | string:correo, Usuario:usuario | int | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DSeguimiento | actualizarPorcentajeComision | string:valor, string:correo | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DAlcance | intereses | Builder:query, Usuario:usuario, string:tabla | Builder | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DAlcance | codigosModuloCoordinador | string:correo | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | NReporte | dashboard | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | NReporte | porcentajes | :conteos, ?array:orden | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 8 | NReporte | serie | :dias, :valores | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 8 | NReporte | estadisticasVendedor | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | NReporte | estadisticas | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | NReporte | listado | ListadoRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DReporte | dashboard | Usuario:usuario, Collection:dias, bool:incluirAccesos | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DReporte | tarjetas | Usuario:usuario | Builder | Private | COINCIDE FIRMA (defaults no certificados) |
| 8 | DReporte | estadisticasVendedor | string:correo | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DReporte | estadisticas | Usuario:usuario, array:filtros | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DReporte | filtrar | Builder:query, array:filtros | Builder | Private | COINCIDE FIRMA (defaults no certificados) |
| 8 | DReporte | listado | Usuario:usuario, array:filtros | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | DReporte | vendedores |  | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 8 | NAcceso | permite | ?Usuario:usuario, string:recurso, string:nivel | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | descuentos |  | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | registrarMetodo | RegistrarMetodoRequest:r, string:prospecto | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | autorizarProspecto | Usuario:usuario, ?Prospecto:prospecto | void | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | crearSetupTarjeta | CrearSetupTarjetaRequest:r, string:prospecto | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | cambiarEstadoMetodo | CambiarEstadoMetodoRequest:r, int:metodo | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | crearOrden | CrearOrdenRequest:r, int:interes | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | anularOrden | AnularOrdenRequest:r, int:orden | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | estadoCuota | DPago:pagos, int:orden, int:numero, string:estado, array:cuota, ?string:observacionPago | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | registrarComprobante | RegistrarComprobanteRequest:r, int:orden, int:cuota | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | metodoActivo | string:documento, int:numero, ?string:tipo, string:mensaje | MetodoPago | Private | DIFERENCIA DE FIRMA |
| 138 | NPago | validarArchivo | string:archivo | string | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | cuotaBloqueada | int:nroOrden, int:cuota | object | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | crearCheckout | CrearCheckoutRequest:r, int:orden, int:cuota | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | confirmarCheckout | ConsultaRequest:r, string:sessionId | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | cancelarCheckout | ConsultaRequest:r, string:sessionId | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | cuotas | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | aprobar | AprobarCuotaRequest:r, int:orden, int:cuota | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | trasAprobar | OrdenPago:orden, int:cuota, Usuario:usuario, string:descripcion | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | rechazar | RechazarCuotaRequest:r, int:orden, int:cuota | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NPago | comprobante | ConsultaRequest:r, int:comprobante | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | descuentos |  | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | prospecto | string:documento | Prospecto | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | crearMetodo | array:datos | MetodoPago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | prospectoEnCartera | Prospecto:prospecto, Usuario:usuario | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | metodo | int:numero | MetodoPago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | metodoConProspecto | MetodoPago:metodo | MetodoPago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | actualizarMetodo | MetodoPago:metodo, array:datos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | interes | int:numero | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | transaccion | callable:operacion | mixed | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | interesBloqueado | int:numero | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | ordenAbierta | int:nroTarjeta | ?object | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | modulos | array:codigos | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | descuentosPorCodigo | array:codigos | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | crearOrden | array:datos | OrdenPago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | insertarDescuentosOrden | array:filas | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | actualizarOrden | OrdenPago:orden, array:datos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | insertarItems | OrdenPago:orden, array:filas | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | insertarCuotas | array:filas | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | crearPago | array:datos | Pago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | registrarInteraccion | Interes:interes, array:datos | Interaccion | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | actualizarInteres | Interes:interes, array:datos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | ordenCompleta | OrdenPago:orden | OrdenPago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | hayCuotasEnEstados | int:orden, array:estados | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | montoCuotasEnEstado | int:orden, string:estado | float | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | orden | int:numero | OrdenPago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | interesDeOrden | OrdenPago:orden | Interes | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | crearComprobante | array:datos | ComprobantePago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | metodoActivo | string:documento, int:numero, ?string:tipo | ?MetodoPago | Public | DIFERENCIA DE FIRMA |
| 138 | DPago | cuotaBloqueada | int:orden, int:numero | ?object | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | cuotas | Usuario:usuario, ?string:estado | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | actualizarComprobantes | int:orden, int:cuota, string:estado, ?string:observacion | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | comprobante | int:numero | ComprobantePago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DPago | ordenDeComprobante | int:numero | OrdenPago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DAlcance | prospectos | Builder:query, Usuario:usuario | Builder | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DAlcance | intereses | Builder:query, Usuario:usuario, string:tabla | Builder | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DAlcance | codigosModuloCoordinador | string:correo | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | iniciarSetupTarjeta | string:documento, Usuario:usuario, ?int:nroTarjeta | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | cliente |  | StripeClient | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | moneda |  | string | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | asegurarCustomer | StripeClient:stripe, Prospecto:prospecto | string | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | validarSandbox | bool:livemode | void | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | urlFrontend |  | string | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | anularOrden | int:nroOrden, Usuario:actor, string:motivo | OrdenPago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | tienePagosNoAnulables | int:nroOrden | bool | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | recuperarSesion | StripeClient:stripe, string:sessionId | Session | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | confirmarPagoDesdeSesion | Session:sesion, TransaccionStripe:txInicial, ?Usuario:actor | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | traducirMarca | string:brand | string | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | armarRespuestaPago | TransaccionStripe:tx, array:faltantesConversion, string:titulo | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | iniciarCheckoutCuota | int:nroOrden, int:nroCuota, Usuario:usuario | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | aCentavos | float\|string:monto | int | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | verificarSesion | string:sessionId, ?Usuario:actor, bool:exigirAutorizacion | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | confirmarSetupDesdeSesion | Session:sesion, TransaccionStripe:txInicial | array | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NStripe | cancelarSesion | string:sessionId, Usuario:actor | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | crearTransaccion | array:datos | TransaccionStripe | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | transaccion | callable:operacion | mixed | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | prospectoBloqueado | string:documento | Prospecto | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | guardarClienteProspecto | Prospecto:prospecto, string:stripeCliente | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | ordenConDetalle | int:nroOrden | OrdenPago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | transaccionesPendientesDeOrden | int:nroOrden | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | ordenBloqueada | int:nroOrden | OrdenPago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | actualizarTransaccion | TransaccionStripe:tx, array:datos | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | hayTransaccionesEnEstado | int:nroOrden, string:estado | bool | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | transaccionPorSesionBloqueada | string:sessionId | ?TransaccionStripe | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | cuotaBloqueada | int:nroOrden, int:nroCuota | ?object | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | registrarMetodoStripe | array:datos | MetodoPago | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | transaccionPorSesion | string:sessionId | ?TransaccionStripe | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | transaccionAbiertaPorCuota | int:nroOrden, int:nroCuota | ?TransaccionStripe | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DStripe | contarIntentosCuota | int:nroOrden, int:nroCuota | int | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NConversion | faltantes | Interes:interes | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NConversion | procesar | Interes:interes, Usuario:usuario | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NAlcance | autorizarTarjeta | Usuario:usuario, object:interes | void | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NAlcance | modulosACargo | Usuario:usuario | No aplica | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NSeguimiento | inscripciones | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DSeguimiento | inscripciones | Usuario:usuario | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NExportacion | pendientes | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NExportacion | modulosACargo | Usuario:usuario | ?array | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | NExportacion | exportar | ConsultaRequest:r | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NExportacion | registrarResultado | RegistrarResultadoRequest:r, int:exportacion | JsonResponse | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | NExportacion | historialDe | Usuario:usuario | Collection | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | DExportacion | exportables | Usuario:usuario, ?array:modulosACargo | Collection | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DExportacion | consultaExportables | Usuario:usuario, ?array:modulosACargo | Builder | Private | COINCIDE FIRMA (defaults no certificados) |
| 138 | DExportacion | exportarPendientes | Usuario:usuario, ?array:modulosACargo | array | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DExportacion | registrarResultado | int:numero, array:datos | Exportacion | Public | COINCIDE FIRMA (defaults no certificados) |
| 138 | DExportacion | historial | Usuario:usuario, ?array:modulosACargo | Collection | Public | COINCIDE FIRMA (defaults no certificados) |

## Atributos y herencia

Los atributos EA están íntegros en ea_t_attribute.json y comparacion_atributos_ea.json. Las propiedades PHP, imports, padre y métodos están en clases.json. El conceptual excluye FK según regla local; no se contabiliza esa abstracción como pérdida de columnas. Sus atributos coinciden con el volcado anterior tras esa exclusión y faltan los ocho campos recientes de BD-001. Las clases de Request derivan de clases base ApiRequest/ConsultaRequest; el detalle heredado no se repite en cada figura. Las dependencias no constituyen composición. No se halló justificación para inventar herencia entre roles o entre las tres capas.

## Relaciones y responsabilidades

relaciones_ea.json conserva cada conector con tipo, extremos y dirección. Se distingue dependencia P→API→N→D de asociación persistente entre tablas. Imports de tipos Interes/Usuario en N no son consultas por sí mismos. DI en constructores sostiene dependencia N→D; el HTTP cliente-servidor no es una llamada de PHP desde React. No se detectaron errores por los patrones de codigo.py, pero sí regla comercial calculada en Comision, instrucciones antiguas y pérdida omitida en cls-cu5. Hallazgos ARQ-001/002 y CL-002. Los métodos relevantes que faltan de una vista parcial no son automáticamente inexistentes en el proyecto.

Clases fundamentales para estudiar: NAuth/DAuth y NAcceso/DAcceso (sesión/permisos); NAlcance/DAlcance (cartera/programas); NProspecto/DProspecto (captación); NInteres/DInteres (embudo/asignación); NPago/DPago, NStripe/DStripe y NConversion/DConversion (cobro/conversión); NNotificacion/DNotificacion (SMTP); NSeguimiento/DSeguimiento (agenda/comisiones); NExportacion/DExportacion (CSV). No basta memorizar nombres: seguir el método y sus postcondiciones.
