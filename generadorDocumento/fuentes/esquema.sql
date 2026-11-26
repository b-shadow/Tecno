-- P1 correo + migraci?n 000008 Stripe: estructura PostgreSQL vigente, sin datos personales.
-- Destino de produccion: db_grupo05sa.public. Instalar SOLO en una base nueva y vacia.
-- Ejecucion: psql -X -v ON_ERROR_STOP=1 --single-transaction -d BASE_NUEVA -f esquema.sql
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
             WHERE n.nspname='public' AND c.relkind IN ('r','p','v','m','S','f')) THEN
    RAISE EXCEPTION 'El esquema public contiene objetos; no se modifica una base existente';
  END IF;
END $$;
--
-- PostgreSQL database dump
--

\restrict KFaEtLSVAxsKlKsdAOocAbYU3GsvBX0dFy6bugFkQ5hGPviD3jXIjbQxcchvL9g

-- Dumped from database version 18.7
-- Dumped by pg_dump version 18.7

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: clasificar_perdida(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.clasificar_perdida() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.estado <> 'Perdido' THEN NEW.motivo_perdida := NULL;
    ELSIF NEW.motivo_perdida IS NULL THEN NEW.motivo_perdida := 'Sin clasificar (web)';
    END IF;
    RETURN NEW;
END $$;


--
-- Name: contar_visita(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.contar_visita() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE recursos SET visitas = visitas + 1 WHERE codigo = NEW.recurso_codigo;
    RETURN NEW;
END $$;


--
-- Name: copiar_estado_cuota_inicial(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.copiar_estado_cuota_inicial() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE cuotas SET estado = NEW.estado,
        fecha_pago = CASE WHEN NEW.estado = 'Pago aprobado' THEN COALESCE(NEW.fecha_validacion, now()) ELSE fecha_pago END,
        updated_at = now()
    WHERE nro_orden = NEW.nro_orden AND nro_cuota = 1 AND estado IS DISTINCT FROM NEW.estado;
    RETURN NEW;
END $$;


--
-- Name: crear_cuota_unica(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.crear_cuota_unica() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO cuotas(nro_orden, nro_cuota, monto, fecha_vencimiento, estado, created_at, updated_at)
    SELECT o.nro_orden, 1, o.total, CURRENT_DATE, NEW.estado, now(), now()
    FROM ordenes_pago o WHERE o.nro_orden = NEW.nro_orden AND o.total > 0
    ON CONFLICT (nro_orden, nro_cuota) DO NOTHING;
    RETURN NEW;
END $$;


--
-- Name: registrar_movimiento_web(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.registrar_movimiento_web() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
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
END $$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: api_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_tokens (
    token_hash character varying(64) NOT NULL,
    ultimo_uso_en timestamp(0) without time zone,
    expira_en timestamp(0) without time zone,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    usuario_correo character varying(255) NOT NULL
);


--
-- Name: bitacora; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bitacora (
    nro_registro bigint NOT NULL,
    evento character varying(20) NOT NULL,
    usuario_correo character varying(255),
    correo_intentado character varying(255),
    recurso_codigo character varying(40),
    ip character varying(45) NOT NULL,
    navegador character varying(255),
    fecha timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT bitacora_evento_check CHECK (((evento)::text = ANY (ARRAY[('login_exitoso'::character varying)::text, ('login_fallido'::character varying)::text, ('logout'::character varying)::text, ('visita'::character varying)::text, ('acceso_denegado'::character varying)::text])))
);


--
-- Name: bitacora_nro_registro_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bitacora_nro_registro_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bitacora_nro_registro_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bitacora_nro_registro_seq OWNED BY public.bitacora.nro_registro;


--
-- Name: catalogo_cache; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.catalogo_cache (
    codigo character varying(255) NOT NULL,
    anuncio_codigo character varying(255),
    programa_codigo character varying(255) NOT NULL,
    nombre character varying(255) NOT NULL,
    descripcion text,
    precio numeric(12,2) NOT NULL,
    estado character varying(255) NOT NULL,
    sincronizado_en timestamp(0) without time zone NOT NULL
);


--
-- Name: comisiones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comisiones (
    nro_solicitud bigint NOT NULL,
    porcentaje numeric(5,2) DEFAULT '2'::numeric NOT NULL,
    monto numeric(12,2) NOT NULL,
    estado character varying(255) DEFAULT 'Pendiente'::character varying NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    fecha_pago timestamp(0) without time zone,
    vendedor_correo character varying(255) NOT NULL,
    CONSTRAINT comisiones_estado_check CHECK (((estado)::text = ANY (ARRAY[('Pendiente'::character varying)::text, ('Pagada'::character varying)::text])))
);


--
-- Name: comprobantes_pago; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comprobantes_pago (
    nro_comprobante bigint NOT NULL,
    archivo text NOT NULL,
    nombre_archivo character varying(255),
    mime character varying(255),
    fecha_envio timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    observacion text,
    estado_revision character varying(255) DEFAULT 'En revision'::character varying NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    remitente character varying(255),
    hora_pago timestamp(0) without time zone,
    nro_orden bigint NOT NULL,
    nro_cuota smallint,
    CONSTRAINT comprobantes_pago_estado_revision_check CHECK (((estado_revision)::text = ANY (ARRAY[('En revision'::character varying)::text, ('Pago aprobado'::character varying)::text, ('Pago rechazado'::character varying)::text])))
);


--
-- Name: comprobantes_pago_nro_comprobante_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comprobantes_pago_nro_comprobante_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comprobantes_pago_nro_comprobante_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.comprobantes_pago_nro_comprobante_seq OWNED BY public.comprobantes_pago.nro_comprobante;


--
-- Name: configuraciones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.configuraciones (
    clave character varying(255) NOT NULL,
    valor character varying(255) NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    actualizado_por character varying(255)
);


--
-- Name: cuotas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cuotas (
    nro_orden bigint NOT NULL,
    nro_cuota smallint NOT NULL,
    monto numeric(12,2) NOT NULL,
    fecha_vencimiento date NOT NULL,
    estado character varying(255) DEFAULT 'Pendiente de pago'::character varying NOT NULL,
    fecha_pago timestamp(0) without time zone,
    nro_metodo bigint,
    observacion text,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    proveedor character varying(20) DEFAULT 'manual'::character varying NOT NULL,
    moneda character varying(10) DEFAULT 'BOB'::character varying NOT NULL,
    stripe_sesion character varying(160),
    stripe_pago_intent character varying(160),
    stripe_metodo character varying(160),
    stripe_recibo_url text,
    CONSTRAINT cuotas_estado_check CHECK (((estado)::text = ANY (ARRAY[('Pendiente de pago'::character varying)::text, ('En revision'::character varying)::text, ('Pago aprobado'::character varying)::text, ('Pago rechazado'::character varying)::text]))),
    CONSTRAINT cuotas_monto_check CHECK ((monto > (0)::numeric)),
    CONSTRAINT cuotas_nro_cuota_check CHECK (((nro_cuota >= 1) AND (nro_cuota <= 24))),
    CONSTRAINT cuotas_proveedor_check CHECK (((proveedor)::text = ANY (ARRAY[('manual'::character varying)::text, ('stripe'::character varying)::text])))
);


--
-- Name: descuentos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.descuentos (
    nombre character varying(255) NOT NULL,
    codigo character varying(255) NOT NULL,
    porcentaje numeric(5,2) NOT NULL,
    estado character varying(255) DEFAULT 'activo'::character varying NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    CONSTRAINT descuentos_estado_check CHECK (((estado)::text = ANY (ARRAY[('activo'::character varying)::text, ('inactivo'::character varying)::text])))
);


--
-- Name: exportaciones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.exportaciones (
    nro_exportacion bigint NOT NULL,
    fecha_exportacion timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    estado character varying(255) DEFAULT 'preparada'::character varying NOT NULL,
    respuesta text,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    usuario_correo character varying(255),
    nro_solicitud bigint NOT NULL,
    CONSTRAINT exportaciones_estado_check CHECK (((estado)::text = ANY (ARRAY[('preparada'::character varying)::text, ('exportada'::character varying)::text, ('recibida'::character varying)::text, ('error'::character varying)::text])))
);


--
-- Name: exportaciones_nro_exportacion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.exportaciones_nro_exportacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: exportaciones_nro_exportacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.exportaciones_nro_exportacion_seq OWNED BY public.exportaciones.nro_exportacion;


--
-- Name: inscripciones_comerciales; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inscripciones_comerciales (
    nro_solicitud bigint NOT NULL,
    fecha_confirmacion timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone
);


--
-- Name: interacciones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.interacciones (
    nro_interaccion bigint NOT NULL,
    tipo character varying(255) NOT NULL,
    descripcion text NOT NULL,
    resultado text,
    fecha timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    nro_tarjeta bigint NOT NULL,
    usuario_correo character varying(255) NOT NULL,
    CONSTRAINT interacciones_tipo_check CHECK (((tipo)::text = ANY (ARRAY[('WhatsApp'::character varying)::text, ('Llamada'::character varying)::text, ('Correo electronico'::character varying)::text, ('Reunion'::character varying)::text, ('Nota comercial'::character varying)::text, ('Orden de pago enviada'::character varying)::text, ('Pago informado'::character varying)::text, ('Compra validada'::character varying)::text, ('Orden finalizada'::character varying)::text])))
);


--
-- Name: interacciones_nro_interaccion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.interacciones_nro_interaccion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: interacciones_nro_interaccion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.interacciones_nro_interaccion_seq OWNED BY public.interacciones.nro_interaccion;


--
-- Name: intereses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.intereses (
    nro_tarjeta bigint NOT NULL,
    fecha timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    modulo_codigo character varying(255) NOT NULL,
    programa_nombre character varying(255) NOT NULL,
    modulo_nombre character varying(255) NOT NULL,
    precio numeric(12,2),
    anuncio_codigo character varying(255),
    modulo_descripcion text,
    estado character varying(255) DEFAULT 'Nuevo'::character varying NOT NULL,
    fecha_asignacion timestamp(0) without time zone,
    ultima_actividad_en timestamp(0) without time zone,
    proximo_contacto timestamp(0) without time zone,
    observacion text,
    vendedor_correo character varying(255),
    documento character varying(255) NOT NULL,
    motivo_perdida character varying(80),
    CONSTRAINT intereses_estado_check CHECK (((estado)::text = ANY (ARRAY[('Nuevo'::character varying)::text, ('En Contacto'::character varying)::text, ('Seguimiento'::character varying)::text, ('Promesa de Pago'::character varying)::text, ('Convertido'::character varying)::text, ('Perdido'::character varying)::text])))
);


--
-- Name: intereses_nro_tarjeta_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.intereses_nro_tarjeta_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: intereses_nro_tarjeta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.intereses_nro_tarjeta_seq OWNED BY public.intereses.nro_tarjeta;


--
-- Name: log_comandos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.log_comandos (
    nro_registro bigint NOT NULL,
    remitente character varying(160) NOT NULL,
    asunto character varying(300) NOT NULL,
    resultado character varying(20) NOT NULL,
    detalle text,
    fecha timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    rol_registrado character varying(40),
    usuario_correo character varying(255)
);


--
-- Name: log_comandos_nro_registro_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.log_comandos_nro_registro_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: log_comandos_nro_registro_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.log_comandos_nro_registro_seq OWNED BY public.log_comandos.nro_registro;


--
-- Name: metodos_pago; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.metodos_pago (
    nro_metodo bigint NOT NULL,
    documento character varying(255) NOT NULL,
    tipo character varying(20) NOT NULL,
    titular character varying(255) NOT NULL,
    marca character varying(20),
    ultimos_digitos character varying(4),
    vencimiento character varying(5),
    estado character varying(10) DEFAULT 'activo'::character varying NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    proveedor character varying(20) DEFAULT 'manual'::character varying NOT NULL,
    stripe_cliente character varying(120),
    stripe_metodo character varying(120),
    registrado_por character varying(255),
    CONSTRAINT metodos_pago_estado_check CHECK (((estado)::text = ANY (ARRAY[('activo'::character varying)::text, ('inactivo'::character varying)::text]))),
    CONSTRAINT metodos_pago_proveedor_check CHECK (((proveedor)::text = ANY (ARRAY[('manual'::character varying)::text, ('stripe'::character varying)::text]))),
    CONSTRAINT metodos_pago_tarjeta_check CHECK ((((tipo)::text <> 'Tarjeta'::text) OR ((marca IS NOT NULL) AND ((ultimos_digitos)::text ~ '^[0-9]{4}$'::text) AND ((vencimiento)::text ~ '^(0[1-9]|1[0-2])/[0-9]{2}$'::text)))),
    CONSTRAINT metodos_pago_tipo_check CHECK (((tipo)::text = ANY (ARRAY[('Tarjeta'::character varying)::text, ('QR'::character varying)::text, ('Transferencia'::character varying)::text])))
);


--
-- Name: metodos_pago_nro_metodo_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.metodos_pago_nro_metodo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: metodos_pago_nro_metodo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.metodos_pago_nro_metodo_seq OWNED BY public.metodos_pago.nro_metodo;


--
-- Name: motivos_perdida; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.motivos_perdida (
    nombre character varying(80) NOT NULL,
    categoria character varying(20) NOT NULL,
    CONSTRAINT motivos_categoria_check CHECK (((categoria)::text = ANY (ARRAY[('Económico'::character varying)::text, ('Horario'::character varying)::text, ('Incompatibilidad'::character varying)::text, ('Contacto'::character varying)::text, ('Otro'::character varying)::text])))
);


--
-- Name: movimientos_interes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.movimientos_interes (
    nro_movimiento bigint NOT NULL,
    nro_tarjeta bigint NOT NULL,
    estado_anterior character varying(255),
    estado_nuevo character varying(255) NOT NULL,
    detalle text,
    fecha timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    usuario_correo character varying(255)
);


--
-- Name: movimientos_interes_nro_movimiento_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.movimientos_interes_nro_movimiento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: movimientos_interes_nro_movimiento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.movimientos_interes_nro_movimiento_seq OWNED BY public.movimientos_interes.nro_movimiento;


--
-- Name: notificaciones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notificaciones (
    nro_notificacion bigint NOT NULL,
    destinatario character varying(255),
    tipo character varying(255) NOT NULL,
    mensaje text NOT NULL,
    estado character varying(255) DEFAULT 'enviada'::character varying NOT NULL,
    fecha_envio timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    usuario_correo character varying(255),
    CONSTRAINT notificaciones_estado_check CHECK (((estado)::text = ANY (ARRAY[('enviada'::character varying)::text, ('fallida'::character varying)::text, ('leida'::character varying)::text])))
);


--
-- Name: notificaciones_nro_notificacion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notificaciones_nro_notificacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notificaciones_nro_notificacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notificaciones_nro_notificacion_seq OWNED BY public.notificaciones.nro_notificacion;


--
-- Name: orden_pago_descuentos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orden_pago_descuentos (
    nro_orden bigint NOT NULL,
    porcentaje numeric(5,2) NOT NULL,
    monto numeric(12,2) NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    descuento_codigo character varying(255) NOT NULL
);


--
-- Name: ordenes_pago; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ordenes_pago (
    nro_orden bigint NOT NULL,
    nro_tarjeta bigint NOT NULL,
    subtotal numeric(12,2) NOT NULL,
    descuento_total numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    total numeric(12,2) NOT NULL,
    fecha_generacion timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    vendedor_correo character varying(255) NOT NULL,
    estado character varying(20) DEFAULT 'Activa'::character varying NOT NULL,
    motivo_anulacion text,
    fecha_anulacion timestamp(0) without time zone,
    anulada_por character varying(255),
    CONSTRAINT ordenes_pago_estado_check CHECK (((estado)::text = ANY (ARRAY[('Activa'::character varying)::text, ('Anulada'::character varying)::text])))
);


--
-- Name: ordenes_pago_nro_orden_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ordenes_pago_nro_orden_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ordenes_pago_nro_orden_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ordenes_pago_nro_orden_seq OWNED BY public.ordenes_pago.nro_orden;


--
-- Name: pagos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pagos (
    codigo_qr character varying(255) NOT NULL,
    estado character varying(255) DEFAULT 'Pendiente de pago'::character varying NOT NULL,
    fecha_validacion timestamp(0) without time zone,
    observacion_validacion text,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    nro_orden bigint NOT NULL,
    CONSTRAINT pagos_estado_check CHECK (((estado)::text = ANY (ARRAY[('Pendiente de pago'::character varying)::text, ('En revision'::character varying)::text, ('Pago aprobado'::character varying)::text, ('Pago rechazado'::character varying)::text])))
);


--
-- Name: permisos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.permisos (
    rol character varying(40) NOT NULL,
    recurso_codigo character varying(40) NOT NULL,
    acceso character varying(20) NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    CONSTRAINT permisos_acceso_check CHECK (((acceso)::text = ANY (ARRAY[('lectura'::character varying)::text, ('modificacion'::character varying)::text, ('eliminacion'::character varying)::text])))
);


--
-- Name: programas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.programas (
    codigo character varying(255) NOT NULL,
    nombre character varying(255) NOT NULL
);


--
-- Name: programas_responsables; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.programas_responsables (
    programa_codigo character varying(255) NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    coordinador_correo character varying(255) NOT NULL
);


--
-- Name: prospectos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prospectos (
    nombre character varying(255) NOT NULL,
    apellido character varying(255) NOT NULL,
    documento character varying(255) NOT NULL,
    correo character varying(255) NOT NULL,
    telefono character varying(255) NOT NULL,
    estado character varying(255) DEFAULT 'Nuevo'::character varying NOT NULL,
    fecha_registro timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    profesion character varying(255),
    ubicacion character varying(255),
    origen character varying(20) DEFAULT 'Web'::character varying NOT NULL,
    stripe_cliente character varying(120),
    CONSTRAINT prospectos_estado_check CHECK (((estado)::text = ANY (ARRAY[('Nuevo'::character varying)::text, ('En Contacto'::character varying)::text, ('Seguimiento'::character varying)::text, ('Promesa de Pago'::character varying)::text, ('Convertido'::character varying)::text, ('Perdido'::character varying)::text])))
);


--
-- Name: recordatorios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recordatorios (
    nro_recordatorio bigint NOT NULL,
    fecha_programada timestamp(0) without time zone NOT NULL,
    descripcion text NOT NULL,
    estado character varying(255) DEFAULT 'Pendiente'::character varying NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    nro_tarjeta bigint NOT NULL,
    fecha_realizada timestamp(0) without time zone,
    notificado boolean DEFAULT false NOT NULL,
    usuario_correo character varying(255) NOT NULL,
    CONSTRAINT recordatorios_estado_check CHECK (((estado)::text = ANY (ARRAY[('Pendiente'::character varying)::text, ('Realizada'::character varying)::text, ('Atrasada'::character varying)::text, ('Cancelado'::character varying)::text])))
);


--
-- Name: recordatorios_nro_recordatorio_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.recordatorios_nro_recordatorio_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: recordatorios_nro_recordatorio_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.recordatorios_nro_recordatorio_seq OWNED BY public.recordatorios.nro_recordatorio;


--
-- Name: recursos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recursos (
    codigo character varying(40) NOT NULL,
    nombre character varying(80) NOT NULL,
    ruta character varying(80) NOT NULL,
    icono character varying(40) NOT NULL,
    orden smallint NOT NULL,
    caso_uso character varying(4) NOT NULL,
    publico boolean DEFAULT false NOT NULL,
    visitas bigint DEFAULT '0'::bigint NOT NULL,
    CONSTRAINT recursos_caso_uso_check CHECK (((caso_uso)::text ~ '^CU[1-8]$'::text))
);


--
-- Name: roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles (
    nombre character varying(40) NOT NULL,
    descripcion character varying(255) NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone
);


--
-- Name: solicitudes_compra; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.solicitudes_compra (
    nro_solicitud bigint NOT NULL,
    precio_acordado numeric(12,2),
    fecha timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    anuncio_codigo character varying(255),
    modulo_codigo character varying(255) NOT NULL,
    programa_nombre character varying(255) NOT NULL,
    modulo_nombre character varying(255) NOT NULL,
    modulo_descripcion text,
    anuncio_titulo character varying(255),
    nro_orden bigint NOT NULL
);


--
-- Name: solicitudes_compra_nro_solicitud_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.solicitudes_compra_nro_solicitud_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: solicitudes_compra_nro_solicitud_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.solicitudes_compra_nro_solicitud_seq OWNED BY public.solicitudes_compra.nro_solicitud;


--
-- Name: transacciones_stripe; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transacciones_stripe (
    nro_transaccion bigint NOT NULL,
    tipo character varying(20) NOT NULL,
    nro_orden bigint,
    nro_cuota smallint,
    documento character varying(255),
    usuario_correo character varying(255),
    stripe_sesion character varying(160) NOT NULL,
    stripe_pago_intent character varying(160),
    stripe_setup_intent character varying(160),
    stripe_cliente character varying(120),
    stripe_metodo character varying(120),
    moneda character varying(10) DEFAULT 'bob'::character varying NOT NULL,
    monto_esperado numeric(12,2),
    monto_centavos integer,
    monto_confirmado numeric(12,2),
    estado_sesion character varying(40) DEFAULT 'open'::character varying NOT NULL,
    estado_pago character varying(40) DEFAULT 'unpaid'::character varying NOT NULL,
    estado_interno character varying(35) DEFAULT 'pendiente'::character varying NOT NULL,
    livemode boolean DEFAULT false NOT NULL,
    marca_tarjeta character varying(30),
    ultimos_digitos character varying(4),
    receipt_url text,
    url_checkout text,
    clave_idempotencia character varying(120),
    detalle_error text,
    confirmado_en timestamp(0) without time zone,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    CONSTRAINT transacciones_stripe_estado_interno_check CHECK (((estado_interno)::text = ANY (ARRAY[('pendiente'::character varying)::text, ('confirmado'::character varying)::text, ('rechazado'::character varying)::text, ('cancelado'::character varying)::text, ('expirado'::character varying)::text, ('reconciliacion_duplicada'::character varying)::text]))),
    CONSTRAINT transacciones_stripe_tipo_check CHECK (((tipo)::text = ANY (ARRAY[('payment'::character varying)::text, ('setup'::character varying)::text])))
);


--
-- Name: transacciones_stripe_nro_transaccion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.transacciones_stripe_nro_transaccion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: transacciones_stripe_nro_transaccion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.transacciones_stripe_nro_transaccion_seq OWNED BY public.transacciones_stripe.nro_transaccion;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    nombre character varying(255) NOT NULL,
    apellido character varying(255) NOT NULL,
    correo character varying(255) NOT NULL,
    telefono character varying(255),
    password character varying(255) NOT NULL,
    rol character varying(40) NOT NULL,
    estado character varying(255) DEFAULT 'activo'::character varying NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    fecha_inicio date DEFAULT CURRENT_DATE NOT NULL,
    fecha_fin date NOT NULL,
    foto character varying(255),
    CONSTRAINT usuarios_estado_check CHECK (((estado)::text = ANY (ARRAY[('activo'::character varying)::text, ('inactivo'::character varying)::text]))),
    CONSTRAINT usuarios_vigencia_check CHECK ((fecha_fin >= fecha_inicio))
);


--
-- Name: webhook_eventos_stripe; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.webhook_eventos_stripe (
    stripe_evento character varying(160) NOT NULL,
    tipo character varying(100) NOT NULL,
    nro_transaccion bigint,
    stripe_sesion character varying(160),
    stripe_pago_intent character varying(160),
    livemode boolean DEFAULT false NOT NULL,
    estado character varying(30) DEFAULT 'procesado'::character varying NOT NULL,
    resumen text,
    procesado_en timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    CONSTRAINT webhook_eventos_stripe_estado_check CHECK (((estado)::text = ANY (ARRAY[('procesado'::character varying)::text, ('ignorado'::character varying)::text, ('duplicado'::character varying)::text, ('error'::character varying)::text])))
);


--
-- Name: bitacora nro_registro; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bitacora ALTER COLUMN nro_registro SET DEFAULT nextval('public.bitacora_nro_registro_seq'::regclass);


--
-- Name: comprobantes_pago nro_comprobante; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comprobantes_pago ALTER COLUMN nro_comprobante SET DEFAULT nextval('public.comprobantes_pago_nro_comprobante_seq'::regclass);


--
-- Name: exportaciones nro_exportacion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exportaciones ALTER COLUMN nro_exportacion SET DEFAULT nextval('public.exportaciones_nro_exportacion_seq'::regclass);


--
-- Name: interacciones nro_interaccion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.interacciones ALTER COLUMN nro_interaccion SET DEFAULT nextval('public.interacciones_nro_interaccion_seq'::regclass);


--
-- Name: intereses nro_tarjeta; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intereses ALTER COLUMN nro_tarjeta SET DEFAULT nextval('public.intereses_nro_tarjeta_seq'::regclass);


--
-- Name: log_comandos nro_registro; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.log_comandos ALTER COLUMN nro_registro SET DEFAULT nextval('public.log_comandos_nro_registro_seq'::regclass);


--
-- Name: metodos_pago nro_metodo; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metodos_pago ALTER COLUMN nro_metodo SET DEFAULT nextval('public.metodos_pago_nro_metodo_seq'::regclass);


--
-- Name: movimientos_interes nro_movimiento; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.movimientos_interes ALTER COLUMN nro_movimiento SET DEFAULT nextval('public.movimientos_interes_nro_movimiento_seq'::regclass);


--
-- Name: notificaciones nro_notificacion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificaciones ALTER COLUMN nro_notificacion SET DEFAULT nextval('public.notificaciones_nro_notificacion_seq'::regclass);


--
-- Name: ordenes_pago nro_orden; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordenes_pago ALTER COLUMN nro_orden SET DEFAULT nextval('public.ordenes_pago_nro_orden_seq'::regclass);


--
-- Name: recordatorios nro_recordatorio; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recordatorios ALTER COLUMN nro_recordatorio SET DEFAULT nextval('public.recordatorios_nro_recordatorio_seq'::regclass);


--
-- Name: solicitudes_compra nro_solicitud; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solicitudes_compra ALTER COLUMN nro_solicitud SET DEFAULT nextval('public.solicitudes_compra_nro_solicitud_seq'::regclass);


--
-- Name: transacciones_stripe nro_transaccion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transacciones_stripe ALTER COLUMN nro_transaccion SET DEFAULT nextval('public.transacciones_stripe_nro_transaccion_seq'::regclass);


--
-- Name: api_tokens api_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_tokens
    ADD CONSTRAINT api_tokens_pkey PRIMARY KEY (token_hash);


--
-- Name: bitacora bitacora_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bitacora
    ADD CONSTRAINT bitacora_pkey PRIMARY KEY (nro_registro);


--
-- Name: catalogo_cache catalogo_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalogo_cache
    ADD CONSTRAINT catalogo_cache_pkey PRIMARY KEY (codigo);


--
-- Name: comisiones comisiones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comisiones
    ADD CONSTRAINT comisiones_pkey PRIMARY KEY (nro_solicitud);


--
-- Name: comprobantes_pago comprobantes_pago_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comprobantes_pago
    ADD CONSTRAINT comprobantes_pago_pkey PRIMARY KEY (nro_comprobante);


--
-- Name: configuraciones configuraciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuraciones
    ADD CONSTRAINT configuraciones_pkey PRIMARY KEY (clave);


--
-- Name: cuotas cuotas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cuotas
    ADD CONSTRAINT cuotas_pkey PRIMARY KEY (nro_orden, nro_cuota);


--
-- Name: descuentos descuentos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.descuentos
    ADD CONSTRAINT descuentos_pkey PRIMARY KEY (codigo);


--
-- Name: exportaciones exportaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exportaciones
    ADD CONSTRAINT exportaciones_pkey PRIMARY KEY (nro_exportacion);


--
-- Name: inscripciones_comerciales inscripciones_comerciales_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inscripciones_comerciales
    ADD CONSTRAINT inscripciones_comerciales_pkey PRIMARY KEY (nro_solicitud);


--
-- Name: interacciones interacciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.interacciones
    ADD CONSTRAINT interacciones_pkey PRIMARY KEY (nro_interaccion);


--
-- Name: intereses intereses_documento_modulo_codigo_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intereses
    ADD CONSTRAINT intereses_documento_modulo_codigo_unique UNIQUE (documento, modulo_codigo);


--
-- Name: intereses intereses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intereses
    ADD CONSTRAINT intereses_pkey PRIMARY KEY (nro_tarjeta);


--
-- Name: log_comandos log_comandos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.log_comandos
    ADD CONSTRAINT log_comandos_pkey PRIMARY KEY (nro_registro);


--
-- Name: metodos_pago metodos_pago_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metodos_pago
    ADD CONSTRAINT metodos_pago_pkey PRIMARY KEY (nro_metodo);


--
-- Name: motivos_perdida motivos_perdida_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.motivos_perdida
    ADD CONSTRAINT motivos_perdida_pkey PRIMARY KEY (nombre);


--
-- Name: movimientos_interes movimientos_interes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.movimientos_interes
    ADD CONSTRAINT movimientos_interes_pkey PRIMARY KEY (nro_movimiento);


--
-- Name: notificaciones notificaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_pkey PRIMARY KEY (nro_notificacion);


--
-- Name: orden_pago_descuentos orden_pago_descuentos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_pago_descuentos
    ADD CONSTRAINT orden_pago_descuentos_pkey PRIMARY KEY (nro_orden, descuento_codigo);


--
-- Name: ordenes_pago ordenes_pago_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordenes_pago
    ADD CONSTRAINT ordenes_pago_pkey PRIMARY KEY (nro_orden);


--
-- Name: pagos pagos_codigo_qr_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pagos
    ADD CONSTRAINT pagos_codigo_qr_unique UNIQUE (codigo_qr);


--
-- Name: pagos pagos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pagos
    ADD CONSTRAINT pagos_pkey PRIMARY KEY (nro_orden);


--
-- Name: permisos permisos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permisos
    ADD CONSTRAINT permisos_pkey PRIMARY KEY (rol, recurso_codigo);


--
-- Name: programas programas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programas
    ADD CONSTRAINT programas_pkey PRIMARY KEY (codigo);


--
-- Name: programas_responsables programas_responsables_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programas_responsables
    ADD CONSTRAINT programas_responsables_pkey PRIMARY KEY (programa_codigo);


--
-- Name: prospectos prospectos_correo_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prospectos
    ADD CONSTRAINT prospectos_correo_unique UNIQUE (correo);


--
-- Name: prospectos prospectos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prospectos
    ADD CONSTRAINT prospectos_pkey PRIMARY KEY (documento);


--
-- Name: recordatorios recordatorios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recordatorios
    ADD CONSTRAINT recordatorios_pkey PRIMARY KEY (nro_recordatorio);


--
-- Name: recursos recursos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recursos
    ADD CONSTRAINT recursos_pkey PRIMARY KEY (codigo);


--
-- Name: recursos recursos_ruta_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recursos
    ADD CONSTRAINT recursos_ruta_unique UNIQUE (ruta);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (nombre);


--
-- Name: solicitudes_compra solicitudes_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solicitudes_compra
    ADD CONSTRAINT solicitudes_compra_pkey PRIMARY KEY (nro_solicitud);


--
-- Name: transacciones_stripe transacciones_stripe_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transacciones_stripe
    ADD CONSTRAINT transacciones_stripe_pkey PRIMARY KEY (nro_transaccion);


--
-- Name: transacciones_stripe transacciones_stripe_sesion_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transacciones_stripe
    ADD CONSTRAINT transacciones_stripe_sesion_unique UNIQUE (stripe_sesion);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (correo);


--
-- Name: webhook_eventos_stripe webhook_eventos_stripe_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.webhook_eventos_stripe
    ADD CONSTRAINT webhook_eventos_stripe_pkey PRIMARY KEY (stripe_evento);


--
-- Name: bitacora_evento_fecha_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bitacora_evento_fecha_idx ON public.bitacora USING btree (evento, fecha);


--
-- Name: bitacora_recurso_fecha_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bitacora_recurso_fecha_idx ON public.bitacora USING btree (recurso_codigo, fecha);


--
-- Name: exportaciones_estado_fecha_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX exportaciones_estado_fecha_idx ON public.exportaciones USING btree (estado, fecha_exportacion);


--
-- Name: interacciones_usuario_fecha_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX interacciones_usuario_fecha_idx ON public.interacciones USING btree (usuario_correo, fecha);


--
-- Name: metodos_pago_stripe_metodo_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX metodos_pago_stripe_metodo_unique ON public.metodos_pago USING btree (stripe_metodo) WHERE (stripe_metodo IS NOT NULL);


--
-- Name: movimientos_interes_nro_tarjeta_fecha_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX movimientos_interes_nro_tarjeta_fecha_idx ON public.movimientos_interes USING btree (nro_tarjeta, fecha);


--
-- Name: notificaciones_usuario_estado_fecha_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notificaciones_usuario_estado_fecha_idx ON public.notificaciones USING btree (usuario_correo, estado, fecha_envio);


--
-- Name: pagos_estado_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX pagos_estado_idx ON public.pagos USING btree (estado);


--
-- Name: prospectos_correo_lower_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX prospectos_correo_lower_unique ON public.prospectos USING btree (lower((correo)::text));


--
-- Name: prospectos_stripe_cliente_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX prospectos_stripe_cliente_unique ON public.prospectos USING btree (stripe_cliente) WHERE (stripe_cliente IS NOT NULL);


--
-- Name: recordatorios_usuario_estado_fecha_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX recordatorios_usuario_estado_fecha_idx ON public.recordatorios USING btree (usuario_correo, estado, fecha_programada);


--
-- Name: solicitudes_modulo_fecha_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX solicitudes_modulo_fecha_idx ON public.solicitudes_compra USING btree (modulo_codigo, fecha);


--
-- Name: transacciones_stripe_cuota_estado_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX transacciones_stripe_cuota_estado_idx ON public.transacciones_stripe USING btree (nro_orden, nro_cuota, estado_interno);


--
-- Name: transacciones_stripe_pi_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX transacciones_stripe_pi_unique ON public.transacciones_stripe USING btree (stripe_pago_intent) WHERE (stripe_pago_intent IS NOT NULL);


--
-- Name: transacciones_stripe_si_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX transacciones_stripe_si_unique ON public.transacciones_stripe USING btree (stripe_setup_intent) WHERE (stripe_setup_intent IS NOT NULL);


--
-- Name: usuarios_correo_lower_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX usuarios_correo_lower_unique ON public.usuarios USING btree (lower((correo)::text));


--
-- Name: usuarios_rol_estado_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX usuarios_rol_estado_index ON public.usuarios USING btree (rol, estado);


--
-- Name: bitacora bitacora_contar_visita; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER bitacora_contar_visita AFTER INSERT ON public.bitacora FOR EACH ROW WHEN ((((new.evento)::text = 'visita'::text) AND (new.recurso_codigo IS NOT NULL))) EXECUTE FUNCTION public.contar_visita();


--
-- Name: intereses intereses_clasificar; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER intereses_clasificar BEFORE INSERT OR UPDATE ON public.intereses FOR EACH ROW EXECUTE FUNCTION public.clasificar_perdida();


--
-- Name: intereses intereses_historial; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER intereses_historial AFTER INSERT OR UPDATE ON public.intereses FOR EACH ROW EXECUTE FUNCTION public.registrar_movimiento_web();


--
-- Name: pagos pagos_copiar_estado; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER pagos_copiar_estado AFTER UPDATE OF estado ON public.pagos FOR EACH ROW EXECUTE FUNCTION public.copiar_estado_cuota_inicial();


--
-- Name: pagos pagos_crear_cuota; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER pagos_crear_cuota AFTER INSERT ON public.pagos FOR EACH ROW EXECUTE FUNCTION public.crear_cuota_unica();


--
-- Name: api_tokens api_tokens_usuario_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_tokens
    ADD CONSTRAINT api_tokens_usuario_correo_fk FOREIGN KEY (usuario_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: bitacora bitacora_recurso_codigo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bitacora
    ADD CONSTRAINT bitacora_recurso_codigo_fk FOREIGN KEY (recurso_codigo) REFERENCES public.recursos(codigo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: bitacora bitacora_usuario_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bitacora
    ADD CONSTRAINT bitacora_usuario_correo_fk FOREIGN KEY (usuario_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: catalogo_cache catalogo_cache_programa_codigo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.catalogo_cache
    ADD CONSTRAINT catalogo_cache_programa_codigo_fk FOREIGN KEY (programa_codigo) REFERENCES public.programas(codigo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: comisiones comisiones_nro_solicitud_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comisiones
    ADD CONSTRAINT comisiones_nro_solicitud_fk FOREIGN KEY (nro_solicitud) REFERENCES public.solicitudes_compra(nro_solicitud) ON DELETE RESTRICT;


--
-- Name: comisiones comisiones_vendedor_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comisiones
    ADD CONSTRAINT comisiones_vendedor_correo_fk FOREIGN KEY (vendedor_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: comprobantes_pago comprobantes_pago_cuota_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comprobantes_pago
    ADD CONSTRAINT comprobantes_pago_cuota_fk FOREIGN KEY (nro_orden, nro_cuota) REFERENCES public.cuotas(nro_orden, nro_cuota) ON DELETE CASCADE;


--
-- Name: comprobantes_pago comprobantes_pago_nro_orden_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comprobantes_pago
    ADD CONSTRAINT comprobantes_pago_nro_orden_fk FOREIGN KEY (nro_orden) REFERENCES public.pagos(nro_orden) ON DELETE CASCADE;


--
-- Name: configuraciones configuraciones_actualizado_por_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuraciones
    ADD CONSTRAINT configuraciones_actualizado_por_fk FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: cuotas cuotas_nro_metodo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cuotas
    ADD CONSTRAINT cuotas_nro_metodo_fk FOREIGN KEY (nro_metodo) REFERENCES public.metodos_pago(nro_metodo) ON DELETE RESTRICT;


--
-- Name: cuotas cuotas_nro_orden_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cuotas
    ADD CONSTRAINT cuotas_nro_orden_fk FOREIGN KEY (nro_orden) REFERENCES public.ordenes_pago(nro_orden) ON DELETE CASCADE;


--
-- Name: exportaciones exportaciones_nro_solicitud_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exportaciones
    ADD CONSTRAINT exportaciones_nro_solicitud_fk FOREIGN KEY (nro_solicitud) REFERENCES public.inscripciones_comerciales(nro_solicitud) ON DELETE RESTRICT;


--
-- Name: exportaciones exportaciones_usuario_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.exportaciones
    ADD CONSTRAINT exportaciones_usuario_correo_fk FOREIGN KEY (usuario_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: inscripciones_comerciales inscripciones_comerciales_nro_solicitud_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inscripciones_comerciales
    ADD CONSTRAINT inscripciones_comerciales_nro_solicitud_fk FOREIGN KEY (nro_solicitud) REFERENCES public.solicitudes_compra(nro_solicitud) ON DELETE RESTRICT;


--
-- Name: interacciones interacciones_nro_tarjeta_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.interacciones
    ADD CONSTRAINT interacciones_nro_tarjeta_fk FOREIGN KEY (nro_tarjeta) REFERENCES public.intereses(nro_tarjeta) ON DELETE RESTRICT;


--
-- Name: interacciones interacciones_usuario_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.interacciones
    ADD CONSTRAINT interacciones_usuario_correo_fk FOREIGN KEY (usuario_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: intereses intereses_documento_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intereses
    ADD CONSTRAINT intereses_documento_fk FOREIGN KEY (documento) REFERENCES public.prospectos(documento) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: intereses intereses_modulo_codigo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intereses
    ADD CONSTRAINT intereses_modulo_codigo_fk FOREIGN KEY (modulo_codigo) REFERENCES public.catalogo_cache(codigo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: intereses intereses_motivo_perdida_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intereses
    ADD CONSTRAINT intereses_motivo_perdida_fk FOREIGN KEY (motivo_perdida) REFERENCES public.motivos_perdida(nombre) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: intereses intereses_vendedor_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intereses
    ADD CONSTRAINT intereses_vendedor_correo_fk FOREIGN KEY (vendedor_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: log_comandos log_comandos_usuario_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.log_comandos
    ADD CONSTRAINT log_comandos_usuario_correo_fk FOREIGN KEY (usuario_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: metodos_pago metodos_pago_documento_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metodos_pago
    ADD CONSTRAINT metodos_pago_documento_fk FOREIGN KEY (documento) REFERENCES public.prospectos(documento) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: metodos_pago metodos_pago_registrado_por_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metodos_pago
    ADD CONSTRAINT metodos_pago_registrado_por_fk FOREIGN KEY (registrado_por) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: movimientos_interes movimientos_interes_nro_tarjeta_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.movimientos_interes
    ADD CONSTRAINT movimientos_interes_nro_tarjeta_fk FOREIGN KEY (nro_tarjeta) REFERENCES public.intereses(nro_tarjeta) ON DELETE RESTRICT;


--
-- Name: movimientos_interes movimientos_interes_usuario_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.movimientos_interes
    ADD CONSTRAINT movimientos_interes_usuario_correo_fk FOREIGN KEY (usuario_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: notificaciones notificaciones_usuario_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_usuario_correo_fk FOREIGN KEY (usuario_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: orden_pago_descuentos orden_pago_descuentos_descuento_codigo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_pago_descuentos
    ADD CONSTRAINT orden_pago_descuentos_descuento_codigo_fk FOREIGN KEY (descuento_codigo) REFERENCES public.descuentos(codigo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: orden_pago_descuentos orden_pago_descuentos_nro_orden_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_pago_descuentos
    ADD CONSTRAINT orden_pago_descuentos_nro_orden_fk FOREIGN KEY (nro_orden) REFERENCES public.ordenes_pago(nro_orden) ON DELETE CASCADE;


--
-- Name: ordenes_pago ordenes_pago_anulada_por_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordenes_pago
    ADD CONSTRAINT ordenes_pago_anulada_por_fk FOREIGN KEY (anulada_por) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: ordenes_pago ordenes_pago_nro_tarjeta_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordenes_pago
    ADD CONSTRAINT ordenes_pago_nro_tarjeta_fk FOREIGN KEY (nro_tarjeta) REFERENCES public.intereses(nro_tarjeta) ON DELETE RESTRICT;


--
-- Name: ordenes_pago ordenes_pago_vendedor_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordenes_pago
    ADD CONSTRAINT ordenes_pago_vendedor_correo_fk FOREIGN KEY (vendedor_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: pagos pagos_nro_orden_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pagos
    ADD CONSTRAINT pagos_nro_orden_fk FOREIGN KEY (nro_orden) REFERENCES public.ordenes_pago(nro_orden) ON DELETE RESTRICT;


--
-- Name: permisos permisos_recurso_codigo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permisos
    ADD CONSTRAINT permisos_recurso_codigo_fk FOREIGN KEY (recurso_codigo) REFERENCES public.recursos(codigo) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: permisos permisos_rol_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permisos
    ADD CONSTRAINT permisos_rol_fk FOREIGN KEY (rol) REFERENCES public.roles(nombre) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: programas_responsables programas_responsables_coordinador_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programas_responsables
    ADD CONSTRAINT programas_responsables_coordinador_correo_fk FOREIGN KEY (coordinador_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: programas_responsables programas_responsables_programa_codigo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.programas_responsables
    ADD CONSTRAINT programas_responsables_programa_codigo_fk FOREIGN KEY (programa_codigo) REFERENCES public.programas(codigo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: recordatorios recordatorios_nro_tarjeta_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recordatorios
    ADD CONSTRAINT recordatorios_nro_tarjeta_fk FOREIGN KEY (nro_tarjeta) REFERENCES public.intereses(nro_tarjeta) ON DELETE RESTRICT;


--
-- Name: recordatorios recordatorios_usuario_correo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recordatorios
    ADD CONSTRAINT recordatorios_usuario_correo_fk FOREIGN KEY (usuario_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: solicitudes_compra solicitudes_compra_modulo_codigo_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solicitudes_compra
    ADD CONSTRAINT solicitudes_compra_modulo_codigo_fk FOREIGN KEY (modulo_codigo) REFERENCES public.catalogo_cache(codigo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: solicitudes_compra solicitudes_compra_nro_orden_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solicitudes_compra
    ADD CONSTRAINT solicitudes_compra_nro_orden_fk FOREIGN KEY (nro_orden) REFERENCES public.ordenes_pago(nro_orden) ON DELETE CASCADE;


--
-- Name: transacciones_stripe transacciones_stripe_cuota_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transacciones_stripe
    ADD CONSTRAINT transacciones_stripe_cuota_fk FOREIGN KEY (nro_orden, nro_cuota) REFERENCES public.cuotas(nro_orden, nro_cuota) ON DELETE RESTRICT;


--
-- Name: transacciones_stripe transacciones_stripe_documento_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transacciones_stripe
    ADD CONSTRAINT transacciones_stripe_documento_fk FOREIGN KEY (documento) REFERENCES public.prospectos(documento) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: transacciones_stripe transacciones_stripe_orden_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transacciones_stripe
    ADD CONSTRAINT transacciones_stripe_orden_fk FOREIGN KEY (nro_orden) REFERENCES public.ordenes_pago(nro_orden) ON DELETE RESTRICT;


--
-- Name: transacciones_stripe transacciones_stripe_usuario_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transacciones_stripe
    ADD CONSTRAINT transacciones_stripe_usuario_fk FOREIGN KEY (usuario_correo) REFERENCES public.usuarios(correo) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: usuarios usuarios_rol_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_rol_fk FOREIGN KEY (rol) REFERENCES public.roles(nombre) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: webhook_eventos_stripe webhook_eventos_stripe_tx_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.webhook_eventos_stripe
    ADD CONSTRAINT webhook_eventos_stripe_tx_fk FOREIGN KEY (nro_transaccion) REFERENCES public.transacciones_stripe(nro_transaccion) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict KFaEtLSVAxsKlKsdAOocAbYU3GsvBX0dFy6bugFkQ5hGPviD3jXIjbQxcchvL9g

