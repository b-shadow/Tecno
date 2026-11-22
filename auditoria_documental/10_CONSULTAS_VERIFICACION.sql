-- UNEXO: consultas de metadatos. No extrae prospectos, tarjetas ni pagos.
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL statement_timeout = '20s';

-- contexto: comparar nombres y definiciones con evidencias/pg_contexto.json.
SELECT current_database() AS base, current_schema() AS esquema, version(), current_setting('TimeZone') AS zona_horaria, inet_server_addr()::text AS servidor, inet_server_port() AS puerto, current_setting('transaction_read_only') AS solo_lectura;

-- tipos_exactos: comparar nombres y definiciones con evidencias/pg_tipos_exactos.json.
SELECT n.nspname AS esquema,c.relname AS tabla,a.attname AS columna,format_type(a.atttypid,a.atttypmod) AS tipo FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('public','laravel') AND c.relkind='r' AND a.attnum>0 AND NOT a.attisdropped ORDER BY 1,2,a.attnum;

-- tablas: comparar nombres y definiciones con evidencias/pg_tablas.json.
SELECT table_schema,table_name,table_type FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY 1,2;

-- columnas: comparar nombres y definiciones con evidencias/pg_columnas.json.
SELECT table_schema,table_name,column_name,ordinal_position,data_type,udt_name,character_maximum_length,numeric_precision,numeric_scale,is_nullable,column_default,is_identity,identity_generation,is_generated,generation_expression FROM information_schema.columns WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY 1,2,4;

-- restricciones: comparar nombres y definiciones con evidencias/pg_restricciones.json.
SELECT ns.nspname AS esquema,cl.relname AS tabla,c.conname AS nombre,c.contype AS tipo,pg_get_constraintdef(c.oid,true) AS definicion, c.convalidated AS validada, c.condeferrable AS diferible FROM pg_constraint c JOIN pg_class cl ON cl.oid=c.conrelid JOIN pg_namespace ns ON ns.oid=cl.relnamespace WHERE ns.nspname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2,3;

-- fk_columnas: comparar nombres y definiciones con evidencias/pg_fk_columnas.json.
SELECT n.nspname AS esquema,t.relname AS tabla,c.conname AS nombre, array_agg(a.attname ORDER BY s.i) AS columnas, nt.nspname AS esquema_destino,tt.relname AS destino,array_agg(at.attname ORDER BY s.i) AS columnas_destino,c.confdeltype AS on_delete,c.confupdtype AS on_update FROM pg_constraint c JOIN pg_class t ON t.oid=c.conrelid JOIN pg_namespace n ON n.oid=t.relnamespace JOIN pg_class tt ON tt.oid=c.confrelid JOIN pg_namespace nt ON nt.oid=tt.relnamespace CROSS JOIN LATERAL generate_subscripts(c.conkey,1) s(i) JOIN pg_attribute a ON a.attrelid=t.oid AND a.attnum=c.conkey[s.i] JOIN pg_attribute at ON at.attrelid=tt.oid AND at.attnum=c.confkey[s.i] WHERE c.contype='f' AND n.nspname NOT IN ('pg_catalog','information_schema') GROUP BY n.nspname,t.relname,c.conname,nt.nspname,tt.relname,c.confdeltype,c.confupdtype ORDER BY 1,2,3;

-- indices: comparar nombres y definiciones con evidencias/pg_indices.json.
SELECT schemaname,tablename,indexname,indexdef FROM pg_indexes WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2,3;

-- triggers: comparar nombres y definiciones con evidencias/pg_triggers.json.
SELECT n.nspname AS esquema,c.relname AS tabla,t.tgname AS nombre,pg_get_triggerdef(t.oid,true) AS definicion,p.proname AS funcion,t.tgenabled AS habilitado FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_proc p ON p.oid=t.tgfoid WHERE NOT t.tgisinternal AND n.nspname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2,3;

-- funciones: comparar nombres y definiciones con evidencias/pg_funciones.json.
SELECT n.nspname AS esquema,p.proname AS nombre,pg_get_function_identity_arguments(p.oid) AS argumentos, pg_get_functiondef(p.oid) AS definicion FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND p.prokind IN ('f','p') ORDER BY 1,2;

-- secuencias: comparar nombres y definiciones con evidencias/pg_secuencias.json.
SELECT * FROM pg_sequences WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2;

-- vistas: comparar nombres y definiciones con evidencias/pg_vistas.json.
SELECT schemaname,viewname,definition FROM pg_views WHERE schemaname NOT IN ('pg_catalog','information_schema');

-- materializadas: comparar nombres y definiciones con evidencias/pg_materializadas.json.
SELECT schemaname,matviewname,definition FROM pg_matviews WHERE schemaname NOT IN ('pg_catalog','information_schema');

-- tipos: comparar nombres y definiciones con evidencias/pg_tipos.json.
SELECT n.nspname AS esquema,t.typname AS nombre,t.typtype AS tipo FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND t.typtype IN ('e','d');

-- migraciones: comparar nombres y definiciones con evidencias/pg_migraciones.json.
SELECT migration,batch FROM laravel.migrations ORDER BY migration;

-- roles_aplicacion: comparar nombres y definiciones con evidencias/pg_roles_aplicacion.json.
SELECT * FROM public.roles;

-- permisos_aplicacion: comparar nombres y definiciones con evidencias/pg_permisos_aplicacion.json.
SELECT * FROM public.permisos;

-- cardinalidades_garantizadas: hijo->padre según NULL; padre->hijos según UNIQUE/PK.
-- 0..* no significa que haya hijos: la FK nunca exige una fila hija al padre.
SELECT n.nspname AS esquema,t.relname AS hija,c.conname AS fk,
       pt.relname AS padre, pg_get_constraintdef(c.oid,true) AS definicion,
       CASE WHEN EXISTS (SELECT 1 FROM unnest(c.conkey) k(attnum)
                         JOIN pg_attribute a ON a.attrelid=t.oid AND a.attnum=k.attnum
                         WHERE NOT a.attnotnull) THEN '0..1' ELSE '1' END AS padres_por_hijo,
       CASE WHEN EXISTS (SELECT 1 FROM pg_constraint u WHERE u.conrelid=t.oid
                          AND u.contype IN ('p','u') AND u.conkey <@ c.conkey)
            THEN '0..1' ELSE '0..*' END AS hijos_por_padre
FROM pg_constraint c JOIN pg_class t ON t.oid=c.conrelid
JOIN pg_namespace n ON n.oid=t.relnamespace JOIN pg_class pt ON pt.oid=c.confrelid
WHERE c.contype='f' AND n.nspname='public' ORDER BY hija,fk;

ROLLBACK;
