"""Vistas complementarias Conallen reutilizando elementos y enlaces originales."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parent))
import sincronizar_documentacion as S
import win32com.client
import navegacion as N

def sync_original(r,d,actor):
    pages,edges=N.ACTORES[actor]();pkg=r.GetPackageByID(d.PackageID)
    old={r.GetElementByID(o.ElementID).Name:r.GetElementByID(o.ElementID) for o in d.DiagramObjects}
    objects={};stereotypes={'cliente':'client page','ps':'server page','form':'Formulario','bd':'database','externo':'servicio externo'}
    for key,(kind,name,attributes,operations) in pages.items():
        e=old.get(name)
        if e is None:
            assert kind!='actor','No crear actores'
            e=pkg.Elements.AddNew(name,'Object' if kind=='externo' else 'Class');S.checked(e)
            e.Stereotype=stereotypes[kind];S.checked(e)
        if kind!='actor':
            e.Notes='Abstracción navegacional Conallen. '+('API real: '+N.API.get(key,'') if kind=='ps' else 'Representación de página, componente, formulario, tabla o servicio externo existente. No es una nueva clase PHP.');S.checked(e)
            declarations=[x.partition('=') for x in S.split_args(attributes)]
            attrs=[x[0].strip() for x in declarations]
            existing={a.Name:a for a in e.Attributes}
            for i,(declaration,name_attr) in enumerate(zip(declarations,attrs)):
                a=existing.get(name_attr) or e.Attributes.AddNew(name_attr,'')
                a.Name=name_attr;a.Default=declaration[2].strip() if declaration[1] else ''
                a.Visibility='Private';a.Pos=i;a.IsCollection=True;a.AllowDuplicates=True;a.IsOrdered=False
                a.Notes='Campo de la abstracción navegacional Conallen {bag}; tipos físicos en el diccionario de datos.';S.checked(a)
            for i in reversed(range(e.Attributes.Count)):
                if e.Attributes.GetAt(i).Name not in attrs:e.Attributes.DeleteAt(i,False)
            existing={m.Name:m for m in e.Methods};methods=[m.strip().removesuffix('()') for m in operations.split(',') if m.strip()]
            for i,name_method in enumerate(methods):
                m=existing.get(name_method) or e.Methods.AddNew(name_method,'');m.Visibility='Public';m.Pos=i;S.checked(m)
            for i in reversed(range(e.Methods.Count)):
                if e.Methods.GetAt(i).Name not in methods:e.Methods.DeleteAt(i,False)
        objects[key]=e
    wanted=set()
    for a,b,st,text in edges:
        source,target=objects[a],objects[b]
        c=next((c for c in source.Connectors if c.SupplierID==target.ElementID and c.Stereotype==st and c.Name==text),None)
        if c is None:
            c=next((c for c in source.Connectors if c.SupplierID==target.ElementID and c.Stereotype==st and c.ConnectorID not in wanted),None)
        if c is None:c=source.Connectors.AddNew(text,'Association');c.SupplierID=target.ElementID
        c.Name=text;c.Stereotype=st;c.Direction='Source -> Destination';S.checked(c);wanted.add(c.ConnectorID)
    # Retirar enlaces obsoletos de navegación por la API, sin borrar elementos
    # originales ni tocar el diagrama de actores o las asociaciones del dominio.
    oldids={e.ElementID for e in old.values()};newids={e.ElementID for e in objects.values()}
    for e in old.values():
        for i in reversed(range(e.Connectors.Count)):
            c=e.Connectors.GetAt(i)
            if c.ClientID in oldids|newids and c.SupplierID in oldids|newids and c.ConnectorID not in wanted:e.Connectors.DeleteAt(i,False)
        if e.ElementID not in newids and e.Type!='Actor':e.Notes='Elemento histórico conservado por su ID/GUID. Excluido de la navegación vigente: no se ofrecen nuevos métodos QR/transferencia ni envío de comprobantes manuales.';S.checked(e)
    for i in reversed(range(d.DiagramObjects.Count)):
        if d.DiagramObjects.GetAt(i).ElementID not in newids:d.DiagramObjects.DeleteAt(i,False)
    y=max([-o.bottom for o in d.DiagramObjects] or [0])+220
    for key,e in objects.items():
        o=next((o for o in d.DiagramObjects if o.ElementID==e.ElementID),None)
        if o is None:S.put(d,e,40,y,500,100+24*(e.Attributes.Count+e.Methods.Count));y+=200+24*(e.Attributes.Count+e.Methods.Count)
    d.Notes='Navegación vigente contrastada con React y rutas API; conserva los elementos originales correctos. Retira del flujo activo los formularios rechazados por el backend y agrega pagos públicos y compartición manual. Sin nuevos actores ni CU.';S.checked(d)
    return objects

def navigation(r):
    registry=[];coverage=[];general=[]
    for did in range(134,138):
        original=r.GetDiagramByID(did);pkg=r.GetPackageByID(original.PackageID)
        sync_original(r,original,list(N.ACTORES)[did-134])
        objects={o.ElementID:r.GetElementByID(o.ElementID) for o in original.DiagramObjects}
        links={c.ConnectorID:c for e in objects.values() for c in e.Connectors if c.ClientID in objects and c.SupplierID in objects}
        pending=set(links);covered=set();index=0
        for eid,central in objects.items():
            outgoing=[c for cid,c in links.items() if cid in pending and c.ClientID==eid]
            if not outgoing:continue
            for start in range(0,len(outgoing),2):
                group=outgoing[start:start+2];index+=1
                name=original.Name+' — '+central.Name+f' — vista {start//2+1}'
                d=next((x for x in pkg.Diagrams if x.Name==name),None)
                if d is None:d=pkg.Diagrams.AddNew(name,'Logical');S.checked(d)
                d.Notes='Vista complementaria Conallen del diagrama '+str(did)+'. Elementos y relaciones originales reutilizados. No crea actores ni casos de uso. Páginas y bases de datos representan abstracciones navegacionales.';S.checked(d)
                central_h=max(130,95+(central.Attributes.Count+central.Methods.Count)*24)
                S.put(d,central,350,40,420,central_h)
                covered.add(eid)
                targets=list(dict.fromkeys(c.SupplierID for c in group))
                for i,target in enumerate(targets):
                    e=objects[target];S.put(d,e,40+(i%2)*660,central_h+220,420,max(130,95+(e.Attributes.Count+e.Methods.Count)*24));covered.add(target)
                stem=f'nav-{did}-vista-{index:03d}'
                S.export(r,d,stem,registry,'navegacion')
                registry[-1].update(actor=list(N.ACTORES)[did-134],original_id=did)
                for c in group:pending.remove(c.ConnectorID)
                coverage.append({'original':did,'diagram_id':d.DiagramID,'elements':[eid]+targets,'connectors':[c.ConnectorID for c in group]})
                S.dump('exportaciones_navegacion.json',registry);S.dump('cobertura_navegacion.json',coverage)
        assert not pending,(did,pending)
        for eid in objects.keys()-covered:
            e=objects[eid];name=original.Name+' — elemento '+e.Name
            d=next((x for x in pkg.Diagrams if x.Name==name),None)
            if d is None:d=pkg.Diagrams.AddNew(name,'Logical');S.checked(d)
            S.put(d,e,40,40,500,max(130,75+e.Attributes.Count*24));index+=1
            S.export(r,d,f'nav-{did}-vista-{index:03d}',registry,'navegacion')
            registry[-1].update(actor=list(N.ACTORES)[did-134],original_id=did)
            coverage.append({'original':did,'diagram_id':d.DiagramID,'elements':[eid],'connectors':[]});covered.add(eid)
        assert covered==objects.keys()
        S.dump('exportaciones_navegacion.json',registry);S.dump('cobertura_navegacion.json',coverage)
        S.export(r,original,'nav-'+list(N.ACTORES)[did-134].lower(),general,'navegacion-general')
        S.dump('exportaciones_navegacion_general.json',general)

def base(r):
    # Diagrama de actores 9: solo exportación. No se llama Update ni put sobre él.
    registry=[]
    for did,stem in [(9,'actores')]+[(n+9,f'uc-cu{n}') for n in range(1,9)]+[(18,'uc-general'),(19,'paquetes')]+[(n+19,f'paquete-{n}') for n in range(1,7)]:
        d=r.GetDiagramByID(did)
        if did==15:
            visitor=r.GetElementByID(201)
            if not any(o.ElementID==201 for o in d.DiagramObjects):S.put(d,visitor,700,500,150,150)
        if did==9:
            # export() actualiza metadatos del diagrama: evitar incluso esa escritura.
            # La imagen inicial íntegra sigue siendo la referencia protegida.
            original=S.ROOT/'backups/documental-20261126/generadorDocumento/diagramas/actores.emf'
            import shutil
            shutil.copyfile(original,S.DOC/'diagramas/actores.emf')
            registry.append({'id':9,'name':d.Name,'stem':'actores','category':'actores','guid':d.DiagramGUID})
        else:S.export(r,d,stem,registry,'base')
    S.dump('exportaciones_base.json',registry)

def main():
    S.prepare_export_environment()
    r=win32com.client.Dispatch('EA.Repository');assert r.OpenFile(str(S.DOC/'ea/crm-p2.eapx'))
    try:
        if sys.argv[1]=='base':base(r)
        else:navigation(r)
    finally:r.CloseFile();r.Exit()
if __name__=='__main__':main()
