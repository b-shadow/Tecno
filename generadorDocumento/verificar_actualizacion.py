"""Control incremental de integridad documental con evidencias locales de EA.

No abre bases comerciales ni escribe en EA; consume instantáneas de solo lectura.
"""
from pathlib import Path
import json,hashlib,zipfile,sys,re
from lxml import etree as E
import actualizar_documento as D

def load(name):return json.loads((D.OUT/name).read_text(encoding='utf-8'))
def check(condition,message):
    if not condition:raise AssertionError(message)

def main():
    before=load('ea_antes_edicion.json');after=load('ea_actual.json');report={}
    for table,identifier,guid in [('t_object','Object_ID','ea_guid'),('t_diagram','Diagram_ID','ea_guid'),('t_package','Package_ID','ea_guid')]:
        current={x[identifier]:x for x in after[table]}
        for old in before[table]:
            check(old[identifier] in current,f'Falta elemento original {table} {old[identifier]}')
            check(current[old[identifier]][guid]==old[guid],f'GUID original cambiado {table} {old[identifier]}')
    def actors(s):return {x['Object_ID']:x for x in s['t_object'] if x['Object_Type']=='Actor'}
    oldactors,newactors=actors(before),actors(after)
    check(oldactors.keys()==newactors.keys(),'Cantidad/ID de actores alterado')
    for eid,old in oldactors.items():
        check(old['Name']==newactors[eid]['Name'] and old['ea_guid']==newactors[eid]['ea_guid'],'Actor cambiado')
    canonical=[x['Name'] for x in newactors.values() if x['Package_ID']=='36']
    check(set(canonical)=={'Administrador','Coordinador','Vendedor','Visitante'},'Actores canónicos alterados')
    for table in ['t_diagram','t_diagramobjects','t_diagramlinks']:
        field='DiagramID' if table=='t_diagramlinks' else 'Diagram_ID'
        a=[x for x in before[table] if x[field]=='9'];b=[x for x in after[table] if x[field]=='9']
        check(a==b,'Diagrama de actores 9 modificado: '+table)
    ids={x['Object_ID'] for x in before['t_diagramobjects'] if x['Diagram_ID']=='9'}
    for table in ['t_object','t_connector']:
        if table=='t_object':f=lambda x:x['Object_ID'] in ids
        else:f=lambda x:x['Start_Object_ID'] in ids and x['End_Object_ID'] in ids
        check([x for x in before[table] if f(x)]==[x for x in after[table] if f(x)],'Elementos/relaciones del diagrama protegido alterados')
    _,root,body=D.doc_read();initial=E.fromstring((D.OUT/'document-inicial.xml').read_bytes()).find('w:body',D.NS)
    check(D.protected(initial)==D.protected(body),'Capítulo IV alterado')
    functional=load('archivos_iniciales.json');changed=[]
    for rel,item in functional.items():
        if rel.startswith('generadorDocumento/'):continue
        path=D.ROOT/rel
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:changed.append(rel)
    check(not changed,'Código funcional alterado: '+str(changed))
    cases=lambda s:{x['Object_ID']:(x['Name'],x['ea_guid']) for x in s['t_object'] if x['Object_Type']=='UseCase' and x['Package_ID']=='36'}
    check(cases(before)==cases(after) and len(cases(after))==8,'CU originales alterados')
    cat=load('catalogo_fuente.json');objects={x['Object_ID']:x for x in after['t_object']}
    diagrams={x['Diagram_ID']:x for x in after['t_diagram']}
    attrs={};methods={};params={}
    for x in after['t_attribute']:attrs.setdefault(x['Object_ID'],{})[x['Name']]=x
    for x in after['t_operation']:methods.setdefault(x['Object_ID'],{})[x['Name']]=x
    for x in after['t_operationparams']:params.setdefault(x['OperationID'],{})[x['Name']]=x
    counts={}
    for cu,data in cat.items():
        did=str({'CU1':1,'CU2':2,'CU3':3,'CU4':4,'CU5':5,'CU6':138,'CU7':7,'CU8':8}[cu])
        present={objects[o['Object_ID']]['Name']:o['Object_ID'] for o in after['t_diagramobjects'] if o['Diagram_ID']==did and objects[o['Object_ID']]['Object_Type']=='Class'}
        for name,item in data['nodes'].items():
            check(name in present,f'{cu}: falta clase {name}');eid=present[name]
            check(set(methods.get(eid,{}))=={m['name'] for m in item['methods']},f'{name}: operaciones ajenas al código')
            check(set(attrs.get(eid,{}))=={a['name'] for a in item['attrs']},f'{name}: atributos ajenos a la fuente/mapeo')
            for a in item['attrs']:
                actual=attrs.get(eid,{}).get(a['name']);check(actual is not None,f'{name}: falta atributo {a["name"]}')
                check(actual['Type']==a['type'],f'{name}.{a["name"]}: tipo diferente')
                check(actual['Scope']==a['visibility'] and actual['Default']==(a.get('default') or ''),f'{name}.{a["name"]}: visibilidad/default diferente')
                check(actual['IsStatic']==str(int(bool(a.get('static')))) and actual['Const']==str(int(bool(a.get('constant') or a.get('readonly')))),f'{name}.{a["name"]}: static/readonly diferente')
            for m in item['methods']:
                actual=methods.get(eid,{}).get(m['name']);check(actual is not None,f'{name}: falta método {m["name"]}')
                check(actual['Type']==m['return'] and actual['Scope']==m['visibility'],f'{name}.{m["name"]}: firma/visibilidad diferente')
                check(actual['IsStatic']==str(int(m['static'])),f'{name}.{m["name"]}: static diferente')
                actual_params=params.get(actual['OperationID'],{})
                check(len(actual_params)==len(m['params']),f'{name}.{m["name"]}: cantidad de parámetros diferente')
                for p in m['params']:
                    pn=p['name'].replace("'",'"') if item['kind']!='php' else p['name']
                    ap=actual_params.get(pn);check(ap is not None,f'{name}.{m["name"]}: falta parámetro {pn}')
                    check(ap['Type']==p['type'] and ap['Default']==(p.get('default') or ''),f'{name}.{m["name"]}.{pn}: tipo/default diferente')
        counts[cu]={'clases':len(data['nodes']),'metodos':sum(len(x['methods']) for x in data['nodes'].values()),'atributos':sum(len(x['attrs']) for x in data['nodes'].values())}
    traces=load('trazas_interacciones.json');group={}
    for t in traces:group.setdefault((t['cu'],t['flow']),{}).setdefault(t['mode'],[]).extend(t['messages'])
    for key,modes in group.items():check(modes.get('seq')==modes.get('com'),'Secuencia/comunicación difieren: '+str(key))
    report.update(originales_y_GUID_preservados=True,actores_canonicos=canonical,actores_total_modelo=len(newactors),diagrama_actores_9_intacto=True,capitulo_IV_intacto=True,codigo_funcional_intacto=True,cu_originales=8,clases_por_cu=counts,flujos=len(group),diagramas_interaccion=len(traces))
    (D.OUT/'integridad_documental.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
