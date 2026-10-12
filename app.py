from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse,JSONResponse,RedirectResponse
import os,psutil,subprocess,hashlib,shutil,zipfile,pathlib,time,glob
app=FastAPI(docs_url=None,redoc_url=None)
B='/root/apps';os.makedirs(B,exist_ok=True);S='cloudpusat54';P=hashlib.sha256(('cloud54'+S).encode()).hexdigest()
def ok(r):return r.cookies.get('auth','')==P
def is_running(bot_path, bot_name):
    pf=os.path.join(bot_path,'.pid')
    if os.path.exists(pf):
        try:
            pid=int(open(pf).read().strip())
            if psutil.pid_exists(pid):
                pr=psutil.Process(pid)
                if pr.is_running() and pr.status()!='zombie':return True,pid
        except:pass
    for pr in psutil.process_iter(['pid','cmdline']):
        try:
            cwd=pr.cwd();cmd=' '.join(pr.info['cmdline'] or [])
            if cwd==bot_path or bot_path in cmd or (bot_name in cmd and 'python' in cmd):
                if 'python' in cmd.lower() or 'main.py' in cmd:return True,pr.info['pid']
            if cwd.startswith(bot_path+'/'):return True,pr.info['pid']
        except:continue
    return False,0
LOGIN="""<html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#070711;color:#fff;font-family:system-ui}.box{width:92%;max-width:360px;background:linear-gradient(145deg,#1e1e45,#151530);border:1px solid #3a3a6a;border-radius:24px;padding:32px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.6)}.logo{font-weight:900;font-style:italic;font-size:30px}.logo span{background:linear-gradient(90deg,#22d3ee,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}input{width:100%;margin-top:14px;padding:14px 16px;border-radius:14px;border:1px solid #3a3a6a;background:#1a1a3a;color:#fff;outline:none}input:focus{border-color:#22d3ee;box-shadow:0 0 0 3px rgba(34,211,238,.2)}button{width:100%;margin-top:18px;padding:14px;border-radius:14px;border:0;background:linear-gradient(90deg,#00e676,#00c853);font-weight:900;color:#000;box-shadow:0 8px 20px rgba(0,230,118,.3)}</style></head><body><div class=box><div class=logo>Cloud<span>Pusat54</span></div><p style=color:#8a8ac0;font-size:13px;margin-top:8px>Premium Panel</p><form method=post action=/login><input name=user placeholder=admin><input name=pass type=password placeholder=cloud54><button>LOGIN</button></form></div></body></html>"""
MAIN="""<html><head><meta name=viewport content="width=device-width,initial-scale=1"><link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap" rel="stylesheet"><style>*{box-sizing:border-box;font-family:'Outfit',system-ui}body{margin:0;background:#070711;color:#e2e2ff;padding-bottom:100px;position:relative;overflow-x:hidden}body::before{content:'';position:fixed;top:0;left:0;right:0;height:600px;background:radial-gradient(600px at 0% 0%,rgba(124,58,237,.25),transparent),radial-gradient(600px at 100% 0%,rgba(34,211,238,.2),transparent);pointer-events:none;z-index:-1}.h{position:sticky;top:0;z-index:10;padding:18px 20px;background:rgba(15,15,35,.8);backdrop-filter:blur(20px);display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,.08)}.logo{font-weight:800;font-style:italic;font-size:20px;color:#fff;letter-spacing:-.5px}.logo span{background:linear-gradient(90deg,#22d3ee,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.h a{font-size:12px;color:#ff7a9a;text-decoration:none;background:rgba(255,100,130,.1);padding:6px 12px;border-radius:20px;border:1px solid rgba(255,100,130,.2)}.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:16px}.mi{position:relative;background:linear-gradient(145deg,rgba(30,30,70,.9),rgba(20,20,50,.9));border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:14px 10px;text-align:center;overflow:hidden}.mi::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.2),transparent)}.mi small{font-size:10px;letter-spacing:1px;color:#8a8ac0;text-transform:uppercase;font-weight:600}.mi b{display:block;margin-top:4px;color:#fff;font-size:20px;font-weight:800}.bar{height:4px;background:rgba(255,255,255,.1);border-radius:10px;margin-top:8px;overflow:hidden}.bar i{display:block;height:100%;border-radius:10px;transition:.5s}.c{margin:16px;background:linear-gradient(145deg,rgba(25,25,60,.9),rgba(18,18,45,.9));border:1px solid rgba(255,255,255,.08);border-radius:24px;padding:18px;backdrop-filter:blur(20px);box-shadow:0 10px 40px rgba(0,0,0,.4)}.c-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}.c-head b{font-size:14px;letter-spacing:.5px}.btn{padding:8px 14px;border-radius:12px;border:0;font-weight:700;font-size:11px;cursor:pointer;transition:.2s;letter-spacing:.3px}.btn:active{transform:scale(.95)}.gr{background:linear-gradient(135deg,#00e676,#00c853);color:#000;box-shadow:0 4px 15px rgba(0,230,118,.3)}.rd{background:rgba(255,80,100,.12);color:#ff8aa0;border:1px solid rgba(255,80,100,.2)}.dk{background:rgba(255,255,255,.06);color:#a0a0d0;border:1px solid rgba(255,255,255,.1)}.bot-card{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;margin:10px 0;background:rgba(0,0,0,.25);border:1px solid rgba(255,255,255,.06);border-radius:16px;position:relative;overflow:hidden;transition:.2s}.bot-card.on{border-left:3px solid #00e676;background:linear-gradient(90deg,rgba(0,230,118,.08),rgba(0,0,0,.2))}.bot-card.off{border-left:3px solid #ff4455;background:linear-gradient(90deg,rgba(255,68,85,.06),rgba(0,0,0,.2))}.bot-info{display:flex;align-items:center;gap:10px}.dot{width:10px;height:10px;border-radius:50%;position:relative}.dot.on{background:#00e676;box-shadow:0 0 12px #00e676,0 0 20px rgba(0,230,118,.5);animation:pulse 2s infinite}.dot.off{background:#ff4455;box-shadow:0 0 10px rgba(255,68,85,.5)}.dot.on::after{content:'';position:absolute;top:-4px;left:-4px;right:-4px;bottom:-4px;border-radius:50%;border:1px solid #00e676;animation:ping 2s infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.7}}@keyframes ping{0%{transform:scale(.8);opacity:1}100%{transform:scale(1.6);opacity:0}}.badge{font-size:9px;padding:3px 8px;border-radius:20px;font-weight:700;letter-spacing:.5px}.badge.on{background:rgba(0,230,118,.15);color:#00e676;border:1px solid rgba(0,230,118,.3)}.badge.off{background:rgba(255,68,85,.12);color:#ff7a9a;border:1px solid rgba(255,68,85,.2)}.log{white-space:pre-wrap;font-size:11px;background:#0a0a1a;padding:14px;border-radius:14px;max-height:320px;overflow:auto;color:#7affa0;border:1px solid rgba(255,255,255,.06);margin-top:12px;font-family:monospace;line-height:1.5}.bt{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);width:92%;max-width:380px;background:rgba(20,20,45,.9);backdrop-filter:blur(25px);display:flex;justify-content:space-around;padding:8px;border-radius:20px;border:1px solid rgba(255,255,255,.1);box-shadow:0 20px 60px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.1)}.bt div{flex:1;text-align:center;padding:10px 6px;border-radius:14px;color:#6a6a8a;cursor:pointer;font-size:12px;font-weight:600;transition:.2s}.bt div.on{background:linear-gradient(135deg,#22d3ee,#7c3aed);color:#fff;box-shadow:0 6px 20px rgba(124,58,237,.4)}.in{width:100%;padding:14px 16px;background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.08);border-radius:14px;color:#fff;font-size:14px;margin-bottom:12px;outline:none;transition:.2s}.in:focus{border-color:#22d3ee;box-shadow:0 0 0 3px rgba(34,211,238,.15);background:rgba(0,0,0,.5)}.file-item{padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.04);cursor:pointer;border-radius:12px;margin:4px 0;display:flex;justify-content:space-between;align-items:center;transition:.2s}.file-item:hover{background:rgba(255,255,255,.06);transform:translateX(4px)}.file-item.sel{background:linear-gradient(90deg,rgba(34,211,238,.15),rgba(124,58,237,.1))!important;border:1px solid rgba(34,211,238,.3)!important}</style></head><body>
<div class=h><div class=logo>Cloud<span>Pusat54</span> <small style=font-size:10px;background:linear-gradient(90deg,#22d3ee,#a78bfa);color:#fff;padding:2px 8px;border-radius:10px;margin-left:8px>PREMIUM</small></div><a href=/logout>Keluar ✕</a></div>
<div id=p1><div class=g3><div class=mi><small>⚡ CPU</small><b id=cpu>-</b><div class=bar><i id=cpu-bar style=width:20%;background:linear-gradient(90deg,#7c3aed,#22d3ee)></i></div></div><div class=mi><small>💾 RAM</small><b id=ram>-</b><div class=bar><i id=ram-bar style=width:40%;background:linear-gradient(90deg,#22d3ee,#00e676)></i></div></div><div class=mi><small>🗄️ DISK</small><b id=disk>-</b><div class=bar><i id=disk-bar style=width:60%;background:linear-gradient(90deg,#f59e0b,#ef4444)></i></div></div></div><div class=c><div class=c-head><b>🤖 MY BOTS</b><button class=btn gr onclick=sh(3)>+ Deploy</button></div><div id=bots>Loading...</div><div id=runlog class=log style=display:none></div></div></div>
<div id=p2 style=display:none><div class=c><div class=c-head><span id=cur style=color:#22d3ee;font-size:11px;font-family:monospace>/root/apps</span><button class=btn dk onclick="lf('/root/apps')">⌂ Root</button></div><div id=files style=margin-top:8px></div></div><div class=c><div style=display:flex;flex-wrap:wrap;gap:6px><button class=btn dk onclick=nf()>+ New</button><button class=btn dk onclick=ef()>✏️ Edit</button><button class=btn gr onclick=sf()>💾 Save</button><button class=btn gr onclick=xf()>📦 Extract</button><button class=btn rd onclick=df()>🗑️ Del</button></div><div id=selinfo style=font-size:10px;color:#6a6a9a;margin-top:10px;font-family:monospace>No file selected</div></div><div class=c id=ec style=display:none><div style=display:flex;justify-content:space-between><small id=en style=color:#22d3ee;font-family:monospace></small><button class=btn dk onclick="ec.style.display='none'">Close</button></div><textarea id=t style=width:100%;height:320px;background:#080818;color:#c8ffc8;font-family:monospace;font-size:12px;border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:12px;margin-top:10px;outline:none></textarea></div></div>
<div id=p3 style=display:none><div class=c><b style=font-size:16px>🚀 Deploy Bot Baru</b><p style=color:#8a8ac0;font-size:12px;margin:6px 0 16px>Upload zip bot kamu</p><input id=n class=in placeholder="Nama bot (contoh: pusat)"><input id=cmd class=in value="python3 main.py"><input type=file id=z style="margin:8px 0;color:#8a8ac0"><button class=btn gr style=width:100%;padding:14px;font-size:13px" onclick=dp()>Deploy Now 🚀</button><div id=dl class=log style=display:none></div></div></div>
<div class=bt><div id=b1 class=on onclick=sh(1)>📊<br>Monitor</div><div id=b2 onclick=sh(2)>📁<br>Files</div><div id=b3 onclick=sh(3)>🚀<br>Deploy</div></div>
<script>
let cur='/root/apps',sel=null
function sh(x){p1.style.display=x==1?'block':'none';p2.style.display=x==2?'block':'none';p3.style.display=x==3?'block':'none';b1.className=x==1?'on':'';b2.className=x==2?'on':'';b3.className=x==3?'on':'';if(x==2)lf(cur);if(x==1)lm()}
function lm(){fetch('/api/s').then(r=>r.json()).then(d=>{cpu.innerText=d.c+'%';ram.innerText=d.m+'GB';disk.innerText=d.d+'GB';document.getElementById('cpu-bar').style.width=d.c+'%';document.getElementById('ram-bar').style.width=Math.min(d.m/4*100,100)+'%';document.getElementById('disk-bar').style.width=Math.min(d.d/20*100,100)+'%'});fetch('/api/b').then(r=>r.json()).then(d=>{let h='';for(let x of d){let on=x[1]=='running';h+=`<div class="bot-card ${on?'on':'off'}"><div class=bot-info><span class="dot ${on?'on':'off'}"></span><div><b style=font-size:14px>${x[0]}</b><div style=display:flex;gap:6px;margin-top:3px><span class="badge ${on?'on':'off'}">${on?'● LIVE':'○ STOPPED'}</span><span style=font-size:10px;color:#6a6a8a>P ID: ${x[2]||'-'}</span></div></div></div><div style=display:flex;gap:4px><button class=btn gr onclick="runBot('${x[0]}')">▶</button><button class=btn rd onclick="stopBot('${x[0]}')">■</button><button class=btn dk onclick="logBot('${x[0]}')">≡</button></div></div>`}bots.innerHTML=h||'<div style=text-align:center;padding:30px;color:#6a6a8a>Belum ada bot<br><small>Klik + Deploy</small></div>'})}
function runBot(n){runlog.style.display='block';runlog.innerText='⏳ Starting '+n+'...';fetch('/api/bot/'+n+'/start',{method:'POST'}).then(r=>r.json()).then(d=>{runlog.innerText=d.log;lm()})}
function stopBot(n){fetch('/api/bot/'+n+'/stop',{method:'POST'}).then(()=>{runlog.style.display='block';runlog.innerText='🛑 Stopped '+n;lm()})}
function logBot(n){fetch('/api/bot/'+n+'/log').then(r=>r.text()).then(t=>{runlog.style.display='block';runlog.innerText=t.slice(-5000)||'📭 No log yet'})}
function lf(p){cur=p;document.getElementById('cur').innerText=p;fetch('/api/ls?path='+encodeURIComponent(p)).then(r=>r.json()).then(d=>{let h='';for(let x of d){let sp=x.p.replace(/'/g,"\\'");h+=`<div class="file-item" onclick="sl('${sp}',${x.d})"><span>${x.d?'📁':'📄'} <b>${x.n}</b></span><small style=color:#5a5a8a>${x.d?'DIR':''}</small></div>`}files.innerHTML=h||'<small style=color:#6a6a8a>Empty folder</small>'})}
function sl(p,d){sel=p;document.getElementById('selinfo').innerText='📍 '+p;if(d){lf(p)}else{ef()}}
function ef(){if(!sel){alert('Klik file dulu!');return;}fetch('/api/rd?path='+encodeURIComponent(sel)).then(r=>r.text()).then(t=>{ec.style.display='block';en.innerText=sel;document.getElementById('t').value=t})}
function sf(){if(!sel){alert('Klik file dulu!');return;}let ct=document.getElementById('t').value;fetch('/api/wr',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel,content:ct})}).then(()=>{alert('✅ Saved '+sel);lf(cur)})}
function xf(){if(!sel)return alert('Pilih zip');fetch('/api/ex',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel})}).then(r=>r.json()).then(d=>{alert(d.log);lf(cur)})}
function df(){if(!sel)return;if(!confirm('Hapus '+sel+'?'))return;fetch('/api/rm',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel})}).then(()=>{ec.style.display='none';sel=null;lf(cur)})}
function nf(){let n=prompt('Nama file baru');if(!n)return;fetch('/api/wr',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:cur+'/'+n,content:''})}).then(()=>lf(cur))}
function dp(){let n=document.getElementById('n').value;if(!n)return alert('isi nama');let fd=new FormData();fd.append('name',n);fd.append('command',document.getElementById('cmd').value);fd.append('file',document.getElementById('z').files[0]);dl.style.display='block';dl.innerText='⏳ Uploading...';fetch('/api/dp',{method:'POST',body:fd}).then(r=>r.json()).then(d=>{dl.innerText=d.log;lm();sh(1)})}
lm();setInterval(()=>{if(p1.style.display!='none')lm()},3000)
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
   run,pid=is_running(p,n)
   o.append([n,'running' if run else 'stopped',pid])
 return JSONResponse(sorted(o))
@app.post('/api/bot/{name}/start')
async def f(name: str):
 bp=os.path.join(B,name)
 cf=os.path.join(bp,'.command');cmd=pathlib.Path(cf).read_text().strip() if os.path.exists(cf) else 'python3 main.py'
 for pr in psutil.process_iter(['pid']):
  try:
   if pr.cwd()==bp:pr.kill()
  except:pass
 time.sleep(1)
 for pat in ['*.db-shm','*.db-wal','*.sqlite-shm','*.sqlite-wal','*.session-journal','FILE_PO/*.db-shm','FILE_PO/*.db-wal','.pid']:
  try:
   for ff in glob.glob(os.path.join(bp,pat)):os.remove(ff)
  except:pass
 venv_py="/root/panel-venv/bin/python";py_to_use=venv_py if os.path.exists(venv_py) else "python3"
 if "python3" in cmd:cmd=cmd.replace("python3",py_to_use)
 if "-u" not in cmd:cmd=cmd.replace(py_to_use,f"{py_to_use} -u")
 full_cmd=f"cd {bp} && nohup {cmd} > bot.log 2>&1 & echo $!"
 try:
  r=subprocess.run(full_cmd,shell=True,capture_output=True,text=True,timeout=10)
  pid=r.stdout.strip()
  try:open(os.path.join(bp,'.pid'),'w').write(pid)
  except:pass
  time.sleep(2.5)
  run,realpid=is_running(bp,name)
  log_content=""
  try:log_content=open(os.path.join(bp,'bot.log'),errors='ignore').read()[-2000:]
  except:pass
  if run:return JSONResponse({'running':True,'log':f'✅ SUKSES RUN {name}\nPID {realpid}\nCMD: {cmd}\n\nLOG:\n{log_content}'})
  else:return JSONResponse({'running':False,'log':f'❌ GAGAL RUN {name}\nCMD: {cmd}\n\nLOG ERROR:\n{log_content}'})
 except Exception as e:return JSONResponse({'running':False,'log':f'Error {e}'})
@app.post('/api/bot/{name}/stop')
async def g(name: str):
 bp=os.path.join(B,name);cnt=0
 for pr in psutil.process_iter(['pid']):
  try:
   if pr.cwd()==bp:pr.kill();cnt+=1
  except:pass
 try:os.remove(os.path.join(bp,'.pid'))
 except:pass
 return JSONResponse({'ok':True,'killed':cnt})
@app.get('/api/bot/{name}/log')
async def g2(name: str):
 bp=os.path.join(B,name,'bot.log')
 if os.path.exists(bp):return HTMLResponse(open(bp,errors='ignore').read()[-5000:])
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
 return JSONResponse({'ok':True,'log':log})
@app.get('/api/s')
async def o():
 return JSONResponse({'c':round(psutil.cpu_percent(),1),'m':round(psutil.virtual_memory().used/1024/1024/1024,1),'d':round(psutil.disk_usage('/').used/1024/1024/1024,1)})
