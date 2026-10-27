-- Solo lectura. Ejecutar con psql -v ON_ERROR_STOP=1 -f verificar_integridad.sql.
-- migrations es infraestructura de Laravel, no una entidad del negocio.
BEGIN READ ONLY;
DO $$
DECLARE faltantes text;
BEGIN
    SELECT string_agg(t.relname, ', ') INTO faltantes
    FROM pg_class t JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE n.nspname = 'public' AND t.relkind = 'r'
      AND NOT EXISTS (SELECT 1 FROM pg_constraint c WHERE c.conrelid = t.oid AND c.contype = 'p');
    IF faltantes IS NOT NULL THEN RAISE EXCEPTION 'Tablas sin PK: %', faltantes; END IF;

    WITH RECURSIVE aristas(a,b) AS (
        SELECT conrelid, confrelid FROM pg_constraint WHERE contype = 'f'
        UNION SELECT confrelid, conrelid FROM pg_constraint WHERE contype = 'f'
    ), conectadas(id) AS (
        SELECT 'public.usuarios'::regclass::oid
        UNION SELECT a.b FROM aristas a JOIN conectadas c ON a.a = c.id
    )
    SELECT string_agg(t.relname, ', ') INTO faltantes
    FROM pg_class t JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE n.nspname = 'public' AND t.relkind = 'r' AND t.relname <> 'migrations'
      AND t.oid NOT IN (SELECT id FROM conectadas);
    IF faltantes IS NOT NULL THEN RAISE EXCEPTION 'Tablas desconectadas: %', faltantes; END IF;

    SELECT string_agg(t.relname || '.' || a.attname, ', ') INTO faltantes
    FROM pg_attribute a JOIN pg_class t ON t.oid = a.attrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE n.nspname = 'public' AND t.relkind = 'r' AND NOT a.attisdropped
      AND a.attname LIKE '%\_id' ESCAPE '\' AND a.attname NOT LIKE 'external\_%' ESCAPE '\'
      AND NOT EXISTS (SELECT 1 FROM pg_constraint c
          WHERE c.conrelid = t.oid AND c.contype = 'f' AND a.attnum = ANY(c.conkey));
    IF faltantes IS NOT NULL THEN RAISE EXCEPTION 'Referencias locales sin FK: %', faltantes; END IF;

    -- Clase 46: la clave es la del diseño, sin columna id extra.
    SELECT string_agg(t.relname, ', ') INTO faltantes
    FROM pg_attribute a JOIN pg_class t ON t.oid = a.attrelid JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE n.nspname = 'public' AND t.relkind = 'r' AND NOT a.attisdropped AND a.attname = 'id';
    IF faltantes IS NOT NULL THEN RAISE EXCEPTION 'Tablas con columna id extra: %', faltantes; END IF;

    IF EXISTS (SELECT 1 FROM pg_constraint WHERE connamespace = 'public'::regnamespace AND NOT convalidated)
    THEN RAISE EXCEPTION 'Hay restricciones sin validar'; END IF;
    IF to_regclass('public.orden_pago_items') IS NOT NULL
       OR to_regclass('public.chat_conversaciones') IS NOT NULL
       OR to_regclass('public.chat_mensajes') IS NOT NULL
    THEN RAISE EXCEPTION 'Persisten tablas retiradas'; END IF;
    IF EXISTS (SELECT 1 FROM pagos WHERE nro_orden IS NULL)
       OR EXISTS (SELECT 1 FROM solicitudes_compra WHERE nro_orden IS NULL)
    THEN RAISE EXCEPTION 'Hay pagos o ventas sin orden'; END IF;
    RAISE NOTICE 'OK: PK, grafo conectado, FK locales, sin id extra, restricciones validadas y ventas unificadas';
END $$;
SELECT contype AS tipo, count(*) AS cantidad FROM pg_constraint
WHERE connamespace = 'public'::regnamespace GROUP BY contype ORDER BY contype;
ROLLBACK;
