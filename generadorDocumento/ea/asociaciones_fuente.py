"""Asociaciones Eloquent verificadas contra FK y nulabilidad reales; COM oficial."""
from pathlib import Path
import re,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import sincronizar_documentacion as S
from diccionario_actual import foreign_keys
import win32com.client

def main():
    data=S.catalog();nodes={n:x for cu in data.values() for n,x in cu['nodes'].items()}
    db=json.loads((S.OUT/'postgres_actual.json').read_text(encoding='utf-8'));fks=foreign_keys(db)
    columns={(x['table_name'],x['column_name']):x for x in db['columnas'] if x['table_schema']=='public'}
    models={n:x for n,x in nodes.items() if '/Modelos/' in x['source']}
    tables={n:re.search(r"protected\s+\$table\s*=\s*'([^']+)'",x['text'])[1] for n,x in models.items()}
    groups={}
    for name,item in models.items():
        for method in item['methods']:
            m=re.search(r"\$this->(belongsTo|hasMany|hasOne)\((\w+)::class,\s*'([^']+)',\s*'([^']+)'",method['body'])
            if not m or m[2] not in tables:continue
            child,parent=(name,m[2]) if m[1]=='belongsTo' else (m[2],name)
            fk=next((f for f in fks if f['tabla']==tables[child] and f['destino']==tables[parent] and f['columnas']==[m[3]] and f['destino_columnas']==[m[4]]),None)
            assert fk,(name,method['name'],'relación Eloquent sin FK verificable')
            group=groups.setdefault(fk['nombre'],{'fk':fk,'child':child,'parent':parent,'methods':[]})
            group['methods'].append({'class':name,'method':method['name'],'kind':m[1],'source':item['source']})
    if '--verificar' in sys.argv:
        print('Asociaciones verificadas:',len(groups));return
    S.prepare_export_environment()
    r=win32com.client.Dispatch('EA.Repository');assert r.OpenFile(str(S.DOC/'ea/crm-p2.eapx'))
    try:
        elements={}
        for row in S.select(r,'t_object'):
            if row['Object_Type']=='Class' and row['Name'] in nodes:elements.setdefault(row['Name'],r.GetElementByID(int(row['Object_ID'])))
        registry=[];evidence=[];relations=json.loads((S.OUT/'exportaciones_relaciones_clases.json').read_text(encoding='utf-8'))
        relation_objects={}
        for view in relations:
            diagram=r.GetDiagramByID(view['id']);relation_objects[view['id']]={o.ElementID for o in diagram.DiagramObjects}
        for fkname,group in groups.items():
            fk=group['fk'];a,b=elements[group['child']],elements[group['parent']]
            marker='FK documental: '+fkname
            c=next((c for c in a.Connectors if c.Type=='Association' and c.SupplierID==b.ElementID and marker in (c.Notes or '')),None)
            if c is None:c=a.Connectors.AddNew('','Association');c.SupplierID=b.ElementID
            c.Stereotype='Eloquent';c.Notes=marker+'\n'+fk['definicion']+'\n'+json.dumps(group['methods'],ensure_ascii=False)
            S.checked(c);left,right=c.ClientEnd,c.SupplierEnd
            unique=any(k['esquema']=='public' and k['tabla']==fk['tabla'] and k['tipo'] in ('p','u') and re.search(r'\(([^)]+)\)',k['definicion'])[1]==fk['columnas'][0] for k in db['restricciones'])
            left.Cardinality='0..1' if unique else '0..*'
            right.Cardinality='0..1' if columns[fk['tabla'],fk['columnas'][0]]['is_nullable']=='YES' else '1'
            for method in group['methods']:
                if method['kind']=='belongsTo':right.Role=method['method']
                else:left.Role=method['method']
            c.Direction='Bi-Directional' if len({m['class'] for m in group['methods']})>1 else 'Source -> Destination'
            S.checked(left);S.checked(right);S.checked(c)
            # La nueva asociación tiene una vista completa propia. Evitar que
            # altere la legibilidad de las vistas ya distribuidas de dependencias.
            for view in relations:
                ids=relation_objects[view['id']]
                if a.ElementID not in ids or b.ElementID not in ids:continue
                d=r.GetDiagramByID(view['id'])
                link=next((x for x in d.DiagramLinks if x.ConnectorID==c.ConnectorID),None)
                if link is None:link=d.DiagramLinks.AddNew('','');link.ConnectorID=c.ConnectorID
                link.IsHidden=True;S.checked(link)
            pkg=r.GetPackageByID(a.PackageID);title='Relación Eloquent — '+fkname
            d=next((x for x in pkg.Diagrams if x.Name==title),None)
            if d is None:d=pkg.Diagrams.AddNew(title,'Logical');S.checked(d)
            d.Notes=marker+'\n'+fk['definicion']+'\nLas multiplicidades se obtienen de FK, NULL, PK/UNIQUE; no se confunde hasOne con existencia obligatoria.';S.checked(d)
            for e,x in [(a,40),(b,700)]:
                w,h=S.measure(nodes[e.Name],500);S.put(d,e,x,40,w,h)
            ids={a.ElementID,b.ElementID}
            related={x.ConnectorID:x for e in (a,b) for x in e.Connectors if x.ClientID in ids and x.SupplierID in ids}
            for cid in related:
                link=next((x for x in d.DiagramLinks if x.ConnectorID==cid),None)
                if link is None:link=d.DiagramLinks.AddNew('','');link.ConnectorID=cid
                link.IsHidden=cid!=c.ConnectorID;S.checked(link)
            S.export(r,d,'clases-asociacion-'+str(len(registry)+1).zfill(2),registry,'clases-asociacion')
            evidence.append({**group,'connector_id':c.ConnectorID,'diagram_id':d.DiagramID,'child_cardinality':c.ClientEnd.Cardinality,'parent_cardinality':c.SupplierEnd.Cardinality})
            S.dump('exportaciones_asociaciones.json',registry);S.dump('asociaciones_eloquent.json',evidence)
        general=[]
        for cu,did in {'CU1':1,'CU2':2,'CU3':3,'CU4':4,'CU5':5,'CU6':138,'CU7':7,'CU8':8}.items():S.export(r,r.GetDiagramByID(did),'cls-'+cu.lower(),general,'clases-general',cu)
    finally:r.CloseFile();r.Exit()

if __name__=='__main__':main()
