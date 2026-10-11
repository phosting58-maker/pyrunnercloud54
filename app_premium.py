from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse,JSONResponse,RedirectResponse
import os,psutil,subprocess,hashlib,shutil,zipfile,pathlib
app=FastAPI(docs_url=None,redoc_url=None)
B='/root/apps';os.makedirs(B,exist_ok=True);S='cloudpusat54';P=hashlib.sha256(('cloud54'+S).encode()).hexdigest()
def ok(r):return r.cookies.get('auth','')==P
LOGIN='<html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:radial-gradient(ellipse at top,#1a1a3a,#08080f);color:#fff;font-family:system-ui}.box{width:92%;max-width:360px;background:linear-gradient(135deg,#1e1e3a,#16162a);border:1px solid #2a2a5a;border-radius:24px;padding:32px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.6)}.logo{font-weight:900;font-style:italic;font-size:32px}.logo span{background:linear-gradient(90deg,#22d3ee,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent}input{width:100%;margin-top:12px;padding:14px;border-radius:12px;border:1px solid #2a2a4a;background:#0e0e1f;color:#fff}button{width:100%;margin-top:18px;padding:14px;border-radius:12px;border:0;background:linear-gradient(90deg,#00ff88,#22d3ee);color:#000;font-weight:900}</style></head><body><div class=box><div class=logo>Cloud<span>Pusat54</span></div><div style=color:#5a5a8a;font-size:10px;letter-spacing:3px;margin-top:6px>MULTI BOT CLOUD</div><form method=post action=/login><input name=user placeholder=admin><input name=pass type=password placeholder=cloud54><button>LOGIN</button></form></div></body></html>'''
MAIN='''
<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>CloudPusat54</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#08080f;background-image:radial-gradient(ellipse at top,#151530 0%,#08080f 60%);color:#e0e0ff;font-family:system-ui;padding-bottom:100px;min-height:100vh}
.h{padding:18px 20px;display:flex;justify-content:space-between;align-items:center;background:rgba(15,15,31,.85);backdrop-filter:blur(12px);border-bottom:1px solid #1e1e3a;position:sticky;top:0;z-index:5}
.logo{font-weight:900;font-style:italic;font-size:26px}.logo span{background:linear-gradient(90deg,#22d3ee,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.tt{font-size:28px;font-weight:900;color:#fff;margin:20px 16px 4px 16px}.sb{font-size:10px;color:#5a5a8a;margin:0 16px 14px 16px;letter-spacing:2px}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin:14px 12px}
.mi{background:linear-gradient(135deg,#1c1c36,#131326);border:1px solid #23234a;border-radius:18px;padding:14px;position:relative;overflow:hidden;box-shadow:0 8px 20px rgba(0,0,0,.3)}
.mi::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#22d3ee,transparent);opacity:.6}
.mi.lb{font-size:9px;color:#5a5a8a;letter-spacing:1px}.mi.vl{font-size:22px;font-weight:900;color:#fff;margin-top:4px}
.bar{height:4px;background:#1a1a35;border-radius:2px;margin-top:10px;overflow:hidden}.bar i{display:block;height:100%;border-radius:2px}
.c{background:linear-gradient(135deg,#19192f,#121223);border:1px solid #23234a;border-radius:20px;padding:16px;margin:12px;box-shadow:0 8px 32px rgba(0,0,0,.4)}
.r{display:flex;justify-content:space-between;align-items:center;padding:14px 0;border-bottom:1px solid #1e1e3a}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px}.on{background:#00ff88;box-shadow:0 0 8px #00ff88}.off{background:#ff5a7a;box-shadow:0 0 8px #ff5a7a}
.btn{padding:8px 14px;border-radius:10px;border:0;font-weight:800;font-size:11px;cursor:pointer}.gr{background:linear-gradient(135deg,#00ff88,#22d3ee);color:#000}.rd{background:#1e1e35;color:#ff5a7a;border:1px solid #2a2a4a}.dk{background:#1a1a32;color:#8a8ab0;border:1px solid #23234a}
.bt{position:fixed;bottom:12px;left:12px;right:12px;background:rgba(15,15,31,.9);backdrop-filter:blur(16px);border:1px solid #23234a;border-radius:20px;display:flex;justify-content:space-around;padding:8px;z-index:10;box-shadow:0 10px 40px rgba(0,0,0,.6)}
.bt div{padding:10px 18px;border-radius:12px;color:#5a5a8a;font-weight:700;font-size:12px;cursor:pointer}.bt div.ac{background:linear-gradient(135deg,#1e1e3a,#2a2a5a);color:#22d3ee;box-shadow:0 4px 12px rgba(34,211,238,.2)}
.ft{text-align:center;padding:18px;color:#2a2a4a;font-size:9px;letter-spacing:2px}
</style></head><body>
<div class=h><div class=logo>Cloud<span>Pusat54</span></div><a href=/logout style=color:#ff5a7a;text-decoration:none;font-weight:800;font-size:12px;background:#1e1e35;padding:8px 14px;border-radius:10px;border:1px solid #2a2a4a>Keluar</a></div>
<div id=p1><div class=tt>Monitor</div><div class=sb>DASHBOARD • ONLINE</div>
<div class=g3><div class=mi><div class=lb>CPU • Load</div><div class=vl id=cpu>-</div><div class=bar><i id=cb style="background:linear-gradient(90deg,#00ff88,#22d3ee);width:0%"></i></div></div><div class=mi><div class=lb>RAM • Used</div><div class=vl id=ram>-</div><div class=bar><i id=rb style="background:linear-gradient(90deg,#22d3ee,#8b5cf6);width:0%"></i></div></div><div class=mi><div class=lb>DISK • Used</div><div class=vl id=disk>-</div><div class=bar><i id=db style="background:linear-gradient(90deg,#8b5cf6,#ff5a7a);width:0%"></i></div></div></div>
<div class=c><div style=display:flex;justify-content:space-between><b style=font-size:12px;letter-spacing:1px>BOTS • <span id=bc style=color:#22d3ee>0</span></b><button class=btn gr onclick=sh(3)>+ Deploy</button></div><div id=bots>Loading...</div></div></div>
<div id=p2 style=display:none><div class=tt>Files</div><div class=sb>BROWSE • EDIT • EXTRACT</div><div class=c><div style=display:flex;justify-content:space-between><span id=cur style=color:#22d3ee;font-size:12px;font-weight:700>/root/apps</span><button class=btn dk onclick=up()>↑ Up</button></div><div id=files style=margin-top:12px></div></div><div class=c><div style=display:flex;gap:6px;flex-wrap:wrap><button class=btn dk onclick=nf()>+ New</button><button class=btn dk onclick=ef()>Edit</button><button class=btn gr onclick=sf() id=sv style=display:none>Save</button><button class=btn gr onclick=xf()>Extract</button><button class=btn rd onclick=df()>Delete</button><button class=btn dk onclick=document.getElementById('u').click()>Upload</button></div><input type=file id=u style=display:none onchange=uf(this)></div><div class=c id=ec style=display:none><textarea id=t style=width:100%;height:200px;background:#0a0a12;color:#fff;border:1px solid #23234a;border-radius:12px;padding:10px;font-family:monospace></textarea></div></div>
<div id=p3 style=display:none><div class=tt>Deploy</div><div class=sb>UPLOAD ZIP & RUN</div><div class=c><input id=n placeholder='nama bot' style=width:100%;padding:14px;background:#0a0a12;border:1px solid #2a2a4a;border-radius:12px;color:#fff;margin-bottom:10px><input id=cmd value='python3 main.py' style=width:100%;padding:14px;background:#0a0a12;border:1px solid #2a2a4a;border-radius:12px;color:#fff;margin-bottom:10px><input type=file id=z accept=.zip style=margin:8px 0><br><button class=btn gr style=width:100%;padding:14px onclick=dp()>🚀 Deploy Now</button><div id=dl style=margin-top:10px;font-size:11px;color:#7dd3a0;white-space:pre-wrap></div></div></div>
<div class=ft>CLOUDPUSAT54 • PREMIUM • BUILT FOR BOTS</div>
<div class=bt><div id=b1 class=ac onclick=sh(1)>◫ Monitor</div><div id=b2 onclick=sh(2)>📁 Files</div><div id=b3 onclick=sh(3)>☁️ Deploy</div></div>
<script>
let cur='/root/apps',sel=null,isD=false
function sh(x){p1.style.display=x==1?'block':'none';p2.style.display=x==2?'block':'none';p3.style.display=x==3?'block':'none';b1.className=x==1?'ac':'';b2.className=x==2?'ac':'';b3.className=x==3?'ac':'';if(x==2)lf(cur);if(x==1)lm()}
function lm(){fetch('/api/s').then(r=>r.json()).then(d=>{cpu.innerText=d.c+'%';ram.innerText=d.m+'GB';disk.innerText=d.d+'GB';cb.style.width=d.c+'%';rb.style.width=(d.m/d.mt*100)+'%';db.style.width=(d.d/d.dt*100)+'%'});
fetch('/api/b').then(r=>r.json()).then(d=>{bc.innerText=d.length;let h='';for(let x of d){let on=x[1]=='running';h+=`<div class=r><span><span class="dot ${on?'on':'off'}"></span><b>${x[0]}</b> <small style=color:#5a5a8a> ${x[1]}</small></span><span><button class=btn gr onclick="fetch('/api/bot/${x[0]}/start',{method:'POST'}).then(lm)">Run</button><button class=btn rd onclick="fetch('/api/bot/${x[0]}/stop',{method:'POST'}).then(lm)">Stop</button></span></div>`}bots.innerHTML=h||'No bots'})}
function lf(p){cur=p;document.getElementById('cur').innerText=p;fetch('/api/ls?path='+encodeURIComponent(p)).then(r=>r.json()).then(d=>{let h='';for(let x of d)h+=`<div class=r onclick="sl('${x.p}',${x.d})" style="${sel==x.p?'background:#1c1c36;border-radius:10px':''}"><span>${x.d?'📁':'📄'} ${x.n}</span></div>`;files.innerHTML=h})}
function sl(p,d){sel=p;isD=d;if(d)lf(p)}
function up(){if(cur=='/root/apps')return;let u=cur.split('/').slice(0,-1).join('/');if(u.length<11)u='/root/apps';lf(u)}
function ef(){if(!sel||isD)return alert('pilih file');fetch('/api/rd?path='+encodeURIComponent(sel)).then(r=>r.text()).then(t=>{ec.style.display='block';sv.style.display='inline-block';document.getElementById('t').value=t})}
function sf(){fetch('/api/wr',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel,content:document.getElementById('t').value})}).then(()=>{alert('Saved');lf(cur)})}
function xf(){if(!sel)return;fetch('/api/ex',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel})}).then(r=>r.json()).then(d=>{alert(d.log);lf(cur)})}
function df(){if(!sel)return;if(!confirm('hapus?'))return;fetch('/api/rm',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:sel})}).then(()=>lf(cur))}
function nf(){let n=prompt('nama file:');if(!n)return;fetch('/api/wr',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:cur+'/'+n,content:''})}).then(()=>lf(cur))}
function uf(i){let fd=new FormData();fd.append('file',i.files[0]);fd.append('path',cur);fetch('/api/up',{method:'POST',body:fd}).then(()=>lf(cur))}
function dp(){let n=document.getElementById('n').value;if(!n)return alert('nama');let fd=new FormData();fd.append('name',n);fd.append('command',document.getElementById('cmd').value);fd.append('file',document.getElementById('z').files[0]);dl.innerText='Deploying...';fetch('/api/dp',{method:'POST',body:fd}).then(r=>r.json()).then(d=>{dl.innerText=d.log;lm()})}
lm();setInterval(lm,4000)
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
 bp=os.path.join(B,name);cf=os.path.join(bp,'.command');cmd=pathlib.Path(cf).read_text().strip() if os.path.exists(cf) else 'python3 main.py'
 for pr in psutil.process_iter(['pid','cmdline']):
  try:
   cl=' '.join(pr.info['cmdline'] or [])
   if B in cl and name in cl:psutil.Process(pr.info['pid']).kill()
  except:pass
 subprocess.Popen(f"nohup {cmd} > bot.log 2>&1 &",cwd=bp,shell=True);return JSONResponse({'ok':True})
@app.post('/api/bot/{name}/stop')
async def g(name: str):
 for pr in psutil.process_iter(['pid','cmdline']):
  try:
   cl=' '.join(pr.info['cmdline'] or [])
   if B in cl and name in cl:psutil.Process(pr.info['pid']).kill()
  except:pass
 return JSONResponse({'ok':True})
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
@app.post('/api/up')
async def m(request: Request):
 f=await request.form();pa=f.get('path');fi=f.get('file');de=os.path.join(pa,fi.filename);open(de,'wb').write(await fi.read())
 if de.endswith('.zip'):
  try:
   with zipfile.ZipFile(de,'r') as z:z.extractall(pa)
  except:pass
 return JSONResponse({'ok':True})
@app.post('/api/dp')
async def n(request: Request):
 f=await request.form();na=f.get('name');fi=f.get('file');de=os.path.join(B,na);os.makedirs(de,exist_ok=True)
 if fi:
  da=await fi.read();zp=os.path.join(de,'a.zip');open(zp,'wb').write(da)
  with zipfile.ZipFile(zp,'r') as z:z.extractall(de)
  os.remove(zp)
  co=f.get('command');open(os.path.join(de,'.command'),'w').write(co or 'python3 main.py')
 return JSONResponse({'ok':True,'log':f'Deployed {na}'})
@app.get('/api/s')
async def o():
 import psutil as pu
 return JSONResponse({'c':round(pu.cpu_percent(),1),'m':round(pu.virtual_memory().used/1024/1024/1024,1),'mt':round(pu.virtual_memory().total/1024/1024/1024,1),'d':round(pu.disk_usage('/').used/1024/1024/1024,1),'dt':round(pu.disk_usage('/').total/1024/1024/1024,1)})
