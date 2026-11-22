"""Vistas nativas legibles del modelo de datos y despliegue. No escribe SQL EA."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import sincronizar_documentacion as S
import win32com.client

def diagram(pkg,name,kind='Logical'):
    d=next((x for x in pkg.Diagrams if x.Name==name),None)
    if d is None:d=pkg.Diagrams.AddNew(name,kind);S.checked(d)
    return d

def conceptual(r):
    d=r.GetDiagramByID(133);pkg=r.GetPackageByID(d.PackageID)
    elements={o.ElementID:r.GetElementByID(o.ElementID) for o in d.DiagramObjects}
    links={c.ConnectorID:c for e in elements.values() for c in e.Connectors if c.ClientID in elements and c.SupplierID in elements}
    registry=[];covered=set()
    for i,c in enumerate(links.values(),1):
        a,b=elements[c.ClientID],elements[c.SupplierID]
        detail=diagram(pkg,'Modelo conceptual — '+a.Name+' / '+b.Name+' — relación '+str(c.ConnectorID))
        detail.Notes='Vista de los elementos originales del modelo conceptual; conserva atributos y relación original, incluyendo multiplicidades. El mapeo físico, las restricciones y el diccionario detallan los tipos PostgreSQL exactos.'
        x=40
        for e in (a,b):
            w=max(300,max([len(e.Name)]+[len(x.Name) for x in e.Attributes])*9+65)
            h=80+e.Attributes.Count*24
            S.put(detail,e,x,50,w,h);x+=w+220;covered.add(e.ElementID)
        association_class=c.AssociationClass
        if association_class is not None and association_class.ElementID in elements:
            ac=association_class
            y=max(80+a.Attributes.Count*24,80+b.Attributes.Count*24)+230
            S.put(detail,ac,250,y,420,80+ac.Attributes.Count*24);covered.add(ac.ElementID)
        ids={o.ElementID for o in detail.DiagramObjects}
        related={x.ConnectorID:x for e in (a,b) for x in e.Connectors if x.ClientID in ids and x.SupplierID in ids}
        for cid in related:
            dl=next((x for x in detail.DiagramLinks if x.ConnectorID==cid),None)
            if dl is None:dl=detail.DiagramLinks.AddNew('','');dl.ConnectorID=cid
            dl.IsHidden=cid!=c.ConnectorID;S.checked(dl)
        S.export(r,detail,f'datos-relacion-{i:02d}',registry,'conceptual-detalle')
    for e in elements.values():
        if e.ElementID in covered:continue
        detail=diagram(pkg,'Modelo conceptual — '+e.Name)
        S.put(detail,e,40,40,420,80+e.Attributes.Count*24)
        S.export(r,detail,'datos-entidad-'+e.Name,registry,'conceptual-detalle')
        covered.add(e.ElementID)
    S.dump('exportaciones_datos.json',registry)
    S.dump('conceptual_cobertura.json',{'original':133,'elementos':len(elements),'relaciones':len(links),'elementos_cubiertos':len(covered)})
    general=[];S.export(r,d,'conceptual',general,'conceptual-general');S.dump('exportaciones_conceptual_general.json',general)

def deployment(r):
    d=r.GetDiagramByID(152);pkg=r.GetPackageByID(d.PackageID)
    e={o.ElementID:r.GetElementByID(o.ElementID) for o in d.DiagramObjects}
    changes={2048:'www.tecnoweb.org.bo (destino previsto)',2049:'Fedora Linux (previsto)',2050:'Apache / PHP 8.4 (previstos)',2061:'db.tecnoweb.org.bo (destino previsto)',2062:'Linux (previsto)',2063:'PostgreSQL (versión institucional no verificada)',2064:'db_grupo05sa (configuración prevista)'}
    for eid,name in changes.items():
        e[eid].Name=name;e[eid].Notes='Destino institucional documentado en P2_WEB.md. No acredita despliegue ni medición de versiones en el servidor remoto.';S.checked(e[eid])
    smtp=next((x for x in pkg.Elements if x.Name=='Gmail SMTP — correo manual'),None)
    if smtp is None:smtp=pkg.Elements.AddNew('Gmail SMTP — correo manual','Node');S.checked(smtp)
    smtp.Notes='Servicio externo configurado para Laravel Mail. Solo se invoca mediante acción explícita del usuario autorizado. La aceptación SMTP no acredita recepción efectiva.';S.checked(smtp)
    if not any(c.SupplierID==smtp.ElementID for c in e[2052].Connectors):
        c=e[2052].Connectors.AddNew('SMTP / TLS — acción manual','CommunicationPath');c.SupplierID=smtp.ElementID;c.Direction='Source -> Destination';S.checked(c)
    S.put(d,smtp,700,900,450,140)
    local=next((x for x in pkg.Elements if x.Name=='Entorno local verificado'),None)
    if local is None:local=pkg.Elements.AddNew('Entorno local verificado','Node');S.checked(local)
    local.Notes='React/Vite localhost:5173; API Laravel 127.0.0.1:8001; PostgreSQL 17.4 en 127.0.0.1:5432, base crm_educativo. datos es paquete Composer dentro del proceso PHP, no un servidor separado.';S.checked(local)
    S.put(d,local,40,900,550,160)
    note=next((x for x in pkg.Elements if x.Type=='Note' and x.Name=='Verificación de despliegue'),None)
    if note is None:note=pkg.Elements.AddNew('Verificación de despliegue','Note');S.checked(note)
    note.Notes='LOCAL: PostgreSQL 17.4; Vite :5173 y Laravel :8001.\nINSTITUCIONAL: destino previsto, sin despliegue ni versiones remotas verificadas.\nEXTERNOS: Stripe Sandbox y Gmail SMTP.\nDATOS: paquete Composer del proceso Laravel. Sin Scheduler de correos de cuotas.';S.checked(note)
    S.put(d,note,1200,900,550,240)
    for i in range(d.DiagramObjects.Count):
        o=d.DiagramObjects.GetAt(i);o.SetStyleEx('font','Calibri');o.SetStyleEx('fontsz','120');S.checked(o)
    d.Notes='Arquitectura física conservada: PC Administrador, PC Cliente, router, switch, aplicación y PostgreSQL. Se distinguen evidencia local, destino institucional previsto y servicios externos. No se realizó despliegue.';S.checked(d)
    # Reorganizar el original sin retirar sus elementos. Sus vistas nativas
    # complementarias mantienen contenedores y conexiones con letra legible.
    baseline=json.loads((S.OUT/'ea_antes_edicion.json').read_text(encoding='utf-8'))
    positions={int(o['Object_ID']):o for o in baseline['t_diagramobjects'] if int(o['Diagram_ID'])==152}
    for i in range(d.DiagramObjects.Count):
        o=d.DiagramObjects.GetAt(i)
        if o.ElementID in positions:
            p=positions[o.ElementID]
            o.left=round(int(p['RectLeft'])*1.7);o.right=round(int(p['RectRight'])*1.7)
            o.top=round(int(p['RectTop'])*1.7);o.bottom=round(int(p['RectBottom'])*1.7);S.checked(o)
    S.put(d,smtp,1750,1400,600,180);S.put(d,local,40,1600,850,200);S.put(d,note,1200,1700,850,280)
    general=[];S.export(r,d,'despliegue',general,'despliegue-general')
    registry=[]
    def view(title,placements):
        v=diagram(pkg,'Despliegue — '+title,'Deployment')
        v.Notes='Vista complementaria de los mismos equipos, nodos y artefactos originales del diagrama 152. No acredita despliegue remoto. Configuración local e institucional prevista se distinguen explícitamente.';S.checked(v)
        for eid,x,y,w,h in placements:S.put(v,r.GetElementByID(eid),x,y,w,h)
        S.export(r,v,'despliegue-vista-'+str(len(registry)+1),registry,'despliegue')
    for a,b,title in [(2048,2054,'HTTPS de acceso'),(2054,2055,'router y switch'),(2055,2065,'acceso del administrador'),(2055,2068,'acceso del cliente'),(2048,2061,'conexión PostgreSQL'),(2048,2056,'API Stripe'),(2052,smtp.ElementID,'correo manual SMTP')]:
        view(title,[(a,40,40,440,200),(b,700,40,440,200)])
    view('servidor de aplicación previsto',[(2048,40,40,1500,1000),(2049,70,160,1440,840),(2050,100,280,1380,680),(2051,140,470,380,300),(2052,580,470,380,300),(2053,1020,470,380,300)])
    view('servidor PostgreSQL previsto',[(2061,40,40,1300,850),(2062,80,200,1220,640),(2063,120,350,1140,440),(2064,200,590,980,150)])
    view('Stripe Sandbox',[(2056,40,40,1500,850),(2057,80,200,1420,640),(2058,140,490,380,200),(2059,580,490,380,200),(2060,1020,490,380,200)])
    view('clientes y verificación local',[(2065,40,40,650,620),(2066,80,190,570,420),(2067,120,390,490,160),(2068,850,40,650,620),(2069,890,190,570,420),(2070,930,390,490,160),(local.ElementID,40,800,650,200),(note.ElementID,850,800,650,300)])
    S.dump('exportaciones_despliegue.json',registry)

def main():
    S.prepare_export_environment()
    r=win32com.client.Dispatch('EA.Repository');assert r.OpenFile(str(S.DOC/'ea/crm-p2.eapx'))
    try:
        if sys.argv[1]=='conceptual':conceptual(r)
        elif sys.argv[1]=='despliegue':deployment(r)
    finally:r.CloseFile();r.Exit()
if __name__=='__main__':main()
