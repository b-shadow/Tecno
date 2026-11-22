"""Retira únicamente vistas temporales creadas en esta actualización y reemplazadas."""
from pathlib import Path
import sys,json,re
sys.path.insert(0,str(Path(__file__).resolve().parent))
import sincronizar_documentacion as S
import win32com.client

REGISTRIES=['exportaciones_clases_visibles.json','exportaciones_relaciones_clases.json','exportaciones_asociaciones.json','exportaciones_algoritmos.json','exportaciones_interacciones.json','exportaciones_datos.json','exportaciones_despliegue.json','exportaciones_navegacion.json','exportaciones_base.json']

def main():
    baseline=json.loads((S.OUT/'ea_antes_edicion.json').read_text(encoding='utf-8'))
    original={int(x['Diagram_ID']) for x in baseline['t_diagram']};original_elements={int(x['Object_ID']) for x in baseline['t_object']}
    active=set(original)
    for name in REGISTRIES:active.update(x['id'] for x in json.loads((S.OUT/name).read_text(encoding='utf-8')))
    S.prepare_export_environment();r=win32com.client.Dispatch('EA.Repository');assert r.OpenFile(str(S.DOC/'ea/crm-p2.eapx'))
    try:
        state=S.snapshot(r,'ea_antes_limpieza.json');retired=[];removed_elements=[]
        for row in state['t_diagram']:
            did=int(row['Diagram_ID']);name=row['Name']
            owned=bool(re.match(r'CU[1-8]\. (?:Clase |Secuencia — |Comunicación — |Cálculo literal — )',name) or name.startswith(('Relación de clases — ','Relación Eloquent — ','Modelo conceptual — ','Despliegue — ')) or ('Diagrama de Navegacion - ' in name and ' — ' in name))
            if did in active or not owned:continue
            for c in state['t_connector']:
                if c['DiagramID']==str(did) and c['Connector_Type'] in ('Sequence','Collaboration'):
                    owner=r.GetElementByID(int(c['Start_Object_ID']))
                    for i in reversed(range(owner.Connectors.Count)):
                        if owner.Connectors.GetAt(i).ConnectorID==int(c['Connector_ID']):owner.Connectors.DeleteAt(i,False);break
            pkg=r.GetPackageByID(int(row['Package_ID']))
            for i in reversed(range(pkg.Diagrams.Count)):
                if pkg.Diagrams.GetAt(i).DiagramID==did:pkg.Diagrams.DeleteAt(i,False);break
            retired.append({'id':did,'guid':row['ea_guid'],'name':name})
        retired_ids={x['id'] for x in retired}
        used={int(x['Object_ID']) for x in state['t_diagramobjects'] if int(x['Diagram_ID']) not in retired_ids}
        interaction_packages={int(d['Package_ID']) for d in baseline['t_diagram'] if d['Diagram_Type'] in ('Sequence','Collaboration')}
        for row in state['t_object']:
            eid=int(row['Object_ID'])
            if eid in original_elements or eid in used or row['Object_Type'] not in ('Note','InteractionFragment','Object') or int(row['Package_ID']) not in interaction_packages:continue
            pkg=r.GetPackageByID(int(row['Package_ID']))
            for i in reversed(range(pkg.Elements.Count)):
                if pkg.Elements.GetAt(i).ElementID==eid:pkg.Elements.DeleteAt(i,False);break
            removed_elements.append(eid)
        S.dump('limpieza_vistas.json',{'retired_diagrams':retired,'removed_unreferenced_owned_elements':removed_elements,'original_diagrams_preserved':len(original)})
    finally:r.CloseFile();r.Exit()

if __name__=='__main__':main()
