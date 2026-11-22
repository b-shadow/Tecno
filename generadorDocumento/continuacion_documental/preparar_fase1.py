from pathlib import Path
import json,hashlib,shutil,xml.etree.ElementTree as ET,re,sys
root=Path.cwd(); out=root/'tmp/actualizacion_documental'
baseline=json.loads((out/'archivos_iniciales.json').read_text(encoding='utf-8'))
protected=['generadorDocumento/ea/crm-p2.eapx',*[f'generadorDocumento/documento/P2-INF513-GRUPO05SA.{ext}' for ext in ('docx','doc','pdf')]]
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==baseline[p]['sha256'] for p in protected), 'Cambió un original protegido; revisar antes de continuar'
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
body=ET.fromstring((out/'document-inicial.xml').read_bytes()).find('w:body',ns)
blocks=list(body); text=lambda e:''.join(e.itertext()) if False else ''.join(t.text or '' for t in e.findall('.//w:t',ns))
starts=[i for i,b in enumerate(blocks) if text(b).startswith('Capítulo IV:')]
assert starts, 'No se encontró el capítulo IV'
start=starts[-1]; end=next(i for i in range(start+1,len(blocks)) if text(blocks[i]).startswith('Capítulo V:'))
chapter=b''.join(ET.tostring(b) for b in blocks[start:end]); (out/'capitulo_IV_protegido.xml').write_bytes(chapter)
data=json.loads((out/'postgres_actual.json').read_text(encoding='utf-8'))
types={(x['tabla'],x['columna']):x['tipo'] for x in data['tipos']}
assert types['cuotas','token_pago']=='character varying(80)'
assert types['transacciones_stripe','token_publico']=='character varying(80)'
assert types['transacciones_stripe','expira_en']=='timestamp(0) without time zone'
source=out/'esquema_actual.sql'; sql=source.read_text(encoding='utf-8')
assert not re.search(r'^COPY |^INSERT INTO |sk_(live|test)_[A-Za-z0-9]{16,}|whsec_[A-Za-z0-9]{16,}',sql,re.M)
previous=(root/'backups/documental-20261126/generadorDocumento/fuentes/esquema.sql').read_text(encoding='utf-8-sig')
guard=previous[previous.index('DO $$ BEGIN'):previous.index('\n--\n-- PostgreSQL database dump')]
header='-- UNEXO: esquema documental verificado contra PostgreSQL local 17.4, sin datos ni credenciales.\n-- Conserva la proteccion original para impedir su aplicacion sobre un esquema existente.\n-- No se ejecuto este archivo durante la actualizacion documental.\n'
(root/'generadorDocumento/fuentes/esquema.sql').write_text(header+guard+'\n'+sql,encoding='utf-8',newline='\n')
sys.path.insert(0,str(root/'generadorDocumento')); import esquema
assert len(esquema.tablas())==31 and sum(map(len,esquema.tablas().values()))==287
assert len(esquema.pks())==31 and len(esquema.fks())==46
objects=json.loads((root/'auditoria_documental/evidencias/ea_t_object.json').read_text(encoding='utf-8-sig'))
diagrams=json.loads((root/'auditoria_documental/evidencias/ea_t_diagram.json').read_text(encoding='utf-8-sig'))
packages=json.loads((root/'auditoria_documental/evidencias/ea_t_package.json').read_text(encoding='utf-8-sig'))
actor_diagram=next(x for x in diagrams if x['Name']=='Actores del sistema')
inventory={'fuente':'Inventario histórico reutilizado; EAPX original con hash intacto al inicio y tras la apertura COM incompleta. Pendiente apertura segura mediante EA.', 'packages':packages,'diagrams':diagrams,'actores':[x for x in objects if x['Object_Type']=='Actor' and x['Package_ID']==actor_diagram['Package_ID']]}
(out/'inventario_ea_reutilizado.json').write_text(json.dumps(inventory,indent=2,ensure_ascii=False),encoding='utf-8')
assert len(inventory['actores'])==4
control=root/'auditoria_documental/15_CONTROL_ACTUALIZACION_DOCUMENTAL.md'
s=control.read_text(encoding='utf-8').replace('| Preparación | En curso | HEAD verificado, Git sin modificaciones versionadas, originales respaldados. Verificar apertura EA y COM; reutilizar inventarios de auditoría. |','| Preparación | Bloqueada en acceso EA | Originales respaldados; cuatro archivos maestros sin cambios. COM disponible, pero OpenFile no finalizó. Control de aplicaciones rechazó el acceso a EA. |').replace('| 1 PostgreSQL documentado | Pendiente | Consultas de lectura y actualización de fuentes documentales. |','| 1 PostgreSQL documentado | Verificación y SQL completados; Word/EA pendientes | PostgreSQL en transacción READ ONLY: 31 tablas, 287 columnas; 113 restricciones conservadas. fuentes/esquema.sql actualizado y validado con esquema.py. |')
s+='''
## Evidencia actual y bloqueo

- PostgreSQL efectivo de Laravel: `crm_educativo`, `127.0.0.1:5432`, esquema `public`, PostgreSQL 17.4. No se realizaron escrituras ni migraciones.
- Conteos: 31 tablas públicas, 287 columnas, 31 PK, 46 FK, siete UNIQUE, 28 CHECK, 55 índices, cinco triggers; incluyendo laravel.migrations: 32 tablas, 290 columnas.
- Atributos: cuotas.token_pago y transacciones_stripe.token_publico son character varying(80), NULL permitido y sin DEFAULT. transacciones_stripe.expira_en es timestamp(0) without time zone, NULL permitido y sin DEFAULT.
- Restricciones cuotas_token_pago_unique y transacciones_stripe_token_publico_unique verificadas; las 113 restricciones coinciden con el inventario anterior. No aparecen las cinco columnas retiradas.
- `generadorDocumento/fuentes/esquema.sql` actualizado mediante pg_dump schema-only de public, sin propietarios, permisos, datos ni credenciales. Parser documental verificado: 31 tablas, 287 columnas, 31 PK y 46 FK.
- Evidencias de lectura: `tmp/actualizacion_documental/postgres_actual.json`, esquema_actual.sql e inventario_ea_reutilizado.json. Se reutilizaron 47 diagramas, paquetes y cuatro actores del inventario histórico sin volver a auditar documentos.
- Capítulo IV protegido como bloques OOXML en capitulo_IV_protegido.xml; DOCX/DOC/PDF/EAPX permanecen exactamente iguales al respaldo. Ningún diagrama ha sido modificado.
- Rechazo textual de la herramienta: **Computer Use was not approved to use Enterprise Architect**. No se intentará eludir mediante COM ni editar tablas internas. Los clientes de apertura COM de prueba se detuvieron; apertura original, edición y exportación EA pendientes de acceso.
- Se solicitó habilitar Enterprise Architect en permisos del control de aplicaciones. La autorización editorial ya existe; falta disponibilidad técnica.
- No se ejecutaron pruebas con escrituras ni se produjeron capturas nuevas. No se generaron versiones finales, commit ni push de una entrega incompleta.

## Siguiente paso exacto

Al habilitar EA: confirmar apertura del EAPX original sin cambiarlo, inventariar por API oficial y comparar GUID con el inventario reutilizado. Completar Fase 1 en modelo EA y Word. Continuar luego las fases 2–12 en orden. No ejecutar documento_p2.py ni generadores EA destructivos.
'''
control.write_text(s,encoding='utf-8')
print('SQL documental actualizado. Maestros y EAPX intactos. Control guardado para reanudación.')
print('Capítulo IV protegido:',hashlib.sha256(chapter).hexdigest())
