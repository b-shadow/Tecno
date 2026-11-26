"""Inserción puntual de vistas nativas EA; no regenera el documento maestro.

Mantiene el capítulo IV y sustituye solo las secciones gráficas autorizadas.
La escala se fija por la tipografía del EMF; nunca por ajustar a una página.
"""
from pathlib import Path
import sys,json,copy,struct,re,zipfile,hashlib
from lxml import etree as E
import actualizar_documento as D

V='urn:schemas-microsoft-com:vml'; R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
O='urn:schemas-microsoft-com:office:office'; PR='http://schemas.openxmlformats.org/package/2006/relationships'
CT='http://schemas.openxmlformats.org/package/2006/content-types'
NS={**D.NS,'v':V,'r':R,'o':O}
ROOT=D.ROOT; DOC=D.DOC; OUT=D.OUT
MAX=1550; MARGIN=36

def load(name):return json.loads((OUT/name).read_text(encoding='utf-8'))

class Inserter:
    def __init__(self):
        self.path,self.root,self.body=D.doc_read();self.guard=D.protected(self.body)
        with zipfile.ZipFile(self.path) as z:
            self.parts={n:z.read(n) for n in z.namelist()}
        self.rels=E.fromstring(self.parts['word/_rels/document.xml.rels'])
        self.types=E.fromstring(self.parts['[Content_Types].xml'])
        self.base=copy.deepcopy(self.body.find('w:sectPr',D.NS))
        self.template=next(copy.deepcopy(p) for p in self.body.findall('w:p',D.NS) if p.find('.//v:shape/v:imagedata',NS) is not None)
        self.n=10000;self.manifest=[]

    def section_end(self,width,height):
        p=D.paragraph('',size=2);pr=p.find('w:pPr',D.NS)
        for c in list(pr):pr.remove(c)
        E.SubElement(pr,D.q('spacing'),{D.q('after'):'0',D.q('before'):'0',D.q('line'):'20',D.q('lineRule'):'exact'})
        s=copy.deepcopy(self.base)
        for tag in ('pgSz','pgMar','type','cols'):
            c=s.find('w:'+tag,D.NS)
            if c is not None:s.remove(c)
        E.SubElement(s,D.q('type'),{D.q('val'):'nextPage'})
        E.SubElement(s,D.q('pgSz'),{D.q('w'):str(round(width*20)),D.q('h'):str(round(height*20))})
        E.SubElement(s,D.q('pgMar'),{D.q(k):str(round(v*20)) for k,v in {'top':MARGIN,'right':MARGIN,'bottom':MARGIN,'left':MARGIN,'header':16,'footer':16,'gutter':0}.items()})
        pr.append(s);return p

    def restore_end(self):
        p=D.paragraph('',size=2);p.find('w:pPr',D.NS).append(copy.deepcopy(self.base));return p

    def dimensions(self,path):
        data=path.read_bytes();bounds=struct.unpack_from('<4i',data,8);frame=struct.unpack_from('<4i',data,24)
        w=(frame[2]-frame[0])*72/2540;h=(frame[3]-frame[1])*72/2540
        # Medir los textos realmente dibujados por EA, también rótulos de enlaces.
        # El marco se repite como pie Word de 12 pt y no determina la reducción.
        fonts={};selected=None;sizes=[];position=0;first=True
        while position+8<=len(data):
            kind,length=struct.unpack_from('<II',data,position);record=data[position:position+length]
            if kind==82:fonts[struct.unpack_from('<I',record,8)[0]]=abs(struct.unpack_from('<i',record,12)[0])
            elif kind==37:
                handle=struct.unpack_from('<I',record,8)[0]
                if handle in fonts:selected=handle
            elif kind==84:
                count,offset=struct.unpack_from('<II',record,44)
                text=record[offset:offset+count*2].decode('utf-16le')
                if text:
                    if not first and selected in fonts and fonts[selected]>0:sizes.append(fonts[selected])
                    first=False
            if length<8:raise ValueError('EMF inválido')
            position+=length
        logical_unit=h/max(1,bounds[3]-bounds[1]);scale=12.2/(min(sizes or [16])*logical_unit)
        scale=max(scale,1)
        return w*scale,h*scale,scale

    def image(self,item):
        path=DOC/'diagramas'/(item['stem']+'.emf');assert path.exists(),path
        width,height,scale=self.dimensions(path)
        if width+MARGIN*2>MAX or height+MARGIN*2+70>MAX:
            raise ValueError(f"Reorganizar vista nativa, no reducir fuente: {item['stem']} {width:.1f}x{height:.1f} pt")
        self.n+=1;rid='rIdUnexo'+str(self.n);media='media/unexo-'+item['stem']+'.emf'
        E.SubElement(self.rels,'{'+PR+'}Relationship',Id=rid,Type=R+'/image',Target=media)
        self.parts['word/'+media]=path.read_bytes()
        p=copy.deepcopy(self.template);pr=p.find('w:pPr',D.NS)
        if pr is None:pr=E.Element(D.q('pPr'));p.insert(0,pr)
        for tag in ('sectPr','pageBreakBefore','keepNext','spacing','ind'):
            for e in pr.findall('w:'+tag,D.NS):pr.remove(e)
        E.SubElement(pr,D.q('spacing'),{D.q('before'):'0',D.q('after'):'60'})
        E.SubElement(pr,D.q('jc'),{D.q('val'):'center'})
        shape=p.find('.//v:shape',NS)
        shape.set('id','_x0000_i'+str(self.n));shape.set('alt',path.relative_to(ROOT).as_posix())
        shape.set('style',f'width:{width:.3f}pt;height:{height:.3f}pt;visibility:visible;mso-wrap-style:square')
        im=shape.find('v:imagedata',NS);im.set('{'+R+'}id',rid);im.set('{'+O+'}title',item['stem'])
        caption=D.paragraph('Figura ',size=24)
        cp=caption.find('w:pPr',D.NS);E.SubElement(cp,D.q('keepNext'))
        field=E.SubElement(caption,D.q('fldSimple'),{D.q('instr'):' SEQ Figura \\* ARABIC '})
        rr=E.SubElement(field,D.q('r'));E.SubElement(rr,D.q('t')).text=str(len(self.manifest)+1)
        rr=E.SubElement(caption,D.q('r'));rp=E.SubElement(rr,D.q('rPr'));E.SubElement(rp,D.q('sz'),{D.q('val'):'24'})
        E.SubElement(rr,D.q('t'),{'{http://www.w3.org/XML/1998/namespace}space':'preserve'}).text=' — '+item['name']+' (EA '+str(item['id'])+').'
        self.manifest.append({**item,'width_pt':width,'height_pt':height,'scale':scale,'technical_target_pt':12.2,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        caption_length=len('Figura 0000 — '+item['name']+' (EA '+str(item['id'])+').')
        caption_lines=max(1,int((caption_length*6.2+max(540,width)-1)//max(540,width)))
        return [caption,p],width,height+20*caption_lines+12

    def figures(self,items,group_headers=None):
        out=[self.restore_end()];page=[];used=0;wide=0
        current=object()
        def flush():
            nonlocal page,used,wide
            if page:
                out.extend(page);out.append(self.section_end(max(612,wide+MARGIN*2),max(792,used+MARGIN*2+10)))
                page=[];used=0;wide=0
        for item in items:
            group=item.get('cu') or item.get('actor')
            if group_headers and group!=current:
                flush();current=group
                header=group_headers.get(group)
                if header is not None:
                    header=copy.deepcopy(header);pr=header.find('w:pPr',D.NS)
                    if pr is not None:
                        for tag in ('sectPr','pageBreakBefore'):
                            for old in pr.findall('w:'+tag,D.NS):pr.remove(old)
                    page.append(header);used=40
            blocks,w,h=self.image(item)
            if page and used+h+MARGIN*2+10>MAX:flush()
            page.extend(blocks);used+=h;wide=max(wide,w)
        flush();return out

    def replace_section(self,start,end,items,intro,group_headers=None):
        a,b=D.section_range(self.body,start,end)
        if group_headers is None and start in ('5.3.1.','5.3.2.','7.4.'):
            group_headers={}
            for node in list(self.body)[a:b]:
                match=re.match(r'CU[- ]?0?([1-8])\b',D.txt(node))
                if match and len(D.txt(node))<300:group_headers.setdefault('CU'+match[1],copy.deepcopy(node))
            import contenido
            for cu,name in contenido.CU.items():group_headers.setdefault(cu,D.paragraph(cu+'. '+name,bold=True,size=26))
            group_headers[None]=D.paragraph('Relaciones y cálculos compartidos',bold=True,size=26)
            rank={cu:i for i,cu in enumerate(contenido.CU)}
            items=sorted(items,key=lambda x:rank.get(x.get('cu'),99))
        old=self.body[a];content=[copy.deepcopy(old),D.paragraph(intro)]+self.figures(items,group_headers)
        # Los nuevos saltos reemplazan los saltos internos de estas secciones
        # gráficas. Conservar también los antiguos crearía páginas vacías.
        for p in list(self.body)[a:b]:self.body.remove(p)
        for i,p in enumerate(content):self.body.insert(a+i,p)

    def replace_base_figures(self,items):
        by_stem={x['stem']:x for x in items}
        for p in list(self.body):
            im=p.find('.//v:shape/v:imagedata',NS)
            if im is None:continue
            stem=im.get('{'+O+'}title','')
            if stem not in by_stem:continue
            i=list(self.body).index(p);headers=None
            if stem.startswith('uc-cu') and i:
                previous=self.body[i-1]
                if re.match(r'CU[- ]?0?[1-8]\b',D.txt(previous)):
                    headers={None:copy.deepcopy(previous)};self.body.remove(previous);i-=1
            new=self.figures([by_stem[stem]],headers)
            self.body.remove(p)
            for offset,block in enumerate(new):self.body.insert(i+offset,block)

    def save(self):
        assert D.protected(self.body)==self.guard,'Capítulo IV modificado'
        if not any(x.get('Extension')=='emf' for x in self.types):E.SubElement(self.types,'{'+CT+'}Default',Extension='emf',ContentType='image/x-emf')
        self.parts['word/document.xml']=E.tostring(self.root,xml_declaration=True,encoding='UTF-8',standalone=True)
        self.parts['word/_rels/document.xml.rels']=E.tostring(self.rels,xml_declaration=True,encoding='UTF-8',standalone=True)
        self.parts['[Content_Types].xml']=E.tostring(self.types,xml_declaration=True,encoding='UTF-8',standalone=True)
        temp=self.path.with_name(self.path.stem+'.figuras.tmp.docx')
        with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
            for name,data in self.parts.items():z.writestr(name,data)
        temp.replace(self.path)
        (OUT/'figuras_word.json').write_text(json.dumps(self.manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        print('Figuras nativas insertadas:',len(self.manifest))

def main():
    f=Inserter();inter=load('exportaciones_interacciones.json')
    f.replace_section('5.3.1.','5.3.2.',[x for x in inter if x['category']=='comunicacion'],'Las vistas consecutivas conservan los participantes y todos los mensajes, condiciones y firmas del recorrido real. La numeración continúa dentro de cada flujo. Los participantes técnicos externos son objetos, no actores. Cada vista permanece editable en el proyecto EA original.')
    classes=load('exportaciones_clases_visibles.json');relations=load('exportaciones_relaciones_clases.json')+load('exportaciones_asociaciones.json')
    f.replace_section('5.3.2.','Capítulo VII:',[x for x in classes if x['category']=='clases-detalle']+relations,'Cada clase se presenta con la totalidad de sus atributos, operaciones, visibilidad, parámetros y tipos declarados. Los valores predeterminados se conservan además en notas nativas. Las vistas de relaciones reutilizan las mismas clases completas. Las funciones React/JavaScript se identifican como componentes o módulos, sin inventar tipos ni clases PHP. Los ocho diagramas generales se conservan íntegros en EA.')
    f.replace_section('6.1.','7. Diseño',load('exportaciones_despliegue.json'),'Se distingue el entorno local comprobado del destino institucional previsto. Los equipos, la red y los elementos originales se conservan. Stripe Sandbox y SMTP corresponden a servicios externos; no existe envío comercial automático.')
    f.replace_section('7.1.','7.2.',load('exportaciones_datos.json'),'Vistas nativas del mismo modelo conceptual. Todas las entidades, atributos, asociaciones y multiplicidades originales se conservan; las tablas de asociación continúan representadas. Los tipos físicos exactos, restricciones y valores predeterminados se documentan a continuación.')
    f.replace_section('7.4.','7.5.',[x for x in inter if x['category']=='secuencia']+load('exportaciones_algoritmos.json'),'Secuencias de las operaciones implementadas, con validaciones, alternativas, condiciones, transacciones y servicios externos. Las continuaciones retoman el mismo recorrido; no constituyen nuevos casos de uso. Las firmas y condiciones extensas se leen completas en las notas nativas de la vista. Las vistas de cálculo de CU6 conservan el código literal de cuotas y comisión.')
    navheaders={}
    for i,actor in enumerate(('Administrador','Coordinador','Vendedor','Visitante'),1):
        text='7.5.'+str(i)+'. Diagrama de Navegación del '+actor
        navheaders[actor]=next((copy.deepcopy(p) for p in f.body if D.txt(p)==text),D.heading(text,3))
    f.replace_section('7.5.','7.6.',load('exportaciones_navegacion.json'),'Vistas complementarias del modelo navegacional Conallen original. Las páginas, formularios, conexiones y elementos de datos se reutilizan; representan abstracciones de navegación, no nuevas clases de la implementación.',navheaders)
    f.replace_base_figures(load('exportaciones_base.json'))
    f.save()

if __name__=='__main__':main()
