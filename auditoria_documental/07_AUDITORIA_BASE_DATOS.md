# Auditoría exhaustiva de PostgreSQL

Commit auditado: `5bf47b2e863631908e37718fb343fd776003fb5b`. Fecha: 26/11/2026 (America/La_Paz). Solo lectura de originales.

## Instancia, alcance y conteos

Conexión efectiva Laravel verificada: 127.0.0.1:5432, base crm_educativo, esquema public, PostgreSQL17.4 sobre Windows y America/La_Paz. config_cached=false; configuración saneada en configuracion_efectiva.json. La consulta devuelve transaction_read_only=on. No se confundió esta instancia con Docker55432/db_grupo05sa ni con el servidor institucional previsto.

| Objeto | Real public | Documentado en volcado | Conclusión |
| --- | --- | --- | --- |
| Tablas | 31 | 31 | Nombres coinciden |
| Columnas | 292 | 284 | 284 coinciden;8 faltan |
| PK | 31 | 31 | Todas coinciden en columnas |
| FK | 46 | 46 | Definiciones y acciones coinciden |
| UNIQUE (constraints) | 7 | 5 | Faltan2 tokens nuevos |
| CHECK | 28 | 28 | Definiciones coinciden normalizando paréntesis |
| Índices | 55 | Ver inventario de DDL | No confundir con7 UNIQUE; comparar por definición |
| Triggers propios | 5 | 5 | Nombres y funciones; cuerpos idénticos |
| Funciones propias | 5 | 5 | Cuerpo coincide |
| Secuencias | 14 | 14 | Ver pg_secuencias y DDL |
| Vistas/materializadas | 0 | 0 | No localizadas |

Infraestructura adicional: laravel.migrations tiene3 columnas y1 PK/índice. Total ambos esquemas:32 tablas,295 columnas,32 PK,46 FK,7 UNIQUE,28 CHECK y56 índices. Conteos excluyen objetos internos de PostgreSQL.

## Comparación de las tres fuentes

A) DOCX mapeo/físico y conceptual EA derivados del volcado. B) Migraciones y modelos del repositorio, incluidas000009/000010. C) Catálogo real. Las 31 tablas del mapeo tienen los mismos284 nombres del volcado. Los tipos exactos se obtuvieron con format_type para no confundir timestamp(0) con precisión omitida de information_schema. Los 13 defaults nextval con public explícito son equivalentes por search_path y no son errores. Las migraciones nuevas crean los 8 campos que faltan en A y están registradas como ejecutadas. No se reconstruyó una base vacía: la reconstrucción integral desde cero queda No verificable.

## Campos recientes ausentes

| Tabla | Columna | Tipo real | Nullable | Default | Uso |
| --- | --- | --- | --- | --- | --- |
| cuotas | primer_envio_en | timestamp(0) without time zone | YES | No aplica | Token público/expiración o control de avisos automáticos |
| cuotas | recordatorio_mora_en | timestamp(0) without time zone | YES | No aplica | Token público/expiración o control de avisos automáticos |
| cuotas | recordatorio_previo_en | timestamp(0) without time zone | YES | No aplica | Token público/expiración o control de avisos automáticos |
| cuotas | recordatorio_vencimiento_en | timestamp(0) without time zone | YES | No aplica | Token público/expiración o control de avisos automáticos |
| cuotas | token_pago | character varying(80) | YES | No aplica | Token público/expiración o control de avisos automáticos |
| ordenes_pago | envio_automatico | boolean | NO | false | Token público/expiración o control de avisos automáticos |
| transacciones_stripe | expira_en | timestamp(0) without time zone | YES | No aplica | Token público/expiración o control de avisos automáticos |
| transacciones_stripe | token_publico | character varying(80) | YES | No aplica | Token público/expiración o control de avisos automáticos |

## Diccionario estructural real

Todas las columnas se muestran una sola vez aquí; la matriz completa tipo documental/real, precisión, nulabilidad, default y diferencias está en08 y comparacion_columnas.json/pg_columnas.json. Los propósitos son inferencias del uso de clases/modelos, no descripciones institucionales oficiales. PK/FK por columna se derivan de restricciones, no de sufijos de nombre.
### api_tokens

Hash y vigencia de token opaco de sesión. Modelo: ApiToken. Clases D candidatas: DAcceso, DAlcance, DAuth, DBitacora, DSitio; N candidatas: NAuth, NSitio. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| token_hash | character varying(64) | NO | No aplica | True |  | COINCIDE |
| ultimo_uso_en | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| expira_en | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| usuario_correo | character varying(255) | NO | No aplica | False | usuarios.correo | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| api_tokens_pkey | PK | PRIMARY KEY (token_hash) | COINCIDE |
| api_tokens_usuario_correo_fk | FK | FOREIGN KEY (usuario_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE CASCADE | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| api_tokens_pkey | CREATE UNIQUE INDEX api_tokens_pkey ON public.api_tokens USING btree (token_hash) |
### bitacora

Intentos y accesos, IP, evento y recurso; dispara contador de visitas. Modelo: Bitacora. Clases D candidatas: DAcceso, DAlcance, DAuth, DBitacora, DReporte, DSeguridad, DSitio; N candidatas: NAuth, NReporte, NSeguridad, NSitio. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_registro | bigint | NO | nextval('bitacora_nro_registro_seq'::regclass) | True |  | COINCIDE |
| evento | character varying(20) | NO | No aplica | False |  | COINCIDE |
| usuario_correo | character varying(255) | YES | No aplica | False | usuarios.correo | COINCIDE |
| correo_intentado | character varying(255) | YES | No aplica | False |  | COINCIDE |
| recurso_codigo | character varying(40) | YES | No aplica | False | recursos.codigo | COINCIDE |
| ip | character varying(45) | NO | No aplica | False |  | COINCIDE |
| navegador | character varying(255) | YES | No aplica | False |  | COINCIDE |
| fecha | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| bitacora_evento_check | CHECK | CHECK (evento::text = ANY (ARRAY['login_exitoso'::character varying::text, 'login_fallido'::character varying::text, 'logout'::character varying::text, 'visita'::character varying::text, 'acceso_denegado'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| bitacora_pkey | PK | PRIMARY KEY (nro_registro) | COINCIDE |
| bitacora_recurso_codigo_fk | FK | FOREIGN KEY (recurso_codigo) REFERENCES recursos(codigo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |
| bitacora_usuario_correo_fk | FK | FOREIGN KEY (usuario_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| bitacora_evento_fecha_idx | CREATE INDEX bitacora_evento_fecha_idx ON public.bitacora USING btree (evento, fecha) |
| bitacora_pkey | CREATE UNIQUE INDEX bitacora_pkey ON public.bitacora USING btree (nro_registro) |
| bitacora_recurso_fecha_idx | CREATE INDEX bitacora_recurso_fecha_idx ON public.bitacora USING btree (recurso_codigo, fecha) |
### catalogo_cache

Copia local de módulos ofrecidos, vinculados al programa. Modelo: CatalogoCache. Clases D candidatas: DAlcance, DCatalogo, DNotificacion, DPago, DProspecto; N candidatas: NCatalogo, NPago, NProspecto. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| codigo | character varying(255) | NO | No aplica | True |  | COINCIDE |
| anuncio_codigo | character varying(255) | YES | No aplica | False |  | COINCIDE |
| programa_codigo | character varying(255) | NO | No aplica | False | programas.codigo | COINCIDE |
| nombre | character varying(255) | NO | No aplica | False |  | COINCIDE |
| descripcion | text | YES | No aplica | False |  | COINCIDE |
| precio | numeric(12,2) | NO | No aplica | False |  | COINCIDE |
| estado | character varying(255) | NO | No aplica | False |  | COINCIDE |
| sincronizado_en | timestamp(0) without time zone | NO | No aplica | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| catalogo_cache_pkey | PK | PRIMARY KEY (codigo) | COINCIDE |
| catalogo_cache_programa_codigo_fk | FK | FOREIGN KEY (programa_codigo) REFERENCES programas(codigo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| catalogo_cache_pkey | CREATE UNIQUE INDEX catalogo_cache_pkey ON public.catalogo_cache USING btree (codigo) |
### comisiones

Comisión por solicitud comercial, porcentaje aplicado y estado de pago. Modelo: Comision. Clases D candidatas: DAlcance, DReporte, DSeguimiento; N candidatas: NReporte, NSeguimiento. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_solicitud | bigint | NO | No aplica | True | solicitudes_compra.nro_solicitud | COINCIDE |
| porcentaje | numeric(5,2) | NO | '2'::numeric | False |  | COINCIDE |
| monto | numeric(12,2) | NO | No aplica | False |  | COINCIDE |
| estado | character varying(255) | NO | 'Pendiente'::character varying | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| fecha_pago | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| vendedor_correo | character varying(255) | NO | No aplica | False | usuarios.correo | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| comisiones_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['Pendiente'::character varying::text, 'Pagada'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| comisiones_nro_solicitud_fk | FK | FOREIGN KEY (nro_solicitud) REFERENCES solicitudes_compra(nro_solicitud) ON DELETE RESTRICT | COINCIDE |
| comisiones_pkey | PK | PRIMARY KEY (nro_solicitud) | COINCIDE |
| comisiones_vendedor_correo_fk | FK | FOREIGN KEY (vendedor_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| comisiones_pkey | CREATE UNIQUE INDEX comisiones_pkey ON public.comisiones USING btree (nro_solicitud) |
### comprobantes_pago

Archivo/metadata de comprobantes manuales históricos. Modelo: ComprobantePago. Clases D candidatas: DAlcance, DPago; N candidatas: NPago. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_comprobante | bigint | NO | nextval('comprobantes_pago_nro_comprobante_seq'::regclass) | True |  | COINCIDE |
| archivo | text | NO | No aplica | False |  | COINCIDE |
| nombre_archivo | character varying(255) | YES | No aplica | False |  | COINCIDE |
| mime | character varying(255) | YES | No aplica | False |  | COINCIDE |
| fecha_envio | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| observacion | text | YES | No aplica | False |  | COINCIDE |
| estado_revision | character varying(255) | NO | 'En revision'::character varying | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| remitente | character varying(255) | YES | No aplica | False |  | COINCIDE |
| hora_pago | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| nro_orden | bigint | NO | No aplica | False | cuotas.nro_orden,nro_cuota; pagos.nro_orden | COINCIDE |
| nro_cuota | smallint | YES | No aplica | False | cuotas.nro_orden,nro_cuota | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| comprobantes_pago_cuota_fk | FK | FOREIGN KEY (nro_orden, nro_cuota) REFERENCES cuotas(nro_orden, nro_cuota) ON DELETE CASCADE | COINCIDE |
| comprobantes_pago_estado_revision_check | CHECK | CHECK (estado_revision::text = ANY (ARRAY['En revision'::character varying::text, 'Pago aprobado'::character varying::text, 'Pago rechazado'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| comprobantes_pago_nro_orden_fk | FK | FOREIGN KEY (nro_orden) REFERENCES pagos(nro_orden) ON DELETE CASCADE | COINCIDE |
| comprobantes_pago_pkey | PK | PRIMARY KEY (nro_comprobante) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| comprobantes_pago_pkey | CREATE UNIQUE INDEX comprobantes_pago_pkey ON public.comprobantes_pago USING btree (nro_comprobante) |
### configuraciones

Parámetros comerciales, incluido porcentaje de comisión. Modelo: Configuracion. Clases D candidatas: DSeguimiento; N candidatas: NSeguimiento. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| clave | character varying(255) | NO | No aplica | True |  | COINCIDE |
| valor | character varying(255) | NO | No aplica | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| actualizado_por | character varying(255) | YES | No aplica | False | usuarios.correo | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| configuraciones_actualizado_por_fk | FK | FOREIGN KEY (actualizado_por) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL | COINCIDE |
| configuraciones_pkey | PK | PRIMARY KEY (clave) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| configuraciones_pkey | CREATE UNIQUE INDEX configuraciones_pkey ON public.configuraciones USING btree (clave) |
### cuotas

Calendario, importe, estado, Stripe y marcas de recordatorios por orden/cuota. Modelo: Cuota. Clases D candidatas: DAlcance, DNotificacion, DPago, DStripe; N candidatas: NPago. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_orden | bigint | NO | No aplica | True | ordenes_pago.nro_orden | COINCIDE |
| nro_cuota | smallint | NO | No aplica | True |  | COINCIDE |
| monto | numeric(12,2) | NO | No aplica | False |  | COINCIDE |
| fecha_vencimiento | date | NO | No aplica | False |  | COINCIDE |
| estado | character varying(255) | NO | 'Pendiente de pago'::character varying | False |  | COINCIDE |
| fecha_pago | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| nro_metodo | bigint | YES | No aplica | False | metodos_pago.nro_metodo | COINCIDE |
| observacion | text | YES | No aplica | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| proveedor | character varying(20) | NO | 'manual'::character varying | False |  | COINCIDE |
| moneda | character varying(10) | NO | 'BOB'::character varying | False |  | COINCIDE |
| stripe_sesion | character varying(160) | YES | No aplica | False |  | COINCIDE |
| stripe_pago_intent | character varying(160) | YES | No aplica | False |  | COINCIDE |
| stripe_metodo | character varying(160) | YES | No aplica | False |  | COINCIDE |
| stripe_recibo_url | text | YES | No aplica | False |  | COINCIDE |
| token_pago | character varying(80) | YES | No aplica | False |  | DIFERENTE |
| primer_envio_en | timestamp(0) without time zone | YES | No aplica | False |  | DIFERENTE |
| recordatorio_previo_en | timestamp(0) without time zone | YES | No aplica | False |  | DIFERENTE |
| recordatorio_vencimiento_en | timestamp(0) without time zone | YES | No aplica | False |  | DIFERENTE |
| recordatorio_mora_en | timestamp(0) without time zone | YES | No aplica | False |  | DIFERENTE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| cuotas_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['Pendiente de pago'::character varying::text, 'En revision'::character varying::text, 'Pago aprobado'::character varying::text, 'Pago rechazado'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| cuotas_monto_check | CHECK | CHECK (monto > 0::numeric) | COINCIDE (paréntesis redundantes normalizados) |
| cuotas_nro_cuota_check | CHECK | CHECK (nro_cuota >= 1 AND nro_cuota <= 24) | COINCIDE (paréntesis redundantes normalizados) |
| cuotas_nro_metodo_fk | FK | FOREIGN KEY (nro_metodo) REFERENCES metodos_pago(nro_metodo) ON DELETE RESTRICT | COINCIDE |
| cuotas_nro_orden_fk | FK | FOREIGN KEY (nro_orden) REFERENCES ordenes_pago(nro_orden) ON DELETE CASCADE | COINCIDE |
| cuotas_pkey | PK | PRIMARY KEY (nro_orden, nro_cuota) | COINCIDE |
| cuotas_proveedor_check | CHECK | CHECK (proveedor::text = ANY (ARRAY['manual'::character varying::text, 'stripe'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| cuotas_token_pago_unique | UNIQUE | UNIQUE (token_pago) | NO DOCUMENTADA EN VOLCADO |

Índices:

| Nombre | Definición |
| --- | --- |
| cuotas_pkey | CREATE UNIQUE INDEX cuotas_pkey ON public.cuotas USING btree (nro_orden, nro_cuota) |
| cuotas_token_pago_unique | CREATE UNIQUE INDEX cuotas_token_pago_unique ON public.cuotas USING btree (token_pago) |
### descuentos

Catálogo de descuentos porcentuales y activación. Modelo: Descuento. Clases D candidatas: DNotificacion, DPago; N candidatas: NPago. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nombre | character varying(255) | NO | No aplica | False |  | COINCIDE |
| codigo | character varying(255) | NO | No aplica | True |  | COINCIDE |
| porcentaje | numeric(5,2) | NO | No aplica | False |  | COINCIDE |
| estado | character varying(255) | NO | 'activo'::character varying | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| descuentos_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['activo'::character varying::text, 'inactivo'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| descuentos_pkey | PK | PRIMARY KEY (codigo) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| descuentos_pkey | CREATE UNIQUE INDEX descuentos_pkey ON public.descuentos USING btree (codigo) |
### exportaciones

Historial de exportación de matrícula y resultado de registro. Modelo: Exportacion. Clases D candidatas: DAlcance, DExportacion; N candidatas: NExportacion. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_exportacion | bigint | NO | nextval('exportaciones_nro_exportacion_seq'::regclass) | True |  | COINCIDE |
| fecha_exportacion | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| estado | character varying(255) | NO | 'preparada'::character varying | False |  | COINCIDE |
| respuesta | text | YES | No aplica | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| usuario_correo | character varying(255) | YES | No aplica | False | usuarios.correo | COINCIDE |
| nro_solicitud | bigint | NO | No aplica | False | inscripciones_comerciales.nro_solicitud | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| exportaciones_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['preparada'::character varying::text, 'exportada'::character varying::text, 'recibida'::character varying::text, 'error'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| exportaciones_nro_solicitud_fk | FK | FOREIGN KEY (nro_solicitud) REFERENCES inscripciones_comerciales(nro_solicitud) ON DELETE RESTRICT | COINCIDE |
| exportaciones_pkey | PK | PRIMARY KEY (nro_exportacion) | COINCIDE |
| exportaciones_usuario_correo_fk | FK | FOREIGN KEY (usuario_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| exportaciones_estado_fecha_idx | CREATE INDEX exportaciones_estado_fecha_idx ON public.exportaciones USING btree (estado, fecha_exportacion) |
| exportaciones_pkey | CREATE UNIQUE INDEX exportaciones_pkey ON public.exportaciones USING btree (nro_exportacion) |
### inscripciones_comerciales

Confirmación de matrícula comercial por solicitud. Modelo: InscripcionComercial. Clases D candidatas: DAlcance, DExportacion, DSeguimiento; N candidatas: NExportacion, NSeguimiento. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_solicitud | bigint | NO | No aplica | True | solicitudes_compra.nro_solicitud | COINCIDE |
| fecha_confirmacion | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| inscripciones_comerciales_nro_solicitud_fk | FK | FOREIGN KEY (nro_solicitud) REFERENCES solicitudes_compra(nro_solicitud) ON DELETE RESTRICT | COINCIDE |
| inscripciones_comerciales_pkey | PK | PRIMARY KEY (nro_solicitud) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| inscripciones_comerciales_pkey | CREATE UNIQUE INDEX inscripciones_comerciales_pkey ON public.inscripciones_comerciales USING btree (nro_solicitud) |
### interacciones

Contactos/notas/resultados vinculados al interés y usuario. Modelo: Interaccion. Clases D candidatas: DReporte, DSeguimiento; N candidatas: NReporte, NSeguimiento. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_interaccion | bigint | NO | nextval('interacciones_nro_interaccion_seq'::regclass) | True |  | COINCIDE |
| tipo | character varying(255) | NO | No aplica | False |  | COINCIDE |
| descripcion | text | NO | No aplica | False |  | COINCIDE |
| resultado | text | YES | No aplica | False |  | COINCIDE |
| fecha | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| nro_tarjeta | bigint | NO | No aplica | False | intereses.nro_tarjeta | COINCIDE |
| usuario_correo | character varying(255) | NO | No aplica | False | usuarios.correo | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| interacciones_nro_tarjeta_fk | FK | FOREIGN KEY (nro_tarjeta) REFERENCES intereses(nro_tarjeta) ON DELETE RESTRICT | COINCIDE |
| interacciones_pkey | PK | PRIMARY KEY (nro_interaccion) | COINCIDE |
| interacciones_tipo_check | CHECK | CHECK (tipo::text = ANY (ARRAY['WhatsApp'::character varying::text, 'Llamada'::character varying::text, 'Correo electronico'::character varying::text, 'Reunion'::character varying::text, 'Nota comercial'::character varying::text, 'Orden de pago enviada'::character varying::text, 'Pago informado'::character varying::text, 'Compra validada'::character varying::text, 'Orden finalizada'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| interacciones_usuario_correo_fk | FK | FOREIGN KEY (usuario_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| interacciones_pkey | CREATE UNIQUE INDEX interacciones_pkey ON public.interacciones USING btree (nro_interaccion) |
| interacciones_usuario_fecha_idx | CREATE INDEX interacciones_usuario_fecha_idx ON public.interacciones USING btree (usuario_correo, fecha) |
### intereses

Tarjeta de oportunidad por prospecto y módulo, vendedor y estado del embudo. Modelo: Interes. Clases D candidatas: DAlcance, DAuth, DInteres, DMotivo, DNotificacion, DPago, DProspecto, DReporte, DSeguimiento, DSitio, DStripe; N candidatas: NInteres, NMotivo, NPago, NProspecto, NReporte, NSeguimiento, NSitio. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_tarjeta | bigint | NO | nextval('intereses_nro_tarjeta_seq'::regclass) | True |  | COINCIDE |
| fecha | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| modulo_codigo | character varying(255) | NO | No aplica | False | catalogo_cache.codigo | COINCIDE |
| programa_nombre | character varying(255) | NO | No aplica | False |  | COINCIDE |
| modulo_nombre | character varying(255) | NO | No aplica | False |  | COINCIDE |
| precio | numeric(12,2) | YES | No aplica | False |  | COINCIDE |
| anuncio_codigo | character varying(255) | YES | No aplica | False |  | COINCIDE |
| modulo_descripcion | text | YES | No aplica | False |  | COINCIDE |
| estado | character varying(255) | NO | 'Nuevo'::character varying | False |  | COINCIDE |
| fecha_asignacion | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| ultima_actividad_en | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| proximo_contacto | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| observacion | text | YES | No aplica | False |  | COINCIDE |
| vendedor_correo | character varying(255) | YES | No aplica | False | usuarios.correo | COINCIDE |
| documento | character varying(255) | NO | No aplica | False | prospectos.documento | COINCIDE |
| motivo_perdida | character varying(80) | YES | No aplica | False | motivos_perdida.nombre | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| intereses_documento_fk | FK | FOREIGN KEY (documento) REFERENCES prospectos(documento) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |
| intereses_documento_modulo_codigo_unique | UNIQUE | UNIQUE (documento, modulo_codigo) | COINCIDE |
| intereses_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['Nuevo'::character varying::text, 'En Contacto'::character varying::text, 'Seguimiento'::character varying::text, 'Promesa de Pago'::character varying::text, 'Convertido'::character varying::text, 'Perdido'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| intereses_modulo_codigo_fk | FK | FOREIGN KEY (modulo_codigo) REFERENCES catalogo_cache(codigo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |
| intereses_motivo_perdida_fk | FK | FOREIGN KEY (motivo_perdida) REFERENCES motivos_perdida(nombre) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |
| intereses_pkey | PK | PRIMARY KEY (nro_tarjeta) | COINCIDE |
| intereses_vendedor_correo_fk | FK | FOREIGN KEY (vendedor_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| intereses_documento_modulo_codigo_unique | CREATE UNIQUE INDEX intereses_documento_modulo_codigo_unique ON public.intereses USING btree (documento, modulo_codigo) |
| intereses_pkey | CREATE UNIQUE INDEX intereses_pkey ON public.intereses USING btree (nro_tarjeta) |
### log_comandos

Historia del canal de correo P1 compartido; no es una pantalla nueva del P2. Modelo: Sin modelo propio localizado. Clases D candidatas: consulta transversal/histórica; N candidatas: sin endpoint propio. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_registro | bigint | NO | nextval('log_comandos_nro_registro_seq'::regclass) | True |  | COINCIDE |
| remitente | character varying(160) | NO | No aplica | False |  | COINCIDE |
| asunto | character varying(300) | NO | No aplica | False |  | COINCIDE |
| resultado | character varying(20) | NO | No aplica | False |  | COINCIDE |
| detalle | text | YES | No aplica | False |  | COINCIDE |
| fecha | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| rol_registrado | character varying(40) | YES | No aplica | False |  | COINCIDE |
| usuario_correo | character varying(255) | YES | No aplica | False | usuarios.correo | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| log_comandos_pkey | PK | PRIMARY KEY (nro_registro) | COINCIDE |
| log_comandos_usuario_correo_fk | FK | FOREIGN KEY (usuario_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| log_comandos_pkey | CREATE UNIQUE INDEX log_comandos_pkey ON public.log_comandos USING btree (nro_registro) |
### metodos_pago

Referencias Stripe y últimos dígitos; datos manuales históricos consultables. Modelo: MetodoPago. Clases D candidatas: DAlcance, DNotificacion, DPago, DStripe; N candidatas: NPago. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_metodo | bigint | NO | nextval('metodos_pago_nro_metodo_seq'::regclass) | True |  | COINCIDE |
| documento | character varying(255) | NO | No aplica | False | prospectos.documento | COINCIDE |
| tipo | character varying(20) | NO | No aplica | False |  | COINCIDE |
| titular | character varying(255) | NO | No aplica | False |  | COINCIDE |
| marca | character varying(20) | YES | No aplica | False |  | COINCIDE |
| ultimos_digitos | character varying(4) | YES | No aplica | False |  | COINCIDE |
| vencimiento | character varying(5) | YES | No aplica | False |  | COINCIDE |
| estado | character varying(10) | NO | 'activo'::character varying | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| proveedor | character varying(20) | NO | 'manual'::character varying | False |  | COINCIDE |
| stripe_cliente | character varying(120) | YES | No aplica | False |  | COINCIDE |
| stripe_metodo | character varying(120) | YES | No aplica | False |  | COINCIDE |
| registrado_por | character varying(255) | YES | No aplica | False | usuarios.correo | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| metodos_pago_documento_fk | FK | FOREIGN KEY (documento) REFERENCES prospectos(documento) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |
| metodos_pago_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['activo'::character varying::text, 'inactivo'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| metodos_pago_pkey | PK | PRIMARY KEY (nro_metodo) | COINCIDE |
| metodos_pago_proveedor_check | CHECK | CHECK (proveedor::text = ANY (ARRAY['manual'::character varying::text, 'stripe'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| metodos_pago_registrado_por_fk | FK | FOREIGN KEY (registrado_por) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL | COINCIDE |
| metodos_pago_tarjeta_check | CHECK | CHECK (tipo::text <> 'Tarjeta'::text OR marca IS NOT NULL AND ultimos_digitos::text ~ '^[0-9]{4}$'::text AND vencimiento::text ~ '^(0[1-9]\|1[0-2])/[0-9]{2}$'::text) | COINCIDE (paréntesis redundantes normalizados) |
| metodos_pago_tipo_check | CHECK | CHECK (tipo::text = ANY (ARRAY['Tarjeta'::character varying::text, 'QR'::character varying::text, 'Transferencia'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |

Índices:

| Nombre | Definición |
| --- | --- |
| metodos_pago_pkey | CREATE UNIQUE INDEX metodos_pago_pkey ON public.metodos_pago USING btree (nro_metodo) |
| metodos_pago_stripe_metodo_unique | CREATE UNIQUE INDEX metodos_pago_stripe_metodo_unique ON public.metodos_pago USING btree (stripe_metodo) WHERE (stripe_metodo IS NOT NULL) |
### motivos_perdida

Catálogo clasificado de motivos. Modelo: MotivoPerdida. Clases D candidatas: DAlcance, DInteres, DMotivo; N candidatas: NInteres, NMotivo. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nombre | character varying(80) | NO | No aplica | True |  | COINCIDE |
| categoria | character varying(20) | NO | No aplica | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| motivos_categoria_check | CHECK | CHECK (categoria::text = ANY (ARRAY['Económico'::character varying::text, 'Horario'::character varying::text, 'Incompatibilidad'::character varying::text, 'Contacto'::character varying::text, 'Otro'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| motivos_perdida_pkey | PK | PRIMARY KEY (nombre) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| motivos_perdida_pkey | CREATE UNIQUE INDEX motivos_perdida_pkey ON public.motivos_perdida USING btree (nombre) |
### movimientos_interes

Historial disparado por trigger en cambios de estado/asignación. Modelo: MovimientoInteres. Clases D candidatas: consulta transversal/histórica; N candidatas: sin endpoint propio. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_movimiento | bigint | NO | nextval('movimientos_interes_nro_movimiento_seq'::regclass) | True |  | COINCIDE |
| nro_tarjeta | bigint | NO | No aplica | False | intereses.nro_tarjeta | COINCIDE |
| estado_anterior | character varying(255) | YES | No aplica | False |  | COINCIDE |
| estado_nuevo | character varying(255) | NO | No aplica | False |  | COINCIDE |
| detalle | text | YES | No aplica | False |  | COINCIDE |
| fecha | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| usuario_correo | character varying(255) | YES | No aplica | False | usuarios.correo | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| movimientos_interes_nro_tarjeta_fk | FK | FOREIGN KEY (nro_tarjeta) REFERENCES intereses(nro_tarjeta) ON DELETE RESTRICT | COINCIDE |
| movimientos_interes_pkey | PK | PRIMARY KEY (nro_movimiento) | COINCIDE |
| movimientos_interes_usuario_correo_fk | FK | FOREIGN KEY (usuario_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| movimientos_interes_nro_tarjeta_fecha_idx | CREATE INDEX movimientos_interes_nro_tarjeta_fecha_idx ON public.movimientos_interes USING btree (nro_tarjeta, fecha) |
| movimientos_interes_pkey | CREATE UNIQUE INDEX movimientos_interes_pkey ON public.movimientos_interes USING btree (nro_movimiento) |
### notificaciones

Historial de mensajes y estado de envío; no garantiza recepción. Modelo: Notificacion. Clases D candidatas: DAlcance, DNotificacion, DPago, DStripe; N candidatas: NNotificacion, NPago. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_notificacion | bigint | NO | nextval('notificaciones_nro_notificacion_seq'::regclass) | True |  | COINCIDE |
| destinatario | character varying(255) | YES | No aplica | False |  | COINCIDE |
| tipo | character varying(255) | NO | No aplica | False |  | COINCIDE |
| mensaje | text | NO | No aplica | False |  | COINCIDE |
| estado | character varying(255) | NO | 'enviada'::character varying | False |  | COINCIDE |
| fecha_envio | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| usuario_correo | character varying(255) | YES | No aplica | False | usuarios.correo | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| notificaciones_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['enviada'::character varying::text, 'fallida'::character varying::text, 'leida'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| notificaciones_pkey | PK | PRIMARY KEY (nro_notificacion) | COINCIDE |
| notificaciones_usuario_correo_fk | FK | FOREIGN KEY (usuario_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| notificaciones_pkey | CREATE UNIQUE INDEX notificaciones_pkey ON public.notificaciones USING btree (nro_notificacion) |
| notificaciones_usuario_estado_fecha_idx | CREATE INDEX notificaciones_usuario_estado_fecha_idx ON public.notificaciones USING btree (usuario_correo, estado, fecha_envio) |
### orden_pago_descuentos

Tabla asociativa con porcentaje/monto aplicados a cada orden. Modelo: OrdenPagoDescuento. Clases D candidatas: DNotificacion, DPago; N candidatas: NPago. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_orden | bigint | NO | No aplica | True | ordenes_pago.nro_orden | COINCIDE |
| porcentaje | numeric(5,2) | NO | No aplica | False |  | COINCIDE |
| monto | numeric(12,2) | NO | No aplica | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| descuento_codigo | character varying(255) | NO | No aplica | True | descuentos.codigo | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| orden_pago_descuentos_descuento_codigo_fk | FK | FOREIGN KEY (descuento_codigo) REFERENCES descuentos(codigo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |
| orden_pago_descuentos_nro_orden_fk | FK | FOREIGN KEY (nro_orden) REFERENCES ordenes_pago(nro_orden) ON DELETE CASCADE | COINCIDE |
| orden_pago_descuentos_pkey | PK | PRIMARY KEY (nro_orden, descuento_codigo) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| orden_pago_descuentos_pkey | CREATE UNIQUE INDEX orden_pago_descuentos_pkey ON public.orden_pago_descuentos USING btree (nro_orden, descuento_codigo) |
### ordenes_pago

Cabecera comercial, importes, anulación y envío automático. Modelo: OrdenPago. Clases D candidatas: DAlcance, DNotificacion, DPago, DStripe; N candidatas: NPago. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_orden | bigint | NO | nextval('ordenes_pago_nro_orden_seq'::regclass) | True |  | COINCIDE |
| nro_tarjeta | bigint | NO | No aplica | False | intereses.nro_tarjeta | COINCIDE |
| subtotal | numeric(12,2) | NO | No aplica | False |  | COINCIDE |
| descuento_total | numeric(12,2) | NO | '0'::numeric | False |  | COINCIDE |
| total | numeric(12,2) | NO | No aplica | False |  | COINCIDE |
| fecha_generacion | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| vendedor_correo | character varying(255) | NO | No aplica | False | usuarios.correo | COINCIDE |
| estado | character varying(20) | NO | 'Activa'::character varying | False |  | COINCIDE |
| motivo_anulacion | text | YES | No aplica | False |  | COINCIDE |
| fecha_anulacion | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| anulada_por | character varying(255) | YES | No aplica | False | usuarios.correo | COINCIDE |
| envio_automatico | boolean | NO | false | False |  | DIFERENTE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| ordenes_pago_anulada_por_fk | FK | FOREIGN KEY (anulada_por) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL | COINCIDE |
| ordenes_pago_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['Activa'::character varying::text, 'Anulada'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| ordenes_pago_nro_tarjeta_fk | FK | FOREIGN KEY (nro_tarjeta) REFERENCES intereses(nro_tarjeta) ON DELETE RESTRICT | COINCIDE |
| ordenes_pago_pkey | PK | PRIMARY KEY (nro_orden) | COINCIDE |
| ordenes_pago_vendedor_correo_fk | FK | FOREIGN KEY (vendedor_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| ordenes_pago_pkey | CREATE UNIQUE INDEX ordenes_pago_pkey ON public.ordenes_pago USING btree (nro_orden) |
### pagos

Estado de pago compartido con P1 y primera cuota; mantiene triggers de compatibilidad. Modelo: Pago. Clases D candidatas: DNotificacion, DPago; N candidatas: NPago. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| codigo_qr | character varying(255) | NO | No aplica | False |  | COINCIDE |
| estado | character varying(255) | NO | 'Pendiente de pago'::character varying | False |  | COINCIDE |
| fecha_validacion | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| observacion_validacion | text | YES | No aplica | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| nro_orden | bigint | NO | No aplica | True | ordenes_pago.nro_orden | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| pagos_codigo_qr_unique | UNIQUE | UNIQUE (codigo_qr) | COINCIDE |
| pagos_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['Pendiente de pago'::character varying::text, 'En revision'::character varying::text, 'Pago aprobado'::character varying::text, 'Pago rechazado'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| pagos_nro_orden_fk | FK | FOREIGN KEY (nro_orden) REFERENCES ordenes_pago(nro_orden) ON DELETE RESTRICT | COINCIDE |
| pagos_pkey | PK | PRIMARY KEY (nro_orden) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| pagos_codigo_qr_unique | CREATE UNIQUE INDEX pagos_codigo_qr_unique ON public.pagos USING btree (codigo_qr) |
| pagos_estado_idx | CREATE INDEX pagos_estado_idx ON public.pagos USING btree (estado) |
| pagos_pkey | CREATE UNIQUE INDEX pagos_pkey ON public.pagos USING btree (nro_orden) |
### permisos

Relación rol/recurso con nivel de acceso. Modelo: Permiso. Clases D candidatas: DAlcance, DAuth, DBitacora, DProspecto, DReporte, DSeguridad, DSitio; N candidatas: NProspecto, NReporte, NSeguridad, NSitio. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| rol | character varying(40) | NO | No aplica | True | roles.nombre | COINCIDE |
| recurso_codigo | character varying(40) | NO | No aplica | True | recursos.codigo | COINCIDE |
| acceso | character varying(20) | NO | No aplica | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| permisos_acceso_check | CHECK | CHECK (acceso::text = ANY (ARRAY['lectura'::character varying::text, 'modificacion'::character varying::text, 'eliminacion'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| permisos_pkey | PK | PRIMARY KEY (rol, recurso_codigo) | COINCIDE |
| permisos_recurso_codigo_fk | FK | FOREIGN KEY (recurso_codigo) REFERENCES recursos(codigo) ON UPDATE CASCADE ON DELETE CASCADE | COINCIDE |
| permisos_rol_fk | FK | FOREIGN KEY (rol) REFERENCES roles(nombre) ON UPDATE CASCADE ON DELETE CASCADE | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| permisos_pkey | CREATE UNIQUE INDEX permisos_pkey ON public.permisos USING btree (rol, recurso_codigo) |
### programas

Programas académicos de oferta local. Modelo: Programa. Clases D candidatas: DAlcance, DCatalogo, DUsuario; N candidatas: NCatalogo, NUsuario. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| codigo | character varying(255) | NO | No aplica | True |  | COINCIDE |
| nombre | character varying(255) | NO | No aplica | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| programas_pkey | PK | PRIMARY KEY (codigo) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| programas_pkey | CREATE UNIQUE INDEX programas_pkey ON public.programas USING btree (codigo) |
### programas_responsables

Responsable por programa: PK simple programa_codigo permite una asignación por programa; cada coordinador puede tener varios programas. Modelo: ProgramaResponsable. Clases D candidatas: DUsuario; N candidatas: NUsuario. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| programa_codigo | character varying(255) | NO | No aplica | True | programas.codigo | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| coordinador_correo | character varying(255) | NO | No aplica | False | usuarios.correo | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| programas_responsables_coordinador_correo_fk | FK | FOREIGN KEY (coordinador_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |
| programas_responsables_pkey | PK | PRIMARY KEY (programa_codigo) | COINCIDE |
| programas_responsables_programa_codigo_fk | FK | FOREIGN KEY (programa_codigo) REFERENCES programas(codigo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| programas_responsables_pkey | CREATE UNIQUE INDEX programas_responsables_pkey ON public.programas_responsables USING btree (programa_codigo) |
### prospectos

Persona interesada, identificación/contacto/origen y estado agregado. Modelo: Prospecto. Clases D candidatas: DAlcance, DNotificacion, DPago, DProspecto, DStripe; N candidatas: NNotificacion, NPago, NProspecto. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nombre | character varying(255) | NO | No aplica | False |  | COINCIDE |
| apellido | character varying(255) | NO | No aplica | False |  | COINCIDE |
| documento | character varying(255) | NO | No aplica | True |  | COINCIDE |
| correo | character varying(255) | NO | No aplica | False |  | COINCIDE |
| telefono | character varying(255) | NO | No aplica | False |  | COINCIDE |
| estado | character varying(255) | NO | 'Nuevo'::character varying | False |  | COINCIDE |
| fecha_registro | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| profesion | character varying(255) | YES | No aplica | False |  | COINCIDE |
| ubicacion | character varying(255) | YES | No aplica | False |  | COINCIDE |
| origen | character varying(20) | NO | 'Web'::character varying | False |  | COINCIDE |
| stripe_cliente | character varying(120) | YES | No aplica | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| prospectos_correo_unique | UNIQUE | UNIQUE (correo) | COINCIDE |
| prospectos_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['Nuevo'::character varying::text, 'En Contacto'::character varying::text, 'Seguimiento'::character varying::text, 'Promesa de Pago'::character varying::text, 'Convertido'::character varying::text, 'Perdido'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| prospectos_pkey | PK | PRIMARY KEY (documento) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| prospectos_correo_lower_unique | CREATE UNIQUE INDEX prospectos_correo_lower_unique ON public.prospectos USING btree (lower((correo)::text)) |
| prospectos_correo_unique | CREATE UNIQUE INDEX prospectos_correo_unique ON public.prospectos USING btree (correo) |
| prospectos_pkey | CREATE UNIQUE INDEX prospectos_pkey ON public.prospectos USING btree (documento) |
| prospectos_stripe_cliente_unique | CREATE UNIQUE INDEX prospectos_stripe_cliente_unique ON public.prospectos USING btree (stripe_cliente) WHERE (stripe_cliente IS NOT NULL) |
### recordatorios

Agenda de contacto, realización y cancelación. Consultar puede marcar Atrasada después de 24 h: API-001. Modelo: Recordatorio. Clases D candidatas: DAlcance, DReporte, DSeguimiento; N candidatas: NReporte, NSeguimiento. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_recordatorio | bigint | NO | nextval('recordatorios_nro_recordatorio_seq'::regclass) | True |  | COINCIDE |
| fecha_programada | timestamp(0) without time zone | NO | No aplica | False |  | COINCIDE |
| descripcion | text | NO | No aplica | False |  | COINCIDE |
| estado | character varying(255) | NO | 'Pendiente'::character varying | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| nro_tarjeta | bigint | NO | No aplica | False | intereses.nro_tarjeta | COINCIDE |
| fecha_realizada | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| notificado | boolean | NO | false | False |  | COINCIDE |
| usuario_correo | character varying(255) | NO | No aplica | False | usuarios.correo | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| recordatorios_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['Pendiente'::character varying::text, 'Realizada'::character varying::text, 'Atrasada'::character varying::text, 'Cancelado'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| recordatorios_nro_tarjeta_fk | FK | FOREIGN KEY (nro_tarjeta) REFERENCES intereses(nro_tarjeta) ON DELETE RESTRICT | COINCIDE |
| recordatorios_pkey | PK | PRIMARY KEY (nro_recordatorio) | COINCIDE |
| recordatorios_usuario_correo_fk | FK | FOREIGN KEY (usuario_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| recordatorios_pkey | CREATE UNIQUE INDEX recordatorios_pkey ON public.recordatorios USING btree (nro_recordatorio) |
| recordatorios_usuario_estado_fecha_idx | CREATE INDEX recordatorios_usuario_estado_fecha_idx ON public.recordatorios USING btree (usuario_correo, estado, fecha_programada) |
### recursos

Páginas/menú, CU, condición pública y contador de visitas. Modelo: Recurso. Clases D candidatas: DAlcance, DAuth, DBitacora, DReporte, DSeguridad, DSitio; N candidatas: NReporte, NSeguridad, NSitio. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| codigo | character varying(40) | NO | No aplica | True |  | COINCIDE |
| nombre | character varying(80) | NO | No aplica | False |  | COINCIDE |
| ruta | character varying(80) | NO | No aplica | False |  | COINCIDE |
| icono | character varying(40) | NO | No aplica | False |  | COINCIDE |
| orden | smallint | NO | No aplica | False |  | COINCIDE |
| caso_uso | character varying(4) | NO | No aplica | False |  | COINCIDE |
| publico | boolean | NO | false | False |  | COINCIDE |
| visitas | bigint | NO | '0'::bigint | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| recursos_caso_uso_check | CHECK | CHECK (caso_uso::text ~ '^CU[1-8]$'::text) | COINCIDE (paréntesis redundantes normalizados) |
| recursos_pkey | PK | PRIMARY KEY (codigo) | COINCIDE |
| recursos_ruta_unique | UNIQUE | UNIQUE (ruta) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| recursos_pkey | CREATE UNIQUE INDEX recursos_pkey ON public.recursos USING btree (codigo) |
| recursos_ruta_unique | CREATE UNIQUE INDEX recursos_ruta_unique ON public.recursos USING btree (ruta) |
### roles

Roles de aplicación. Modelo: Rol. Clases D candidatas: DAlcance, DSeguridad, DUsuario; N candidatas: NSeguridad, NUsuario. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nombre | character varying(40) | NO | No aplica | True |  | COINCIDE |
| descripcion | character varying(255) | NO | No aplica | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| roles_pkey | PK | PRIMARY KEY (nombre) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| roles_pkey | CREATE UNIQUE INDEX roles_pkey ON public.roles USING btree (nombre) |
### solicitudes_compra

Ítems por módulo de una orden y instantánea de precio/texto. Modelo: SolicitudCompra. Clases D candidatas: consulta transversal/histórica; N candidatas: sin endpoint propio. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_solicitud | bigint | NO | nextval('solicitudes_compra_nro_solicitud_seq'::regclass) | True |  | COINCIDE |
| precio_acordado | numeric(12,2) | YES | No aplica | False |  | COINCIDE |
| fecha | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| anuncio_codigo | character varying(255) | YES | No aplica | False |  | COINCIDE |
| modulo_codigo | character varying(255) | NO | No aplica | False | catalogo_cache.codigo | COINCIDE |
| programa_nombre | character varying(255) | NO | No aplica | False |  | COINCIDE |
| modulo_nombre | character varying(255) | NO | No aplica | False |  | COINCIDE |
| modulo_descripcion | text | YES | No aplica | False |  | COINCIDE |
| anuncio_titulo | character varying(255) | YES | No aplica | False |  | COINCIDE |
| nro_orden | bigint | NO | No aplica | False | ordenes_pago.nro_orden | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| solicitudes_compra_modulo_codigo_fk | FK | FOREIGN KEY (modulo_codigo) REFERENCES catalogo_cache(codigo) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |
| solicitudes_compra_nro_orden_fk | FK | FOREIGN KEY (nro_orden) REFERENCES ordenes_pago(nro_orden) ON DELETE CASCADE | COINCIDE |
| solicitudes_compra_pkey | PK | PRIMARY KEY (nro_solicitud) | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| solicitudes_compra_pkey | CREATE UNIQUE INDEX solicitudes_compra_pkey ON public.solicitudes_compra USING btree (nro_solicitud) |
| solicitudes_modulo_fecha_idx | CREATE INDEX solicitudes_modulo_fecha_idx ON public.solicitudes_compra USING btree (modulo_codigo, fecha) |
### transacciones_stripe

Sesiones de Checkout/Setup, identificadores externos, importe y conciliación. Modelo: TransaccionStripe. Clases D candidatas: DAlcance, DNotificacion, DPago, DStripe; N candidatas: NPago. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nro_transaccion | bigint | NO | nextval('transacciones_stripe_nro_transaccion_seq'::regclass) | True |  | COINCIDE |
| tipo | character varying(20) | NO | No aplica | False |  | COINCIDE |
| nro_orden | bigint | YES | No aplica | False | cuotas.nro_orden,nro_cuota; ordenes_pago.nro_orden | COINCIDE |
| nro_cuota | smallint | YES | No aplica | False | cuotas.nro_orden,nro_cuota | COINCIDE |
| documento | character varying(255) | YES | No aplica | False | prospectos.documento | COINCIDE |
| usuario_correo | character varying(255) | YES | No aplica | False | usuarios.correo | COINCIDE |
| stripe_sesion | character varying(160) | NO | No aplica | False |  | COINCIDE |
| stripe_pago_intent | character varying(160) | YES | No aplica | False |  | COINCIDE |
| stripe_setup_intent | character varying(160) | YES | No aplica | False |  | COINCIDE |
| stripe_cliente | character varying(120) | YES | No aplica | False |  | COINCIDE |
| stripe_metodo | character varying(120) | YES | No aplica | False |  | COINCIDE |
| moneda | character varying(10) | NO | 'bob'::character varying | False |  | COINCIDE |
| monto_esperado | numeric(12,2) | YES | No aplica | False |  | COINCIDE |
| monto_centavos | integer | YES | No aplica | False |  | COINCIDE |
| monto_confirmado | numeric(12,2) | YES | No aplica | False |  | COINCIDE |
| estado_sesion | character varying(40) | NO | 'open'::character varying | False |  | COINCIDE |
| estado_pago | character varying(40) | NO | 'unpaid'::character varying | False |  | COINCIDE |
| estado_interno | character varying(35) | NO | 'pendiente'::character varying | False |  | COINCIDE |
| livemode | boolean | NO | false | False |  | COINCIDE |
| marca_tarjeta | character varying(30) | YES | No aplica | False |  | COINCIDE |
| ultimos_digitos | character varying(4) | YES | No aplica | False |  | COINCIDE |
| receipt_url | text | YES | No aplica | False |  | COINCIDE |
| url_checkout | text | YES | No aplica | False |  | COINCIDE |
| clave_idempotencia | character varying(120) | YES | No aplica | False |  | COINCIDE |
| detalle_error | text | YES | No aplica | False |  | COINCIDE |
| confirmado_en | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| token_publico | character varying(80) | YES | No aplica | False |  | DIFERENTE |
| expira_en | timestamp(0) without time zone | YES | No aplica | False |  | DIFERENTE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| transacciones_stripe_cuota_fk | FK | FOREIGN KEY (nro_orden, nro_cuota) REFERENCES cuotas(nro_orden, nro_cuota) ON DELETE RESTRICT | COINCIDE |
| transacciones_stripe_documento_fk | FK | FOREIGN KEY (documento) REFERENCES prospectos(documento) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |
| transacciones_stripe_estado_interno_check | CHECK | CHECK (estado_interno::text = ANY (ARRAY['pendiente'::character varying::text, 'confirmado'::character varying::text, 'rechazado'::character varying::text, 'cancelado'::character varying::text, 'expirado'::character varying::text, 'reconciliacion_duplicada'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| transacciones_stripe_orden_fk | FK | FOREIGN KEY (nro_orden) REFERENCES ordenes_pago(nro_orden) ON DELETE RESTRICT | COINCIDE |
| transacciones_stripe_pkey | PK | PRIMARY KEY (nro_transaccion) | COINCIDE |
| transacciones_stripe_sesion_unique | UNIQUE | UNIQUE (stripe_sesion) | COINCIDE |
| transacciones_stripe_tipo_check | CHECK | CHECK (tipo::text = ANY (ARRAY['payment'::character varying::text, 'setup'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| transacciones_stripe_token_publico_unique | UNIQUE | UNIQUE (token_publico) | NO DOCUMENTADA EN VOLCADO |
| transacciones_stripe_usuario_fk | FK | FOREIGN KEY (usuario_correo) REFERENCES usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| transacciones_stripe_cuota_estado_idx | CREATE INDEX transacciones_stripe_cuota_estado_idx ON public.transacciones_stripe USING btree (nro_orden, nro_cuota, estado_interno) |
| transacciones_stripe_pi_unique | CREATE UNIQUE INDEX transacciones_stripe_pi_unique ON public.transacciones_stripe USING btree (stripe_pago_intent) WHERE (stripe_pago_intent IS NOT NULL) |
| transacciones_stripe_pkey | CREATE UNIQUE INDEX transacciones_stripe_pkey ON public.transacciones_stripe USING btree (nro_transaccion) |
| transacciones_stripe_sesion_unique | CREATE UNIQUE INDEX transacciones_stripe_sesion_unique ON public.transacciones_stripe USING btree (stripe_sesion) |
| transacciones_stripe_si_unique | CREATE UNIQUE INDEX transacciones_stripe_si_unique ON public.transacciones_stripe USING btree (stripe_setup_intent) WHERE (stripe_setup_intent IS NOT NULL) |
| transacciones_stripe_token_publico_unique | CREATE UNIQUE INDEX transacciones_stripe_token_publico_unique ON public.transacciones_stripe USING btree (token_publico) |
### usuarios

Personal autenticado, credencial, rol, estado y vigencia. Modelo: Usuario. Clases D candidatas: DAcceso, DAlcance, DAuth, DBitacora, DInteres, DReporte, DSeguimiento, DSitio, DUsuario; N candidatas: NAuth, NInteres, NReporte, NSeguimiento, NSitio, NUsuario. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| nombre | character varying(255) | NO | No aplica | False |  | COINCIDE |
| apellido | character varying(255) | NO | No aplica | False |  | COINCIDE |
| correo | character varying(255) | NO | No aplica | True |  | COINCIDE |
| telefono | character varying(255) | YES | No aplica | False |  | COINCIDE |
| password | character varying(255) | NO | No aplica | False |  | COINCIDE |
| rol | character varying(40) | NO | No aplica | False | roles.nombre | COINCIDE |
| estado | character varying(255) | NO | 'activo'::character varying | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| fecha_inicio | date | NO | CURRENT_DATE | False |  | COINCIDE |
| fecha_fin | date | NO | No aplica | False |  | COINCIDE |
| foto | character varying(255) | YES | No aplica | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| usuarios_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['activo'::character varying::text, 'inactivo'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| usuarios_pkey | PK | PRIMARY KEY (correo) | COINCIDE |
| usuarios_rol_fk | FK | FOREIGN KEY (rol) REFERENCES roles(nombre) ON UPDATE CASCADE ON DELETE RESTRICT | COINCIDE |
| usuarios_vigencia_check | CHECK | CHECK (fecha_fin >= fecha_inicio) | COINCIDE (paréntesis redundantes normalizados) |

Índices:

| Nombre | Definición |
| --- | --- |
| usuarios_correo_lower_unique | CREATE UNIQUE INDEX usuarios_correo_lower_unique ON public.usuarios USING btree (lower((correo)::text)) |
| usuarios_pkey | CREATE UNIQUE INDEX usuarios_pkey ON public.usuarios USING btree (correo) |
| usuarios_rol_estado_index | CREATE INDEX usuarios_rol_estado_index ON public.usuarios USING btree (rol, estado) |
### webhook_eventos_stripe

Idempotencia e historial de eventos firmados de la pasarela. Modelo: WebhookEventoStripe. Clases D candidatas: DAlcance, DNotificacion, DPago, DStripe; N candidatas: NPago. La asociación de clases es inferida por llamadas y puede incluir lectura indirecta Eloquent; no equivale a propiedad exclusiva de paquete.

| Columna | Tipo exacto | NULL | Default | PK | FK | Comparación documental |
| --- | --- | --- | --- | --- | --- | --- |
| stripe_evento | character varying(160) | NO | No aplica | True |  | COINCIDE |
| tipo | character varying(100) | NO | No aplica | False |  | COINCIDE |
| nro_transaccion | bigint | YES | No aplica | False | transacciones_stripe.nro_transaccion | COINCIDE |
| stripe_sesion | character varying(160) | YES | No aplica | False |  | COINCIDE |
| stripe_pago_intent | character varying(160) | YES | No aplica | False |  | COINCIDE |
| livemode | boolean | NO | false | False |  | COINCIDE |
| estado | character varying(30) | NO | 'procesado'::character varying | False |  | COINCIDE |
| resumen | text | YES | No aplica | False |  | COINCIDE |
| procesado_en | timestamp(0) without time zone | NO | CURRENT_TIMESTAMP | False |  | COINCIDE |
| created_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |
| updated_at | timestamp(0) without time zone | YES | No aplica | False |  | COINCIDE |

Restricciones:

| Nombre | Tipo | Definición real | Verificación |
| --- | --- | --- | --- |
| webhook_eventos_stripe_estado_check | CHECK | CHECK (estado::text = ANY (ARRAY['procesado'::character varying::text, 'ignorado'::character varying::text, 'duplicado'::character varying::text, 'error'::character varying::text])) | COINCIDE (paréntesis redundantes normalizados) |
| webhook_eventos_stripe_pkey | PK | PRIMARY KEY (stripe_evento) | COINCIDE |
| webhook_eventos_stripe_tx_fk | FK | FOREIGN KEY (nro_transaccion) REFERENCES transacciones_stripe(nro_transaccion) ON DELETE SET NULL | COINCIDE |

Índices:

| Nombre | Definición |
| --- | --- |
| webhook_eventos_stripe_pkey | CREATE UNIQUE INDEX webhook_eventos_stripe_pkey ON public.webhook_eventos_stripe USING btree (stripe_evento) |

### Infraestructura laravel.migrations

Registra nombre de migración y lote, no personas ni operaciones de negocio. Se excluye del conceptual por convención académica, pero se incluye en inventario real.

| Columna | Tipo | NULL | Default |
| --- | --- | --- | --- |
| id | integer | NO | nextval('laravel.migrations_id_seq'::regclass) |
| migration | character varying | NO | No aplica |
| batch | integer | NO | No aplica |

## Cada relación y su cardinalidad

Una FK no única permite0..* hijos por padre y exige1 o0..1 padre por hijo según nulabilidad; no obliga al padre a tener hijos. Si las columnas FK contienen una PK/UNIQUE completa del hijo, máximo1 hijo por padre. Las cardinalidades no se deducen del número actual de filas. En MATCH SIMPLE compuesto nullable, revisar semántica de NULL parcial además de la lectura abreviada.

| FK | Origen(columnas) | Destino(columnas) | Hijos por padre | Padres por hijo | DELETE/UPDATE | Comparación conceptual |
| --- | --- | --- | --- | --- | --- | --- |
| api_tokens_usuario_correo_fk | api_tokens(usuario_correo) | usuarios(correo) | 0..* | 1 | CASCADE/CASCADE | COINCIDE |
| bitacora_recurso_codigo_fk | bitacora(recurso_codigo) | recursos(codigo) | 0..* | 0..1 | RESTRICT/CASCADE | COINCIDE |
| bitacora_usuario_correo_fk | bitacora(usuario_correo) | usuarios(correo) | 0..* | 0..1 | SET NULL/CASCADE | COINCIDE |
| catalogo_cache_programa_codigo_fk | catalogo_cache(programa_codigo) | programas(codigo) | 0..* | 1 | RESTRICT/CASCADE | COINCIDE |
| comisiones_nro_solicitud_fk | comisiones(nro_solicitud) | solicitudes_compra(nro_solicitud) | 0..1 | 1 | RESTRICT/NO ACTION | COINCIDE |
| comisiones_vendedor_correo_fk | comisiones(vendedor_correo) | usuarios(correo) | 0..* | 1 | RESTRICT/CASCADE | COINCIDE |
| comprobantes_pago_cuota_fk | comprobantes_pago(nro_orden,nro_cuota) | cuotas(nro_orden,nro_cuota) | 0..* | 0..1 | CASCADE/NO ACTION | COINCIDE |
| comprobantes_pago_nro_orden_fk | comprobantes_pago(nro_orden) | pagos(nro_orden) | 0..* | 1 | CASCADE/NO ACTION | COINCIDE |
| configuraciones_actualizado_por_fk | configuraciones(actualizado_por) | usuarios(correo) | 0..* | 0..1 | SET NULL/CASCADE | COINCIDE |
| cuotas_nro_metodo_fk | cuotas(nro_metodo) | metodos_pago(nro_metodo) | 0..* | 0..1 | RESTRICT/NO ACTION | COINCIDE |
| cuotas_nro_orden_fk | cuotas(nro_orden) | ordenes_pago(nro_orden) | 0..* | 1 | CASCADE/NO ACTION | COINCIDE |
| exportaciones_nro_solicitud_fk | exportaciones(nro_solicitud) | inscripciones_comerciales(nro_solicitud) | 0..* | 1 | RESTRICT/NO ACTION | COINCIDE |
| exportaciones_usuario_correo_fk | exportaciones(usuario_correo) | usuarios(correo) | 0..* | 0..1 | SET NULL/CASCADE | COINCIDE |
| inscripciones_comerciales_nro_solicitud_fk | inscripciones_comerciales(nro_solicitud) | solicitudes_compra(nro_solicitud) | 0..1 | 1 | RESTRICT/NO ACTION | COINCIDE |
| interacciones_nro_tarjeta_fk | interacciones(nro_tarjeta) | intereses(nro_tarjeta) | 0..* | 1 | RESTRICT/NO ACTION | COINCIDE |
| interacciones_usuario_correo_fk | interacciones(usuario_correo) | usuarios(correo) | 0..* | 1 | RESTRICT/CASCADE | COINCIDE |
| intereses_documento_fk | intereses(documento) | prospectos(documento) | 0..* | 1 | RESTRICT/CASCADE | COINCIDE |
| intereses_modulo_codigo_fk | intereses(modulo_codigo) | catalogo_cache(codigo) | 0..* | 1 | RESTRICT/CASCADE | COINCIDE |
| intereses_motivo_perdida_fk | intereses(motivo_perdida) | motivos_perdida(nombre) | 0..* | 0..1 | RESTRICT/CASCADE | COINCIDE |
| intereses_vendedor_correo_fk | intereses(vendedor_correo) | usuarios(correo) | 0..* | 0..1 | SET NULL/CASCADE | COINCIDE |
| log_comandos_usuario_correo_fk | log_comandos(usuario_correo) | usuarios(correo) | 0..* | 0..1 | RESTRICT/CASCADE | COINCIDE |
| metodos_pago_documento_fk | metodos_pago(documento) | prospectos(documento) | 0..* | 1 | RESTRICT/CASCADE | COINCIDE |
| metodos_pago_registrado_por_fk | metodos_pago(registrado_por) | usuarios(correo) | 0..* | 0..1 | SET NULL/CASCADE | COINCIDE |
| movimientos_interes_nro_tarjeta_fk | movimientos_interes(nro_tarjeta) | intereses(nro_tarjeta) | 0..* | 1 | RESTRICT/NO ACTION | COINCIDE |
| movimientos_interes_usuario_correo_fk | movimientos_interes(usuario_correo) | usuarios(correo) | 0..* | 0..1 | RESTRICT/CASCADE | COINCIDE |
| notificaciones_usuario_correo_fk | notificaciones(usuario_correo) | usuarios(correo) | 0..* | 0..1 | SET NULL/CASCADE | COINCIDE |
| orden_pago_descuentos_descuento_codigo_fk | orden_pago_descuentos(descuento_codigo) | descuentos(codigo) | 0..* | 1 | RESTRICT/CASCADE | ABSTRACCIÓN N:N VÁLIDA; dos FK y entidad asociativa |
| orden_pago_descuentos_nro_orden_fk | orden_pago_descuentos(nro_orden) | ordenes_pago(nro_orden) | 0..* | 1 | CASCADE/NO ACTION | ABSTRACCIÓN N:N VÁLIDA; dos FK y entidad asociativa |
| ordenes_pago_anulada_por_fk | ordenes_pago(anulada_por) | usuarios(correo) | 0..* | 0..1 | SET NULL/CASCADE | COINCIDE |
| ordenes_pago_nro_tarjeta_fk | ordenes_pago(nro_tarjeta) | intereses(nro_tarjeta) | 0..* | 1 | RESTRICT/NO ACTION | COINCIDE |
| ordenes_pago_vendedor_correo_fk | ordenes_pago(vendedor_correo) | usuarios(correo) | 0..* | 1 | RESTRICT/CASCADE | COINCIDE |
| pagos_nro_orden_fk | pagos(nro_orden) | ordenes_pago(nro_orden) | 0..1 | 1 | RESTRICT/NO ACTION | COINCIDE |
| permisos_recurso_codigo_fk | permisos(recurso_codigo) | recursos(codigo) | 0..* | 1 | CASCADE/CASCADE | ABSTRACCIÓN N:N VÁLIDA; dos FK y entidad asociativa |
| permisos_rol_fk | permisos(rol) | roles(nombre) | 0..* | 1 | CASCADE/CASCADE | ABSTRACCIÓN N:N VÁLIDA; dos FK y entidad asociativa |
| programas_responsables_coordinador_correo_fk | programas_responsables(coordinador_correo) | usuarios(correo) | 0..* | 1 | RESTRICT/CASCADE | COINCIDE |
| programas_responsables_programa_codigo_fk | programas_responsables(programa_codigo) | programas(codigo) | 0..1 | 1 | RESTRICT/CASCADE | COINCIDE |
| recordatorios_nro_tarjeta_fk | recordatorios(nro_tarjeta) | intereses(nro_tarjeta) | 0..* | 1 | RESTRICT/NO ACTION | COINCIDE |
| recordatorios_usuario_correo_fk | recordatorios(usuario_correo) | usuarios(correo) | 0..* | 1 | RESTRICT/CASCADE | COINCIDE |
| solicitudes_compra_modulo_codigo_fk | solicitudes_compra(modulo_codigo) | catalogo_cache(codigo) | 0..* | 1 | RESTRICT/CASCADE | COINCIDE |
| solicitudes_compra_nro_orden_fk | solicitudes_compra(nro_orden) | ordenes_pago(nro_orden) | 0..* | 1 | CASCADE/NO ACTION | COINCIDE |
| transacciones_stripe_cuota_fk | transacciones_stripe(nro_orden,nro_cuota) | cuotas(nro_orden,nro_cuota) | 0..* | 0..1 | RESTRICT/NO ACTION | COINCIDE |
| transacciones_stripe_documento_fk | transacciones_stripe(documento) | prospectos(documento) | 0..* | 0..1 | RESTRICT/CASCADE | COINCIDE |
| transacciones_stripe_orden_fk | transacciones_stripe(nro_orden) | ordenes_pago(nro_orden) | 0..* | 0..1 | RESTRICT/NO ACTION | COINCIDE |
| transacciones_stripe_usuario_fk | transacciones_stripe(usuario_correo) | usuarios(correo) | 0..* | 0..1 | SET NULL/CASCADE | COINCIDE |
| usuarios_rol_fk | usuarios(rol) | roles(nombre) | 0..* | 1 | RESTRICT/CASCADE | COINCIDE |
| webhook_eventos_stripe_tx_fk | webhook_eventos_stripe(nro_transaccion) | transacciones_stripe(nro_transaccion) | 0..* | 0..1 | SET NULL/NO ACTION | COINCIDE |

Las cuatro FK de permisos y orden_pago_descuentos se abstraen como dos asociaciones N:N y sus entidades asociativas. No son relaciones ausentes. programas_responsables tiene PK simple programa_codigo: cada programa tiene como máximo un coordinador asignado, y un coordinador puede tener varios programas. No es una tabla N:N con PK compuesta. La matriz anterior muestra garantía estructural, no justifica toda regla comercial de asignación.

## Triggers propios: momento, efecto y dependencia

### bitacora_contar_visita

Tabla `bitacora`, función `contar_visita`, habilitado `O`. Después de INSERT de evento visita con recurso no nulo, actualiza recursos.visitas. Sin él la bitácora se registra pero el contador persistente deja de sumar. No corresponde a cualquier SELECT.

Definición observada:

```sql
CREATE TRIGGER bitacora_contar_visita AFTER INSERT ON bitacora FOR EACH ROW WHEN (new.evento::text = 'visita'::text AND new.recurso_codigo IS NOT NULL) EXECUTE FUNCTION contar_visita()
```

Cuerpo conservado como evidencia (no ejecutar):

```text
CREATE OR REPLACE FUNCTION public.contar_visita()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$

BEGIN

    UPDATE recursos SET visitas = visitas + 1 WHERE codigo = NEW.recurso_codigo;

    RETURN NEW;

END $function$

```

Coincide con el cuerpo del volcado; falta explicación en documento BD-002. No se desactivó ni disparó este trigger durante la auditoría.

### intereses_clasificar

Tabla `intereses`, función `clasificar_perdida`, habilitado `O`. Antes de INSERT/UPDATE limpia motivo si no es Perdido; si Perdido sin motivo coloca Sin clasificar (web). Sin él un cambio por otro canal podría conservar motivo inapropiado o no clasificado. Laravel exige motivo en su flujo; el trigger no equivale al rechazo de frontend.

Definición observada:

```sql
CREATE TRIGGER intereses_clasificar BEFORE INSERT OR UPDATE ON intereses FOR EACH ROW EXECUTE FUNCTION clasificar_perdida()
```

Cuerpo conservado como evidencia (no ejecutar):

```text
CREATE OR REPLACE FUNCTION public.clasificar_perdida()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$

BEGIN

    IF NEW.estado <> 'Perdido' THEN NEW.motivo_perdida := NULL;

    ELSIF NEW.motivo_perdida IS NULL THEN NEW.motivo_perdida := 'Sin clasificar (web)';

    END IF;

    RETURN NEW;

END $function$

```

Coincide con el cuerpo del volcado; falta explicación en documento BD-002. No se desactivó ni disparó este trigger durante la auditoría.

### intereses_historial

Tabla `intereses`, función `registrar_movimiento_web`, habilitado `O`. Después de INSERT/UPDATE registra estado/asignación en movimientos_interes si cambia y crm.canal no es correo. Usa crm.usuario_correo cuando está fijado. Sin él se pierde el historial automático de cambios web. El canal correo se excluye para evitar duplicación con P1.

Definición observada:

```sql
CREATE TRIGGER intereses_historial AFTER INSERT OR UPDATE ON intereses FOR EACH ROW EXECUTE FUNCTION registrar_movimiento_web()
```

Cuerpo conservado como evidencia (no ejecutar):

```text
CREATE OR REPLACE FUNCTION public.registrar_movimiento_web()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$

DECLARE anterior text; vendedor_anterior text;

BEGIN

    IF current_setting('crm.canal',true) IS DISTINCT FROM 'correo' THEN

        IF TG_OP='UPDATE' THEN

            anterior := OLD.estado;

            vendedor_anterior := OLD.vendedor_correo;

        END IF;

        IF TG_OP='INSERT' OR NEW.estado IS DISTINCT FROM anterior OR NEW.vendedor_correo IS DISTINCT FROM vendedor_anterior THEN

            INSERT INTO movimientos_interes(nro_tarjeta,usuario_correo,estado_anterior,estado_nuevo,detalle)

            VALUES(NEW.nro_tarjeta, NULLIF(current_setting('crm.usuario_correo',true),''),anterior,NEW.estado,

                'Cambio desde web. Vendedor: ' || COALESCE(vendedor_anterior,'sin asignar') || ' -> ' || COALESCE(NEW.vendedor_correo,'sin asignar'));

        END IF;

    END IF;

    RETURN NEW;

END $function$

```

Coincide con el cuerpo del volcado; falta explicación en documento BD-002. No se desactivó ni disparó este trigger durante la auditoría.

### pagos_copiar_estado

Tabla `pagos`, función `copiar_estado_cuota_inicial`, habilitado `O`. Después de UPDATE OF estado en pagos copia a cuota1 cuando estado difiere y fija fecha_pago al aprobar. Sin él el canal P1 podría quedar con pago y primera cuota desincronizados. No copia estado de toda la orden a todas las cuotas.

Definición observada:

```sql
CREATE TRIGGER pagos_copiar_estado AFTER UPDATE OF estado ON pagos FOR EACH ROW EXECUTE FUNCTION copiar_estado_cuota_inicial()
```

Cuerpo conservado como evidencia (no ejecutar):

```text
CREATE OR REPLACE FUNCTION public.copiar_estado_cuota_inicial()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$

BEGIN

    UPDATE cuotas SET estado = NEW.estado,

        fecha_pago = CASE WHEN NEW.estado = 'Pago aprobado' THEN COALESCE(NEW.fecha_validacion, now()) ELSE fecha_pago END,

        updated_at = now()

    WHERE nro_orden = NEW.nro_orden AND nro_cuota = 1 AND estado IS DISTINCT FROM NEW.estado;

    RETURN NEW;

END $function$

```

Coincide con el cuerpo del volcado; falta explicación en documento BD-002. No se desactivó ni disparó este trigger durante la auditoría.

### pagos_crear_cuota

Tabla `pagos`, función `crear_cuota_unica`, habilitado `O`. Después de INSERT en pagos crea cuota1 por total de orden si no existe, ON CONFLICT DO NOTHING. Sin él las inserciones del canal legado no asegurarían una cuota inicial. En P2 crearOrden inserta plan antes de pagos, por lo que el trigger no debe duplicarlo.

Definición observada:

```sql
CREATE TRIGGER pagos_crear_cuota AFTER INSERT ON pagos FOR EACH ROW EXECUTE FUNCTION crear_cuota_unica()
```

Cuerpo conservado como evidencia (no ejecutar):

```text
CREATE OR REPLACE FUNCTION public.crear_cuota_unica()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$

BEGIN

    INSERT INTO cuotas(nro_orden, nro_cuota, monto, fecha_vencimiento, estado, created_at, updated_at)

    SELECT o.nro_orden, 1, o.total, CURRENT_DATE, NEW.estado, now(), now()

    FROM ordenes_pago o WHERE o.nro_orden = NEW.nro_orden AND o.total > 0

    ON CONFLICT (nro_orden, nro_cuota) DO NOTHING;

    RETURN NEW;

END $function$

```

Coincide con el cuerpo del volcado; falta explicación en documento BD-002. No se desactivó ni disparó este trigger durante la auditoría.

## Normalización y redundancia: evaluación limitada al esquema y uso

1FN: columnas escalares e identificadores estables; campos text como mensaje, archivo o resumen contienen contenido, no prueban grupos repetidos. No se inspeccionaron todas las filas.2FN: revisar dependencias de tablas asociativas con PK/UNIQUE compuesto; orden_pago_descuentos conserva porcentaje/monto aplicados a una orden y descuento.3FN: no puede certificarse globalmente sin dependencias funcionales del negocio. intereses repite programa_nombre, modulo_nombre y precio del catálogo; solicitudes_compra conserva instantáneas de venta. Son desnormalizaciones aparentemente intencionales para historia, pero necesitan documentar qué se congela y qué se sincroniza.

prospectos.estado frente a intereses.estado permite divergencia conceptual cuando una persona tiene varios intereses; NInteres actualiza el agregado y hace falta una definición de cómo se interpreta. recursos.visitas es contador materializado por trigger. pagos.estado replica la primera cuota por compatibilidad de canal. comisiones.monto conserva cálculo monetario al registro. No se recomienda eliminar estas redundancias sin confirmar historia y reglas. La auditoría no encontró una prueba suficiente para afirmar que toda la BD cumple3FN.

## Migraciones, índices y reconstrucción

| Migración registrada | Lote |
| --- | --- |
| 2026_11_21_000001_crear_esquema_compartido | 1 |
| 2026_11_21_000002_estados_embudo_rf32 | 1 |
| 2026_11_21_000003_crear_matriz_acceso | 1 |
| 2026_11_21_000004_crear_bitacora | 1 |
| 2026_11_21_000005_crear_metodos_y_cuotas | 1 |
| 2026_11_21_000006_agregar_foto_usuarios | 1 |
| 2026_11_24_000007_agregar_pagina_error | 1 |
| 2026_11_25_000008_agregar_soporte_stripe | 2 |
| 2026_11_25_000009_agregar_token_publico_stripe | 3 |
| 2026_11_25_000010_agregar_envio_automatico_y_recordatorios | 4 |

Las 10 migraciones registradas tienen archivo local. No hay migraciones pendientes según comparación de nombres, pero esto no prueba ausencia de cambios manuales: el catálogo se comparó aparte. No se ejecutaron up/down. Las14 secuencias y su configuración se conservan en pg_secuencias.json; no se utilizó last_value como dato comercial. pg_indices.json distingue PRIMARY/UNIQUE de índices auxiliares, incluidos funcionales y parciales por definición. PostgreSQL no indexa automáticamente cada FK; revisar índices por columnas iniciales antes de proponer optimizaciones. No se midió rendimiento.

Los datos guardados de tarjetas son identificadores Stripe, marca, últimos dígitos y vencimiento. No se localizaron columnas PAN completo/CVC en el esquema; esto no es una certificación del contenido de cualquier campo text. Tokens públicos se inventariaron como metadatos, sin extraer sus valores. La idempotencia de webhook usa PK stripe_evento y la de sesión UNIQUE stripe_sesion/clave según catálogo, además de bloqueos del código. No se infiere garantía absoluta de concurrencia a partir de un índice.

Cierre exacto de objetos: los55 índices public comprenden36 generados por constraints documentadas y17 índices explícitos coincidentes, más2 índices UNIQUE de tokens ausentes del volcado (BD-001). Las14 secuencias tienen los mismos nombres en volcado y catálogo. Las definiciones de los5 triggers coinciden normalizando cualificación y paréntesis. Evidencias: comparacion_indices.json, comparacion_secuencias.json y comparacion_triggers.json.
