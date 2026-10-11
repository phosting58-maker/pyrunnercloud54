from fastapi import FastAPI,Request,Form,UploadFile,File
from fastapi.responses import HTMLResponse,JSONResponse,RedirectResponse,FileResponse
import os,psutil,subprocess,zipfile,shutil,hashlib,io,socket,time
app=FastAPI()
BASE='/root/apps';os.makedirs(BASE,exist_ok=True)
SECRET='cloudpusat54';PH=hashlib.sha256(('cloud54'+SECRET).encode()).hexdigest()
def ca(r): return r.cookies.get('auth','')==PH
def up():
 try:
  with open('/proc/uptime') as f: s=float(f.read().split()[0]); d=int(s//86400); h=int((s%86400)//3600); m=int((s%3600)//60); return f"{d}d {h}h {m}m"
 except: return "0d 0h 0m"
def is_running(n):
 try:
  for p in psutil.process_iter(['pid','cwd','cmdline']):
   try:
    cwd=(p.info.get('cwd') or ''); cmd=' '.join(p.info.get('cmdline') or [])
    if f"/root/apps/{n}" in cwd or f"/root/apps/{n}" in cmd: return True
   except: continue
 except: pass
 return False
def gb():
 o=[]
 for d in os.listdir(BASE):
  p=os.path.join(BASE,d)
  if not os.path.isdir(p) or d.startswith('.'): continue
  o.append((d,'running' if is_running(d) else 'stopped',open(os.path.join(p,'.command')).read().strip() if os.path.exists(os.path.join(p,'.command')) else 'python3 main.py'))
 return sorted(o)
def force_kill(n):
  dest=os.path.join(BASE,n)
  try:
   for p in psutil.process_iter(['pid','cwd','cmdline']):
    try:
     cwd=(p.info.get('cwd') or ''); cmd=' '.join(p.info.get('cmdline') or [])
     if dest in cwd or dest in cmd: os.kill(p.info['pid'],9)
    except: continue
  except: pass
  subprocess.run(f"pkill -9 -f '/root/apps/{n}' 2>/dev/null; rm -f /tmp/{n}.log",shell=True); time.sleep(0.5)
def deploy(n,c,d):
 n=''.join(x for x in n.lower() if x.isalnum() or x in '-_')[:30] or 'bot'
 dest=os.path.join(BASE,n); force_kill(n)
 if os.path.exists(dest): shutil.rmtree(dest,ignore_errors=True)
 os.makedirs(dest,exist_ok=True)
 try:
  z=zipfile.ZipFile(io.BytesIO(d)); z.extractall(dest)
  items=os.listdir(dest)
  if len(items)==1 and os.path.isdir(os.path.join(dest,items[0])):
   inner=os.path.join(dest,items[0])
   for f in os.listdir(inner): shutil.move(os.path.join(inner,f),os.path.join(dest,f))
   os.rmdir(inner)
 except Exception as e: return f'ZIP ERR {e}'
 open(os.path.join(dest,'.command'),'w').write(c)
 subprocess.run('pip3 install -q telethon httpx requests 2>/dev/null',shell=True)
 subprocess.Popen(f'cd {dest} && setsid nohup {c} > /tmp/{n}.log 2>&1 &',shell=True, preexec_fn=os.setsid)
 return f'{n} OK'
def list_files(bot,sub=""):
 root=os.path.join(BASE,bot,sub)
 if not os.path.exists(root): return []
 out=[]
 for f in os.listdir(root):
  if f.startswith('.'): continue
  fp=os.path.join(root,f); rel=os.path.join(sub,f) if sub else f
  out.append({"name":f,"path":rel,"is_dir":os.path.isdir(fp),"size":os.path.getsize(fp) if os.path.isfile(fp) else 0})
 return sorted(out,key=lambda x:(not x["is_dir"],x["name"].lower()))

LOGIN="""<!DOCTYPE html><html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>*{box-sizing:border-box;margin:0;padding:0}body{background:#0a0a12;color:#fff;font-family:system-ui;min-height:100vh;display:flex;flex-direction:column}.marquee{width:100%;background:#00d4ff;color:#000;white-space:nowrap;overflow:hidden;padding:8px 0;font-weight:900;font-size:13px;position:fixed;top:0;z-index:999}.marquee-content{display:inline-block;animation:scroll 12s linear infinite;padding-left:100%}@keyframes scroll{0%{transform:translateX(0)}100%{transform:translateX(-100%)}}.wrap{flex:1;display:flex;align-items:center;justify-content:center;padding:60px 14px 20px}.box{width:100%;max-width:360px;background:#121224;border:1px solid #1e1e32;border-radius:22px;padding:26px}.logo{font-weight:900;font-style:italic;font-size:30px;text-align:center}.logo span{color:#22d3ee}.sub{color:#5a5a7a;font-size:11px;text-align:center;letter-spacing:2px;margin:8px 0 22px}input{width:100%;padding:14px;border-radius:12px;border:1px solid #2a2a44;background:#0e0e1e;color:#fff;margin-top:10px}button{width:100%;background:#00e676;color:#000;border:0;padding:14px;border-radius:12px;font-weight:900;margin-top:20px}</style></head><body><div class=marquee><div class=marquee-content>WELCOME TO PYRUNNER CLOUD54 PANEL</div></div><div class=wrap><div class=box><div class=logo>PyRunner<span>Cloud54</span></div><div class=sub>PYTHON RUNNER</div><form method=post action=/login><input name=user placeholder=Username><input name=pass type=password placeholder=Password><button>LOGIN</button></form></div></div></body></html>"""
MAIN="""<!DOCTYPE html><html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>*{box-sizing:border-box}body{margin:0;background:#0a0a12;color:#fff;font-family:system-ui;padding-bottom:90px}.topbar{position:fixed;top:24px;left:0;right:0;background:#0f0f1e;border-bottom:1px solid #22223a;display:flex;justify-content:space-between;align-items:center;padding:8px 12px;z-index:999}.marquee{width:100%;background:#00d4ff;color:#000;white-space:nowrap;overflow:hidden;padding:6px 0;font-weight:900;font-size:11px;position:fixed;top:0;z-index:1000}.marquee-content{display:inline-block;animation:scroll 15s linear infinite;padding-left:100%}@keyframes scroll{0%{transform:translateX(0)}100%{transform:translateX(-100%)}}.page{display:none;padding:12px;padding-top:70px;max-width:1200px;margin:0 auto}.page.on{display:block!important}.btn{border:0;padding:8px 14px;border-radius:10px;font-weight:800;font-size:12px;margin:2px}.btn-blue{background:#00d4ff;color:#000}.btn-green{background:#00e676;color:#000}.btn-red{background:#ff4d4d;color:#fff}.btn-yellow{background:#ffeb3b;color:#000}.btn-gray{background:#2a2a44;color:#fff}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.card{background:#151528;border:1px solid #22223a;border-radius:16px;padding:14px}.tbl{background:#151528;border:1px solid #22223a;border-radius:16px;overflow:hidden;margin-top:12px}table{width:100%;border-collapse:collapse}td{padding:10px;border-bottom:1px solid #1e1e32;font-size:12px}.badge-run{background:#0a2a1a;color:#00e676;border:1px solid #00e67633;padding:4px 10px;border-radius:20px}.badge-stop{background:#2a0a0a;color:#ff5a5a;border:1px solid #ff5a5a33;padding:4px 10px;border-radius:20px}input,textarea{width:100%;padding:12px;border-radius:12px;border:1px solid #2a2a44;background:#151528;color:#fff;margin:6px 0}.drop{border:2px dashed #2a2a44;border-radius:16px;padding:20px;text-align:center;background:#151528;margin:10px 0}.n{position:fixed;bottom:0;left:0;right:0;background:#0f0f1ee6;backdrop-filter:blur(12px);border-top:1px solid #22223a;display:flex;justify-content:space-around;padding:8px 0}.n button{border:0;background:0;color:#5a5a7a;padding:12px 20px;border-radius:16px;flex:1}.n button.on{background:#1e1e36;color:#00d4ff}.editor{position:fixed;top:0;left:0;right:0;bottom:0;background:#0a0a12;z-index:2000;display:none;flex-direction:column;padding:12px}.editor.on{display:flex}.file-item{padding:12px;border-bottom:1px solid #1e1e32;display:flex;justify-content:space-between;align-items:center}</style></head><body><div class=marquee><div class=marquee-content>WELCOME TO PYRUNNER CLOUD54 PANEL - PYTHON RUNNER - </div></div><div class=topbar><div style="font-weight:900;font-style:italic">PyRunner<span style="color:#22d3ee">Cloud54</span></div><a href="/logout" style="text-decoration:none"><button class="btn btn-red" style="padding:6px 12px">Logout</button></a></div>
<div class="page on" id="p-d"><h2>Monitor</h2><div class=grid><div class=card>CPU <b id=cpu>-</b></div><div class=card>RAM <b id=ram>-</b></div><div class=card>DISK <b id=disk>-</b></div><div class=card>BOTS <b id=bcnt>-</b></div></div><div class=tbl><table><tbody id=bt1></tbody></table></div></div>
<div class="page" id="p-b"><h2>Bots</h2><button class="btn btn-blue" onclick="lb()">Refresh</button><button class="btn btn-green" onclick="sp('y')">+ Deploy</button><button class="btn btn-red" onclick="cleanAll()">Clean All</button><div class=tbl><table><tbody id=bt></tbody></table></div></div>
<div class="page" id="p-y"><h2>Deploy</h2><input id=dn value=my-bot><input id=dc value="python3 main.py"><div class=drop onclick="df.click()">Pilih ZIP<input type=file id=df style="display:none"><div id=dfn></div></div><button class="btn btn-green" onclick="dd()">Deploy</button><div id=dl></div></div>
<div class="page" id="p-f"><h2>File Manager</h2><div id=botlist class=tbl></div><div id=breadcrumb style="margin:10px 0;color:#5a5a7a"></div><div id=filelist class=tbl style="display:none"></div><div class=tbl style="padding:12px;margin-top:10px"><b id=ebot>Belum pilih bot</b><div class=drop onclick="ef.click()" style="margin-top:8px">📤 Upload ZIP / File ke bot ini<input type=file id=ef style="display:none"><div id=efn style="font-size:11px;color:#00d4ff"></div></div><div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px"><button class="btn btn-yellow" onclick="doExtract()">📦 Extract ZIP</button><button class="btn btn-blue" onclick="doBackup()">💾 Backup ZIP</button><button class="btn btn-gray" onclick="openBot(curBot)">🔄 Refresh Files</button></div></div></div>
<div class=n><button id=b-d class=on onclick="sp('d')">📊</button><button id=b-b onclick="sp('b')">🤖</button><button id=b-y onclick="sp('y')">☁️</button><button id=b-f onclick="sp('f')">📁</button></div>
<div class=editor id=ed><div style="display:flex;justify-content:space-between;align-items:center"><b id=edname style="font-size:13px"></b><div style="display:flex;gap:6px"><button class="btn btn-green" onclick="saveEdit()">💾 Simpan</button><button class="btn btn-gray" onclick="closeEdit()">✕ Tutup</button></div></div><textarea id=edarea style="flex:1;margin-top:10px;font-family:monospace;font-size:13px"></textarea><div id=edsave style="color:#00e676;padding:6px;font-size:12px"></div></div>
<script>
let curBot=null,curFile=null,extFile=null,curSub="",selFile=null
function sp(p){document.querySelectorAll('.page').forEach(e=>e.classList.remove('on'));document.querySelectorAll('.n button').forEach(e=>e.classList.remove('on'));document.getElementById('p-'+p).classList.add('on');document.getElementById('b-'+p).classList.add('on');if(p=='d'||p=='b'){ld();lb()}if(p=='f'){lf()}}
async function ld(){try{let r=await fetch('/api/stats');let j=await r.json();cpu.innerText=j.cpu+'%';ram.innerText=j.ram_used+'/'+j.ram_total;disk.innerText=j.disk_used+'/'+j.disk_total;bcnt.innerText=j.bot_count}catch{}}
async function lb(){try{let r=await fetch('/api/bots');let b=await r.json();bt.innerHTML='';bt1.innerHTML='';b.forEach(x=>{let badge=x[1]=='running'?'<span class=badge-run>running</span>':'<span class=badge-stop>stopped</span>';let ctrl=x[1]=='running'?`<button class="btn btn-yellow" onclick="stopBot('${x[0]}')">Stop</button> <button class="btn btn-red" onclick="delBot('${x[0]}')">Hapus</button>`:`<button class="btn btn-green" onclick="runBot('${x[0]}')">Run</button> <button class="btn btn-red" onclick="delBot('${x[0]}')">Hapus</button>`;bt.innerHTML+=`<tr><td>${badge}</td><td>${x[0]}</td><td>${ctrl}</td></tr>`;bt1.innerHTML+=`<tr><td>${badge}</td><td>${x[0]}</td><td>${x[2]}</td></tr>`})}catch{}}
async function stopBot(n){let r=await fetch('/api/bot/'+n+'/stop',{method:'POST'});let j=await r.json();alert(j.log);lb()}async function runBot(n){let r=await fetch('/api/bot/'+n+'/start',{method:'POST'});let j=await r.json();alert(j.log);lb()}async function delBot(n){if(!confirm('Hapus '+n))return;await fetch('/api/bot/'+n,{method:'DELETE'});lb()}async function cleanAll(){if(!confirm('Clean all?'))return;await fetch('/api/clean',{method:'POST'});lb()}
df.addEventListener('change',e=>{selFile=e.target.files[0];dfn.innerText=selFile.name});ef.addEventListener('change',e=>{extFile=e.target.files[0];efn.innerText=extFile.name+' siap extract'})
async function dd(){if(!selFile){alert('Pilih ZIP');return}let fd=new FormData();fd.append('name',dn.value);fd.append('cmd',dc.value);fd.append('file',selFile);dl.innerText='Upload...';let r=await fetch('/api/deploy',{method:'POST',body:fd});let j=await r.json();dl.innerText=j.log;sp('b')}
async function lf(){let r=await fetch('/api/bots');let b=await r.json();botlist.innerHTML='';b.forEach(x=>{botlist.innerHTML+=`<div class=file-item onclick="openBot('${x[0]}')" style="cursor:pointer"><span>📦 ${x[0]} - ${x[1]}</span><span style="color:#00d4ff">➜ Buka</span></div>`})}
async function openBot(bot,sub=""){curBot=bot;curSub=sub;ebot.innerText='Bot: '+bot+(sub?' / '+sub:'');breadcrumb.innerHTML=sub?`<span onclick="openBot('${bot}','')" style="color:#00d4ff;cursor:pointer">root</span> / ${sub}`:'';let url='/api/bot/'+bot+'/files'+(sub?'?sub='+encodeURIComponent(sub):'');let r=await fetch(url);let j=await r.json();renderFiles(j)}
function renderFiles(files){filelist.style.display='block';filelist.innerHTML='';if(curSub){filelist.innerHTML+=`<div class=file-item onclick="openBot(curBot,'${curSub.split('/').slice(0,-1).join('/')}')" style="cursor:pointer;color:#5a5a7a">⬆️.. (kembali)</div>`}files.forEach(f=>{let icon=f.is_dir?'📁':'📄';let action=f.is_dir?`onclick="openBot(curBot,'${f.path}')"`:`onclick="editFile('${f.path}')" `;let size=f.is_dir?'folder':(f.size>1024?Math.round(f.size/1024)+'KB':f.size+'B');filelist.innerHTML+=`<div class=file-item ${action} style="cursor:pointer"><span>${icon} ${f.name}</span><span style="font-size:11px;color:#5a5a7a">${size} ${f.is_dir?'➜':'✏️'}</span></div>`})}
async function editFile(path){curFile=path;let r=await fetch('/api/bot/'+curBot+'/read?file='+encodeURIComponent(path));let j=await r.json();if(j.error){alert(j.error);return}edname.innerText=curBot+' / '+path;edarea.value=j.content;ed.classList.add('on');edsave.innerText=''}
async function saveEdit(){let fd=new FormData();fd.append('file',curFile);fd.append('content',edarea.value);let r=await fetch('/api/bot/'+curBot+'/save',{method:'POST',body:fd});let j=await r.json();edsave.innerText=j.log+' ✅'}function closeEdit(){ed.classList.remove('on')}
async function doExtract(){if(!curBot||!extFile){alert('Pilih bot & file ZIP dulu!');return}let fd=new FormData();fd.append('file',extFile);let r=await fetch('/api/bot/'+curBot+'/extract',{method:'POST',body:fd});let j=await r.json();alert(j.log);openBot(curBot,curSub);extFile=null;efn.innerText=''}async function doBackup(){if(!curBot){alert('Pilih bot dulu');return}window.location='/api/bot/'+curBot+'/backup'}
sp('d');ld();lb();setInterval(()=>{ld();lb()},3000);
</script></body></html>"""
@app.get('/login',response_class=HTMLResponse)
async def lg(): return HTMLResponse(LOGIN)
@app.post('/login')
async def lp(user:str=Form(...),pass_:str=Form(...,alias='pass')):
 if user=='admin' and hashlib.sha256((pass_+SECRET).encode()).hexdigest()==PH:
  r=RedirectResponse('/',302);r.set_cookie('auth',PH,max_age=86400*30);return r
 return HTMLResponse(LOGIN)
@app.get('/logout')
async def lo():
 r=RedirectResponse('/login',302); r.delete_cookie('auth'); return r
@app.get('/',response_class=HTMLResponse)
async def hm(request:Request):
 if not ca(request): return RedirectResponse('/login',302)
 return HTMLResponse(MAIN)
@app.get('/api/stats')
async def s():
 vm=psutil.virtual_memory();du=psutil.disk_usage('/');cnt=len([d for d in os.listdir(BASE) if os.path.isdir(os.path.join(BASE,d))])
 return JSONResponse({'cpu':psutil.cpu_percent(),'ram_used':round(vm.used/1024**3,1),'ram_total':round(vm.total/1024**3,1),'disk_used':round(du.used/1024**3,1),'disk_total':round(du.total/1024**3,1),'bot_count':cnt,'hostname':socket.gethostname(),'uptime':up()})
@app.get('/api/bots')
async def b(): return JSONResponse(gb())
@app.post('/api/deploy')
async def d(file:UploadFile=File(...),name:str=Form(...),cmd:str=Form(default='python3 main.py')):
 data=await file.read(); return JSONResponse({'log':deploy(name,cmd,data)})
@app.post('/api/bot/{name}/stop')
async def stopb(name:str):
 force_kill(name); return JSONResponse({'log':f'{name} stopped'})
@app.post('/api/bot/{name}/start')
async def startb(name:str):
 cf=f'/root/apps/{name}/.command'; cmd=open(cf).read().strip() if os.path.exists(cf) else 'python3 main.py'
 force_kill(name); subprocess.Popen(f'cd /root/apps/{name} && setsid nohup {cmd} > /tmp/{name}.log 2>&1 &',shell=True, preexec_fn=os.setsid); return JSONResponse({'log':f'{name} running'})
@app.delete('/api/bot/{name}')
async def delb(name:str):
 force_kill(name); shutil.rmtree(os.path.join(BASE,name),ignore_errors=True); return JSONResponse({'log':'deleted'})
@app.post('/api/clean')
async def clean():
 c=0
 for d in os.listdir(BASE): force_kill(d); shutil.rmtree(os.path.join(BASE,d),ignore_errors=True);c+=1
 return JSONResponse({'log':f'{c} cleaned'})
@app.get('/api/bot/{name}/files')
async def files(name:str,sub:str=""): return JSONResponse(list_files(name,sub))
@app.get('/api/bot/{name}/read')
async def readf(name:str,file:str):
 fp=os.path.join(BASE,name,file)
 if not os.path.exists(fp) or os.path.isdir(fp): return JSONResponse({'error':'not found'})
 if os.path.getsize(fp)>200000: return JSONResponse({'error':'file too big >200KB'})
 return JSONResponse({'content':open(fp,'r',errors='ignore').read()})
@app.post('/api/bot/{name}/save')
async def savef(name:str,file:str=Form(...),content:str=Form(...)):
 open(os.path.join(BASE,name,file),'w').write(content); return JSONResponse({'log':'saved OK'})
@app.post('/api/bot/{name}/extract')
async def ext(name:str,file:UploadFile=File(...)):
 data=await file.read()
 try: z=zipfile.ZipFile(io.BytesIO(data)); z.extractall(os.path.join(BASE,name)); return JSONResponse({'log':f'Extract OK {len(z.namelist())} files'})
 except Exception as e: return JSONResponse({'log':str(e)})
@app.get('/api/bot/{name}/backup')
async def backup(name:str):
 zip_path=f'/tmp/{name}-backup'; shutil.make_archive(zip_path,'zip',os.path.join(BASE,name)); return FileResponse(f'{zip_path}.zip',filename=f'{name}.zip')
