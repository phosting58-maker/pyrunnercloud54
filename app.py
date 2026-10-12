from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse,JSONResponse,RedirectResponse
from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse,JSONResponse,RedirectResponse
import os,psutil,subprocess,hashlib,shutil,zipfile,pathlib,time,glob
app=FastAPI(docs_url=None,redoc_url=None)
B='/root/apps';os.makedirs(B,exist_ok=True);S='cloudpusat54';P=hashlib.sha256(('cloud54'+S).encode()).hexdigest()
def ok(r):return r.cookies.get('auth','')==P
def is_run(bp,bn):
 pf=os.path.join(bp,'.pid')
 if os.path.exists(pf):
  try:
   pid=int(open(pf).read().strip())
   if psutil.pid_exists(pid):return True,pid
  except:pass
 for pr in psutil.process_iter(['pid','cmdline']):
  try:
   if pr.cwd()==bp:return True,pr.info['pid']
   c=' '.join(pr.info['cmdline'] or [])
   if bp in c and 'python' in c:return True,pr.info['pid']
  except:continue
 return False,0
LOGIN='<html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#08070e;color:#fff;font-family:system-ui}.bx{width:92%;max-width:360px;background:rgba(15,15,25,.9);border:1px solid rgba(255,255,255,.08);border-radius:24px;padding:28px;text-align:center}.lg{font-weight:900;font-size:26px}.lg span{color:#a78bfa}input{width:100%;margin-top:12px;padding:13px;border-radius:14px;border:1px solid rgba(255,255,255,.1);background:rgba(0,0,0,.3);color:#fff}button{width:100%;margin-top:16px;padding:13px;border-radius:14px;border:0;background:#fff;color:#000;font-weight:800}</style></head><body><div class=bx><div class=lg>Cloud<span>Pusat54</span></div><form method=post action=/login><input name=user placeholder=admin><input name=pass type=password placeholder=cloud54><button>LOGIN</button></form></div></body></html>'
MAIN='''<html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>*{box-sizing:border-box;font-family:Inter,system-ui}body{margin:0;background:#08070e;color:#fff;padding-bottom:110px}body::before{content:'';position:fixed;inset:0;background:radial-gradient(900px at 50% 0%,rgba(120,60,255,.25),transparent 70%),radial-gradient(700px at 0% 100%,rgba(80,30,180,.4),transparent 60%);pointer-events:none}.wrap{position:relative;z-index:1;max-width:480px;margin:0 auto;padding:14px}.header{display:flex;justify-content:space-between;padding:12px 6px}.logo{font-weight:900;font-size:22px}.logo span{color:#a78bfa}.cp{width:40px;height:40px;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid rgba(167,139,250,.3);display:flex;align-items:center;justify-content:center;font-weight:900;color:#a78bfa}.sub{display:flex;justify-content:space-between;background:rgba(15,15,28,.7);border:1px solid rgba(255,255,255,.06);border-radius:20px;padding:10px 14px;margin:10px 0 18px}.online{display:flex;gap:6px;font-size:12px;color:#86efac;background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.2);padding:4px 10px;border-radius:20px}.stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:18px}.card{border-radius:22px;padding:16px;border:1px solid rgba(255,255,255,.08)}.card.cpu{background:linear-gradient(135deg,rgba(16,185,129,.25),rgba(6,78,59,.4),rgba(15,15,30,.9))}.card.ram{background:linear-gradient(135deg,rgba(139,92,246,.3),rgba(76,29,149,.4),rgba(15,15,30,.9))}.card.disk{background:linear-gradient(135deg,rgba(6,182,212,.25),rgba(14,116,144,.4),rgba(15,15,30,.9))}.card b{font-size:28px;font-weight:900;display:block;margin:8px 0 4px}.progress{height:5px;background:rgba(0,0,0,.3);border-radius:10px;margin-top:14px;overflow:hidden}.progress i{display:block;height:100%;border-radius:10px}.bots-sec{background:rgba(15,15,28,.75);border:1px solid rgba(255,255,255,.08);border-radius:26px;padding:18px}.bot-item{background:rgba(10,10,18,.6);border:1px solid rgba(255,255,255,.06);border-radius:18px;padding:14px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center}.status{font-size:11px;font-weight:700}.status.running{color:#4ade80}.status.stopped{color:#fb7185}.dot{width:10px;height:10px;border-radius:50%;display:inline-block}.dot.running{background:#22c55e;box-shadow:0 0 10px #22c55e}.dot.stopped{background:#ef4444}.btn{padding:7px 12px;border-radius:12px;font-size:11px;font-weight:700;border:1px solid;cursor:pointer;background:transparent}.btn-run{color:#4ade80;border-color:rgba(74,222,128,.3);background:rgba(74,222,128,.08)}.btn-stop{color:#94a3b8;border-color:rgba(255,255,255,.1)}.bottom{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);width:92%;max-width:400px;background:rgba(15,15,28,.95);border:1px solid rgba(255,255,255,.12);border-radius:26px;display:flex;padding:6px;z-index:9999}.bottom div{flex:1;text-align:center;padding:14px 6px;border-radius:18px;font-size:12px;font-weight:800;color:#6b7280;cursor:pointer;pointer-events:auto}.bottom div.on{background:rgba(255,255,255,.1);color:#5eead4}.logbox{background:rgba(0,0,0,.4);border:1px solid rgba(255,255,255,.06);border-radius:14px;padding:12px;font-family:monospace;font-size:11px;max-height:280px;overflow:auto;color:#5eead4;white-space:pre-wrap;margin-top:12px}.inp{width:100%;padding:12px;background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.08);border-radius:12px;color:#fff;margin-bottom:10px}.file{padding:10px 12px;border-radius:10px;display:flex;justify-content:space-between;cursor:pointer;margin:3px 0;background:rgba(255,255,255,.02)}</style></head><body><div class=wrap><div class=header><div class=logo>Cloud<span>Pusat54</span></div><div class=cp>CP</div></div><div class=sub><span style=color:#94a3b8;font-size:13px>Cloud Bot Panel - Dashboard</span><span class=online><span class=dot running></span> Online</span></div><div id=p1><div class=stats><div class="card cpu"><label>CPU</label><b id=cpu>0.4%</b><div class=progress><i id=cb style=width:10%;background:linear-gradient(90deg,#10b981,#6ee7b7)></i></div><small id=cpu2 style=display:block;margin-top:6px;text-align:right>0.4% / 100%</small></div><div class="card ram"><label>RAM</label><b id=ram>0.6GB</b><div class=progress><i id=rb style=width:30%;background:linear-gradient(90deg,#8b5cf6,#a78bfa)></i></div><small id=ram2 style=display:block;margin-top:6px;text-align:right>0.6GB / 2GB</small></div><div class="card disk"><label>DISK</label><b id=disk>3GB</b><div class=progress><i id=db style=width:25%;background:linear-gradient(90deg,#06b6d4,#67e8f9)></i></div><small id=disk2 style=display:block;margin-top:6px;text-align:right>3GB / 12GB</small></div></div><div class=bots-sec><div style=display:flex;justify-content:space-between;margin-bottom:14px><b>Bots</b><span style="font-size:12px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.05);padding:6px 14px;border-radius:20px;color:#a78bfa;cursor:pointer" onclick="sh(3)">+ Add</span></div><div id=bots>Loading bots...</div><div id=rlog class=logbox style=display:none></div></div></div><div id=p2 style=display:none><div class=bots-sec><b>File Manager</b><div style=margin-top:12px><div style=display:flex;justify-content:space-between><span id=cur style=color:#5eead4;font-family:monospace;font-size:11px>/root/apps</span><button class=btn btn-run onclick="lf('/root/apps')">Root</button></div><div id=fl style=margin-top:10px></div></div><div style=display:flex;gap:6px;flex-wrap:wrap;margin-top:14px><button class=btn btn-run onclick="nf()">+ New</button><button class=btn btn-run onclick="ed()">Edit</button><button class=btn btn-run onclick="sv()">Save</button><button class=btn btn-stop onclick="xf()">Extract</button><button class=btn btn-stop onclick="df()">Delete</button></div><div id=si style=font-size:10px;color:#475569;margin-top:8px>No file selected</div></div><div class=bots-sec id=ec style=display:none;margin-top:12px><div style=display:flex;justify-content:space-between><small id=en style=color:#5eead4;font-family:monospace></small><button class=btn btn-stop onclick="document.getElementById('ec').style.display='none'">Close</button></div><textarea id=t style=width:100%;height:340px;background:rgba(0,0,0,.4);border:1px solid rgba(255,255,255,.08);border-radius:12px;color:#5eead4;padding:12px;font-family:monospace;font-size:12px;margin-top:8px></textarea></div></div><div id=p3 style=display:none><div class=bots-sec><b>Deploy Bot</b><p style=color:#64748b;font-size:12px;margin:6px 0 14px>Upload ZIP bot kamu</p><input id=n class=inp placeholder="Nama bot"><input id=cmd class=inp value="python3 main.py"><input type=file id=z style=margin:8px 0;color:#64748b><button class=btn btn-run style=width:100%;padding:14px;background:#fff;color:#000" onclick="dp()">Deploy Now</button><div id=dl class=logbox style=display:none></div></div></div></div><div class=bottom><div id=b1 class=on onclick="sh(1)">Monitor</div><div id=b2 onclick="sh(2)">Files</div><div id=b3 onclick="sh(3)">Deploy</div></div><script>
function sh(x){
 document.getElementById('p1').style.display=x==1?'block':'none';
 document.getElementById('p2').style.display=x==2?'block':'none';
 document.getElementById('p3').style.display=x==3?'block':'none';
 document.getElementById('b1').className=x==1?'on':'';
 document.getElementById('b2').className=x==2?'on':'';
 document.getElementById('b3').className=x==3?'on':'';
 if(x==2)lf('/root/apps');
 if(x==1)lm();
}
function lm(){
 fetch('/api/s').then(r=>r.json()).then(d=>{
  document.getElementById('cpu').innerText=d.c+'%';
  document.getElementById('ram').innerText=d.m+'GB';
  document.getElementById('disk').innerText=d.d+'GB';
  document.getElementById('cpu2').innerText=d.c+'% / 100%';
  document.getElementById('ram2').innerText=d.m+'GB / 2GB';
  document.getElementById('disk2').innerText=d.d+'GB / 12GB';
  document.getElementById('cb').style.width=d.c+'%';
  document.getElementById('rb').style.width=(d.m/2*100)+'%';
  document.getElementById('db').style.width=(d.d/12*100)+'%';
 });
 fetch('/api/b').then(r=>r.json()).then(d=>{
  let h='';
  for(let x of d){
   let on=x[1]=='running';
   h+='<div class=bot-item><div><div class="status '+(on?'running':'stopped')+'"><span class="dot '+(on?'running':'stopped')+'"></span> '+(on?'Running':'Stopped')+'</div><div style=font-weight:800>'+x[0]+'</div><div style=font-size:11px;color:rgba(255,255,255,.45)'>Instance - PID '+x[2]+'</div></div><div><button class=btn btn-run onclick="rb(\\''+x[0]+'\\')">Run</button><button class=btn btn-stop onclick="sb(\\''+x[0]+'\\')">Stop</button></div></div>';
  }
  document.getElementById('bots').innerHTML=h||'<div style=text-align:center;color:#6b7280;padding:20px>No bots found in /root/apps</div>';
 }).catch(e=>{
  document.getElementById('bots').innerHTML='<div style=color:#ef4444>Error load bots: '+e+'</div>';
 });
}
function rb(n){document.getElementById('rlog').style.display='block';document.getElementById('rlog').innerText='Starting '+n+'...';fetch('/api/bot/'+n+'/start',{method:'POST'}).then(r=>r.json()).then(d=>{document.getElementById('rlog').innerText=d.log;lm()})}
function sb(n){fetch('/api/bot/'+n+'/stop',{method:'POST'}).then(()=>{document.getElementById('rlog').style.display='block';document.getElementById('rlog').innerText='Stopped '+n;lm()})}
function lf(p){cur=p;document.getElementById('cur').innerText=p;fetch('/api/ls?path='+encodeURIComponent(p)).then(r=>r.json()).then(d=>{let h='';for(let x of d){let sp=x.p.replace(/'/g,"_");h+='<div class=file onclick="sl(\\''+sp+'\\','+x.d+')"><span><b>'+(x.d?'[DIR]':'[FILE]')+' '+x.n+'</b></span></div>'}document.getElementById('fl').innerHTML=h})}
function sl(p,d){sel=p;document.getElementById('si').innerText=p;if(d)lf(p);else ed()}
function ed(){if(!sel){alert('Pilih file dulu!');return}fetch('/api/rd?path='+encodeURIComponent(sel)).then(r=>r.text()).then(t=>{document.getElementById('ec').style.display='block';document.getElementById('en').innerText=sel;document.getElementById('t').value=t})}
function sv(){if(!sel)return;fetch('/api/wr',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel,content:document.getElementById('t').value})}).then(()=>{alert('Saved!');lf(cur)})}
function df(){if(!sel)return;if(!confirm('Hapus '+sel+'?'))return;fetch('/api/rm',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel})}).then(()=>{document.getElementById('ec').style.display='none';sel=null;lf(cur)})}
function xf(){if(!sel)return;fetch('/api/ex',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel})}).then(r=>r.json()).then(d=>{alert(d.log);lf(cur)})}
function nf(){let n=prompt('Nama file baru');if(!n)return;fetch('/api/wr',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:cur+'/'+n,content:''})}).then(()=>lf(cur))}
function dp(){let n=document.getElementById('n').value;if(!n)return alert('Isi nama');let fd=new FormData();fd.append('name',n);fd.append('command',document.getElementById('cmd').value);fd.append('file',document.getElementById('z').files[0]);document.getElementById('dl').style.display='block';document.getElementById('dl').innerText='Uploading...';fetch('/api/dp',{method:'POST',body:fd}).then(r=>r.json()).then(d=>{document.getElementById('dl').innerText=d.log;lm();sh(1)})}
let cur='/root/apps',sel=null;
lm();
setInterval(lm,4000);
</script></body></html>'''
@app.get('/login',response_class=HTMLResponse)
async def a():return HTMLResponse(LOGIN)
@app.post('/login')
async def b(user: str=Form(...),pass_: str=Form(...,alias='pass')):
 if user=='admin' and hashlib.sha256((pass_+S).encode()).hexdigest()==P:
  r=RedirectResponse('/',302);r.set_cookie('auth',P,max_age=86400*30,httponly=True);return r
 return HTMLResponse(LOGIN,401)
@app.get('/logout')
async def c():
 r=RedirectResponse('/login',302);r.delete_cookie('auth');return r
@app.get('/',response_class=HTMLResponse)
async def d(request: Request):
 if not ok(request):return RedirectResponse('/login',302)
 return HTMLResponse(MAIN)
@app.get('/api/b')
async def e():
 o=[]
 try:
  for n in os.listdir(B):
   p=os.path.join(B,n)
   if os.path.isdir(p) and not n.startswith('.'):
    run,pid=is_run(p,n)
    o.append([n,'running' if run else 'stopped',pid])
 except Exception as ex:
  return JSONResponse({'error':str(ex)})
 return JSONResponse(sorted(o))
@app.post('/api/bot/{name}/start')
async def f(name: str):
 bp=os.path.join(B,name)
 cf=os.path.join(bp,'.command');cmd=pathlib.Path(cf).read_text().strip() if os.path.exists(cf) else 'python3 main.py'
 for pr in psutil.process_iter(['pid']):
  try:
   if pr.cwd()==bp:pr.kill()
  except:pass
 time.sleep(0.5)
 for pat in ['*.db-shm','*.db-wal','*.sqlite-shm','*.sqlite-wal','*.session-journal','.pid']:
  try:
   for ff in glob.glob(os.path.join(bp,pat)):os.remove(ff)
  except:pass
 venv="/root/panel-venv/bin/python";py=venv if os.path.exists(venv) else "python3"
 if "python3" in cmd:cmd=cmd.replace("python3",py)
 if "-u" not in cmd:cmd=cmd.replace(py,f"{py} -u")
 full=f"cd {bp} && nohup {cmd} > bot.log 2>&1 & echo $!"
 try:
  r=subprocess.run(full,shell=True,capture_output=True,text=True,timeout=10)
  open(os.path.join(bp,'.pid'),'w').write(r.stdout.strip())
  time.sleep(2)
  run,pid=is_run(bp,name)
  log=""
  try:log=open(os.path.join(bp,'bot.log'),errors='ignore').read()[-2000:]
  except:pass
  return JSONResponse({'log':f'LIVE {name} PID {pid}\n{log}'})
 except Exception as e:return JSONResponse({'log':str(e)})
@app.post('/api/bot/{name}/stop')
async def g(name: str):
 bp=os.path.join(B,name)
 for pr in psutil.process_iter(['pid']):
  try:
   if pr.cwd()==bp:pr.kill()
  except:pass
 try:os.remove(os.path.join(bp,'.pid'))
 except:pass
 return JSONResponse({'ok':True})
@app.get('/api/bot/{name}/log')
async def g2(name: str):
 p=os.path.join(B,name,'bot.log')
 return HTMLResponse(open(p,errors='ignore').read()[-5000:] if os.path.exists(p) else "no log")
@app.get('/api/ls')
async def h(path: str):
 if not path.startswith('/root/'):path=B
 o=[]
 for nm in sorted(os.listdir(path)):
  if nm.startswith('.'):continue
  fp=os.path.join(path,nm);o.append({'n':nm,'p':fp,'d':os.path.isdir(fp)})
 return JSONResponse(o)
@app.get('/api/rd')
async def i(path: str):return HTMLResponse(open(path,errors='ignore').read())
@app.post('/api/wr')
async def j(request: Request):
 d=await request.json();open(d['path'],'w',errors='ignore').write(d['content']);return JSONResponse({'ok':True})
@app.post('/api/rm')
async def k(request: Request):
 d=await request.json();p=d['path']
 try:shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
 except:pass
 return JSONResponse({'ok':True})
@app.post('/api/ex')
async def l(request: Request):
 d=await request.json();p=d['path']
 try:
  with zipfile.ZipFile(p,'r') as z:z.extractall(os.path.dirname(p))
  return JSONResponse({'ok':True,'log':f'Extracted {p}'})
 except Exception as e:return JSONResponse({'ok':False,'log':str(e)})
@app.post('/api/dp')
async def n(request: Request):
 f=await request.form();na=f.get('name');fi=f.get('file');de=os.path.join(B,na);os.makedirs(de,exist_ok=True)
 log=f"Deploy {na}\n"
 if fi:
  da=await fi.read();zp=os.path.join(de,'a.zip');open(zp,'wb').write(da)
  try:
   with zipfile.ZipFile(zp,'r') as z:z.extractall(de)
   log+=f"Extract OK\n"
  except Exception as e:log+=f"Fail {e}\n"
  try:os.remove(zp)
  except:pass
 open(os.path.join(de,'.command'),'w').write(f.get('command') or 'python3 main.py')
 return JSONResponse({'ok':True,'log':log})
@app.get('/api/s')
async def o():
 return JSONResponse({'c':round(psutil.cpu_percent(),1),'m':round(psutil.virtual_memory().used/1024/1024/1024,1),'d':round(psutil.disk_usage('/').used/1024/1024/1024,1)})
