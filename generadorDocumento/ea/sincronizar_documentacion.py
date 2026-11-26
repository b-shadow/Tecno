"""Sincronización documental conservadora por la API oficial de EA.

No usa Execute, no escribe tablas internas y no recrea el proyecto ni sus diagramas.
El catálogo se contrasta con archivos propios; las consultas SQL a EA son solo SELECT.
"""
from pathlib import Path
import json,re,sys,struct,os,shutil,subprocess,xml.etree.ElementTree as ET
import win32com.client

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'generadorDocumento'; OUT=ROOT/'tmp/actualizacion_documental'
sys.path.insert(0,str(DOC))
import codigo,contenido,esquema

def prepare_export_environment():
    # Preferencia no sensible de presentación del usuario, fuera del EAPX.
    # EA 15 toma la fuente de rótulos de conectores al iniciar el proceso.
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Sparx Systems\EA400\EA\OPTIONS',0,winreg.KEY_READ|winreg.KEY_SET_VALUE) as key:
        value,kind=winreg.QueryValueEx(key,'FONTSIZE13')
        assert str(value) in ('8','12'),'No reemplazar una preferencia desconocida'
        evidence=OUT/'fuente_exportacion_ea.json'
        if not evidence.exists():dump('fuente_exportacion_ea.json',{'preference':'FONTSIZE13','before':value,'after':'12','scope':'user','model_tables_changed':False})
        winreg.SetValueEx(key,'FONTSIZE13',0,kind,'12' if isinstance(value,str) else 12)

def dump(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8')

def balanced(text,start,opening='(',closing=')'):
    level=0; quote=None; escape=False
    for i in range(start,len(text)):
        ch=text[i]
        if quote:
            if escape: escape=False
            elif ch=='\\': escape=True
            elif ch==quote: quote=None
            continue
        if ch in "'\"`": quote=ch;continue
        if ch==opening:level+=1
        elif ch==closing:
            level-=1
            if level==0:return text[start+1:i],i+1
    raise ValueError('Delimitador sin cierre')

def split_args(text):
    out=[]; start=0; depth=0; quote=None; escape=False
    for i,ch in enumerate(text):
        if quote:
            if escape:escape=False
            elif ch=='\\':escape=True
            elif ch==quote:quote=None
        elif ch in "'\"`":quote=ch
        elif ch in '([{':depth+=1
        elif ch in ')]}':depth-=1
        elif ch==',' and depth==0:out.append(text[start:i].strip());start=i+1
    if text[start:].strip():out.append(text[start:].strip())
    return out

def php_class(path):
    text=path.read_text(encoding='utf-8-sig')
    head=re.search(r'^(?:(?:final|abstract|readonly)\s+)*class\s+(\w+)([^\{]*)\{',text,re.M)
    if not head:return None
    name=head[1]; methods=[]; attrs=[]
    for m in re.finditer(r'\b(public|protected|private)\s+(static\s+)?function\s+(\w+)\s*\(',text):
        params,end=balanced(text,m.end()-1)
        after=text[end:]; ret=re.match(r'\s*:\s*([^\{;]+)',after)
        parsed=[]
        for arg in split_args(params):
            match=re.match(r'(?:(?:public|private|protected|readonly)\s+)*(.*?)\s*(&?\.\.\.)?\$(\w+)\s*(?:=\s*(.*))?$',arg,re.S)
            if not match:raise ValueError(f'Parámetro no reconocido {path}:{arg}')
            ptype=match[1].strip(); pn=match[3]; default=match[4]
            parsed.append({'name':pn,'type':ptype,'default':default,'raw':arg})
            promoted=re.match(r'(public|protected|private)\s+(readonly\s+)?',arg)
            if promoted:attrs.append({'name':pn,'type':ptype,'visibility':promoted[1].capitalize(),'default':None,'readonly':bool(promoted[2])})
        body_start=text.find('{',end)
        body,_=balanced(text,body_start,'{','}') if body_start>=0 else ('',end)
        methods.append({'name':m[3],'visibility':m[1].capitalize(),'static':bool(m[2]),'params':parsed,'return':ret[1].strip() if ret else '', 'body':body})
    # Atributos declarados fuera de los métodos; incluye las propiedades reales del modelo.
    without=text
    spans=[]
    for m in re.finditer(r'\b(?:public|protected|private)\s+(?:static\s+)?function\s+\w+\s*\(',text):
        _,end=balanced(text,m.end()-1); b=text.find('{',end)
        if b>=0:
            _,e=balanced(text,b,'{','}');spans.append((m.start(),e))
    for a,b in reversed(spans):without=without[:a]+' '*(b-a)+without[b:]
    for m in re.finditer(r'\b(public|protected|private)\s+(?:(static|readonly)\s+)?(?:(\??[\w\\|]+)\s+)?\$(\w+)\s*(?:=\s*([^;]+))?;',without):
        attrs.append({'name':m[4],'type':m[3] or '', 'visibility':m[1].capitalize(),'default':m[5].strip() if m[5] else None,'readonly':m[2]=='readonly','static':m[2]=='static'})
    for m in re.finditer(r'\b(public|protected|private)\s+const\s+(?:(\w+)\s+)?(\w+)\s*=\s*([^;]+);',without):
        attrs.append({'name':m[3],'type':m[2] or '', 'visibility':m[1].capitalize(),'default':m[4].strip(),'static':True,'constant':True})
    table=re.search(r"protected\s+\$table\s*=\s*'([^']+)'",text)
    if table:
        for col,typ,nn,default in esquema.tablas().get(table[1],[]):
            attrs.append({'name':col,'type':typ,'visibility':'Public','default':default or None,'persisted':True,'nullable':not nn})
    extends=re.search(r'extends\s+(\w+)',head[2])
    return {'name':name,'source':path.relative_to(ROOT).as_posix(),'kind':'php','methods':methods,'attrs':attrs,'extends':extends[1] if extends else None,'text':text}

def js_file(path,name=None):
    text=path.read_text(encoding='utf-8-sig'); methods=[]; names=set()
    patterns=[r'\b(?:async\s+)?function\s+(\w+)\s*\(',r'\b(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(']
    for pattern in patterns:
        for m in re.finditer(pattern,text):
            params,end=balanced(text,m.end()-1)
            if 'const' in m[0] and not re.match(r'\s*=>',text[end:]):continue
            if m[1] in names:continue
            names.add(m[1]); methods.append({'name':m[1],'visibility':'Public','static':False,'return':'','params':[{'name':p,'type':'','default':None} for p in split_args(params)]})
    return {'name':name or path.name,'source':path.relative_to(ROOT).as_posix(),'kind':'react' if path.suffix=='.jsx' else 'javascript','methods':methods,'attrs':[],'text':text}

EXTRA={
 'CU1':['NAuth','NUsuario','NSeguridad','NSitio','NFoto','TokenAuthMiddleware','AccesoRecurso','ApiRequest'],
 'CU2':['NCatalogo','NProspecto'],
 'CU3':['NInteres','NProspecto','DInteres','DProspecto'],
 'CU4':['NInteres','DInteres','NConversion','DConversion'],
 'CU5':['NMotivo','DMotivo','NInteres','DInteres','NAlcance','DAlcance','PEmbudo.jsx','api/intereses.js'],
 'CU6':['NPago','NStripe','NNotificacion','NConversion','NExportacion','DPago','DStripe','DNotificacion','DConversion','DExportacion'],
 'CU7':['NSeguimiento','NNotificacion','DSeguimiento','DNotificacion'],
 'CU8':['NReporte','DReporte'],
}

def route_cu(route):
    if route['cu'] in contenido.CU:return route['cu']
    return {'NPago':'CU6','NStripe':'CU6','NNotificacion':'CU7','NAuth':'CU1','NSitio':'CU1','NFoto':'CU1'}.get(route['controlador'])

def catalog():
    allphp={}
    for folder in (ROOT/'negocio/app',ROOT/'datos/src'):
        for path in folder.rglob('*.php'):
            item=php_class(path)
            if item:allphp[item['name']]=item
    cus={};functions=codigo.funciones_api();used=set().union(*codigo.usos_api().values());routes={r['clave']:r for r in codigo.rutas_api()}
    for cu in contenido.CU:
        chain,deps,errors=codigo.cadena(cu);assert not errors,errors
        nodes={}
        required=set(chain)|set(EXTRA[cu])
        for called in used:
            fn=functions.get(called)
            if not fn:continue
            route=routes.get((fn['verbo'],codigo.norm(fn['ruta'])))
            if route and route_cu(route)==cu:required.update((route['controlador'],'api/'+fn['modulo']+'.js'))
        todo=list(required)
        # Dependencias propias declaradas/importadas y modelos usados por la persistencia.
        while todo:
            name=todo.pop()
            if name not in allphp:continue
            item=allphp[name]
            referenced=set(re.findall(r'\b(?:use\s+Datos\\(?:Modelos\\)?|app\(|new\s+)(\w+)',item['text']))
            referenced|=set(re.findall(r'^\s*use\s+(?:App|Datos)\\(?:\w+\\)*(\w+)\s*;',item['text'],re.M))
            referenced|=set(re.findall(r'\b([A-Z]\w+)::',item['text']))
            referenced|={a['type'].lstrip('?').rsplit('\\',1)[-1] for a in item['attrs'] if a['type']}
            if item['extends']:referenced.add(item['extends'])
            for dep in referenced & allphp.keys():
                if dep not in required:required.add(dep);todo.append(dep)
        for name in sorted(required):
            if name in allphp:nodes[name]=allphp[name];continue
            found=next((p for p in (ROOT/'presentacion/src').rglob('*') if p.is_file() and (p.name==name or p.relative_to(ROOT/'presentacion/src').as_posix()==name)),None)
            if found:nodes[name]=js_file(found,name)
        if cu=='CU6':
            for path in (ROOT/'presentacion/src/componentes/pagos').glob('*.jsx'):nodes.setdefault(path.name,js_file(path))
            for rel in ('api/notificaciones.js','servicios/pagosCompartir.js','api/pagos.js'):
                path=ROOT/'presentacion/src'/rel;nodes.setdefault(rel,js_file(path,rel))
        edges=[]
        for (a,b),messages in deps.items():
            if a in nodes and b in nodes:edges.append({'a':a,'b':b,'type':'Dependency','messages':messages})
        for name,item in nodes.items():
            if item['source'].startswith('presentacion/'):
                relative=item['source'].removeprefix('presentacion/src/')
                for called in codigo.usos_api().get(relative,()):
                    module=called.split('.')[0];target='api/'+module+'.js'
                    if target in nodes and target!=name and not any(e['a']==name and e['b']==target for e in edges):edges.append({'a':name,'b':target,'type':'Dependency','messages':[called]})
                for called,fn in functions.items():
                    if name!='api/'+fn['modulo']+'.js':continue
                    route=routes.get((fn['verbo'],codigo.norm(fn['ruta'])))
                    if route and route['controlador'] in nodes and not any(e['a']==name and e['b']==route['controlador'] for e in edges):edges.append({'a':name,'b':route['controlador'],'type':'Dependency','messages':[fn['verbo']+' '+fn['ruta']]})
            for a in item['attrs']:
                target=a['type'].lstrip('?').rsplit('\\',1)[-1]
                if target in nodes:edges.append({'a':name,'b':target,'type':'Dependency','messages':['inyección declarada']})
            if item.get('extends') in nodes:edges.append({'a':name,'b':item['extends'],'type':'Generalization','messages':[]})
            for target in nodes:
                if target==name:continue
                if re.search(r'\b'+re.escape(target)+r'(?:::|\s*\$)',item['text']):
                    if not any(x['a']==name and x['b']==target for x in edges):edges.append({'a':name,'b':target,'type':'Dependency','messages':['referencia en fuente']})
        cus[cu]={'title':contenido.CU[cu],'nodes':nodes,'edges':edges}
    return cus

def select(repo,table):
    root=ET.fromstring(repo.SQLQuery('SELECT * FROM '+table))
    return [{c.tag:c.text or '' for c in row} for row in root.findall('.//Row')]

def snapshot(repo,name):
    data={t:select(repo,t) for t in ['t_package','t_object','t_attribute','t_operation','t_operationparams','t_connector','t_diagram','t_diagramobjects','t_diagramlinks']}
    dump(name,data);return data

def checked(obj):
    if not obj.Update():raise RuntimeError(obj.GetLastError())

def phase1(repo):
    state=snapshot(repo,'ea_antes_edicion.json')
    packages={int(x['Package_ID']):x for x in state['t_package']}
    diagram=next(x for x in state['t_diagram'] if x['Name']=='Diseño Conceptual de Base de Datos')
    pkgid=int(diagram['Package_ID'])
    elements={x['Name']:repo.GetElementByID(int(x['Object_ID'])) for x in state['t_object'] if int(x['Package_ID'])==pkgid and x['Object_Type']=='Class'}
    changes=[]
    for table,column in [('cuotas','token_pago'),('transacciones_stripe','token_publico'),('transacciones_stripe','expira_en')]:
        e=elements[table]
        existing=next((a for a in e.Attributes if a.Name==column),None)
        a=existing or e.Attributes.AddNew(column,'')
        # Convención conceptual original: nombres sin tipo; el tipo exacto se documenta en Notes.
        a.Name=column;a.Visibility='Public'
        meta=next(x for x in json.loads((OUT/'postgres_actual.json').read_text(encoding='utf-8'))['tipos'] if x['esquema']=='public' and x['tabla']==table and x['columna']==column)
        a.Notes=f"Columna real {table}.{column}; {meta['tipo']}; admite NULL; sin valor predeterminado. " + ('Identificador público único para el enlace; UNIQUE permite varios NULL en PostgreSQL.' if column.startswith('token') else 'Expiración de la sesión pública de Stripe; no es un vencimiento comercial de cuota.')
        a.Pos=len(list(e.Attributes)) if not existing else a.Pos;checked(a);checked(e)
        changes.append({'table':table,'column':column,'element_id':e.ElementID,'attribute_guid':a.AttributeGUID})
    repo.ReloadDiagram(int(diagram['Diagram_ID']))
    dump('cambios_fase1_ea.json',changes)
    print('Modelo conceptual: tres atributos incorporados mediante API, sin cambiar relaciones.',flush=True)

def update_members(element,item):
    original_notes=element.Notes or ''
    marker='\n[Fuente documental verificada]'
    element.Notes=original_notes.split(marker)[0]+marker+'\n'+item['source']+'\n'+('Componente funcional React; no representa una clase PHP.' if item['kind']=='react' else 'Módulo JavaScript; tipos no declarados se mantienen sin tipo UML.' if item['kind']=='javascript' else 'Firmas, visibilidad, propiedades y valores predeterminados tomados del código. Los atributos persistidos representan columnas mapeadas de PostgreSQL, no propiedades PHP declaradas.')
    existing={m.Name:m for m in element.Methods}
    wanted={m['name'] for m in item['methods']}
    for i in reversed(range(element.Methods.Count)):
        if element.Methods.GetAt(i).Name not in wanted:element.Methods.DeleteAt(i,False)
    element.Methods.Refresh()
    existing={element.Methods.GetAt(i).Name:element.Methods.GetAt(i) for i in range(element.Methods.Count)}
    for pos,data in enumerate(item['methods']):
        method=existing.get(data['name']) or element.Methods.AddNew(data['name'],data['return'])
        method.Name=data['name'];method.ReturnType=data['return'];method.Visibility=data['visibility'];method.IsStatic=data['static'];method.Pos=pos
        checked(method)
        ps={p.Name:p for p in method.Parameters}
        # JScript usa patrones destructurados, no identificadores PHP. EA 15 no
        # escapa apóstrofos dentro del nombre al actualizar un parámetro.
        # La notación UML usa comillas dobles equivalentes y conserva el original en Notes.
        api_name=lambda p:p['name'].replace("'",'"') if item['kind']!='php' else p['name']
        wanted_params={api_name(p) for p in data['params']}
        for i in reversed(range(method.Parameters.Count)):
            if method.Parameters.GetAt(i).Name not in wanted_params:method.Parameters.DeleteAt(i,False)
        method.Parameters.Refresh()
        ps={method.Parameters.GetAt(i).Name:method.Parameters.GetAt(i) for i in range(method.Parameters.Count)}
        for j,data_p in enumerate(data['params']):
            pname=api_name(data_p)
            p=ps.get(pname) or method.Parameters.AddNew(pname,data_p['type'])
            p.Name=pname;p.Type=data_p['type'];p.Position=j;p.Default=data_p['default'] or ''
            if pname!=data_p['name']:p.Notes='Sintaxis original de JavaScript: '+data_p['name']
            try:checked(p)
            except Exception as exc:raise RuntimeError(f"Parámetro EA: {item['name']}.{data['name']} {data_p!r}") from exc
        checked(method)
    existing={a.Name:a for a in element.Attributes};wanted={a['name'] for a in item['attrs']}
    for i in reversed(range(element.Attributes.Count)):
        if element.Attributes.GetAt(i).Name not in wanted:element.Attributes.DeleteAt(i,False)
    element.Attributes.Refresh()
    existing={element.Attributes.GetAt(i).Name:element.Attributes.GetAt(i) for i in range(element.Attributes.Count)}
    for pos,data in enumerate(item['attrs']):
        a=existing.get(data['name']) or element.Attributes.AddNew(data['name'],data['type'])
        a.Name=data['name'];a.Type=data['type'];a.Visibility=data['visibility'];a.Pos=pos;a.Default=data['default'] or '';a.IsStatic=data.get('static',False)
        a.Notes=('Columna persistida mapeada; ' + ('NULL permitido' if data['nullable'] else 'NOT NULL')) if data.get('persisted') else ('Constante PHP declarada en fuente.' if data.get('constant') else 'Propiedad readonly declarada en PHP.' if data.get('readonly') else 'Propiedad declarada en fuente.')
        a.IsConst=bool(data.get('constant') or data.get('readonly'))
        checked(a)
    checked(element)

def measure(item,max_width=900):
    lines=[item['name']]
    lines += [f"{a['name']}: {a['type']}"+(f" = {a['default']}" if a.get('default') else '')+(' {readOnly}' if a.get('constant') or a.get('readonly') else '') for a in item['attrs']]
    lines += [m['name']+'('+', '.join(p['name']+(': '+p['type'] if p['type'] else '')+(' = '+p['default'] if p.get('default') else '') for p in m['params'])+')'+(': '+m['return'] if m['return'] else '') for m in item['methods']]
    width=min(max_width,max(230,max(map(len,lines))*8+42))
    height=max(90,65+21*sum(max(1,(len(line)*8+width-43)//(width-42)) for line in lines[1:]))
    return width,height

def put(diagram,element,x,y,w,h,font=12):
    obj=next((o for o in diagram.DiagramObjects if o.ElementID==element.ElementID),None)
    if obj is None:
        obj=diagram.DiagramObjects.AddNew(f'l={x};r={x+w};t={y};b={y+h};','');obj.ElementID=element.ElementID
    obj.left=int(x);obj.right=int(x+w);obj.top=-int(y);obj.bottom=-int(y+h)
    obj.SetStyleEx('font','Calibri');obj.SetStyleEx('fontsz',str(font*10))
    try:obj.ElementDisplayMode=2
    except AttributeError:pass
    # Las propiedades oficiales eliminan las marcas de supresión de EA 15.
    # No interpretar los tokens internos AttPub/OpPub como booleanos de mostrar.
    for name in ['ShowPublicOperations','ShowPrivateOperations','ShowProtectedOperations','ShowPackageOperations',
                 'ShowPublicAttributes','ShowPrivateAttributes','ShowProtectedAttributes','ShowPackageAttributes']:
        setattr(obj,name,True)
    obj.SetStyleEx('AttCustom','0');obj.SetStyleEx('OpCustom','0')
    checked(obj);return obj

def defaults_note(repo,diagram,element,item):
    lines=[]
    for a in item['attrs']:
        declaration=a['visibility'].lower()+' '+('const ' if a.get('constant') else 'readonly ' if a.get('readonly') else '')+a['name']+(': '+a['type'] if a['type'] else '')
        if a.get('default') is not None:lines.append(declaration+' = '+a['default'])
        elif a.get('readonly'):lines.append(declaration)
    for m in item['methods']:
        values=[p['name']+' = '+p['default'] for p in m['params'] if p.get('default') is not None]
        if values:lines.append(m['name']+'(): '+', '.join(values))
        if item['kind']!='php':
            for parameter in m['params']:
                if "'" in parameter['name']:lines.append('Parámetro JavaScript original de '+m['name']+'(): '+parameter['name'])
    if not lines:return
    pkg=repo.GetPackageByID(diagram.PackageID)
    name='Predeterminados de '+element.Name
    note=next((e for e in pkg.Elements if e.Type=='Note' and e.Name==name),None)
    if note is None:note=pkg.Elements.AddNew(name,'Note');checked(note)
    note.Notes='Declaraciones de propiedades y valores predeterminados de fuente\n'+'\n'.join(lines)
    checked(note)
    obj=next(o for o in diagram.DiagramObjects if o.ElementID==element.ElementID)
    width=obj.right-obj.left
    height=55+23*sum(max(1,(len(line)*8+width-35)//(width-35)) for value in ['Declaraciones de propiedades y valores predeterminados de fuente']+lines for line in value.splitlines())
    if -obj.bottom+height+70>1650:
        put(diagram,note,obj.right+80,40,max(700,width),height)
    else:put(diagram,note,obj.left,-obj.bottom+35,width,height)
    if not any(c.Type=='NoteLink' and c.SupplierID==element.ElementID for c in note.Connectors):
        c=note.Connectors.AddNew('','NoteLink');c.SupplierID=element.ElementID;checked(c)

def export(repo,diagram,stem,registry,category,cu=None):
    target=DOC/'diagramas';target.mkdir(exist_ok=True)
    checked(diagram);repo.ReloadDiagram(diagram.DiagramID)
    pi=repo.GetProjectInterface()
    emf=target/(stem+'.emf');png=target/(stem+'.png')
    # EA 15 puede emitir EMF sin transformación de viewport: Word recorta todo
    # salvo el encabezado. No publicar esos archivos como figuras utilizables.
    rawdir=OUT/'emf_nativos';rawdir.mkdir(exist_ok=True)
    raw=rawdir/(stem+'.emf')
    assert pi.PutDiagramImageToFile(diagram.DiagramGUID,str(raw),0),'No exportó '+stem
    bounds=struct.unpack_from('<4i',raw.read_bytes(),8)
    emf_ok=bounds[0]>=-1 and bounds[1]>=-1
    normalized=not emf_ok
    if emf_ok:emf.write_bytes(raw.read_bytes())
    else:
        node=os.environ.get('CODEX_DOCUMENT_NODE') or shutil.which('node')
        assert node,'Se requiere Node para explicitar el viewport del EMF nativo'
        subprocess.run([node,str(Path(__file__).with_name('compatibilidad_emf.mjs')),str(raw),str(emf)],check=True)
        emf_ok=True
    positions=list(diagram.DiagramObjects)
    width=max([o.right for o in positions] or [0])-min([o.left for o in positions] or [0])
    height=max([-o.bottom for o in positions] or [0])-min([-o.top for o in positions] or [0])
    # Las vistas extensas conservan EMF completo; evitar un bitmap desmesurado en EA de 32 bits.
    png_ok=False
    if width*height<10000000:png_ok=bool(pi.PutDiagramImageToFile(diagram.DiagramGUID,str(png),1))
    if not png_ok and png.exists() and category.endswith('-general'):
        retired=OUT/'exportaciones_retiradas';retired.mkdir(exist_ok=True);png.replace(retired/png.name)
    if not category.endswith('-general'):assert png_ok,'No exportó el PNG nativo '+stem
    registry.append({'id':diagram.DiagramID,'guid':diagram.DiagramGUID,'name':diagram.Name,'stem':stem,'category':category,'cu':cu,'width':width,'height':height,'png':png_ok,'emf':emf_ok,'viewport_emf_normalizado':normalized,'primitivas_emf_preservadas':True,'resolucion_png_ea_porcentaje':400})
    print('Exportado',stem,diagram.DiagramID,flush=True)
    repo.CloseDiagram(diagram.DiagramID)

def phase3(repo,sync_members=True):
    state=snapshot(repo,'ea_antes_clases.json');data=catalog()
    class_diagrams={cu:next(x for x in state['t_diagram'] if x['Diagram_Type']=='Logical' and x['Name']==cu+'. '+contenido.CU[cu]) for cu in contenido.CU}
    all_elements={int(x['Object_ID']):x for x in state['t_object']}
    class_by_name={}
    for x in state['t_object']:
        if x['Object_Type']=='Class':class_by_name.setdefault(x['Name'],[]).append(int(x['Object_ID']))
    updated=set();registry=[];changes=[]
    for cu,cat in data.items():
        d=repo.GetDiagramByID(int(class_diagrams[cu]['Diagram_ID']));pkg=repo.GetPackageByID(d.PackageID)
        present={all_elements.get(o.ElementID,{}).get('Name'):o.ElementID for o in d.DiagramObjects if all_elements.get(o.ElementID,{}).get('Object_Type')=='Class'}
        elements={}
        for name,item in cat['nodes'].items():
            eid=present.get(name) or next(iter(class_by_name.get(name,[])),None)
            if eid:element=repo.GetElementByID(eid)
            else:
                layer_name='Presentación' if item['source'].startswith('presentacion/') else 'Negocio' if item['source'].startswith('negocio/') else 'Datos'
                owner=next((p for p in pkg.Packages if p.Name==layer_name),pkg)
                element=owner.Elements.AddNew(name,'Class');element.Stereotype='client page' if item['kind']=='react' else 'module' if item['kind']=='javascript' else 'negocio' if item['source'].startswith('negocio/') else 'datos';checked(element)
                class_by_name.setdefault(name,[]).append(element.ElementID)
            if element.ElementID not in updated:
                if sync_members or element.ElementID not in all_elements:
                    print('Sincronizando',cu,name,flush=True);update_members(element,item)
                updated.add(element.ElementID)
            elements[name]=element
        # Reutiliza elementos existentes entre vistas. No crea una copia de clase para cada vista.
        d.Notes=(d.Notes or '')+'\nCatálogo íntegro de miembros en las vistas complementarias; todos los elementos son los mismos del modelo original. Fuente: '+str(ROOT.name)
        style=d.ExtendedStyle or '';d.ExtendedStyle=style+';OpParams=2;';checked(d)
        col_width=[0,0,0];rows=[]
        grouped={0:[],1:[],2:[]}
        for name,item in cat['nodes'].items():
            layer=0 if item['source'].startswith('presentacion/') else 1 if item['source'].startswith('negocio/') else 2
            w,h=measure(item);col_width[layer]=max(col_width[layer],w);grouped[layer].append((name,w,h))
        x=40
        for layer in range(3):
            y=50
            for name,w,h in grouped[layer]:put(d,elements[name],x,y,w,h);y+=h+75
            x+=col_width[layer]+160
        for edge in cat['edges']:
            a,b=elements[edge['a']],elements[edge['b']]
            existing=next((c for c in a.Connectors if c.SupplierID==b.ElementID and c.Type==edge['type']),None)
            if existing is None:
                c=a.Connectors.AddNew('',edge['type']);c.SupplierID=b.ElementID;c.Direction='Source -> Destination';checked(c)
            else:c=existing
            c.Name='';c.Notes='Fuente: '+cat['nodes'][edge['a']]['source']+'\nOperaciones y referencias íntegras:\n'+'\n'.join(edge['messages']);checked(c)
        export(repo,d,f'cls-{cu.lower()}',registry,'clases-general',cu)
        for i,(name,item) in enumerate(cat['nodes'].items(),1):
            title=f'{cu}. Clase {name} — miembros completos'
            detail=next((dg for dg in pkg.Diagrams if dg.Name==title),None)
            if detail is None:detail=pkg.Diagrams.AddNew(title,'Logical');checked(detail)
            detail.Notes='Vista complementaria del mismo CU, sin nuevo caso de uso. '+item['source']+'\nMétodos propios completos, constructor y parámetros con sus valores predeterminados. Los tipos no declarados en JavaScript/PHP no se inventan.'
            detail.ExtendedStyle=(detail.ExtendedStyle or '')+';OpParams=2;';checked(detail)
            w,h=measure(item);put(detail,elements[name],40,40,w,h)
            export(repo,detail,f'cls-{cu.lower()}-detalle-{i:02d}',registry,'clases-detalle',cu)
        changes.append({'cu':cu,'diagram_id':d.DiagramID,'classes':len(elements),'methods':sum(len(n['methods']) for n in cat['nodes'].values()),'attrs':sum(len(n['attrs']) for n in cat['nodes'].values())})
        dump('exportaciones_clases.json',registry);dump('cambios_clases.json',changes)
    snapshot(repo,'ea_despues_clases.json')

def relation_views(repo):
    data=catalog();state=select(repo,'t_diagram');registry=[];seen={};coverage=[]
    for cu,cat in data.items():
        row=next(x for x in state if x['Diagram_Type']=='Logical' and x['Name']==cu+'. '+contenido.CU[cu])
        d=repo.GetDiagramByID(int(row['Diagram_ID']));pkg=repo.GetPackageByID(d.PackageID)
        elements={}
        for i in range(d.DiagramObjects.Count):
            o=d.DiagramObjects.GetAt(i);e=repo.GetElementByID(o.ElementID)
            if e.Type=='Class':elements[e.Name]=e
        edges=list(cat['edges'])
        for edge in edges:
            a,b=elements[edge['a']],elements[edge['b']];key=(a.ElementID,b.ElementID)
            if key in seen:
                coverage.append({'cu':cu,'edge':edge,'diagram_id':seen[key]});continue
            group=[b]
            for other in edges:
                if other['a']!=a.Name:continue
                target=elements[other['b']]
                if target.ElementID==a.ElementID or target.ElementID==b.ElementID or (a.ElementID,target.ElementID) in seen:continue
                h_a=measure(cat['nodes'][a.Name])[1]
                h_b=max(measure(cat['nodes'][x.Name])[1] for x in [b,target])
                if h_a+h_b+220<=1700:group.append(target)
                break
            title='Relación de clases — '+a.Name+' / '+' / '.join(x.Name for x in group)
            detail=next((x for x in pkg.Diagrams if x.Name==title),None)
            if detail is None:detail=pkg.Diagrams.AddNew(title,'Logical');checked(detail)
            detail.ShowPublic=True;detail.ShowPrivate=True;detail.ShowProtected=True;detail.HighlightImports=False
            detail.ExtendedStyle=re.sub(r'OpParams=\d;?','',detail.ExtendedStyle or '')+';OpParams=2;'
            detail.Notes='Vista complementaria legible: mismos elementos, miembros y relaciones originales del CU. No se eliminan atributos ni métodos.\n'+'\n'.join(cat['nodes'][e.Name]['source'] for e in [a]+group)
            checked(detail)
            aw,ah=measure(cat['nodes'][a.Name]);put(detail,a,40 if len(group)==1 else 520,40,aw,ah)
            for i,e in enumerate(group):
                w,h=measure(cat['nodes'][e.Name])
                put(detail,e,1000 if len(group)==1 else 40+i*960,40 if len(group)==1 else ah+180,w,h)
                seen[(a.ElementID,e.ElementID)]=detail.DiagramID
            export(repo,detail,f'clases-relacion-{len(registry)+1:03d}',registry,'clases-relacion',cu)
            coverage.append({'cu':cu,'edge':edge,'diagram_id':detail.DiagramID})
            dump('exportaciones_relaciones_clases.json',registry);dump('cobertura_relaciones_clases.json',coverage)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if sys.argv[1]=='catalogo':
        data=catalog();dump('catalogo_fuente.json',data)
        print({cu:(len(x['nodes']),sum(len(n['methods']) for n in x['nodes'].values())) for cu,x in data.items()});return
    prepare_export_environment()
    repo=win32com.client.Dispatch('EA.Repository')
    assert repo.OpenFile(str(DOC/'ea/crm-p2.eapx'))
    try:
        if sys.argv[1]=='fase1':phase1(repo)
        elif sys.argv[1]=='clases':phase3(repo)
        elif sys.argv[1]=='integrar-clases':phase3(repo,False)
        elif sys.argv[1]=='organizar-clases':
            original=json.loads((OUT/'ea_antes_edicion.json').read_text(encoding='utf-8'));oldids={int(e['Object_ID']) for e in original['t_object']}
            roots={int(d['Package_ID']) for d in original['t_diagram'] if d['Diagram_ID'] in ('1','2','3','4','5','138','7','8')}
            nodes={n:v for c in catalog().values() for n,v in c['nodes'].items()};changes=[]
            for row in select(repo,'t_object'):
                if row['Object_Type']!='Class' or int(row['Object_ID']) in oldids or row['Name'] not in nodes or int(row['Package_ID']) not in roots:continue
                item=nodes[row['Name']];layer='Presentación' if item['source'].startswith('presentacion/') else 'Negocio' if item['source'].startswith('negocio/') else 'Datos'
                package=repo.GetPackageByID(int(row['Package_ID']));owner=next(p for p in package.Packages if p.Name==layer)
                element=repo.GetElementByID(int(row['Object_ID']));element.PackageID=owner.PackageID;checked(element)
                changes.append({'id':element.ElementID,'guid':element.ElementGUID,'from':package.PackageID,'to':owner.PackageID,'layer':layer})
            dump('organizacion_clases_nuevas.json',changes)
        elif sys.argv[1]=='relaciones-clases':relation_views(repo)
        elif sys.argv[1]=='exportar-relaciones':
            registry=[]
            for item in json.loads((OUT/'exportaciones_relaciones_clases.json').read_text(encoding='utf-8')):
                export(repo,repo.GetDiagramByID(item['id']),item['stem'],registry,item['category'],item['cu'])
            dump('exportaciones_relaciones_clases.json',registry)
        elif sys.argv[1]=='capas':
            cat=catalog()
            for cu,did in {'CU1':1,'CU2':2,'CU3':3,'CU4':4,'CU5':5,'CU6':138,'CU7':7,'CU8':8}.items():
                d=repo.GetDiagramByID(did);groups={'Presentación':[],'Negocio':[],'Datos':[]};bounds={}
                for o in d.DiagramObjects:
                    e=repo.GetElementByID(o.ElementID)
                    if e.Type=='Boundary':bounds[e.Name]=o;continue
                    item=cat[cu]['nodes'].get(e.Name)
                    if item:
                        layer='Presentación' if item['source'].startswith('presentacion/') else 'Negocio' if item['source'].startswith('negocio/') else 'Datos'
                        groups[layer].append(o)
                for layer,objects in groups.items():
                    boundary=bounds.get('Capa '+layer)
                    if boundary is None or not objects:continue
                    boundary.left=min(x.left for x in objects)-25;boundary.right=max(x.right for x in objects)+25
                    boundary.top=max(x.top for x in objects)+45;boundary.bottom=min(x.bottom for x in objects)-30
                    boundary.Sequence=100;checked(boundary)
                checked(d)
        elif sys.argv[1] in ('presentacion-clases','defaults-clases'):
            registry=[];cat=catalog()
            originals=json.loads((OUT/'exportaciones_clases.json').read_text(encoding='utf-8'))
            prior={x['stem']:x for x in json.loads((OUT/'exportaciones_clases_visibles.json').read_text(encoding='utf-8'))} if (OUT/'exportaciones_clases_visibles.json').exists() else {}
            for item in originals:
                if sys.argv[1]=='defaults-clases':
                    if item['category']!='clases-detalle' or not any(a.get('default') is not None or a.get('readonly') for a in cat[item['cu']]['nodes'][item['name'].split('Clase ',1)[1].split(' — miembros completos')[0]]['attrs']):
                        registry.append(prior.get(item['stem'],item));continue
                d=repo.GetDiagramByID(item['id'])
                d.ShowPublic=True;d.ShowPrivate=True;d.ShowProtected=True;checked(d)
                d.HighlightImports=False;checked(d)
                for i in range(d.DiagramObjects.Count):
                    o=d.DiagramObjects.GetAt(i);e=repo.GetElementByID(o.ElementID)
                    if e.Type=='Class':
                        data=cat[item['cu']]['nodes'].get(e.Name)
                        if data:
                            declarations={x['name']:x for x in data['attrs']}
                            for attribute in e.Attributes:
                                source=declarations[attribute.Name];attribute.IsConst=bool(source.get('constant') or source.get('readonly'));checked(attribute)
                        if item['category']=='clases-detalle' and e.Name in cat[item['cu']]['nodes']:
                            w,h=measure(cat[item['cu']]['nodes'][e.Name]);put(d,e,o.left,-o.top,w,h)
                        else:put(d,e,o.left,-o.top,o.right-o.left,o.top-o.bottom)
                if item['category']=='clases-detalle':
                    for i in range(d.DiagramObjects.Count):
                        o=d.DiagramObjects.GetAt(i);e=repo.GetElementByID(o.ElementID)
                        if e.Type=='Class' and e.Name in cat[item['cu']]['nodes']:
                            defaults_note(repo,d,e,cat[item['cu']]['nodes'][e.Name]);break
                export(repo,d,item['stem'],registry,item['category'],item['cu'])
                dump('exportaciones_clases_visibles.json',registry)
        elif sys.argv[1]=='snapshot':snapshot(repo,'ea_actual.json')
        else:raise ValueError(sys.argv[1])
    finally:repo.CloseFile();repo.Exit()

if __name__=='__main__':main()
