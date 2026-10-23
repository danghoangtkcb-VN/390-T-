import {createServer} from 'node:http';
import {readFile,stat} from 'node:fs/promises';
import {resolve,extname} from 'node:path';
const root=resolve('dist');
createServer(async(req,res)=>{try{const path=resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(path!==root&&!path.startsWith(root+'/'))throw Error();const file=(await stat(path)).isDirectory()?path+'/index.html':path;res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.mp3':'audio/mpeg','.json':'application/json'})[extname(file)]||'application/octet-stream');res.end(await readFile(file));}catch{res.statusCode=404;res.end('Not found')}}).listen(3900,'0.0.0.0',()=>console.log('http://localhost:3900'));
