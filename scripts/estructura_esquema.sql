-- Huella de la estructura de public (columnas, claves, FK, CHECK, indices, triggers). Comparar dos bases:
-- psql -AtF"|" -d BASE_A -f estructura_esquema.sql > a.txt; idem BASE_B > b.txt; diff a.txt b.txt
select 'COL', table_name, column_name, data_type, coalesce(character_maximum_length::text,''), coalesce(numeric_precision::text||','||numeric_scale::text,''), is_nullable, coalesce(regexp_replace(column_default,'::[a-z ]+','','g'),'') from information_schema.columns where table_schema='public'
union all
select 'CON', tc.table_name, tc.constraint_name, tc.constraint_type, '', '', '', '' from information_schema.table_constraints tc where tc.table_schema='public' and tc.constraint_type<>'CHECK'
union all
select 'CHK', conrelid::regclass::text, conname, regexp_replace(pg_get_constraintdef(oid),'::[a-z ]+','','g'), '', '', '', '' from pg_constraint where contype='c' and connamespace='public'::regnamespace
union all
select 'FK', conrelid::regclass::text, conname, pg_get_constraintdef(oid), '', '', '', '' from pg_constraint where contype='f' and connamespace='public'::regnamespace
union all
select 'IDX', tablename, indexname, regexp_replace(indexdef,'::[a-z ]+','','g'), '', '', '', '' from pg_indexes where schemaname='public'
union all
select 'TRG', event_object_table, trigger_name, action_timing||' '||event_manipulation, '', '', '', '' from information_schema.triggers where trigger_schema='public'
order by 1,2,3,4;
