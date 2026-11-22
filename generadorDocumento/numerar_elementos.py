"""Numeración mecánica de tablas y figuras del maestro, con capítulo IV protegido."""
import re,copy,json,zipfile
from pathlib import Path
from lxml import etree as E
import actualizar_documento as D

XML='{http://www.w3.org/XML/1998/namespace}space'
V='urn:schemas-microsoft-com:vml';O='urn:schemas-microsoft-com:office:office'

def caption(kind,title,index):
    p=D.paragraph(kind+' ',size=24);pr=p.find('w:pPr',D.NS);E.SubElement(pr,D.q('keepNext'))
    field=E.SubElement(p,D.q('fldSimple'),{D.q('instr'):' SEQ '+kind+' \\* ARABIC '})
    r=E.SubElement(field,D.q('r'));rp=E.SubElement(r,D.q('rPr'));E.SubElement(rp,D.q('sz'),{D.q('val'):'24'});E.SubElement(r,D.q('t')).text=str(index)
    r=E.SubElement(p,D.q('r'));rp=E.SubElement(r,D.q('rPr'));E.SubElement(rp,D.q('sz'),{D.q('val'):'24'})
    E.SubElement(r,D.q('t'),{XML:'preserve'}).text=' — '+title
    return p

def has_sequence(p,kind):
    return any('SEQ '+kind in x.get(D.q('instr'),'') for x in p.findall('.//w:fldSimple',D.NS)) or any('SEQ '+kind in (x.text or '') for x in p.findall('.//w:instrText',D.NS))

def main():
    path,root,body=D.doc_read();guard=D.protected(body);chapter='';context='';section='';tables=0;figures=0
    for node in list(body):
        text=D.txt(node)
        if text.startswith('Capítulo'):chapter=text
        if not chapter or chapter.startswith('Capítulo IV:'):continue
        if node.tag==D.q('p'):
            style=node.find('w:pPr/w:pStyle',D.NS)
            if style is not None and style.get(D.q('val'),'').startswith('Ttulo'):context=text
            if re.match(r'7\.[23](?:\.|\s)',text):section=text
        if node.tag==D.q('tbl') and not node.findall('.//{'+V+'}imagedata'):
            tables+=1;index=list(body).index(node)
            if index and has_sequence(body[index-1],'Tabla'):continue
            first=node.find('w:tr',D.NS);header=D.txt(first) if first is not None else ''
            cu=re.search(r'CU0?([1-8])\.',header)
            if cu:
                import contenido
                title='Especificación CU'+cu[1]+'. '+contenido.CU['CU'+cu[1]]
            elif header.startswith('ColumnaTipo exacto'):title='Mapeo de '+context
            elif header.startswith('ColumnaTipoDescripción'):title='Diccionario de '+context
            elif header.startswith('PropiedadDefinición'):title='Trigger '+context
            else:title=context or 'Información documental'
            body.insert(index,caption('Tabla',title,tables))
        image=node.find('.//{'+V+'}imagedata')
        if image is None:continue
        figures+=1;index=list(body).index(node)
        if index and has_sequence(body[index-1],'Figura'):continue
        title=image.get('{'+O+'}title','')
        title={'organigrama':'Organigrama de UNEXO','ubicacion':'Ubicación institucional de referencia'}.get(title,title or context)
        for adjacent in (index+1,index-1):
            if 0<=adjacent<len(body):
                p=body[adjacent]
                if re.match(r'Ilustraci[oó]n\s+\d+',D.txt(p)):body.remove(p)
        body.insert(list(body).index(node),caption('Figura',title,figures))
    assert D.protected(body)==guard,'Capítulo IV modificado'
    with zipfile.ZipFile(path) as z:settings=E.fromstring(z.read('word/settings.xml'))
    if settings.find('w:doNotAutoCompressPictures',D.NS) is None:E.SubElement(settings,D.q('doNotAutoCompressPictures'))
    D.replace_zip(path,{'word/document.xml':E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True),'word/settings.xml':E.tostring(settings,xml_declaration=True,encoding='UTF-8',standalone=True)})
    result={'tablas_numeradas':tables,'figuras_numeradas':figures,'capitulo_IV_intacto':True,'imagenes_sin_autocompresion':True}
    (D.OUT/'numeracion_documental.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(result)

if __name__=='__main__':main()
