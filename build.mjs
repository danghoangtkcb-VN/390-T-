import {readFileSync,writeFileSync,mkdirSync,copyFileSync,existsSync,cpSync,rmSync} from 'node:fs';
import {inflateRawSync} from 'node:zlib';
import {resolve} from 'node:path';
const data=JSON.parse(readFileSync('questions.json','utf8'));
if(data.length!==390||new Set(data.map(q=>q.id)).size!==390)throw Error('Dữ liệu phải đủ 390 mã riêng biệt');
rmSync('dist',{recursive:true,force:true});mkdirSync('dist/am_thanh',{recursive:true});
// Read central directory: the original archive stays in git, audio is extracted at build time.
const z=readFileSync('Hanh_Trinh_390_Cau_Giong_Viet_Offline.zip');
let end=-1;for(let i=z.length-22;i>=Math.max(0,z.length-65557);i--)if(z.readUInt32LE(i)===0x06054b50){end=i;break}
if(end<0)throw Error('Invalid ZIP');let offset=z.readUInt32LE(end+16), count=z.readUInt16LE(end+10), audio=0;
for(let i=0;i<count;i++){
 if(z.readUInt32LE(offset)!==0x02014b50)throw Error('Invalid directory');
 const method=z.readUInt16LE(offset+10),size=z.readUInt32LE(offset+20),nl=z.readUInt16LE(offset+28),xl=z.readUInt16LE(offset+30),cl=z.readUInt16LE(offset+32),local=z.readUInt32LE(offset+42);
 const name=z.toString('utf8',offset+46,offset+46+nl);offset+=46+nl+xl+cl;
 if(!/^am_thanh\/(NH|BS)\d{3}_[qa]\.mp3$/.test(name))continue;
 const start=local+30+z.readUInt16LE(local+26)+z.readUInt16LE(local+28),compressed=z.subarray(start,start+size);
 const bytes=method===0?compressed:method===8?inflateRawSync(compressed):null;if(!bytes?.length)throw Error('Invalid audio');
 writeFileSync(resolve('dist',name),bytes);audio++;
}
if(audio!==780)throw Error(`Thiếu MP3: ${audio}/780`);
copyFileSync('index.html','dist/index.html');
if(existsSync('audio/manifest.json')){
 const manifest=JSON.parse(readFileSync('audio/manifest.json'));
 if(manifest.voice!=='leminh'||!manifest.complete)throw Error('Chưa tạo đủ bản ghi nam miền Bắc');
 for(const q of data)for(const part of ['q','a'])if(!existsSync(`audio/${q.id}_${part}.mp3`))throw Error('Thiếu bản ghi đã xác nhận');
 cpSync('audio','dist/audio',{recursive:true});
}
console.log(`Build OK: ${data.length} câu, 13 chặng, ${audio} MP3 nguồn. Giọng nam Bắc: ${existsSync('audio/manifest.json')?'đã cấu hình':'chưa có bản ghi xác nhận'}`);
