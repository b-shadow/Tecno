-- UNEXO: esquema completo y datos ficticios de demostracion. PostgreSQL 17 o superior.
-- Instalar exclusivamente en una base nueva y vacia; no ejecutar sobre la base institucional.
DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind IN ('r','p','v','m','S','f')) THEN RAISE EXCEPTION 'La base destino no esta vacia'; END IF; END $$;
--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

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

CREATE SCHEMA IF NOT EXISTS public;


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
    token_pago character varying(80),
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
    token_publico character varying(80),
    expira_en timestamp(0) without time zone,
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
-- Data for Name: api_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.api_tokens (token_hash, ultimo_uso_en, expira_en, created_at, updated_at, usuario_correo) FROM stdin;
\.


--
-- Data for Name: bitacora; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.bitacora (nro_registro, evento, usuario_correo, correo_intentado, recurso_codigo, ip, navegador, fecha) FROM stdin;
1	visita	\N	\N	catalogo	192.168.1.10	\N	2026-11-27 12:15:05
2	visita	\N	\N	catalogo	192.168.1.11	\N	2026-11-26 12:15:05
3	visita	\N	\N	catalogo	192.168.1.12	\N	2026-11-25 12:15:05
4	visita	\N	\N	catalogo	192.168.1.13	\N	2026-11-24 12:15:05
5	visita	\N	\N	catalogo	192.168.1.14	\N	2026-11-23 12:15:05
6	visita	\N	\N	catalogo	192.168.1.15	\N	2026-11-22 12:15:05
7	visita	\N	\N	catalogo	192.168.1.16	\N	2026-11-21 12:15:05
8	visita	\N	\N	catalogo	192.168.1.17	\N	2026-11-20 12:15:05
9	visita	\N	\N	catalogo	192.168.1.18	\N	2026-11-19 12:15:05
10	visita	\N	\N	catalogo	192.168.1.19	\N	2026-11-18 12:15:05
11	visita	\N	\N	catalogo	192.168.1.20	\N	2026-11-17 12:15:05
12	visita	\N	\N	catalogo	192.168.1.21	\N	2026-11-16 12:15:05
13	visita	\N	\N	catalogo	192.168.1.22	\N	2026-11-15 12:15:05
14	visita	\N	\N	catalogo	192.168.1.23	\N	2026-11-14 12:15:05
15	visita	\N	\N	catalogo	192.168.1.24	\N	2026-11-27 12:15:05
16	visita	\N	\N	catalogo	192.168.1.25	\N	2026-11-26 12:15:05
17	visita	\N	\N	catalogo	192.168.1.26	\N	2026-11-25 12:15:05
18	visita	\N	\N	catalogo	192.168.1.27	\N	2026-11-24 12:15:05
19	visita	\N	\N	catalogo	192.168.1.28	\N	2026-11-23 12:15:05
20	visita	\N	\N	catalogo	192.168.1.29	\N	2026-11-22 12:15:05
21	visita	\N	\N	catalogo	192.168.1.30	\N	2026-11-21 12:15:05
22	visita	\N	\N	catalogo	192.168.1.31	\N	2026-11-20 12:15:05
23	visita	\N	\N	catalogo	192.168.1.32	\N	2026-11-19 12:15:05
24	visita	\N	\N	catalogo	192.168.1.33	\N	2026-11-18 12:15:05
25	visita	\N	\N	catalogo	192.168.1.34	\N	2026-11-17 12:15:05
26	visita	\N	\N	catalogo	192.168.1.35	\N	2026-11-16 12:15:05
27	visita	\N	\N	catalogo	192.168.1.36	\N	2026-11-15 12:15:05
28	visita	\N	\N	catalogo	192.168.1.37	\N	2026-11-14 12:15:05
29	visita	\N	\N	catalogo	192.168.1.38	\N	2026-11-27 12:15:05
30	visita	\N	\N	catalogo	192.168.1.39	\N	2026-11-26 12:15:05
31	visita	\N	\N	catalogo	192.168.1.10	\N	2026-11-25 12:15:05
32	visita	\N	\N	catalogo	192.168.1.11	\N	2026-11-24 12:15:05
33	visita	\N	\N	catalogo	192.168.1.12	\N	2026-11-23 12:15:05
34	visita	\N	\N	catalogo	192.168.1.13	\N	2026-11-22 12:15:05
35	visita	\N	\N	catalogo	192.168.1.14	\N	2026-11-21 12:15:05
36	visita	\N	\N	catalogo	192.168.1.15	\N	2026-11-20 12:15:05
37	visita	\N	\N	catalogo	192.168.1.16	\N	2026-11-19 12:15:05
38	visita	\N	\N	catalogo	192.168.1.17	\N	2026-11-18 12:15:05
39	visita	\N	\N	catalogo	192.168.1.18	\N	2026-11-17 12:15:05
40	visita	\N	\N	catalogo	192.168.1.19	\N	2026-11-16 12:15:05
41	visita	\N	\N	catalogo	192.168.1.20	\N	2026-11-15 12:15:05
42	visita	\N	\N	catalogo	192.168.1.21	\N	2026-11-14 12:15:05
43	visita	\N	\N	login	192.168.1.10	\N	2026-11-27 12:15:05
44	visita	\N	\N	login	192.168.1.11	\N	2026-11-26 12:15:05
45	visita	\N	\N	login	192.168.1.12	\N	2026-11-25 12:15:05
46	visita	\N	\N	login	192.168.1.13	\N	2026-11-24 12:15:05
47	visita	\N	\N	login	192.168.1.14	\N	2026-11-23 12:15:05
48	visita	\N	\N	login	192.168.1.15	\N	2026-11-22 12:15:05
49	visita	\N	\N	login	192.168.1.16	\N	2026-11-21 12:15:05
50	visita	\N	\N	login	192.168.1.17	\N	2026-11-20 12:15:05
51	visita	\N	\N	login	192.168.1.18	\N	2026-11-19 12:15:05
52	visita	\N	\N	login	192.168.1.19	\N	2026-11-18 12:15:05
53	visita	\N	\N	login	192.168.1.20	\N	2026-11-17 12:15:05
54	visita	\N	\N	login	192.168.1.21	\N	2026-11-16 12:15:05
55	visita	\N	\N	login	192.168.1.22	\N	2026-11-15 12:15:05
56	visita	\N	\N	login	192.168.1.23	\N	2026-11-14 12:15:05
57	visita	\N	\N	login	192.168.1.24	\N	2026-11-27 12:15:05
58	visita	\N	\N	login	192.168.1.25	\N	2026-11-26 12:15:05
59	visita	\N	\N	login	192.168.1.26	\N	2026-11-25 12:15:05
60	visita	\N	\N	login	192.168.1.27	\N	2026-11-24 12:15:05
61	visita	\N	\N	dashboard	192.168.1.10	\N	2026-11-27 12:15:05
62	visita	\N	\N	dashboard	192.168.1.11	\N	2026-11-26 12:15:05
63	visita	\N	\N	dashboard	192.168.1.12	\N	2026-11-25 12:15:05
64	visita	\N	\N	dashboard	192.168.1.13	\N	2026-11-24 12:15:05
65	visita	\N	\N	dashboard	192.168.1.14	\N	2026-11-23 12:15:05
66	visita	\N	\N	dashboard	192.168.1.15	\N	2026-11-22 12:15:05
67	visita	\N	\N	dashboard	192.168.1.16	\N	2026-11-21 12:15:05
68	visita	\N	\N	dashboard	192.168.1.17	\N	2026-11-20 12:15:05
69	visita	\N	\N	dashboard	192.168.1.18	\N	2026-11-19 12:15:05
70	visita	\N	\N	dashboard	192.168.1.19	\N	2026-11-18 12:15:05
71	visita	\N	\N	dashboard	192.168.1.20	\N	2026-11-17 12:15:05
72	visita	\N	\N	dashboard	192.168.1.21	\N	2026-11-16 12:15:05
73	visita	\N	\N	dashboard	192.168.1.22	\N	2026-11-15 12:15:05
74	visita	\N	\N	dashboard	192.168.1.23	\N	2026-11-14 12:15:05
75	visita	\N	\N	dashboard	192.168.1.24	\N	2026-11-27 12:15:05
76	visita	\N	\N	dashboard	192.168.1.25	\N	2026-11-26 12:15:05
77	visita	\N	\N	dashboard	192.168.1.26	\N	2026-11-25 12:15:05
78	visita	\N	\N	dashboard	192.168.1.27	\N	2026-11-24 12:15:05
79	visita	\N	\N	dashboard	192.168.1.28	\N	2026-11-23 12:15:05
80	visita	\N	\N	dashboard	192.168.1.29	\N	2026-11-22 12:15:05
81	visita	\N	\N	dashboard	192.168.1.30	\N	2026-11-21 12:15:05
82	visita	\N	\N	dashboard	192.168.1.31	\N	2026-11-20 12:15:05
83	visita	\N	\N	dashboard	192.168.1.32	\N	2026-11-19 12:15:05
84	visita	\N	\N	dashboard	192.168.1.33	\N	2026-11-18 12:15:05
85	visita	\N	\N	dashboard	192.168.1.34	\N	2026-11-17 12:15:05
86	visita	\N	\N	embudo	192.168.1.10	\N	2026-11-27 12:15:05
87	visita	\N	\N	embudo	192.168.1.11	\N	2026-11-26 12:15:05
88	visita	\N	\N	embudo	192.168.1.12	\N	2026-11-25 12:15:05
89	visita	\N	\N	embudo	192.168.1.13	\N	2026-11-24 12:15:05
90	visita	\N	\N	embudo	192.168.1.14	\N	2026-11-23 12:15:05
91	visita	\N	\N	embudo	192.168.1.15	\N	2026-11-22 12:15:05
92	visita	\N	\N	embudo	192.168.1.16	\N	2026-11-21 12:15:05
93	visita	\N	\N	embudo	192.168.1.17	\N	2026-11-20 12:15:05
94	visita	\N	\N	embudo	192.168.1.18	\N	2026-11-19 12:15:05
95	visita	\N	\N	embudo	192.168.1.19	\N	2026-11-18 12:15:05
96	visita	\N	\N	embudo	192.168.1.20	\N	2026-11-17 12:15:05
97	visita	\N	\N	embudo	192.168.1.21	\N	2026-11-16 12:15:05
98	visita	\N	\N	embudo	192.168.1.22	\N	2026-11-15 12:15:05
99	visita	\N	\N	embudo	192.168.1.23	\N	2026-11-14 12:15:05
100	visita	\N	\N	embudo	192.168.1.24	\N	2026-11-27 12:15:06
101	visita	\N	\N	embudo	192.168.1.25	\N	2026-11-26 12:15:06
102	visita	\N	\N	embudo	192.168.1.26	\N	2026-11-25 12:15:06
103	visita	\N	\N	embudo	192.168.1.27	\N	2026-11-24 12:15:06
104	visita	\N	\N	embudo	192.168.1.28	\N	2026-11-23 12:15:06
105	visita	\N	\N	embudo	192.168.1.29	\N	2026-11-22 12:15:06
106	visita	\N	\N	embudo	192.168.1.30	\N	2026-11-21 12:15:06
107	visita	\N	\N	embudo	192.168.1.31	\N	2026-11-20 12:15:06
108	visita	\N	\N	embudo	192.168.1.32	\N	2026-11-19 12:15:06
109	visita	\N	\N	embudo	192.168.1.33	\N	2026-11-18 12:15:06
110	visita	\N	\N	embudo	192.168.1.34	\N	2026-11-17 12:15:06
111	visita	\N	\N	embudo	192.168.1.35	\N	2026-11-16 12:15:06
112	visita	\N	\N	embudo	192.168.1.36	\N	2026-11-15 12:15:06
113	visita	\N	\N	embudo	192.168.1.37	\N	2026-11-14 12:15:06
114	visita	\N	\N	embudo	192.168.1.38	\N	2026-11-27 12:15:06
115	visita	\N	\N	embudo	192.168.1.39	\N	2026-11-26 12:15:06
116	visita	\N	\N	embudo	192.168.1.10	\N	2026-11-25 12:15:06
117	visita	\N	\N	agenda	192.168.1.10	\N	2026-11-27 12:15:06
118	visita	\N	\N	agenda	192.168.1.11	\N	2026-11-26 12:15:06
119	visita	\N	\N	agenda	192.168.1.12	\N	2026-11-25 12:15:06
120	visita	\N	\N	agenda	192.168.1.13	\N	2026-11-24 12:15:06
121	visita	\N	\N	agenda	192.168.1.14	\N	2026-11-23 12:15:06
122	visita	\N	\N	agenda	192.168.1.15	\N	2026-11-22 12:15:06
123	visita	\N	\N	agenda	192.168.1.16	\N	2026-11-21 12:15:06
124	visita	\N	\N	agenda	192.168.1.17	\N	2026-11-20 12:15:06
125	visita	\N	\N	agenda	192.168.1.18	\N	2026-11-19 12:15:06
126	visita	\N	\N	agenda	192.168.1.19	\N	2026-11-18 12:15:06
127	visita	\N	\N	agenda	192.168.1.20	\N	2026-11-17 12:15:06
128	visita	\N	\N	agenda	192.168.1.21	\N	2026-11-16 12:15:06
129	visita	\N	\N	agenda	192.168.1.22	\N	2026-11-15 12:15:06
130	visita	\N	\N	agenda	192.168.1.23	\N	2026-11-14 12:15:06
131	visita	\N	\N	agenda	192.168.1.24	\N	2026-11-27 12:15:06
132	visita	\N	\N	agenda	192.168.1.25	\N	2026-11-26 12:15:06
133	visita	\N	\N	agenda	192.168.1.26	\N	2026-11-25 12:15:06
134	visita	\N	\N	agenda	192.168.1.27	\N	2026-11-24 12:15:06
135	visita	\N	\N	agenda	192.168.1.28	\N	2026-11-23 12:15:06
136	visita	\N	\N	agenda	192.168.1.29	\N	2026-11-22 12:15:06
137	visita	\N	\N	agenda	192.168.1.30	\N	2026-11-21 12:15:06
138	visita	\N	\N	agenda	192.168.1.31	\N	2026-11-20 12:15:06
139	visita	\N	\N	reportes	192.168.1.10	\N	2026-11-27 12:15:06
140	visita	\N	\N	reportes	192.168.1.11	\N	2026-11-26 12:15:06
141	visita	\N	\N	reportes	192.168.1.12	\N	2026-11-25 12:15:06
142	visita	\N	\N	reportes	192.168.1.13	\N	2026-11-24 12:15:06
143	visita	\N	\N	reportes	192.168.1.14	\N	2026-11-23 12:15:06
144	visita	\N	\N	reportes	192.168.1.15	\N	2026-11-22 12:15:06
145	visita	\N	\N	reportes	192.168.1.16	\N	2026-11-21 12:15:06
146	visita	\N	\N	reportes	192.168.1.17	\N	2026-11-20 12:15:06
147	visita	\N	\N	reportes	192.168.1.18	\N	2026-11-19 12:15:06
148	login_exitoso	vendedor.demo@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-27 12:15:06
149	login_fallido	\N	desconocido@correo.bo	login	181.115.20.0	\N	2026-11-27 12:15:06
150	login_exitoso	vendedor2@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-26 12:15:06
151	login_exitoso	vendedor.demo@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-25 12:15:06
152	login_exitoso	vendedor2@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-24 12:15:06
153	login_fallido	\N	desconocido@correo.bo	login	181.115.20.3	\N	2026-11-24 12:15:06
154	login_exitoso	vendedor.demo@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-23 12:15:06
155	login_exitoso	vendedor2@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-22 12:15:06
156	login_exitoso	vendedor.demo@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-21 12:15:06
157	login_fallido	\N	desconocido@correo.bo	login	181.115.20.6	\N	2026-11-21 12:15:06
158	login_exitoso	vendedor2@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-20 12:15:06
159	login_exitoso	vendedor.demo@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-19 12:15:06
160	login_exitoso	vendedor2@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-18 12:15:06
161	login_fallido	\N	desconocido@correo.bo	login	181.115.20.9	\N	2026-11-18 12:15:06
162	login_exitoso	vendedor.demo@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-17 12:15:06
163	login_exitoso	vendedor2@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-16 12:15:06
164	login_exitoso	vendedor.demo@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-15 12:15:06
165	login_fallido	\N	desconocido@correo.bo	login	181.115.20.12	\N	2026-11-15 12:15:06
166	login_exitoso	vendedor2@crm-educativo.local	\N	login	192.168.1.20	\N	2026-11-14 12:15:06
\.


--
-- Data for Name: catalogo_cache; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.catalogo_cache (codigo, anuncio_codigo, programa_codigo, nombre, descripcion, precio, estado, sincronizado_en) FROM stdin;
desarrollo-web-m1	anuncio-desarrollo-web-m1	desarrollo-web	Fundamentos de Desarrollo Web	Aprende HTML, CSS, JavaScript base y arquitectura web.	420.00	abierto	2026-11-17 07:06:48
desarrollo-web-m2	anuncio-desarrollo-web-m2	desarrollo-web	Desarrollo Frontend	Construye interfaces modernas, responsivas y orientadas a componentes.	780.00	abierto	2026-11-17 07:06:50
desarrollo-web-m3	anuncio-desarrollo-web-m3	desarrollo-web	Desarrollo Backend	Implementa APIs, servicios y lógica de negocio para aplicaciones web.	960.00	abierto	2026-11-17 07:06:53
desarrollo-web-m4	anuncio-desarrollo-web-m4	desarrollo-web	Bases de Datos	Modela, consulta y administra datos para sistemas web.	680.00	abierto	2026-11-17 07:06:55
desarrollo-web-m5	anuncio-desarrollo-web-m5	desarrollo-web	Despliegue de Aplicaciones	Publica aplicaciones con buenas prácticas de configuración y monitoreo.	540.00	abierto	2026-11-17 07:06:57
ia-aplicada-m1	anuncio-ia-aplicada-m1	ia-aplicada	Fundamentos de Inteligencia Artificial	Comprende conceptos, casos de uso y limites de la IA.	600.00	abierto	2026-11-17 07:06:59
ia-aplicada-m2	anuncio-ia-aplicada-m2	ia-aplicada	Programación con Python	Domina Python aplicado a automatización, datos e IA.	720.00	abierto	2026-11-17 07:07:01
ia-aplicada-m3	anuncio-ia-aplicada-m3	ia-aplicada	Machine Learning	Entrena modelos predictivos y evalua su rendimiento.	1280.00	abierto	2026-11-17 07:07:04
ia-aplicada-m4	anuncio-ia-aplicada-m4	ia-aplicada	Redes Neuronales	Explora arquitecturas neuronales para reconocimiento y predicción.	1460.00	abierto	2026-11-17 07:07:06
ia-aplicada-m5	anuncio-ia-aplicada-m5	ia-aplicada	Inteligencia Artificial Generativa	Crea soluciones con modelos generativos, prompts y agentes.	1880.00	abierto	2026-11-17 07:07:08
ciberseguridad-m1	anuncio-ciberseguridad-m1	ciberseguridad	Fundamentos de Ciberseguridad	Identifica amenazas, controles y principios de seguridad.	500.00	abierto	2026-11-17 07:07:10
ciberseguridad-m2	anuncio-ciberseguridad-m2	ciberseguridad	Seguridad de Redes	Protege comunicaciones, topologías y servicios de red.	840.00	abierto	2026-11-17 07:07:13
ciberseguridad-m3	anuncio-ciberseguridad-m3	ciberseguridad	Seguridad de Sistemas Operativos	Endurece sistemas Linux y Windows para entornos productivos.	900.00	abierto	2026-11-17 07:07:15
ciberseguridad-m4	anuncio-ciberseguridad-m4	ciberseguridad	Análisis de Vulnerabilidades	Detecta, prioriza y documenta riesgos técnicos.	1320.00	abierto	2026-11-17 07:07:17
ciberseguridad-m5	anuncio-ciberseguridad-m5	ciberseguridad	Seguridad de Aplicaciones Web	Evalua aplicaciones web con enfoque defensivo y OWASP.	1560.00	abierto	2026-11-17 07:07:19
redes-servidores-m1	anuncio-redes-servidores-m1	redes-servidores	Fundamentos de Redes	Comprende modelos de red, direccionamiento y servicios esenciales.	460.00	abierto	2026-11-17 07:07:21
redes-servidores-m2	anuncio-redes-servidores-m2	redes-servidores	Configuración de Redes	Configura equipos, segmentos, rutas y servicios de conectividad.	740.00	abierto	2026-11-17 07:07:24
redes-servidores-m3	anuncio-redes-servidores-m3	redes-servidores	Administración de Servidores Linux	Administra servicios, usuarios, permisos y automatización en Linux.	980.00	abierto	2026-11-17 07:07:26
redes-servidores-m4	anuncio-redes-servidores-m4	redes-servidores	Administración de Servidores Windows	Gestiona servicios Windows Server y entornos corporativos.	980.00	abierto	2026-11-17 07:07:28
redes-servidores-m5	anuncio-redes-servidores-m5	redes-servidores	Virtualización y Contenedores	Implementa entornos virtualizados y contenedores para despliegue.	1180.00	abierto	2026-11-17 07:07:30
datos-bi-m1	anuncio-datos-bi-m1	datos-bi	Fundamentos de Bases de Datos	Aprende conceptos de datos relacionales para análisis.	520.00	abierto	2026-11-17 07:07:33
datos-bi-m2	anuncio-datos-bi-m2	datos-bi	SQL para Análisis de Datos	Consulta, transforma y resume información con SQL.	700.00	abierto	2026-11-17 07:07:35
datos-bi-m3	anuncio-datos-bi-m3	datos-bi	Análisis de Datos con Python	Procesa datos y genera hallazgos con Python.	1060.00	abierto	2026-11-17 07:07:37
datos-bi-m4	anuncio-datos-bi-m4	datos-bi	Business Intelligence con Power BI	Construye modelos, reportes y visualizaciones ejecutivas.	1220.00	abierto	2026-11-17 07:07:39
datos-bi-m5	anuncio-datos-bi-m5	datos-bi	Diseño de Dashboards	Crea tableros claros, útiles y orientados a decisiones.	880.00	abierto	2026-11-17 07:07:41
\.


--
-- Data for Name: comisiones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.comisiones (nro_solicitud, porcentaje, monto, estado, created_at, updated_at, fecha_pago, vendedor_correo) FROM stdin;
3	2.00	23.60	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	\N	vendedor.demo@crm-educativo.local
4	2.00	18.00	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	\N	vendedor2@crm-educativo.local
\.


--
-- Data for Name: comprobantes_pago; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.comprobantes_pago (nro_comprobante, archivo, nombre_archivo, mime, fecha_envio, observacion, estado_revision, created_at, updated_at, remitente, hora_pago, nro_orden, nro_cuota) FROM stdin;
\.


--
-- Data for Name: configuraciones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.configuraciones (clave, valor, created_at, updated_at, actualizado_por) FROM stdin;
comision_porcentaje	2	2026-11-17 05:18:41	2026-11-17 05:18:41	\N
\.


--
-- Data for Name: cuotas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cuotas (nro_orden, nro_cuota, monto, fecha_vencimiento, estado, fecha_pago, nro_metodo, observacion, created_at, updated_at, proveedor, moneda, stripe_sesion, stripe_pago_intent, stripe_metodo, stripe_recibo_url, token_pago) FROM stdin;
1	1	1460.00	2026-11-27	Pendiente de pago	\N	\N	\N	2026-11-27 12:15:05	2026-11-27 12:15:05	manual	BOB	\N	\N	\N	\N	\N
2	1	246.66	2026-11-27	Pendiente de pago	\N	\N	\N	2026-11-27 12:15:05	2026-11-27 12:15:05	manual	BOB	\N	\N	\N	\N	\N
2	2	246.66	2026-12-27	Pendiente de pago	\N	\N	\N	2026-11-27 12:15:05	2026-11-27 12:15:05	manual	BOB	\N	\N	\N	\N	\N
2	3	246.68	2027-01-27	Pendiente de pago	\N	\N	\N	2026-11-27 12:15:05	2026-11-27 12:15:05	manual	BOB	\N	\N	\N	\N	\N
3	1	1180.00	2026-11-27	Pago aprobado	2026-11-25 12:15:05	\N	\N	2026-11-27 12:15:05	2026-11-27 12:15:06	manual	BOB	\N	\N	\N	\N	\N
4	2	300.00	2026-12-27	Pendiente de pago	\N	\N	\N	2026-11-27 12:15:05	2026-11-27 12:15:05	manual	BOB	\N	\N	\N	\N	\N
4	3	300.00	2027-01-27	Pendiente de pago	\N	\N	\N	2026-11-27 12:15:05	2026-11-27 12:15:05	manual	BOB	\N	\N	\N	\N	\N
4	1	300.00	2026-11-27	Pago aprobado	2026-11-25 12:15:05	\N	\N	2026-11-27 12:15:05	2026-11-27 12:15:06	manual	BOB	\N	\N	\N	\N	\N
\.


--
-- Data for Name: descuentos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.descuentos (nombre, codigo, porcentaje, estado, created_at, updated_at) FROM stdin;
3 o mas modulos	3_MAS_MODULOS	10.00	activo	2026-11-17 07:06:42	2026-11-17 07:06:42
Programa completo	PROGRAMA_COMPLETO	15.00	activo	2026-11-17 07:06:43	2026-11-17 07:06:43
Cliente recurrente	CLIENTE_RECURRENTE	10.00	activo	2026-11-17 07:06:44	2026-11-17 07:06:44
\.


--
-- Data for Name: exportaciones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.exportaciones (nro_exportacion, fecha_exportacion, estado, respuesta, created_at, updated_at, usuario_correo, nro_solicitud) FROM stdin;
\.


--
-- Data for Name: inscripciones_comerciales; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inscripciones_comerciales (nro_solicitud, fecha_confirmacion, created_at, updated_at) FROM stdin;
3	2026-11-27 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05
4	2026-11-27 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05
\.


--
-- Data for Name: interacciones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.interacciones (nro_interaccion, tipo, descripcion, resultado, fecha, created_at, updated_at, nro_tarjeta, usuario_correo) FROM stdin;
1	WhatsApp	Se envió el PDF del programa por WhatsApp.	Pidió detalles de horarios	2026-11-20 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	3	vendedor.demo@crm-educativo.local
2	WhatsApp	Se envió el PDF del programa por WhatsApp.	Pidió detalles de horarios	2026-11-21 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	4	vendedor2@crm-educativo.local
3	WhatsApp	Se envió el PDF del programa por WhatsApp.	Pidió detalles de horarios	2026-11-22 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	5	vendedor.demo@crm-educativo.local
4	WhatsApp	Se envió el PDF del programa por WhatsApp.	Pidió detalles de horarios	2026-11-23 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	6	vendedor2@crm-educativo.local
5	WhatsApp	Se envió el PDF del programa por WhatsApp.	Pidió detalles de horarios	2026-11-24 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	7	vendedor.demo@crm-educativo.local
6	WhatsApp	Se envió el PDF del programa por WhatsApp.	Pidió detalles de horarios	2026-11-25 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	8	vendedor2@crm-educativo.local
7	WhatsApp	Se envió el PDF del programa por WhatsApp.	Pidió detalles de horarios	2026-11-18 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	9	vendedor.demo@crm-educativo.local
8	Compra validada	Datos completos validados. Matrícula comercial confirmada para 1 módulo(s).	Convertido	2026-11-27 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	9	admin@crm-educativo.local
9	WhatsApp	Se envió el PDF del programa por WhatsApp.	Pidió detalles de horarios	2026-11-19 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	10	vendedor2@crm-educativo.local
10	Compra validada	Datos completos validados. Matrícula comercial confirmada para 1 módulo(s).	Convertido	2026-11-27 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	10	admin@crm-educativo.local
11	WhatsApp	Se envió el PDF del programa por WhatsApp.	Pidió detalles de horarios	2026-11-20 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	11	vendedor.demo@crm-educativo.local
12	WhatsApp	Se envió el PDF del programa por WhatsApp.	Pidió detalles de horarios	2026-11-21 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	12	vendedor2@crm-educativo.local
\.


--
-- Data for Name: intereses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.intereses (nro_tarjeta, fecha, created_at, updated_at, modulo_codigo, programa_nombre, modulo_nombre, precio, anuncio_codigo, modulo_descripcion, estado, fecha_asignacion, ultima_actividad_en, proximo_contacto, observacion, vendedor_correo, documento, motivo_perdida) FROM stdin;
1	2026-11-07 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	ciberseguridad-m1	Ciberseguridad	Fundamentos de Ciberseguridad	500.00	anuncio-ciberseguridad-m1	Identifica amenazas, controles y principios de seguridad.	Nuevo	2026-11-12 12:15:05	2026-11-17 12:15:05	\N	\N	vendedor.demo@crm-educativo.local	6100000	\N
2	2026-11-08 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	ciberseguridad-m4	Ciberseguridad	Análisis de Vulnerabilidades	1320.00	anuncio-ciberseguridad-m4	Detecta, prioriza y documenta riesgos técnicos.	Nuevo	2026-11-13 12:15:05	2026-11-18 12:15:05	\N	\N	vendedor2@crm-educativo.local	6107919	\N
3	2026-11-09 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	datos-bi-m2	Análisis de Datos y Business Intelligence	SQL para Análisis de Datos	700.00	anuncio-datos-bi-m2	Consulta, transforma y resume información con SQL.	En Contacto	2026-11-14 12:15:05	2026-11-19 12:15:05	\N	\N	vendedor.demo@crm-educativo.local	6115838	\N
4	2026-11-10 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	datos-bi-m5	Análisis de Datos y Business Intelligence	Diseño de Dashboards	880.00	anuncio-datos-bi-m5	Crea tableros claros, útiles y orientados a decisiones.	En Contacto	2026-11-15 12:15:05	2026-11-20 12:15:05	\N	\N	vendedor2@crm-educativo.local	6123757	\N
5	2026-11-11 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	desarrollo-web-m3	Desarrollo de Aplicaciones Web	Desarrollo Backend	960.00	anuncio-desarrollo-web-m3	Implementa APIs, servicios y lógica de negocio para aplicaciones web.	Seguimiento	2026-11-16 12:15:05	2026-11-21 12:15:05	\N	\N	vendedor.demo@crm-educativo.local	6131676	\N
6	2026-11-12 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	ia-aplicada-m1	Inteligencia Artificial Aplicada	Fundamentos de Inteligencia Artificial	600.00	anuncio-ia-aplicada-m1	Comprende conceptos, casos de uso y limites de la IA.	Seguimiento	2026-11-17 12:15:05	2026-11-22 12:15:05	\N	\N	vendedor2@crm-educativo.local	6139595	\N
7	2026-11-13 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	ia-aplicada-m4	Inteligencia Artificial Aplicada	Redes Neuronales	1460.00	anuncio-ia-aplicada-m4	Explora arquitecturas neuronales para reconocimiento y predicción.	Promesa de Pago	2026-11-18 12:15:05	2026-11-23 12:15:05	\N	\N	vendedor.demo@crm-educativo.local	6147514	\N
8	2026-11-14 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	redes-servidores-m2	Redes y Administración de Servidores	Configuración de Redes	740.00	anuncio-redes-servidores-m2	Configura equipos, segmentos, rutas y servicios de conectividad.	Promesa de Pago	2026-11-19 12:15:05	2026-11-24 12:15:05	\N	\N	vendedor2@crm-educativo.local	6155433	\N
9	2026-11-15 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	redes-servidores-m5	Redes y Administración de Servidores	Virtualización y Contenedores	1180.00	anuncio-redes-servidores-m5	Implementa entornos virtualizados y contenedores para despliegue.	Convertido	2026-11-20 12:15:05	2026-11-27 12:15:05	\N	\N	vendedor.demo@crm-educativo.local	6163352	\N
10	2026-11-16 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	ciberseguridad-m3	Ciberseguridad	Seguridad de Sistemas Operativos	900.00	anuncio-ciberseguridad-m3	Endurece sistemas Linux y Windows para entornos productivos.	Convertido	2026-11-21 12:15:05	2026-11-27 12:15:05	\N	\N	vendedor2@crm-educativo.local	6171271	\N
11	2026-11-17 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	datos-bi-m1	Análisis de Datos y Business Intelligence	Fundamentos de Bases de Datos	520.00	anuncio-datos-bi-m1	Aprende conceptos de datos relacionales para análisis.	Perdido	2026-11-12 12:15:05	2026-11-18 12:15:05	\N	\N	vendedor.demo@crm-educativo.local	6179190	Precio fuera de su presupuesto
12	2026-11-18 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	datos-bi-m4	Análisis de Datos y Business Intelligence	Business Intelligence con Power BI	1220.00	anuncio-datos-bi-m4	Construye modelos, reportes y visualizaciones ejecutivas.	Perdido	2026-11-13 12:15:05	2026-11-19 12:15:05	\N	\N	vendedor2@crm-educativo.local	6187109	Horario incompatible con su trabajo
13	2026-11-19 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	desarrollo-web-m2	Desarrollo de Aplicaciones Web	Desarrollo Frontend	780.00	anuncio-desarrollo-web-m2	Construye interfaces modernas, responsivas y orientadas a componentes.	Nuevo	2026-11-14 12:15:05	2026-11-20 12:15:05	\N	\N	vendedor.demo@crm-educativo.local	6195028	\N
14	2026-11-20 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	desarrollo-web-m5	Desarrollo de Aplicaciones Web	Despliegue de Aplicaciones	540.00	anuncio-desarrollo-web-m5	Publica aplicaciones con buenas prácticas de configuración y monitoreo.	Nuevo	\N	2026-11-21 12:15:05	\N	\N	\N	6202947	\N
15	2026-11-21 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	ia-aplicada-m3	Inteligencia Artificial Aplicada	Machine Learning	1280.00	anuncio-ia-aplicada-m3	Entrena modelos predictivos y evalua su rendimiento.	Nuevo	\N	2026-11-22 12:15:05	\N	\N	\N	6210866	\N
16	2026-11-22 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	redes-servidores-m1	Redes y Administración de Servidores	Fundamentos de Redes	460.00	anuncio-redes-servidores-m1	Comprende modelos de red, direccionamiento y servicios esenciales.	Nuevo	\N	2026-11-23 12:15:05	\N	\N	\N	6218785	\N
\.


--
-- Data for Name: log_comandos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.log_comandos (nro_registro, remitente, asunto, resultado, detalle, fecha, rol_registrado, usuario_correo) FROM stdin;
\.


--
-- Data for Name: metodos_pago; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.metodos_pago (nro_metodo, documento, tipo, titular, marca, ultimos_digitos, vencimiento, estado, created_at, updated_at, proveedor, stripe_cliente, stripe_metodo, registrado_por) FROM stdin;
\.


--
-- Data for Name: motivos_perdida; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.motivos_perdida (nombre, categoria) FROM stdin;
Precio fuera de su presupuesto	Económico
Sin financiamiento o plan de pagos	Económico
Horario incompatible con su trabajo	Horario
Fecha de inicio no le conviene	Horario
No cumple los requisitos de admisión	Incompatibilidad
Eligió otra institución	Incompatibilidad
No responde llamadas ni mensajes	Contacto
Datos de contacto erróneos	Contacto
Otro motivo	Otro
Sin clasificar (web)	Otro
\.


--
-- Data for Name: movimientos_interes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.movimientos_interes (nro_movimiento, nro_tarjeta, estado_anterior, estado_nuevo, detalle, fecha, usuario_correo) FROM stdin;
1	1	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:05	\N
2	2	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor2@crm-educativo.local	2026-11-27 12:15:05	\N
3	3	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
4	3	Nuevo	En Contacto	Cambio desde web. Vendedor: vendedor.demo@crm-educativo.local -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
5	4	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor2@crm-educativo.local	2026-11-27 12:15:06	\N
6	4	Nuevo	En Contacto	Cambio desde web. Vendedor: vendedor2@crm-educativo.local -> vendedor2@crm-educativo.local	2026-11-27 12:15:06	\N
7	5	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
8	5	Nuevo	Seguimiento	Cambio desde web. Vendedor: vendedor.demo@crm-educativo.local -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
9	6	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor2@crm-educativo.local	2026-11-27 12:15:06	\N
10	6	Nuevo	Seguimiento	Cambio desde web. Vendedor: vendedor2@crm-educativo.local -> vendedor2@crm-educativo.local	2026-11-27 12:15:06	\N
11	7	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
12	7	Nuevo	Promesa de Pago	Cambio desde web. Vendedor: vendedor.demo@crm-educativo.local -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
13	8	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor2@crm-educativo.local	2026-11-27 12:15:06	\N
14	8	Nuevo	Promesa de Pago	Cambio desde web. Vendedor: vendedor2@crm-educativo.local -> vendedor2@crm-educativo.local	2026-11-27 12:15:06	\N
15	9	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
16	9	Nuevo	Promesa de Pago	Cambio desde web. Vendedor: vendedor.demo@crm-educativo.local -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
17	9	Promesa de Pago	Convertido	Cambio desde web. Vendedor: vendedor.demo@crm-educativo.local -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
18	10	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor2@crm-educativo.local	2026-11-27 12:15:06	\N
19	10	Nuevo	Promesa de Pago	Cambio desde web. Vendedor: vendedor2@crm-educativo.local -> vendedor2@crm-educativo.local	2026-11-27 12:15:06	\N
20	10	Promesa de Pago	Convertido	Cambio desde web. Vendedor: vendedor2@crm-educativo.local -> vendedor2@crm-educativo.local	2026-11-27 12:15:06	\N
21	11	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
22	11	Nuevo	Perdido	Cambio desde web. Vendedor: vendedor.demo@crm-educativo.local -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
23	12	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor2@crm-educativo.local	2026-11-27 12:15:06	\N
24	12	Nuevo	Perdido	Cambio desde web. Vendedor: vendedor2@crm-educativo.local -> vendedor2@crm-educativo.local	2026-11-27 12:15:06	\N
25	13	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> vendedor.demo@crm-educativo.local	2026-11-27 12:15:06	\N
26	14	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> sin asignar	2026-11-27 12:15:06	\N
27	15	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> sin asignar	2026-11-27 12:15:06	\N
28	16	\N	Nuevo	Cambio desde web. Vendedor: sin asignar -> sin asignar	2026-11-27 12:15:06	\N
\.


--
-- Data for Name: notificaciones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notificaciones (nro_notificacion, destinatario, tipo, mensaje, estado, fecha_envio, created_at, updated_at, usuario_correo) FROM stdin;
\.


--
-- Data for Name: orden_pago_descuentos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orden_pago_descuentos (nro_orden, porcentaje, monto, created_at, updated_at, descuento_codigo) FROM stdin;
\.


--
-- Data for Name: ordenes_pago; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ordenes_pago (nro_orden, nro_tarjeta, subtotal, descuento_total, total, fecha_generacion, created_at, updated_at, vendedor_correo, estado, motivo_anulacion, fecha_anulacion, anulada_por) FROM stdin;
1	7	1460.00	0.00	1460.00	2026-11-22 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	vendedor.demo@crm-educativo.local	Activa	\N	\N	\N
2	8	740.00	0.00	740.00	2026-11-22 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	vendedor2@crm-educativo.local	Activa	\N	\N	\N
3	9	1180.00	0.00	1180.00	2026-11-22 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	vendedor.demo@crm-educativo.local	Activa	\N	\N	\N
4	10	900.00	0.00	900.00	2026-11-22 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	vendedor2@crm-educativo.local	Activa	\N	\N	\N
\.


--
-- Data for Name: pagos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pagos (codigo_qr, estado, fecha_validacion, observacion_validacion, created_at, updated_at, nro_orden) FROM stdin;
CRM-QR-ORD-1-DEMO	Pendiente de pago	\N	\N	2026-11-27 12:15:05	2026-11-27 12:15:05	1
CRM-QR-ORD-2-DEMO	Pendiente de pago	\N	\N	2026-11-27 12:15:05	2026-11-27 12:15:05	2
CRM-QR-ORD-3-DEMO	Pago aprobado	2026-11-25 12:15:05	\N	2026-11-27 12:15:05	2026-11-27 12:15:05	3
CRM-QR-ORD-4-DEMO	Pago aprobado	2026-11-25 12:15:05	\N	2026-11-27 12:15:05	2026-11-27 12:15:05	4
\.


--
-- Data for Name: permisos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.permisos (rol, recurso_codigo, acceso, created_at, updated_at) FROM stdin;
coordinador	dashboard	lectura	2026-11-21 02:12:28	2026-11-21 02:12:28
coordinador	embudo	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
coordinador	prospectos	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
coordinador	interesados	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
coordinador	agenda	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
coordinador	motivos	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
coordinador	validacion-pagos	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
coordinador	alumnos	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
coordinador	gestion-anuncios	lectura	2026-11-21 02:12:28	2026-11-21 02:12:28
coordinador	seguimiento	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
coordinador	reportes	lectura	2026-11-21 02:12:28	2026-11-21 02:12:28
coordinador	notificaciones	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
vendedor	inicio-vendedor	lectura	2026-11-21 02:12:28	2026-11-21 02:12:28
vendedor	embudo	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
vendedor	prospectos	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
vendedor	agenda	modificacion	2026-11-21 02:12:28	2026-11-21 02:12:28
vendedor	seguimiento	lectura	2026-11-21 02:12:28	2026-11-21 02:12:28
vendedor	reportes	lectura	2026-11-21 02:12:28	2026-11-21 02:12:28
vendedor	notificaciones	lectura	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	dashboard	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	embudo	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	prospectos	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	interesados	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	agenda	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	motivos	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	validacion-pagos	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	alumnos	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	gestion-anuncios	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	seguimiento	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	reportes	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	notificaciones	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	usuarios	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	matriz	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
administrador	bitacora	eliminacion	2026-11-21 02:12:28	2026-11-21 02:12:28
\.


--
-- Data for Name: programas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.programas (codigo, nombre) FROM stdin;
desarrollo-web	Desarrollo de Aplicaciones Web
ia-aplicada	Inteligencia Artificial Aplicada
ciberseguridad	Ciberseguridad
redes-servidores	Redes y Administración de Servidores
datos-bi	Análisis de Datos y Business Intelligence
\.


--
-- Data for Name: programas_responsables; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.programas_responsables (programa_codigo, created_at, updated_at, coordinador_correo) FROM stdin;
desarrollo-web	2026-11-27 12:15:05	2026-11-27 12:15:05	coord@test.local
ia-aplicada	2026-11-27 12:15:05	2026-11-27 12:15:05	coord@test.local
datos-bi	2026-11-27 12:15:05	2026-11-27 12:15:05	coord@test.local
\.


--
-- Data for Name: prospectos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.prospectos (nombre, apellido, documento, correo, telefono, estado, fecha_registro, created_at, updated_at, profesion, ubicacion, origen, stripe_cliente) FROM stdin;
Camila	Vargas Méndez	6100000	camila.vargas@correo-demo.bo	71000000	Nuevo	2026-11-07 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Ingeniera comercial	Santa Cruz de la Sierra	Facebook	\N
Jorge	Quiroga Arce	6107919	jorge.quiroga@correo-demo.bo	71037171	Nuevo	2026-11-08 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Contador	Santa Cruz de la Sierra	Instagram	\N
Valeria	Gutiérrez Ribera	6115838	valeria.gutierrez@correo-demo.bo	71074342	Nuevo	2026-11-09 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Diseñadora	Santa Cruz de la Sierra	WhatsApp	\N
Mateo	Céspedes Rocha	6123757	mateo.cespedes@correo-demo.bo	71111513	Nuevo	2026-11-10 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Estudiante	Santa Cruz de la Sierra	Web	\N
Sofía	Moreno Aguilera	6131676	sofia.moreno@correo-demo.bo	71148684	Nuevo	2026-11-11 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Abogada	Santa Cruz de la Sierra	Referido	\N
Rodrigo	Paz Terceros	6139595	rodrigo.paz@correo-demo.bo	71185855	Nuevo	2026-11-12 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Técnico en redes	Santa Cruz de la Sierra	TikTok	\N
Daniela	Chávez Landívar	6147514	daniela.chavez@correo-demo.bo	71223026	Nuevo	2026-11-13 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Administradora	Santa Cruz de la Sierra	Feria	\N
Gabriel	Mercado Soliz	6155433	gabriel.mercado@correo-demo.bo	71260197	Nuevo	2026-11-14 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Ingeniero civil	Santa Cruz de la Sierra	Facebook	\N
Fernanda	Ortiz Callaú	6163352	fernanda.ortiz@correo-demo.bo	71297368	Convertido	2026-11-15 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Analista de datos	Santa Cruz de la Sierra	Web	\N
Andrés	Montaño Ibáñez	6171271	andres.montano@correo-demo.bo	71334539	Convertido	2026-11-16 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Docente	Santa Cruz de la Sierra	Correo	\N
Paola	Saucedo Durán	6179190	paola.saucedo@correo-demo.bo	71371710	Nuevo	2026-11-17 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Economista	Santa Cruz de la Sierra	Instagram	\N
Luis	Fernández Melgar	6187109	luis.fernandez@correo-demo.bo	71408881	Nuevo	2026-11-18 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Programador	Santa Cruz de la Sierra	WhatsApp	\N
Natalia	Rivero Antezana	6195028	natalia.rivero@correo-demo.bo	71446052	Nuevo	2026-11-19 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Psicóloga	Santa Cruz de la Sierra	Referido	\N
Sebastián	Añez Coimbra	6202947	sebastian.anez@correo-demo.bo	71483223	Nuevo	2026-11-20 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Estudiante	Santa Cruz de la Sierra	Web	\N
Mariana	Lijerón Parada	6210866	mariana.lijeron@correo-demo.bo	71520394	Nuevo	2026-11-21 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Auditora	Santa Cruz de la Sierra	Facebook	\N
Ricardo	Hurtado Velasco	6218785	ricardo.hurtado@correo-demo.bo	71557565	Nuevo	2026-11-22 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	Bioquímico	Santa Cruz de la Sierra	Otro	\N
\.


--
-- Data for Name: recordatorios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.recordatorios (nro_recordatorio, fecha_programada, descripcion, estado, created_at, updated_at, nro_tarjeta, fecha_realizada, notificado, usuario_correo) FROM stdin;
1	2026-11-29 12:00:00	Llamar para confirmar interés	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	3	\N	f	vendedor.demo@crm-educativo.local
2	2026-11-30 13:00:00	Llamar para confirmar interés	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	4	\N	f	vendedor2@crm-educativo.local
3	2026-11-27 14:00:00	Llamar para confirmar interés	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	5	\N	f	vendedor.demo@crm-educativo.local
4	2026-11-28 15:00:00	Llamar para confirmar interés	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	6	\N	f	vendedor2@crm-educativo.local
5	2026-11-29 10:00:00	Llamar para confirmar interés	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	7	\N	f	vendedor.demo@crm-educativo.local
6	2026-11-30 11:00:00	Llamar para confirmar interés	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	8	\N	f	vendedor2@crm-educativo.local
7	2026-11-27 12:00:00	Llamar para confirmar interés	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	9	\N	f	vendedor.demo@crm-educativo.local
8	2026-11-28 13:00:00	Llamar para confirmar interés	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	10	\N	f	vendedor2@crm-educativo.local
9	2026-11-29 14:00:00	Llamar para confirmar interés	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	11	\N	f	vendedor.demo@crm-educativo.local
10	2026-11-30 15:00:00	Llamar para confirmar interés	Pendiente	2026-11-27 12:15:05	2026-11-27 12:15:05	12	\N	f	vendedor2@crm-educativo.local
\.


--
-- Data for Name: recursos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.recursos (codigo, nombre, ruta, icono, orden, caso_uso, publico, visitas) FROM stdin;
inicio-vendedor	Mi día	/inicio-vendedor	CalendarDays	11	CU7	f	0
prospectos	Prospectos	/prospectos	UserRound	21	CU3	f	0
interesados	Asignación de prospectos	/interesados	Shuffle	22	CU3	f	0
motivos	Motivos de pérdida	/motivos-perdida	CircleSlash	24	CU5	f	0
validacion-pagos	Validación de pagos	/validacion-pagos	CreditCard	30	CU6	f	0
alumnos	Matrículas y SIS	/alumnos	School	31	CU6	f	0
gestion-anuncios	Oferta académica	/gestion-anuncios	Megaphone	32	CU2	f	0
seguimiento	Ventas y comisiones	/seguimiento	BadgeDollarSign	40	CU8	f	0
notificaciones	Notificaciones	/notificaciones	Mail	42	CU7	f	0
usuarios	Usuarios	/usuarios	Users	50	CU1	f	0
matriz	Matriz de acceso	/matriz-acceso	ShieldCheck	51	CU1	f	0
bitacora	Bitácora de accesos	/bitacora	ScrollText	52	CU1	f	0
login	Iniciar sesión	/login	LogIn	2	CU1	t	18
agenda	Seguimiento y agenda	/agenda	NotebookTabs	23	CU7	f	22
dashboard	Dashboard	/dashboard	LayoutDashboard	10	CU8	f	25
reportes	Reportes y estadísticas	/reportes	BarChart3	41	CU8	f	9
catalogo	Catálogo de programas	/anuncios	GraduationCap	1	CU2	t	42
embudo	Embudo de ventas	/embudo	KanbanSquare	20	CU4	f	31
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.roles (nombre, descripcion, created_at, updated_at) FROM stdin;
administrador	Gestiona usuarios y toda la operacion comercial	2026-11-17 05:18:56	2026-11-17 05:18:56
coordinador	Asigna interesados, valida pagos y supervisa vendedores	2026-11-17 05:18:56	2026-11-17 05:18:56
vendedor	Da seguimiento a los interesados asignados	2026-11-17 05:18:56	2026-11-17 05:18:56
\.


--
-- Data for Name: solicitudes_compra; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solicitudes_compra (nro_solicitud, precio_acordado, fecha, created_at, updated_at, anuncio_codigo, modulo_codigo, programa_nombre, modulo_nombre, modulo_descripcion, anuncio_titulo, nro_orden) FROM stdin;
1	1460.00	2026-11-22 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	anuncio-ia-aplicada-m4	ia-aplicada-m4	Inteligencia Artificial Aplicada	Redes Neuronales	Explora arquitecturas neuronales para reconocimiento y predicción.	\N	1
2	740.00	2026-11-22 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	anuncio-redes-servidores-m2	redes-servidores-m2	Redes y Administración de Servidores	Configuración de Redes	Configura equipos, segmentos, rutas y servicios de conectividad.	\N	2
3	1180.00	2026-11-22 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	anuncio-redes-servidores-m5	redes-servidores-m5	Redes y Administración de Servidores	Virtualización y Contenedores	Implementa entornos virtualizados y contenedores para despliegue.	\N	3
4	900.00	2026-11-22 12:15:05	2026-11-27 12:15:05	2026-11-27 12:15:05	anuncio-ciberseguridad-m3	ciberseguridad-m3	Ciberseguridad	Seguridad de Sistemas Operativos	Endurece sistemas Linux y Windows para entornos productivos.	\N	4
\.


--
-- Data for Name: transacciones_stripe; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.transacciones_stripe (nro_transaccion, tipo, nro_orden, nro_cuota, documento, usuario_correo, stripe_sesion, stripe_pago_intent, stripe_setup_intent, stripe_cliente, stripe_metodo, moneda, monto_esperado, monto_centavos, monto_confirmado, estado_sesion, estado_pago, estado_interno, livemode, marca_tarjeta, ultimos_digitos, receipt_url, url_checkout, clave_idempotencia, detalle_error, confirmado_en, created_at, updated_at, token_publico, expira_en) FROM stdin;
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios (nombre, apellido, correo, telefono, password, rol, estado, created_at, updated_at, fecha_inicio, fecha_fin, foto) FROM stdin;
Andrea	Rojas Salvatierra	admin@crm-educativo.local	73283496	$2y$12$WdJVC/0BTRt0BOmc2o3tEeEd73tuHrhLEGa7nGqqRUNE6GrZZ2da6	administrador	activo	2026-11-27 12:15:04	2026-11-27 12:15:04	2026-08-27	2027-11-27	\N
Marcelo	Antelo Vaca	coord@test.local	74881563	$2y$12$wXxclFQetDcZ8lM/g1oVt.43IMNelKv//9s8V66uoFEOBGSBEoClC	coordinador	activo	2026-11-27 12:15:04	2026-11-27 12:15:04	2026-08-27	2027-11-27	\N
Lucía	Suárez Peña	vendedor.demo@crm-educativo.local	78793058	$2y$12$Mk7nFy3CptPSDUnahpt3x.CflRSiUvMQZWwEjjUaFfYbmc338CIni	vendedor	activo	2026-11-27 12:15:04	2026-11-27 12:15:04	2026-08-27	2027-11-27	\N
Diego	Justiniano Roca	vendedor2@crm-educativo.local	79118405	$2y$12$BN.gCj88kviN9qQl9pW1vOda/4uZ1hfw.Q5Pe.2QbDdpU/gekfdSC	vendedor	activo	2026-11-27 12:15:05	2026-11-27 12:15:05	2026-08-27	2027-11-27	\N
\.


--
-- Data for Name: webhook_eventos_stripe; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.webhook_eventos_stripe (stripe_evento, tipo, nro_transaccion, stripe_sesion, stripe_pago_intent, livemode, estado, resumen, procesado_en, created_at, updated_at) FROM stdin;
\.


--
-- Name: bitacora_nro_registro_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bitacora_nro_registro_seq', 166, true);


--
-- Name: comprobantes_pago_nro_comprobante_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.comprobantes_pago_nro_comprobante_seq', 1, false);


--
-- Name: exportaciones_nro_exportacion_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.exportaciones_nro_exportacion_seq', 1, false);


--
-- Name: interacciones_nro_interaccion_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.interacciones_nro_interaccion_seq', 12, true);


--
-- Name: intereses_nro_tarjeta_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.intereses_nro_tarjeta_seq', 16, true);


--
-- Name: log_comandos_nro_registro_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.log_comandos_nro_registro_seq', 1, false);


--
-- Name: metodos_pago_nro_metodo_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.metodos_pago_nro_metodo_seq', 1, false);


--
-- Name: movimientos_interes_nro_movimiento_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.movimientos_interes_nro_movimiento_seq', 28, true);


--
-- Name: notificaciones_nro_notificacion_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notificaciones_nro_notificacion_seq', 1, false);


--
-- Name: ordenes_pago_nro_orden_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ordenes_pago_nro_orden_seq', 4, true);


--
-- Name: recordatorios_nro_recordatorio_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.recordatorios_nro_recordatorio_seq', 10, true);


--
-- Name: solicitudes_compra_nro_solicitud_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solicitudes_compra_nro_solicitud_seq', 4, true);


--
-- Name: transacciones_stripe_nro_transaccion_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.transacciones_stripe_nro_transaccion_seq', 1, false);


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
-- Name: cuotas cuotas_token_pago_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cuotas
    ADD CONSTRAINT cuotas_token_pago_unique UNIQUE (token_pago);


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
-- Name: transacciones_stripe transacciones_stripe_token_publico_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transacciones_stripe
    ADD CONSTRAINT transacciones_stripe_token_publico_unique UNIQUE (token_publico);


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

