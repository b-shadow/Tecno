"""Interacciones documentales nativas en el EAPX original mediante COM oficial.

Los participantes reutilizan clasificadores reales. Stripe/SMTP son objetos técnicos,
no actores. Los ocho diagramas originales conservan sus ID y GUID.
"""
from pathlib import Path
import sys,json,re,textwrap
from functools import cache
sys.path.insert(0,str(Path(__file__).resolve().parent))
import sincronizar_documentacion as S
from actualizacion_contenido import ESPECIFICACIONES
import win32com.client

# Cada lista corresponde a un recorrido; las condiciones son explícitas, no nuevos CU.
# Un paso (origen, destino, método, guarda) usa el nombre real del método destino.
FLOWS={
 'CU1':[
  ('Inicio de sesión válido','Administrador','PLogin.jsx','NAuth','login',[],
   'Credenciales inválidas o usuario inactivo: rechazar y registrar intento. Menú y rutas se autorizan con permisos persistidos; cerrar sesión revoca el token.'),
 ],
 'CU2':[
  ('Registro de interés público','Visitante','PCatalogo.jsx','NProspecto','registrarInteres',[],
   'Consultar catálogo y seleccionar módulos. Prospecto existente: reutilizar documento y actualizar los datos admitidos. Interés duplicado: rechazar sin duplicar tarjeta. Nuevo interés: fecha/hora y estado inicial reales.'),
 ],
 'CU3':[
  ('Distribución de prospectos','Coordinador','PAsignacion.jsx','NInteres','distribuir',[],
   'Vendedores activos/vigentes ordenados por correo. Carga abierta excluye Convertido y Perdido. Agrupar pendientes por documento; reutilizar vendedor elegible existente o elegir primera carga mínima e incrementarla por tarjeta asignada. No es una rotación circular estricta.'),
 ],
 'CU4':[
  ('Movimiento en Kanban','Vendedor','PEmbudo.jsx','NInteres','mover',[],
   'Comprobar alcance y transición. Una tarjeta Convertido no se mueve. Para destino Perdido exigir motivo válido. Para destino Convertido comprobar datos y primera cuota aprobada con NConversion; registrar estado e historial.'),
 ],
 'CU5':[
  ('Motivos y pérdida de prospectos','Administrador','PMotivos.jsx','NMotivo','store',[],
   'Administrar motivos no reemplaza perder una tarjeta: la pérdida efectiva usa NInteres::mover con estado Perdido y motivo obligatorio. Sin clasificar (web) está reservado; motivo utilizado no se elimina y su renombre conserva la relación mediante FK.'),
 ],
 'CU6':[
  ('Crear orden y plan de cuotas','Vendedor','FormularioOrdenPago.jsx','NPago','crearOrden',[],
   'Solo vendedor asignado; tarjeta abierta; bloqueo y una orden abierta por tarjeta. Precios del servidor, descuentos válidos y total positivo. Pago único o 2–12 cuotas; última cuota absorbe diferencia de redondeo. Tokens por cuota sin correo automático.'),
  ('Abrir enlace público y Checkout','Visitante','PPagoCuota.jsx','NPago','abrirEnlaceCuotaPublico',[],
   'Token de cuota válido; orden activa y cuota no pagada/en revisión. Resolver/reutilizar sesión abierta o crear nueva sesión de Stripe Sandbox. Token permanente de cuota y token de retorno son diferentes; sesión expirada puede renovarse sin duplicar cuota.'),
  ('Retorno público y conciliación','Visitante','PPagoConfirmacion.jsx','NPago','consultarRetornoPublico',[],
   'Autorizar token público, consultar Stripe y verificar moneda, importe y estado. El retorno no es prueba de pago por sí mismo. Confirmación idempotente con bloqueo; no duplicar cuota, inscripción o comisión.'),
  ('Webhook firmado e idempotente',None,'Stripe Sandbox','NPago','webhook',[],
   'Comprobar Stripe-Signature sobre cuerpo íntegro; firma inválida rechazada. Rechazar modo live. Evento ya procesado sin nuevo efecto. payment/Setup y expiración se distinguen; el webhook funciona aunque el navegador no retorne.'),
  ('Solicitar registro de tarjeta','Vendedor','MetodosPago.jsx','NPago','crearSetupTarjeta',[],
   'Sesión mode=setup. Compartir por acción manual. Stripe conserva tarjeta; UNEXO guarda proveedor, marca y últimos dígitos. Setup no paga cuota ni genera cobro o matrícula.'),
  ('Anular orden sin cobros','Vendedor','HistorialPagos.jsx','NPago','anularOrden',[],
   'Exigir motivo y alcance. Rechazar si hay pagos confirmados, cuotas pagadas/en revisión o transacciones no anulables. Expirar/revisar sesiones pendientes y conservar historial. No equivale a cancelar la pantalla de Stripe.'),
  ('Cancelación pública segura','Visitante','PPagoCancelado.jsx','NPago','cancelarRetornoPublico',[],
   'Autorizar token y consultar estado real. Si ya pagó se concilia; si no hay confirmación mantiene cuota pendiente. No anular automáticamente toda la orden.'),
  ('Correo comercial manual','Vendedor','ModalCompartirPago.jsx','NNotificacion','enviar',[],
   'Acción explícita y permiso/cartera. El enlace correcto se genera desde la cuota/sesión autorizada. Laravel envía vía SMTP configurado y registra enviada/fallida. Aceptación SMTP no prueba recepción. WhatsApp abre composición manual y copiar enlace no envía correo.'),
  ('Matrícula desde primera cuota',None,'NStripe','NConversion','procesar',[],
   'Siete datos obligatorios: documento, nombre, apellido, correo válido, teléfono, profesión y ubicación; vendedor asignado. Si faltan datos el pago se mantiene aprobado y conversión pendiente. Comisión = round(precio_acordado del ítem × porcentaje vigente / 100, 2). Cuotas restantes conservan saldo; liquidación al aprobar todas.'),
  ('Exportación académica','Coordinador','PMatriculas.jsx','NExportacion','exportar',[],
   'Consultar pendientes dentro del alcance; generar lote/archivo y registrar resultado mediante registrarResultado. Crear lote no acredita recepción remota SIS. Mantener historial.'),
 ],
 'CU7':[
  ('Agenda de seguimiento comercial','Vendedor','PAgenda.jsx','NSeguimiento','crearRecordatorio',[],
   'Fecha futura y descripción válidas; actividad vinculada a tarjeta y responsable. Estados Pendiente, Realizada, Atrasada, Cancelado. Las actividades comerciales no son correos automáticos de cuotas; notificado es histórico, no prueba de un scheduler.'),
 ],
 'CU8':[
  ('Dashboard e indicadores','Administrador','PDashboard.jsx','NReporte','dashboard',[],
   'Aplicar permisos y alcance por rol. Indicadores calculados sobre registros persistidos. Accesos/visitas no equivalen a personas únicas. Consultas con desde/hasta, vendedor, programa y estado cuando corresponde; tasas con denominador cero devuelven cero.'),
 ],
}

ORIGINALS={'CU1':(124,99),'CU2':(125,100),'CU3':(126,101),'CU4':(127,102),'CU5':(128,103),'CU6':(142,141),'CU7':(130,105),'CU8':(131,106)}

ADDITIONAL={
 'CU1':[
  ('Gestión de usuarios','Administrador','PUsuarios.jsx','NUsuario','store'),
  ('Matriz de acceso','Administrador','PMatriz.jsx','NSeguridad','asignar'),
  ('Consulta de bitácora','Administrador','PBitacora.jsx','NSeguridad','bitacora'),
  ('Cerrar sesión','Administrador','AppShell.jsx','NAuth','logout'),
 ],
 'CU2':[('Consultar oferta académica','Visitante','PCatalogo.jsx','NCatalogo','programas')],
 'CU3':[('Asignación manual','Coordinador','PAsignacion.jsx','NInteres','asignar')],
 'CU5':[('Registrar pérdida efectiva','Vendedor','PEmbudo.jsx','NInteres','mover')],
 'CU7':[
  ('Registrar contacto e interacción','Vendedor','PAgenda.jsx','NSeguimiento','registrarInteraccion'),
  ('Completar actividad','Vendedor','PMiDia.jsx','NSeguimiento','completarRecordatorio'),
  ('Cancelar actividad','Vendedor','PMiDia.jsx','NSeguimiento','cancelarRecordatorio'),
 ],
 'CU8':[
  ('Consultar estadísticas filtradas','Administrador','PReportes.jsx','NReporte','estadisticas'),
  ('Consultar comisiones','Coordinador','PComisiones.jsx','NSeguimiento','comisiones'),
 ],
}
for cu,items in ADDITIONAL.items():
    for title,actor,page,cl,method in items:
        FLOWS[cu].append((title,actor,page,cl,method,[],ESPECIFICACIONES[cu]['Postcondición']))

def complete_http_roots():
    functions=S.codigo.funciones_api();used=set().union(*S.codigo.usos_api().values());routes={r['clave']:r for r in S.codigo.rutas_api()}
    seen={cu:{(f[3],f[4]) for f in flows} for cu,flows in FLOWS.items()}
    for called in sorted(used):
        fn=functions.get(called)
        if not fn:continue
        route=routes.get((fn['verbo'],S.codigo.norm(fn['ruta'])))
        if not route:continue
        cu=S.route_cu(route)
        if not cu or (route['controlador'],route['metodo']) in seen[cu]:continue
        seen[cu].add((route['controlador'],route['metodo']))
        condition='Operación HTTP utilizada por la interfaz mediante '+called+'. '+('Recurso autorizado: '+', '.join(route['recursos'])+'. ' if route['recursos'] else '')+'Se conservan las validaciones y el alcance del código. Vista técnica complementaria del mismo CU; el emisor es el módulo cliente real.'
        FLOWS[cu].append(('HTTP '+fn['verbo']+' '+route['ruta'],None,'api/'+fn['modulo']+'.js',route['controlador'],route['metodo'],[],condition))

complete_http_roots()

def source_catalog():
    data=json.loads((S.OUT/'catalogo_fuente.json').read_text(encoding='utf-8'))
    allnodes={n:v for cat in data.values() for n,v in cat['nodes'].items()}
    for folder in (S.ROOT/'negocio/app',S.ROOT/'datos/src'):
        for p in folder.rglob('*.php'):
            item=S.php_class(p)
            if item:allnodes[item['name']]=item
    return allnodes

@cache
def guard_contexts(body):
    contexts=[];exits=[];switches=[];blocks=[];chains={}
    for bm in re.finditer(r'\{',body):
        try:_,end=S.balanced(body,bm.start(),'{','}');blocks.append((bm.start(),end))
        except ValueError:continue
    for cm in re.finditer(r'\b(if|elseif|foreach|for|while|switch|catch)\s*\(',body):
        try:
            condition,ce=S.balanced(body,cm.end()-1)
            bs=ce+len(body[ce:])-len(body[ce:].lstrip())
            if bs>=len(body) or body[bs]!='{':continue
            inside,be=S.balanced(body,bs,'{','}')
            if cm[1]=='switch':
                cases=list(re.finditer(r"\bcase\s+('[^']+'|\"[^\"]+\")\s*:|\bdefault\s*:",inside))
                for i,case in enumerate(cases):
                    end=bs+1+(cases[i+1].start() if i+1<len(cases) else len(inside))
                    label=condition.strip()+' = '+(case[1] or 'otro valor')
                    contexts.append((bs+1+case.end(),end,label,'case'))
                continue
            previous=[]
            for end,chain in sorted(chains.items(),reverse=True):
                if end>cm.start():continue
                tail=body[end:cm.start()]
                if cm[1]=='elseif' and re.fullmatch(r'\s*',tail):previous=chain;break
                if cm[1]=='if' and re.fullmatch(r'\s*else\s*',tail):previous=chain;break
            effective=' y '.join(['no ('+x+')' for x in previous]+['('+condition.strip()+')']) if previous else condition.strip()
            if cm[1]=='catch':effective='al capturar '+condition.strip()
            contexts.append((bs,be,effective,cm[1]))
            if cm[1] in ('if','elseif'):
                chain=previous+[condition.strip()];chains[be]=chain
                em=re.match(r'\s*else\s*\{',body[be:])
                if em:
                    eb=be+em.end()-1;_,ee=S.balanced(body,eb,'{','}')
                    contexts.append((eb,ee,' y '.join('no ('+x+')' for x in chain),'else'))
                # Un return/throw directo termina esta rama. No atribuir el
                # return de un callback interno a su función contenedora.
                plain='';p=0
                while p<len(inside):
                    if inside.startswith('//',p):
                        end=inside.find('\n',p);p=len(inside) if end<0 else end;continue
                    if inside.startswith('/*',p):
                        end=inside.find('*/',p+2);p=len(inside) if end<0 else end+2;continue
                    if inside[p] in "'\"":
                        quote=inside[p];p+=1
                        while p<len(inside):
                            if inside[p]=='\\':p+=2;continue
                            if inside[p]==quote:p+=1;break
                            p+=1
                        plain+=' ';continue
                    if inside[p]=='{':
                        _,end=S.balanced(inside,p,'{','}');p=end;plain+=' ';continue
                    plain+=inside[p];p+=1
                if re.search(r'\b(return|throw)\b',plain) and not re.search(r'\bif\s*\([^;{]*\)\s*(return|throw)\b',plain):
                    parents=[x for x in blocks if x[0]<bs and x[1]>be]
                    scope=min(parents,key=lambda x:x[1]-x[0]) if parents else (0,len(body))
                    exits.append((be,scope[1],effective))
        except ValueError:continue
    for mm in re.finditer(r'\bmatch\s*\(',body):
        try:
            selector,ce=S.balanced(body,mm.end()-1);bs=ce+len(body[ce:])-len(body[ce:].lstrip())
            if body[bs]!='{':continue
            inside,be=S.balanced(body,bs,'{','}');cursor=0;keys=[];previous=[]
            for arm in S.split_args(inside):
                start=inside.find(arm,cursor);cursor=start+len(arm)
                if '=>' not in arm:keys.append(arm);continue
                key,value=arm.split('=>',1);keys.append(key.strip())
                if keys==['default']:condition='no ('+' o '.join(previous)+')'
                else:
                    equalities=['('+selector.strip()+' === '+x+')' for x in keys]
                    current=' o '.join(equalities)
                    condition=('no ('+' o '.join(previous)+') y ' if previous else '')+'('+current+')'
                    previous.append('('+current+')')
                value_start=bs+1+start+arm.find('=>')+2
                contexts.append((value_start,bs+1+cursor,'rama match: '+condition,'match'));keys=[]
        except (ValueError,IndexError):continue
    return contexts,exits

def context_label(condition,kind):
    return ('por cada ' if kind=='foreach' else 'bucle for: ' if kind=='for' else 'bucle mientras: ' if kind=='while' else '')+' '.join(condition.split())

def joined_guards(values):
    return ' y '.join('('+x+')' for x in values) if len(values)>1 else next(iter(values),'')

def direct_calls(nodes,cl,method,with_guards=False,with_positions=False):
    item=nodes[cl];m=next(x for x in item['methods'] if x['name']==method)
    body=m.get('body','');props={a['name']:a['type'].lstrip('?').rsplit('\\',1)[-1] for a in item['attrs']}
    variables={p['name']:p['type'].lstrip('?').rsplit('\\',1)[-1] for p in m['params']}
    for variable,owner in re.findall(r'\$(\w+)\s*=\s*(\w+)::(?:query|table)\s*\(',body):variables[variable]=cl if owner in ('self','static') else owner
    for variable,called in re.findall(r'\$(\w+)\s*=\s*\$this->(\w+)\s*\(',body):
        called_method=next((x for x in item['methods'] if x['name']==called),None)
        if called_method and called_method['return'].lstrip('?').rsplit('\\',1)[-1]=='Builder':variables[variable]='DB'
    variables.update({v:c for v,c in re.findall(r'\$(\w+)\s*=\s*app\((\w+)::class\)',body)})
    out=[];occurrences=[];contexts,exits=guard_contexts(body)
    pattern=r'\$this->(\w+)->(\w+)\(|\$this->(\w+)\(|app\((\w+)::class\)->(\w+)\(|\$(\w+)->(\w+)\(|\b(self|static|parent|[A-Z]\w+)::(\w+)\('
    for match in re.finditer(pattern,body):
        a=match.groups();target=met=None
        if a[0]:target,met=props.get(a[0]),a[1]
        elif a[2]:target,met=cl,a[2]
        elif a[3]:target,met=a[3],a[4]
        elif a[5]:target,met=variables.get(a[5]),a[6]
        elif a[7]:target,met=(cl if a[7] in ('self','static') else item.get('extends') if a[7]=='parent' else a[7]),a[8]
        if target in nodes and any(x['name']==met for x in nodes[target]['methods']):
            pair=(target,met)
            guards=[context_label(cond,kind) for start,end,cond,kind in contexts if start<match.start()<end]
            guards+=['no ('+' '.join(cond.split())+')' for start,end,cond in exits if start<match.start()<end]
            value=(target,met,joined_guards(guards))
            _,end=S.balanced(body,body.find('(',match.start()))
            out.append(value);occurrences.append((*value,match.start(),end))
    if with_positions:return occurrences
    return out if with_guards else [x[:2] for x in out]

def specifications(repo):
    state=S.select(repo,'t_object');actors={x['Name']:int(x['Object_ID']) for x in state if x['Object_Type']=='Actor' and x['Package_ID']=='36'}
    cases={re.match(r'(CU\d)',x['Name'])[1]:x for x in state if x['Object_Type']=='UseCase' and x['Package_ID']=='36' and re.match(r'CU\d',x['Name'])}
    for cu,spec in ESPECIFICACIONES.items():
        e=repo.GetElementByID(int(cases[cu]['Object_ID'])); original=e.Name
        e.Notes='\n\n'.join(k+'\n'+('\n'.join(v) if isinstance(v,list) else str(v)) for k,v in spec.items());S.checked(e)
        assert e.Name==original
    e=repo.GetElementByID(int(cases['CU6']['Object_ID']))
    visitor=repo.GetElementByID(actors['Visitante'])
    if not any(c.SupplierID==e.ElementID and c.Type=='Association' for c in visitor.Connectors):
        c=visitor.Connectors.AddNew('','Association');c.SupplierID=e.ElementID;S.checked(c)
    S.dump('fase2_ea.json',{'cu':list(cases),'actores':actors,'actor_diagram_9_editado':False})

def signature(nodes,cl,method):
    m=next(x for x in nodes[cl]['methods'] if x['name']==method)
    return method+'('+', '.join(p['name']+(': '+p['type'] if p['type'] else '')+(' = '+p['default'] if p.get('default') else '') for p in m['params'])+')'+(': '+m['return'] if m['return'] else '')

@cache
def fluent_expression(body,start):
    """Cadena PHP literal con todos los argumentos, incluidos callbacks."""
    match=re.match(r'(?:\$\w+->|\w+::)\w+\s*\(',body[start:])
    assert match
    opening=start+match.end()-1;_,end=S.balanced(body,opening)
    while True:
        chain=re.match(r'\s*(?:\?->|->)\w+\s*\(',body[end:])
        if not chain:break
        opening=end+chain.end()-1;_,end=S.balanced(body,opening)
    return body[start:end],end

def persistence_calls(nodes,cl,method):
    item=nodes[cl]
    if not (cl.startswith('D') or '/Modelos/' in item['source']):return []
    m=next(x for x in item['methods'] if x['name']==method);body=m.get('body','')
    models={n for n,x in nodes.items() if '/Modelos/' in x['source']}
    variables={p['name']:p['type'].lstrip('?').rsplit('\\',1)[-1] for p in m['params']}
    for variable,owner in re.findall(r'\$(\w+)\s*=\s*(\w+)::(?:query|table)\s*\(',body):variables[variable]=cl if owner in ('self','static') else owner
    for variable,called in re.findall(r'\$(\w+)\s*=\s*\$this->(\w+)\s*\(',body):
        called_method=next((x for x in item['methods'] if x['name']==called),None)
        if called_method and called_method['return'].lstrip('?').rsplit('\\',1)[-1]=='Builder':variables[variable]='DB'
    out=[];contexts,exits=guard_contexts(body)
    for match in re.finditer(r'\b(self|static|[A-Z]\w*)::(query|table|select|statement|transaction|where\w*|find\w*|all|create|insert|firstOrCreate|updateOrCreate|destroy)\s*\(|\$(\w+)->(\w+)\s*\(',body):
        target=(cl if match[1] in ('self','static') else match[1]) if match[1] else variables.get(match[3])
        if target in models and any(x['name']==match[4] for x in nodes[target]['methods']):continue
        if target=='Builder':target='DB'
        if target not in models and target!='DB':continue
        literal,end=fluent_expression(body,match.start())
        guards=[context_label(cond,kind) for start,end,cond,kind in contexts if start<match.start()<end]
        guards+=['no ('+' '.join(cond.split())+')' for start,end,cond in exits if start<match.start()<end]
        out.append((end,target if target in models else 'Laravel DB / PostgreSQL','Operación de persistencia / biblioteca Eloquent:\n'+literal,joined_guards(guards)))
    return out

def flow_messages(nodes,flow):
    title,actor,page,cl,method,explicit,condition=flow
    messages=[]
    if actor:messages.append((actor,page,'Solicitar '+title.lower(),'','actor'))
    entry=signature(nodes,cl,method)
    if page.endswith(('.jsx','.js')) or page=='Stripe Sandbox':
        route=next((x for x in S.codigo.rutas_api() if x['controlador']==cl and x['metodo']==method),None)
        if route:
            entry=route['verbo']+' /api'+route['ruta']+'\n'+entry
            if route['recursos']:entry+='\nacceso: '+' | '.join(route['recursos'])
    messages.append((page,cl,entry,'','call'))
    if explicit:
        calls=explicit
    else:
        calls=[(cl,c,m,g) for c,m,g in direct_calls(nodes,cl,method,True)]
    body=next(x for x in nodes[cl]['methods'] if x['name']==method).get('body','')
    events=[]
    if explicit:
        events=[(i,a,b,signature(nodes,b,m),guard) for i,(a,b,m,guard) in enumerate(calls)]
    else:
        for c,m,guard,position,end in direct_calls(nodes,cl,method,True,True):
            label=signature(nodes,c,m)
            if c=='ReglaNegocioException' and m=='si':
                opening=body.find('(',position);args,_=S.balanced(body,opening)
                label='si('+args.strip()+')'
            events.append((end,cl,c,label,guard))
    contexts,exits=guard_contexts(body)
    def guard_at(position):
        guards=[context_label(cond,kind) for start,end,cond,kind in contexts if start<position<end]
        guards+=['no ('+' '.join(cond.split())+')' for start,end,cond in exits if start<position<end]
        return joined_guards(guards)
    if cl=='NStripe':
        for match in re.finditer(r'\$stripe->((?:\w+->)+(?:create|retrieve|expire))\s*\(',body):
            opening=body.find('(',match.start());args,end=S.balanced(body,opening)
            events.append((end,cl,'Stripe Sandbox',match[1].replace('->','.')+'('+args.strip()+')',guard_at(match.start())))
        for match in re.finditer(r'Webhook::constructEvent\(',body):
            args,end=S.balanced(body,match.end()-1)
            events.append((end,cl,'Stripe SDK local','Webhook::constructEvent('+args.strip()+')',guard_at(match.start())))
    if cl=='NNotificacion' and method=='enviarCorreo':
        for match in re.finditer(r'Mail::(html|raw)\(',body):
            events.append((match.start(),cl,'Gmail SMTP','SMTP solicitado por Mail::'+match[1]+'(contenido, destinatario y asunto validados)',guard_at(match.start())))
    for position,target,literal,guard in persistence_calls(nodes,cl,method):events.append((position,cl,target,literal,guard))
    for _,a,b,label,guard in sorted(events,key=lambda x:x[0]):messages.append((a,b,label,guard,'call'))
    messages.append((cl,page,'Respuesta validada / errores de la operación','','return'))
    if actor:messages.append((page,actor,'Mostrar resultado y conservar estado correspondiente','','return'))
    return messages

def interactions(repo,limit=None,only_mode=None,resume=False):
    nodes=source_catalog();state=S.select(repo,'t_object')
    byname={}
    for x in state:
        if x['Object_Type']=='Class':byname.setdefault(x['Name'],int(x['Object_ID']))
    actors={x['Name']:int(x['Object_ID']) for x in state if x['Object_Type']=='Actor' and x['Package_ID']=='36'}
    prior={};prior_traces={}
    if resume and (S.OUT/'exportaciones_interacciones.json').exists():
        prior={x['stem']:x for x in json.loads((S.OUT/'exportaciones_interacciones.json').read_text(encoding='utf-8'))}
        prior_traces={x['diagram_id']:x for x in json.loads((S.OUT/'trazas_interacciones.json').read_text(encoding='utf-8'))}
    registry=[];traces=[];changed=0
    association_ids={}
    ax=S.ET.fromstring(repo.SQLQuery("SELECT Connector_ID, Start_Object_ID, End_Object_ID FROM t_connector WHERE Connector_Type='Association'"))
    for row in ax.findall('.//Row'):
        values={c.tag:c.text for c in row};key=tuple(sorted((int(values['Start_Object_ID']),int(values['End_Object_ID']))))
        association_ids.setdefault(key,[]).append(int(values['Connector_ID']))
    revision=5
    for cu,baseflows in FLOWS.items():
        flows=list(baseflows);seen={(f[3],f[4]) for f in flows};todo=list(flows)
        # Desplegar los métodos propios de negocio que completan el recorrido:
        # cada vista retoma exactamente la llamada del participante anterior.
        while todo:
            f=todo.pop(0)
            for target,method in direct_calls(nodes,f[3],f[4]):
                if target not in nodes or (target,method) in seen:continue
                seen.add((target,method))
                if not direct_calls(nodes,target,method) and not persistence_calls(nodes,target,method):continue
                detail=(f[0].split(' — ')[0]+' — '+target+'::'+method,None,f[3],target,method,[],f[6])
                flows.append(detail);todo.append(detail)
        for mode,originalid in zip(('seq','com'),ORIGINALS[cu]):
            if only_mode and mode!=only_mode:continue
            original=repo.GetDiagramByID(originalid);pkg=repo.GetPackageByID(original.PackageID)
            participants={}
            diagrams_by_name={x.Name:x for x in pkg.Diagrams}
            objects_by_key={};notes_by_name={};fragments_by_alias={};association_links={}
            for element in pkg.Elements:
                kind=element.Type
                if kind=='Object':objects_by_key[element.Name,element.ClassifierID]=element
                elif kind=='Note':notes_by_name[element.Name]=element
                elif kind=='InteractionFragment':fragments_by_alias[element.Alias]=element
            def participant(name):
                if name in actors:return repo.GetElementByID(actors[name])
                if name in participants:return participants[name]
                classifier=byname.get(name)
                e=objects_by_key.get((name,classifier or 0))
                if e is None:
                    e=pkg.Elements.AddNew(name,'Object')
                    if classifier:e.ClassifierID=classifier
                    e.Notes=('Instancia del clasificador propio: '+nodes[name]['source'] if name in nodes else 'Biblioteca Stripe dentro del proceso PHP; la firma HMAC se valida localmente, sin petición HTTP.' if name=='Stripe SDK local' else 'Fachada DB / builder de Laravel y persistencia PostgreSQL; no es otro servidor de lógica de negocio.' if name=='Laravel DB / PostgreSQL' else 'Servicio técnico externo; no es actor UML.')
                    S.checked(e)
                    objects_by_key[name,classifier or 0]=e
                # Conservar nombres y clasificadores; evitar iconos de estereotipo
                # que ocultan el rótulo de los participantes en EA 15.
                e.StereotypeEx='';S.checked(e)
                participants[name]=e;return e
            for fi,flow in enumerate(flows):
                messages=flow_messages(nodes,flow)
                # Vistas nativas consecutivas: nunca rasterizar/recortar un diagrama externo.
                step=7 if mode=='seq' else 1
                chunks=[];chunk=[];chunk_names=set();note_budget=0
                for message in messages:
                    needed=set(message[:2])
                    full=message[2]+message[3]
                    needs_note=mode=='com' or len(full)>90 or '\n' in full
                    note_h=45+21*(1+sum(max(1,(len(line)*8+999)//1000) for line in full.splitlines())) if needs_note else 0
                    if chunk and (len(chunk)>=step or (mode=='seq' and (len(chunk_names|needed)>5 or 240+(len(chunk)+1)*35+note_budget+note_h>1050))):
                        chunks.append(chunk);chunk=[];chunk_names=set();note_budget=0
                    chunk.append(message);chunk_names|=needed;note_budget+=note_h+25 if note_h else 0
                if chunk:chunks.append(chunk)
                for ci,chunk in enumerate(chunks):
                    offset=sum(len(x) for x in chunks[:ci])
                    prefix='sd' if mode=='seq' else mode
                    stem=f'{prefix}-{cu.lower()}' if fi==0 and ci==0 else f'{prefix}-{cu.lower()}-flujo-{fi+1:02d}-{ci+1:02d}'
                    previous=prior.get(stem);trace=prior_traces.get(previous['id']) if previous else None
                    if previous and trace and trace.get('revision')==revision and trace['flow']==flow[0] and trace['messages']==[list(x) for x in chunk] and trace['condition']==flow[6]:
                        registry.append(previous);traces.append(trace);continue
                    if fi==0 and ci==0:d=original
                    else:
                        title=cu+'. '+('Secuencia' if mode=='seq' else 'Comunicación')+' — '+flow[0]+(f' — continuación {ci+1}' if ci else '')
                        d=diagrams_by_name.get(title)
                        if d is None:
                            d=pkg.Diagrams.AddNew(title,'Sequence' if mode=='seq' else 'Collaboration');S.checked(d);diagrams_by_name[title]=d
                    # Retirar solo representaciones de la vista que se sustituye.
                    # Los elementos del modelo no se eliminan y ningún actor se modifica.
                    for i in reversed(range(d.DiagramObjects.Count)):d.DiagramObjects.DeleteAt(i,False)
                    d.DiagramObjects.Refresh()
                    oldxml=S.ET.fromstring(repo.SQLQuery('SELECT Connector_ID, Connector_Type FROM t_connector WHERE DiagramID='+str(d.DiagramID)))
                    old=[{c.tag:c.text or '' for c in row} for row in oldxml.findall('.//Row')]
                    oldids=[int(x['Connector_ID']) for x in old if x['Connector_Type'] in ('Sequence','Collaboration')]
                    names=list(dict.fromkeys(n for a,b,*_ in chunk for n in (a,b)))
                    el={name:participant(name) for name in names}
                    d.Notes=cu+' — '+flow[0]+'\n'+flow[6]+'\n'+ESPECIFICACIONES[cu]['Descripción']+'\n\nMensajes de esta vista:\n'+'\n'.join(f'{offset+i}. {a} → {b}: {m} [{g}]' for i,(a,b,m,g,_) in enumerate(chunk,1))
                    d.ShowPublic=True;d.ShowPrivate=True;d.ShowProtected=True;S.checked(d)
                    d.HighlightImports=False;S.checked(d)
                    if mode=='seq':
                        for i,name in enumerate(names):S.put(d,el[name],40+i*220,35,200,120+len(chunk)*35)
                    else:
                        for i,name in enumerate(names):S.put(d,el[name],40+i*850,80,220,110)
                        d.ExtendedStyle=re.sub(r'SuppCN=\d;?','',d.ExtendedStyle or '')+';SuppCN=1;ShowIcons=0;';S.checked(d)
                    used=[];allowed_associations=set()
                    note_y=190+len(chunk)*35 if mode=='seq' else 235
                    for i,(a,b,msg,guard,kind) in enumerate(chunk,1):
                        number=offset+i
                        label=(f'{number}. ' if mode=='com' else '')+msg
                        if guard:label='['+guard+'] '+label
                        full_label=label
                        if mode=='com' or len(label)>90 or '\n' in label:
                            actual_method=re.search(r'(\w+)\s*\(',msg)
                            reference=actual_method[1] if actual_method else msg
                            label=f'{number}. {reference}'
                            note_name=f'Condición y firma — diagrama {d.DiagramID} — mensaje {number}'
                            note=notes_by_name.get(note_name)
                            if note is None:note=pkg.Elements.AddNew(note_name,'Note');S.checked(note);notes_by_name[note_name]=note
                            note.Notes=f'Mensaje {number} — firma, argumentos y condición íntegros\n'+full_label;S.checked(note)
                            note_width=1000
                            note_height=45+21*(1+sum(max(1,(len(line)*8+note_width-1)//note_width) for line in full_label.splitlines()))
                            S.put(d,note,40,note_y,note_width,note_height);note_y+=note_height+20
                        if mode=='com':label='\n'.join(textwrap.wrap(label,75,break_long_words=False,break_on_hyphens=False))
                        if i<=len(oldids):c=repo.GetConnectorByID(oldids[i-1]);c.ClientID=el[a].ElementID
                        else:c=el[a].Connectors.AddNew(label,'Sequence' if mode=='seq' else 'Collaboration')
                        c.Name=label;c.SupplierID=el[b].ElementID;c.DiagramID=d.DiagramID;c.SequenceNo=i;c.Direction='Source -> Destination';c.StateFlags=''
                        c.TransitionGuard='';c.Notes='Recorrido: '+flow[0]+'\n'+flow[6]+'\nMensaje y condición íntegros:\n'+full_label;S.checked(c);used.append(c.ConnectorID)
                        if mode=='seq':c.Properties.Item('IsReturn').Value=(kind=='return')
                        if mode=='com':
                            owner=el[a]
                            key=(el[a].ElementID,el[b].ElementID)
                            link=association_links.get(key)
                            pair=tuple(sorted(key))
                            if link is None and association_ids.get(pair):link=repo.GetConnectorByID(association_ids[pair][0])
                            if link is None:
                                link=owner.Connectors.AddNew('','Association');link.SupplierID=el[b].ElementID;S.checked(link)
                                association_ids.setdefault(pair,[]).append(link.ConnectorID)
                            association_links[key]=link
                            allowed_associations.add(link.ConnectorID)
                            # EA usa el extremo de la comunicación para asociar el mensaje
                            # al enlace. Se persiste con ConnectorEnd.Update, no con SQL.
                            end=c.ClientEnd;end.Aggregation=link.ConnectorID;S.checked(end)
                        elif guard:
                            title=f'Guarda {d.DiagramID} / mensaje {number}'
                            fr=fragments_by_alias.get(title)
                            if fr is None:fr=pkg.Elements.AddNew('','InteractionFragment');fr.Alias=title;S.checked(fr);fragments_by_alias[title]=fr
                            fr.Subtype=4 if 'por cada ' in guard or 'bucle ' in guard else 0 if '$evento->type =' in guard or 'al capturar ' in guard or 'rama match:' in guard else 1
                            fr.Notes='Condición real de la llamada: '+guard
                            for pi in reversed(range(fr.Partitions.Count)):fr.Partitions.DeleteAt(pi,False)
                            S.checked(fr)
                            frame=S.put(d,fr,20,103+(i-1)*35,220*len(names)+20,36);frame.Sequence=60;S.checked(frame)
                    if mode=='com':
                        visible_ids={e.ElementID for e in el.values()}
                        related={cid for a in visible_ids for b in visible_ids for cid in association_ids.get(tuple(sorted((a,b))),[])}
                        for cid in related:
                            dl=next((x for x in d.DiagramLinks if x.ConnectorID==cid),None)
                            if dl is None:dl=d.DiagramLinks.AddNew('','');dl.ConnectorID=cid
                            dl.IsHidden=cid not in allowed_associations;S.checked(dl)
                    for cid in oldids[len(chunk):]:
                        c=repo.GetConnectorByID(cid);owner=repo.GetElementByID(c.ClientID)
                        for i in reversed(range(owner.Connectors.Count)):
                            if owner.Connectors.GetAt(i).ConnectorID==cid:owner.Connectors.DeleteAt(i,False);break
                    repo.ReloadDiagram(d.DiagramID)
                    S.export(repo,d,stem,registry,'secuencia' if mode=='seq' else 'comunicacion',cu)
                    traces.append({'cu':cu,'mode':mode,'flow':flow[0],'diagram_id':d.DiagramID,'messages':chunk,'condition':flow[6],'revision':revision})
                    saved={**prior,**{x['stem']:x for x in registry}}
                    saved_traces={**prior_traces,**{x['diagram_id']:x for x in traces}}
                    S.dump('exportaciones_interacciones.json',list(saved.values()));S.dump('trazas_interacciones.json',list(saved_traces.values()))
                    changed+=1
                    if limit and changed>=limit:return
    S.dump('exportaciones_interacciones.json',registry);S.dump('trazas_interacciones.json',traces)
    print('INTERACCIONES_COMPLETAS',flush=True)

def presentation(repo):
    registry=json.loads((S.OUT/'exportaciones_interacciones.json').read_text(encoding='utf-8'))
    traces={x['diagram_id']:x for x in json.loads((S.OUT/'trazas_interacciones.json').read_text(encoding='utf-8'))}
    result=[];checked_messages=0
    classifiers={x['Name']:int(x['Object_ID']) for x in S.select(repo,'t_object') if x['Object_Type']=='Class'}
    for item in registry:
        trace=traces[item['id']];d=repo.GetDiagramByID(item['id'])
        notes=[]
        for obj in d.DiagramObjects:
            element=repo.GetElementByID(obj.ElementID)
            if element.Type=='Object' and element.Name in classifiers and element.ClassifierID!=classifiers[element.Name]:
                element.ClassifierID=classifiers[element.Name];S.checked(element)
            if trace['mode']=='seq' and element.Type in ('Actor','Object'):
                S.put(d,element,obj.left,-obj.top,obj.right-obj.left,120+len(trace['messages'])*35)
            elif element.Type=='Note':notes.append((obj,element))
        y=190+len(trace['messages'])*35 if trace['mode']=='seq' else 235
        for obj,element in sorted(notes,key=lambda x:-x[0].top):
            h=45+21*sum(max(1,(len(line)*8+999)//1000) for line in element.Notes.splitlines())
            S.put(d,element,40,y,1000,h);y+=h+20
        xml=S.ET.fromstring(repo.SQLQuery('SELECT Connector_ID, SeqNo FROM t_connector WHERE DiagramID='+str(d.DiagramID)+" AND Connector_Type IN ('Sequence','Collaboration') ORDER BY SeqNo"))
        rows=[{c.tag:c.text or '' for c in row} for row in xml.findall('.//Row')]
        assert len(rows)==len(trace['messages']),(item['stem'],'cantidad de mensajes inconsistente')
        for row,message in zip(rows,trace['messages']):
            c=repo.GetConnectorByID(int(row['Connector_ID']))
            c.Name=re.sub(r' \[nota \d+\]','',c.Name);c.StateFlags='';S.checked(c)
            if trace['mode']=='seq':
                c.Properties.Item('IsReturn').Value=(message[4]=='return')
                actual=repo.GetConnectorByID(c.ConnectorID).MiscData(3)
                assert actual==('1' if message[4]=='return' else '0'),(c.ConnectorID,'IsReturn no persistió por API',actual)
            checked_messages+=1
        S.export(repo,d,item['stem'],result,item['category'],item['cu'])
    S.dump('exportaciones_interacciones.json',result);S.dump('presentacion_interacciones.json',{'messages_checked':checked_messages,'return_api':'Connector.Properties.Item(IsReturn).Value','sql_writes':False})

def main():
    # Primera fase separada de las interacciones para facilitar reanudación.
    S.prepare_export_environment()
    r=win32com.client.Dispatch('EA.Repository');assert r.OpenFile(str(S.DOC/'ea/crm-p2.eapx'))
    try:
        if len(sys.argv)>1 and sys.argv[1]=='interacciones':interactions(r,int(sys.argv[2]) if len(sys.argv)>2 else None)
        elif len(sys.argv)>1 and sys.argv[1]=='reanudar':interactions(r,int(sys.argv[2]) if len(sys.argv)>2 else None,resume=True)
        elif len(sys.argv)>1 and sys.argv[1]=='test-com':interactions(r,1,'com')
        elif len(sys.argv)>1 and sys.argv[1]=='presentacion':presentation(r)
        else:specifications(r)
    finally:r.CloseFile();r.Exit()

if __name__=='__main__':main()
