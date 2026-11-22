"""Elimina medios y relaciones de imagen sin uso, conservando todos los visibles."""
import zipfile,posixpath,json
from lxml import etree as E
import actualizar_documento as D
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PR='http://schemas.openxmlformats.org/package/2006/relationships'

def main():
    path,root,body=D.doc_read();guard=D.protected(body)
    with zipfile.ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
    rel=E.fromstring(parts['word/_rels/document.xml.rels'])
    used={v for node in root.iter() for k,v in node.attrib.items() if k.startswith('{'+R+'}')}
    removed_rel=[]
    for node in list(rel):
        if node.get('Type')==R+'/image' and node.get('Id') not in used:removed_rel.append(node.get('Id'));rel.remove(node)
    parts['word/_rels/document.xml.rels']=E.tostring(rel,xml_declaration=True,encoding='UTF-8',standalone=True)
    referenced=set()
    for name,data in parts.items():
        if not name.endswith('.rels'):continue
        owner=name.replace('/_rels/','/')[:-5] if '/_rels/' in name else ''
        directory=posixpath.dirname(owner)
        for node in E.fromstring(data):
            if node.get('TargetMode')=='External':continue
            target=node.get('Target','')
            referenced.add(posixpath.normpath(posixpath.join(directory,target.lstrip('/')) if not target.startswith('/') else target.lstrip('/')))
    removed_media=[n for n in parts if n.startswith('word/media/') and n not in referenced]
    for name in removed_media:del parts[name]
    check=E.fromstring(parts['word/document.xml']).find('w:body',D.NS)
    assert D.protected(check)==guard
    temp=path.with_name(path.stem+'.medios.tmp.docx')
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in parts.items():z.writestr(name,data)
    temp.replace(path)
    result={'relaciones_sin_uso_retiradas':len(removed_rel),'medios_sin_uso_retirados':len(removed_media),'capitulo_IV_intacto':True}
    (D.OUT/'limpieza_medios_word.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(result)

if __name__=='__main__':main()
