/** Compatibilidad del EMF exportado por EA 15 con Word.
 * No dibuja UML ni modifica una sola primitiva gráfica del diagrama.
 * Conserva todos los registros EA; únicamente explicita el viewport que falta
 * en ciertas exportaciones con coordenadas Y negativas y actualiza el encuadre.
 * El modelo editable y el EMF bruto se conservan por separado.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const [input,output]=process.argv.slice(2);
if(!input||!output)throw Error('Uso: node compatibilidad_emf.mjs origen.emf destino.emf');
const source=fs.readFileSync(input);
if(source.readUInt32LE(0)!==1||source.readUInt32LE(40)!==0x464d4520)throw Error('No es un EMF');
const left=source.readInt32LE(8),top=source.readInt32LE(12),right=source.readInt32LE(16),bottom=source.readInt32LE(20);
if(top>=-1){fs.writeFileSync(output,source);process.exit(0);}
const records=[];let position=0;
while(position+8<=source.length){
 const type=source.readUInt32LE(position),size=source.readUInt32LE(position+4);
 if(size<8||position+size>source.length)throw Error('Registro EMF inválido');
 records.push(Buffer.from(source.subarray(position,position+size)));position+=size;
}
if(position!==source.length||records.length!==source.readUInt32LE(52))throw Error('Conteo EMF inconsistente');
if(records.some(r=>[11,12,35,36].includes(r.readUInt32LE(0))))throw Error('Viewport complejo: no normalizar automáticamente');
function pair(type,x,y){const r=Buffer.alloc(16);r.writeUInt32LE(type);r.writeUInt32LE(16,4);r.writeInt32LE(x,8);r.writeInt32LE(y,12);return r;}
const adjusted=[];let extra=0;
for(const record of records){
 adjusted.push(Buffer.from(record));
 if(record.readUInt32LE(0)===17&&record.readInt32LE(8)===8){adjusted.push(pair(11,1,-1),pair(12,-left,bottom));extra+=2;}
}
if(extra!==2)throw Error('No se reconoce el modo anisotrópico sencillo de EA 15');
const result=Buffer.concat(adjusted);
result.writeInt32LE(0,8);result.writeInt32LE(0,12);result.writeInt32LE(right-left,16);result.writeInt32LE(bottom-top,20);
result.writeUInt32LE(result.length,48);result.writeUInt32LE(records.length+extra,52);
// Prueba de integridad: todos los registros gráficos originales siguen siendo
// idénticos byte por byte. Solo el encabezado y los dos nuevos registros varían.
let i=0;
for(const record of adjusted){
 const type=record.readUInt32LE(0);
 if(type===11||type===12)continue;
 if(i>0&&!record.equals(records[i]))throw Error('Cambió una primitiva gráfica');
 i++;
}
if(i!==records.length)throw Error('Se perdió un registro EA');
fs.writeFileSync(output,result);
const restart=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../tmp/actualizacion_documental/solicitar_reinicio.flag');
if(fs.existsSync(restart))throw Error('Reinicio controlado del lote EA tras guardar el EMF nativo.');
