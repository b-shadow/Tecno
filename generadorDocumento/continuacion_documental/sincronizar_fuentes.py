from pathlib import Path
import sys,ast,pprint
root=Path.cwd();sys.path.insert(0,str(root/'generadorDocumento'))
import contenido
p=root/'generadorDocumento/contenido.py';source=p.read_text(encoding='utf-8');tree=ast.parse(source)
assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DETALLE' for t in n.targets))
base={cu:{k:v[k] for k in ('gestionar','iniciador')} for cu,v in contenido.DETALLE.items()}
replacement='from actualizacion_contenido import aplicar_a_contenido\nDETALLE = aplicar_a_contenido('+pprint.pformat(base,sort_dicts=False,width=110)+')\n'
lines=source.splitlines(keepends=True);lines[assignment.lineno-1:assignment.end_lineno]=[replacement]
source=''.join(lines)
source=source.replace('o en cuotas, anulación controlada, comprobantes con validación manual y conciliación de Stripe por sesión ','o en cuotas, anulación controlada, revisión de comprobantes históricos y conciliación de Stripe por sesión ')
p.write_text(source,encoding='utf-8',newline='\n')
print('Fuentes CU sincronizadas; nombres, requisitos y actores sin sustitución.')
