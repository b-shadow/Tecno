"""Retira diagramas creados por esta tarea; nunca elimina elementos ni relaciones."""
from pathlib import Path
import sys,json,collections,hashlib
ROOT=Path.cwd(); O=ROOT/'tmp/actualizacion_documental'
sys.path.insert(0,str(ROOT/'generadorDocumento/ea'))
import sincronizar_documentacion as S
import win32com.client
baseline=json.loads((O/'ea_antes_edicion.json').read_text(encoding='utf-8'))
original={int(x['Diagram_ID']):x for x in baseline['t_diagram']}
assert len(original)==47
backup=ROOT/'backups/documental-20261126/antes-retirar-vistas-masivas.eapx'
assert backup.exists() and backup.stat().st_size>16000000
r=win32com.client.Dispatch('EA.Repository')
assert r.OpenFile(str(ROOT/'generadorDocumento/ea/crm-p2.eapx'))
try:
    before=S.snapshot(r,'ea_antes_retirar_masivas.json')
    current={int(x['Diagram_ID']):x for x in before['t_diagram']}
    assert all(i in current and current[i]['ea_guid']==x['ea_guid'] for i,x in original.items())
    retired=[x for i,x in current.items() if i not in original]
    # Todo identificador no original debe corresponder a un patrón de esta tarea.
    for d in retired:
        n=d['Name']
        assert (n.startswith(('Relación de clases — ','Relación Eloquent — ','Modelo conceptual — ','Despliegue — ')) or
                any(n.startswith(f'CU{i}. '+p) for i in range(1,9) for p in ('Clase ','Secuencia — ','Comunicación — ','Cálculo literal — ')) or
                ('Diagrama de Navegacion - ' in n and ' — ' in n)), (d['Diagram_ID'],n)
    S.dump('plan_retirada_masivas.json',{'originales':list(original.values()),'retirar':retired,
        'solo_diagramas':True,'eliminar_elementos':False,'eliminar_conectores':False})
    print('PLAN',len(original),'originales;',len(retired),'adicionales',flush=True)
    if '--aplicar' not in sys.argv:sys.exit(0)
    grouped=collections.defaultdict(set)
    for d in retired:grouped[int(d['Package_ID'])].add(int(d['Diagram_ID']))
    removed=[]
    for pid,ids in grouped.items():
        pkg=r.GetPackageByID(pid)
        for i in reversed(range(pkg.Diagrams.Count)):
            d=pkg.Diagrams.GetAt(i)
            if d.DiagramID not in ids:continue
            removed.append({'id':d.DiagramID,'guid':d.DiagramGUID,'name':d.Name})
            r.CloseDiagram(d.DiagramID)
            pkg.Diagrams.DeleteAt(i,False)
        pkg.Diagrams.Refresh()
        S.dump('retirada_masivas_progreso.json',removed)
    after=S.snapshot(r,'ea_despues_retirar_masivas.json')
    assert len(after['t_diagram'])==47
    assert {int(x['Diagram_ID']):x['ea_guid'] for x in after['t_diagram']}=={i:x['ea_guid'] for i,x in original.items()}
    protected=['t_object','t_attribute','t_operation','t_operationparams','t_connector']
    changes={}
    for table in protected:
        # Comparación de contenido completa; orden de SELECT no es contractual.
        canon=lambda rows:sorted(json.dumps(x,sort_keys=True,ensure_ascii=False) for x in rows)
        changes[table]=canon(before[table])!=canon(after[table])
    S.dump('retirada_masivas_resultado.json',{'retiradas':removed,'originales_conservados':47,'cambios_tablas_tecnicas':changes})
    assert not any(changes.values()),'Revisar cambios técnicos inesperados antes de seguir'
    print('RETIRADA SEGURA',len(removed),'vistas; 47 originales; elementos, atributos, métodos, parámetros y conectores sin cambios.',flush=True)
finally:
    r.CloseFile();r.Exit()
