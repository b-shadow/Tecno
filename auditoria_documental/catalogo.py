import sys,json,re,os
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent.parent; E=R/'auditoria_documental/evidencias'
sys.path.insert(0,str(R/'generadorDocumento'));import esquema,contenido,codigo
def clean(o):
 if isinstance(o,dict): return {str(k):clean(v) for k,v in o.items()}
 if isinstance(o,(tuple,list,set)): return [clean(v) for v in o]
 return o
def save(n,o): (E/n).write_text(json.dumps(clean(o),ensure_ascii=False,indent=2,default=str),encoding='utf8')
save('esquema_documental.json',{'tablas':esquema.tablas(),'pks':esquema.pks(),'fks':esquema.fks(),'unicas':list(esquema.unicas()),'migraciones':{t:sorted(c) for t,c in esquema.tablas_migraciones().items()}})
for n in ['DETALLE','ALCANCE','ACTORES_CU','PRUEBAS_BLANCA','PRUEBAS_NEGRA','ANEXOS','HERRAMIENTAS','POR_CONFIRMAR']:
 save('contenido_'+n+'.json',getattr(contenido,n))
save('cadenas_cu.json',{cu:codigo.cadena(cu) for cu in contenido.CU})
env={}
for line in (R/'negocio/.env').read_text(encoding='utf-8-sig').splitlines():
 if '=' in line and not line.lstrip().startswith('#'):
  k,v=line.split('=',1);env[k.strip()]=v.strip().strip('\"\'')
queries={
'contexto':"SELECT current_database() AS base, current_schema() AS esquema, version(), current_setting('TimeZone') AS zona_horaria, inet_server_addr()::text AS servidor, inet_server_port() AS puerto, current_setting('transaction_read_only') AS solo_lectura",
'tipos_exactos':"SELECT n.nspname AS esquema,c.relname AS tabla,a.attname AS columna,format_type(a.atttypid,a.atttypmod) AS tipo FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('public','laravel') AND c.relkind='r' AND a.attnum>0 AND NOT a.attisdropped ORDER BY 1,2,a.attnum",
'tablas':"SELECT table_schema,table_name,table_type FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY 1,2",
'columnas':"SELECT table_schema,table_name,column_name,ordinal_position,data_type,udt_name,character_maximum_length,numeric_precision,numeric_scale,is_nullable,column_default,is_identity,identity_generation,is_generated,generation_expression FROM information_schema.columns WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY 1,2,4",
'restricciones':"SELECT ns.nspname AS esquema,cl.relname AS tabla,c.conname AS nombre,c.contype AS tipo,pg_get_constraintdef(c.oid,true) AS definicion, c.convalidated AS validada, c.condeferrable AS diferible FROM pg_constraint c JOIN pg_class cl ON cl.oid=c.conrelid JOIN pg_namespace ns ON ns.oid=cl.relnamespace WHERE ns.nspname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2,3",
'fk_columnas':"SELECT n.nspname AS esquema,t.relname AS tabla,c.conname AS nombre, array_agg(a.attname ORDER BY s.i) AS columnas, nt.nspname AS esquema_destino,tt.relname AS destino,array_agg(at.attname ORDER BY s.i) AS columnas_destino,c.confdeltype AS on_delete,c.confupdtype AS on_update FROM pg_constraint c JOIN pg_class t ON t.oid=c.conrelid JOIN pg_namespace n ON n.oid=t.relnamespace JOIN pg_class tt ON tt.oid=c.confrelid JOIN pg_namespace nt ON nt.oid=tt.relnamespace CROSS JOIN LATERAL generate_subscripts(c.conkey,1) s(i) JOIN pg_attribute a ON a.attrelid=t.oid AND a.attnum=c.conkey[s.i] JOIN pg_attribute at ON at.attrelid=tt.oid AND at.attnum=c.confkey[s.i] WHERE c.contype='f' AND n.nspname NOT IN ('pg_catalog','information_schema') GROUP BY n.nspname,t.relname,c.conname,nt.nspname,tt.relname,c.confdeltype,c.confupdtype ORDER BY 1,2,3",
'indices':"SELECT schemaname,tablename,indexname,indexdef FROM pg_indexes WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2,3",
'triggers':"SELECT n.nspname AS esquema,c.relname AS tabla,t.tgname AS nombre,pg_get_triggerdef(t.oid,true) AS definicion,p.proname AS funcion,t.tgenabled AS habilitado FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_proc p ON p.oid=t.tgfoid WHERE NOT t.tgisinternal AND n.nspname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2,3",
'funciones':"SELECT n.nspname AS esquema,p.proname AS nombre,pg_get_function_identity_arguments(p.oid) AS argumentos, pg_get_functiondef(p.oid) AS definicion FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND p.prokind IN ('f','p') ORDER BY 1,2",
'secuencias':"SELECT * FROM pg_sequences WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2",
'vistas':"SELECT schemaname,viewname,definition FROM pg_views WHERE schemaname NOT IN ('pg_catalog','information_schema')",
'materializadas':"SELECT schemaname,matviewname,definition FROM pg_matviews WHERE schemaname NOT IN ('pg_catalog','information_schema')",
'tipos':"SELECT n.nspname AS esquema,t.typname AS nombre,t.typtype AS tipo FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND t.typtype IN ('e','d')",
'migraciones':"SELECT migration,batch FROM laravel.migrations ORDER BY migration",
'roles_aplicacion':"SELECT * FROM public.roles",
'permisos_aplicacion':"SELECT * FROM public.permisos",
}
sql='-- UNEXO: consultas de metadatos. No extrae prospectos, tarjetas ni pagos.\nBEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;\nSET LOCAL statement_timeout = \'20s\';\n'
for n,q in queries.items(): sql+=f'\n-- {n}: comparar nombres y definiciones con evidencias/pg_{n}.json.\n{q};\n'
sql+='\nROLLBACK;\n'
(R/'auditoria_documental/10_CONSULTAS_VERIFICACION.sql').write_text(sql,encoding='utf8')
import psycopg
from psycopg.rows import dict_row
try:
 conn=psycopg.connect(host=env.get('DB_HOST','127.0.0.1'),port=env.get('DB_PORT','5432'),dbname=env.get('DB_DATABASE'),user=env.get('DB_USERNAME'),password=env.get('DB_PASSWORD'),connect_timeout=6,row_factory=dict_row,options='-c default_transaction_read_only=on -c statement_timeout=20000',autocommit=True)
 conn.execute('BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
 results={}
 for n,q in queries.items():
  conn.execute('SAVEPOINT consulta')
  try:
   rows=conn.execute(q).fetchall(); save('pg_'+n+'.json',rows);results[n]=len(rows)
  except Exception as ex:
   conn.execute('ROLLBACK TO SAVEPOINT consulta');results[n]=type(ex).__name__+': '+str(ex).splitlines()[0]
  conn.execute('RELEASE SAVEPOINT consulta')
 conn.execute('ROLLBACK');conn.close();save('pg_resultados.json',results);print(results)
except Exception as ex: save('pg_error.json',{'tipo':type(ex).__name__,'error':str(ex).splitlines()[0]});print(type(ex).__name__,str(ex).splitlines()[0])
