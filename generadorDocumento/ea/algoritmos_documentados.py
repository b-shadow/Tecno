"""Notas nativas con el código literal de los cálculos comerciales relevantes."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import sincronizar_documentacion as S
import win32com.client

def main():
    nodes={n:x for cu in S.catalog().values() for n,x in cu['nodes'].items()}
    payment=next(m for m in nodes['NPago']['methods'] if m['name']=='crearOrden')['body']
    begin=payment.index("$n = (int) $datos['cuotas'];")
    end=payment.index('$plan =',begin)
    quota=payment[begin:end].strip()
    commission='\n\n'.join('public static function '+m['name']+'('+', '.join(p['raw'] for p in m['params'])+'): '+m['return']+'\n{\n'+m['body'].strip()+'\n}' for m in nodes['Comision']['methods'] if m['name'] in ('porcentajeVigente','registrar'))
    S.prepare_export_environment();r=win32com.client.Dispatch('EA.Repository');assert r.OpenFile(str(S.DOC/'ea/crm-p2.eapx'))
    try:
        pkg=r.GetPackageByID(r.GetDiagramByID(142).PackageID)
        classes={e['Name']:int(e['Object_ID']) for e in S.select(r,'t_object') if e['Object_Type']=='Class' and e['Name'] in ('NPago','Comision')}
        registry=[]
        for name,source,code,explanation in [('NPago','negocio/app/Negocio/NPago.php',quota,'Cálculo literal de cuotas, fechas y tokens. insertarCuotas recibe el lote completo. codigo_qr es el identificador histórico del agregado pagos; no habilita nuevos métodos QR ni comprobantes manuales.'),('Comision','datos/src/Modelos/Comision.php',commission,'Fórmula literal por ítem y porcentaje vigente; firstOrCreate evita duplicar la comisión. Esta vista complementa los mensajes de DConversion y conserva la política implementada.')]:
            title='CU6. Cálculo literal — '+name
            d=next((x for x in pkg.Diagrams if x.Name==title),None)
            if d is None:d=pkg.Diagrams.AddNew(title,'Sequence');S.checked(d)
            obj=next((x for x in pkg.Elements if x.Type=='Object' and x.Name==name and x.ClassifierID==classes[name]),None)
            if obj is None:obj=pkg.Elements.AddNew(name,'Object');obj.ClassifierID=classes[name];S.checked(obj)
            note_name=title+' — código de fuente'
            note=next((x for x in pkg.Elements if x.Type=='Note' and x.Name==note_name),None)
            if note is None:note=pkg.Elements.AddNew(note_name,'Note');S.checked(note)
            note.Notes=explanation+'\nFuente: '+source+'\n\n'+code;S.checked(note)
            height=50+21*sum(max(1,(len(line)*8+999)//1000) for line in note.Notes.splitlines())
            S.put(d,obj,40,40,600,110);o=S.put(d,note,40,210,1000,height);o.SetStyleEx('italic','0');S.checked(o)
            d.Notes='Extracto literal del código vigente. No crea operaciones ni casos de uso, ni reemplaza la clase completa o sus interacciones. '+source;S.checked(d)
            S.export(r,d,'algoritmo-cu6-'+name.lower(),registry,'algoritmo','CU6')
        S.dump('exportaciones_algoritmos.json',registry)
    finally:r.CloseFile();r.Exit()

if __name__=='__main__':main()
