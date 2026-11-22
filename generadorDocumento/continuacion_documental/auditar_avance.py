from pathlib import Path
import sys,json,datetime
ROOT=Path.cwd(); O=ROOT/'tmp/actualizacion_documental'
sys.path.insert(0,str(ROOT/'generadorDocumento/ea'))
import sincronizar_documentacion as S
snapshot=json.loads((O/'ea_despues_clases.json').read_text(encoding='utf-8'))
objects={int(x['Object_ID']):x for x in snapshot['t_object']}
done=json.loads((O/'exportaciones_relaciones_clases.json').read_text(encoding='utf-8'))
plan=[];seen=set(); completed_pairs=set(); by_cu={}
for cu in S.contenido.CU:
    d=next(x for x in snapshot['t_diagram'] if x['Diagram_Type']=='Logical' and x['Name']==cu+'. '+S.contenido.CU[cu])
    by_cu[cu]={objects[int(x['Object_ID'])]['Name']:int(x['Object_ID']) for x in snapshot['t_diagramobjects'] if x['Diagram_ID']==d['Diagram_ID'] and objects[int(x['Object_ID'])]['Object_Type']=='Class'}
for item in done:
    a,*targets=item['name'].split(' — ',1)[1].split(' / ')
    completed_pairs.update((by_cu[item['cu']][a],by_cu[item['cu']][b]) for b in targets)
for cu,cat in S.catalog().items():
    row=next(x for x in snapshot['t_diagram'] if x['Diagram_Type']=='Logical' and x['Name']==cu+'. '+S.contenido.CU[cu])
    elements={objects[int(x['Object_ID'])]['Name']:int(x['Object_ID']) for x in snapshot['t_diagramobjects'] if x['Diagram_ID']==row['Diagram_ID'] and objects[int(x['Object_ID'])]['Object_Type']=='Class'}
    edges=list(cat['edges'])
    for edge in edges:
        a,b=edge['a'],edge['b']; key=(elements[a],elements[b])
        if key in seen:continue
        group=[b]
        for other in edges:
            if other['a']!=a:continue
            target=other['b']
            if elements[target] in (elements[a],elements[b]) or (elements[a],elements[target]) in seen:continue
            if S.measure(cat['nodes'][a])[1]+max(S.measure(cat['nodes'][x])[1] for x in [b,target])+220<=1700:group.append(target)
            break
        seen.update((elements[a],elements[x]) for x in group)
        plan.append({'stem':f'clases-relacion-{len(plan)+1:03d}','cu':cu,'name':'Relación de clases — '+a+' / '+' / '.join(group)})
done=json.loads((O/'exportaciones_relaciones_clases.json').read_text(encoding='utf-8'))
# El catálogo tiene colecciones de origen sin orden estable entre procesos.
# Las aristas pendientes son exactas; no inventar el número de agrupaciones futuras.
pending=[]
for cu,cat in S.catalog().items():
    for edge in cat['edges']:
        key=(by_cu[cu][edge['a']],by_cu[cu][edge['b']])
        if key not in completed_pairs:
            if not any(tuple(x['element_ids'])==key for x in pending):pending.append({'cu':cu,**edge,'element_ids':key})
classes=json.loads((O/'exportaciones_clases_visibles.json').read_text(encoding='utf-8'))
report={'fecha':datetime.datetime.now().astimezone().isoformat(),'clases_terminadas':classes,'relaciones_terminadas':done,'aristas_pendientes':pending,'nota':'Las vistas futuras agrupan hasta dos aristas; su total se confirma al terminar el lote.'}
(O/'avance_exacto_diagramas.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['Avance nativo guardado: '+report['fecha'],'No equivale a validación visual final del documento.','',f'Clases terminadas: {len(classes)}',f'Vistas de relaciones terminadas: {len(done)}',f'Aristas de relaciones pendientes: {len(pending)}',report['nota'],'', 'CLASES TERMINADAS']
lines += [f"{x['cu']} | {x['stem']} | EA {x['id']} | {x['name']}" for x in classes]
lines += ['', 'RELACIONES TERMINADAS']+[f"{x['cu']} | {x['stem']} | EA {x['id']} | {x['name']}" for x in done]
lines += ['', 'ARISTAS PENDIENTES']+[f"{x['cu']} | {x['a']} -> {x['b']}" for x in pending]
(O/'avance_exacto_diagramas.txt').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'clases':len(classes),'relaciones_terminadas':len(done),'aristas_pendientes':len(pending),'ultima':{k:done[-1][k] for k in ('id','name','stem','cu')}},ensure_ascii=False))
