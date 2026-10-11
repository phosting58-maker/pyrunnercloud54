from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse,JSONResponse,RedirectResponse
import os,psutil,subprocess,hashlib,shutil,zipfile,pathlib,time
app=FastAPI(docs_url=None,redoc_url=None)
B='/root/apps';os.makedirs(B,exist_ok=True);S='cloudpusat54';P=hashlib.sha256(('cloud54'+S).encode()).hexdigest()
def ok(r):return r.cookies.get('auth','')==P
LOGIN="""<html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0e0e22;color:#fff;font-family:system-ui}.b{width:92%;max-width:360px;background:#23234d;border:1px solid #5a5aaa;border-radius:20px;padding:28px;text-align:center}.logo{font-weight:900;font-style:italic;font-size:28px;color:#fff}.logo span{color:#22d3ee}input{width:100%;margin-top:12px;padding:14px;border-radius:12px;border:1px solid #5a5aaa;background:#2e2e5a;color:#fff;font-size:15px}input::placeholder{color:#9a9ac0}button{width:100%;margin-top:16px;padding:14px;border-radius:12px;border:0;background:#00e676;font-weight:900;color:#000}</style></head><body><div class=b><div class=logo>Cloud<span>Pusat54</span></div><form method=post action=/login><input name=user placeholder="admin"><input name=pass type=password placeholder="cloud54"><button>LOGIN</button></form></div></body></html>"""
MAIN="""<html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>*{box-sizing:border-box}body{margin:0;background:#08080f;color:#e0e0ff;font-family:system-ui;padding-bottom:90px}.h{padding:16px;background:#1c1c3a;display:flex;justify-content:space-between;border-bottom:1px solid #4a4a8a}.logo{font-weight:900;font-style:italic;color:#fff}.logo span{color:#22d3ee}.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:12px}.mi{background:#2a2a5a;border:1px solid #5a5aaa;border-radius:14px;padding:12px;text-align:center}.mi b{display:block;color:#fff;font-size:18px}.c{margin:12px;background:#22224a;border:1px solid #5a5aaa;border-radius:16px;padding:14px}.btn{padding:8px 12px;border-radius:8px;border:0;font-weight:800;font-size:11px;margin:2px}.gr{background:#00ff88;color:#000}.rd{background:#2a2a4a;color:#ff8a9a;border:1px solid #5a5aaa}.dk{background:#2a2a4a;color:#a0a0d0;border:1px solid #5a5aaa}.in{width:100%;padding:14px;background:#2e2e5a;border:1px solid #6a6abb;border-radius:10px;color:#fff;font-size:15px;margin-bottom:10px}.bt{position:fixed;bottom:10px;left:10px;right:10px;background:#1c1c3a;display:flex;justify-content:space-around;padding:10px;border-radius:14px;border:1px solid #4a4a8a}.bt div{padding:8px 14px;border-radius:10px;color:#6a6a8a}.bt div.on{background:#3a3a6a;color:#22d3ee}.log{white-space:pre-wrap;font-size:11px;background:#111126;padding:10px;border-radius:10px;max-height:300px;overflow:auto;color:#7affa0;border:1px solid #3a3a6a;margin-top:10px}</style></head><body>
<div class=h><div class=logo>Cloud<span>Pusat54</span></div><a href=/logout style=color:#ff8a9a;text-decoration:none>Keluar</a></div>
<div id=p1><div class=g3><div class=mi>CPU<b id=cpu>-</b></div><div class=mi>RAM<b id=ram>-</b></div><div class=mi>DISK<b id=disk>-</b></div></div><div class=c><div style=display:flex;justify-content:space-between><b>BOTS</b><button class=btn gr onclick=sh(3)>+ Deploy</button></div><div id=bots>Loading...</div><div id=runlog class=log style=display:none></div></div></div>
<div id=p2 style=display:none><div class=c><span id=cur style=color:#22d3ee>/root/apps</span><div id=files></div></div><div class=c><button class=btn dk onclick=nf()>+New</button><button class=btn dk onclick=ef()>Edit</button><button class=btn gr onclick=sf() id=sv style=display:none>Save</button><button class=btn gr onclick=xf()>Extract</button><button class=btn rd onclick=df()>Delete</button></div><div class=c id=ec style=display:none><textarea id=t style=width:100%;height:150px;background:#1a1a3a;color:#fff></textarea></div></div>
<div id=p3 style=display:none><div class=c><input id=n class=in placeholder="NAMA BOT"><input id=cmd class=in value="python3 main.py"><input type=file id=z><button class=btn gr style=width:100%;padding:12px" onclick=dp()>Deploy Now</button><div id=dl class=log style=display:none></div></div></div>
<div class=bt><div id=b1 class=on onclick=sh(1)>Monitor</div><div id=b2 onclick=sh(2)>Files</div><div id=b3 onclick=sh(3)>Deploy</div></div>
<script>
let cur='/root/apps',sel=null
function sh(x){p1.style.display=x==1?'block':'none';p2.style.display=x==2?'block':'none';p3.style.display=x==3?'block':'none';b1.className=x==1?'on':'';b2.className=x==2?'on':'';b3.className=x==3?'on':'';if(x==2)lf(cur);if(x==1)lm()}
function lm(){fetch('/api/s').then(r=>r.json()).then(d=>{cpu.innerText=d.c+'%';ram.innerText=d.m+'GB';disk.innerText=d.d+'GB'});fetch('/api/b').then(r=>r.json()).then(d=>{let h='';for(let x of d){let on=x[1]=='running';h+=`<div style=display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #3a3a6a><span>${on?'ON':'OFF'} <b>${x[0]}</b> <small style=color:#8a8ac0>${x[1]}</small></span><span><button class=btn gr onclick="runBot('${x[0]}')">Run</button><button class=btn rd onclick="stopBot('${x[0]}')">Stop</button><button class=btn dk onclick="logBot('${x[0]}')">Log</button></span></div>`}bots.innerHTML=h||'No bots'})}
function runBot(n){runlog.style.display='block';runlog.innerText='Starting '+n+'...';fetch('/api/bot/'+n+'/start',{method:'POST'}).then(r=>r.json()).then(d=>{runlog.innerText=d.log;lm()})}
function stopBot(n){fetch('/api/bot/'+n+'/stop',{method:'POST'}).then(()=>{runlog.style.display='block';runlog.innerText='Stopped '+n;lm()})}
function logBot(n){fetch('/api/bot/'+n+'/log').then(r=>r.text()).then(t=>{runlog.style.display='block';runlog.innerText=t.slice(-3000)||'no log'})}
function lf(p){cur=p;document.getElementById('cur').innerText=p;fetch('/api/ls?path='+encodeURIComponent(p)).then(r=>r.json()).then(d=>{let h='';for(let x of d)h+=`<div onclick="sl('${x.p}',${x.d})" style=padding:8px;border-bottom:1px solid #2a2a4a>${x.d?'DIR':'FILE'} ${x.n}</div>`;files.innerHTML=h})}
function sl(p,d){sel=p;if(d)lf(p)}
function ef(){if(!sel)return;fetch('/api/rd?path='+encodeURIComponent(sel)).then(r=>r.text()).then(t=>{ec.style.display='block';sv.style.display='inline-block';document.getElementById('t').value=t})}
function sf(){fetch('/api/wr',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel,content:document.getElementById('t').value})}).then(()=>alert('Saved'))}
function xf(){fetch('/api/ex',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel})}).then(r=>r.json()).then(d=>{alert(d.log);lf(cur)})}
function df(){fetch('/api/rm',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel})}).then(()=>lf(cur))}
function nf(){let n=prompt('nama');if(!n)return;fetch('/api/wr',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:cur+'/'+n,content:''})}).then(()=>lf(cur))}
function dp(){let n=document.getElementById('n').value;if(!n)return alert('isi nama');let fd=new FormData();fd.append('name',n);fd.append('command',document.getElementById('cmd').value);fd.append('file',document.getElementById('z').files[0]);dl.style.display='block';dl.innerText='Uploading...';fetch('/api/dp',{method:'POST',body:fd}).then(r=>r.json()).then(d=>{dl.innerText=d.log;lm();sh(1)})}
lm()
</script></body></html>"""
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
 for n in os.listdir(B):
  p=os.path.join(B,n)
  if os.path.isdir(p) and not n.startswith('.'):
   run=False
   for pr in psutil.process_iter(['cmdline']):
    try:
     cl=' '.join(pr.info['cmdline'] or [])
     if B in cl and n in cl:run=True
    except:pass
   o.append([n,'running' if run else 'stopped'])
 return JSONResponse(sorted(o))
@app.post('/api/bot/{name}/start')
async def f(name: str):
 bp=os.path.join(B,name)
 if not os.path.isdir(bp):return JSONResponse({'running':False,'log':f'Folder {bp} tidak ada','detail':'Folder hilang'})
 cf=os.path.join(bp,'.command');cmd=pathlib.Path(cf).read_text().strip() if os.path.exists(cf) else 'python3 main.py'
 for pr in psutil.process_iter(['pid','cmdline']):
  try:
   cl=' '.join(pr.info['cmdline'] or [])
   if B in cl and name in cl:psutil.Process(pr.info['pid']).kill()
  except:pass
 time.sleep(0.8)
 # hapus lock sqlite yang bikin database is locked
 for ext in ['*.db-shm','*.db-wal','*.sqlite-shm','*.sqlite-wal','*.session-journal']:
  try:
   import glob
   for ff in glob.glob(os.path.join(bp,ext)):os.remove(ff)
  except:pass
 main_path=os.path.join(bp,'main.py')
 if not os.path.exists(main_path):
  pys=[f for f in os.listdir(bp) if f.endswith('.py')]
  if pys:cmd=f"python3 {pys[0]}"
  else:return JSONResponse({'running':False,'log':f'main.py tidak ada di {bp}\nIsi: {os.listdir(bp)}','detail':'main.py hilang'})
 venv_py="/root/panel-venv/bin/python"
 py_to_use=venv_py if os.path.exists(venv_py) else "python3"
 if "python3" in cmd:cmd=cmd.replace("python3",py_to_use)
 full_cmd=f"cd {bp} && nohup {cmd} > bot.log 2>&1 & echo $!"
 try:
  r=subprocess.run(full_cmd,shell=True,capture_output=True,text=True,timeout=10)
  pid=r.stdout.strip()
  time.sleep(2)
  running=False
  for pr in psutil.process_iter(['pid','cmdline']):
   try:
    cl=' '.join(pr.info['cmdline'] or [])
    if B in cl and name in cl:running=True
   except:pass
  log_content=""
  try:log_content=open(os.path.join(bp,'bot.log'),errors='ignore').read()[-1500:]
  except:pass
  if running:
   return JSONResponse({'running':True,'log':f'SUKSES RUN {name}\nPID {pid}\nCMD: {cmd}\n\nLOG:\n{log_content}'})
  else:
   return JSONResponse({'running':False,'log':f'GAGAL RUN {name}\nCMD: {cmd}\n\nLOG ERROR:\n{log_content}\n\nCek requirements atau token!','detail':log_content})
 except Exception as e:
  return JSONResponse({'running':False,'log':f'Error {e}','detail':str(e)})
@app.post('/api/bot/{name}/stop')
async def g(name: str):
 cnt=0
 for pr in psutil.process_iter(['pid','cmdline']):
  try:
   cl=' '.join(pr.info['cmdline'] or [])
   if B in cl and name in cl:psutil.Process(pr.info['pid']).kill();cnt+=1
  except:pass
 return JSONResponse({'ok':True,'killed':cnt})
@app.get('/api/bot/{name}/log')
async def g2(name: str):
 bp=os.path.join(B,name,'bot.log')
 if os.path.exists(bp):return HTMLResponse(open(bp,errors='ignore').read()[-4000:])
 return HTMLResponse("no log")
@app.get('/api/ls')
async def h(path: str):
 if not path.startswith(B):path=B
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
  except Exception as e:log+=f"Extract fail {e}\n"
  try:os.remove(zp)
  except:pass
  open(os.path.join(de,'.command'),'w').write(f.get('command') or 'python3 main.py')
  req=os.path.join(de,'requirements.txt')
  if os.path.exists(req):
   log+="Install requirements...\n"
   try:
    r=subprocess.run(["/root/panel-venv/bin/pip","install","-r",req],cwd=de,capture_output=True,text=True,timeout=180)
    log+=r.stdout[-800:]+"\n"
   except Exception as e:log+=f"pip err {e}\n"
  cmd=open(os.path.join(de,'.command')).read().strip()
  venv_py="/root/panel-venv/bin/python"
  if "python3" in cmd and os.path.exists(venv_py):cmd=cmd.replace("python3",venv_py)
  try:
   subprocess.Popen(f"cd {de} && nohup {cmd} > bot.log 2>&1 &",shell=True)
   log+=f"Auto started {cmd}\n"
  except Exception as e:log+=f"Start fail {e}\n"
 return JSONResponse({'ok':True,'log':log})
@app.get('/api/s')
async def o():
 return JSONResponse({'c':round(psutil.cpu_percent(),1),'m':round(psutil.virtual_memory().used/1024/1024/1024,1),'mt':1,'d':round(psutil.disk_usage('/').used/1024/1024/1024,1),'dt':1})
