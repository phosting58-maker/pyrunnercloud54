#!/bin/bash
set -e
echo "== CloudPusat54 Auto Re-Installer V10 =="
apt update -y
apt install -y python3-venv python3-pip curl wget git zip unzip psmisc -y
mkdir -p /root/panel /root/apps
python3 -m venv /root/panel-venv
/root/panel-venv/bin/pip install fastapi uvicorn psutil python-multipart --quiet
# Download app.py terbaru dari repo lu sendiri (jadi ga perlu bikin baru)
wget -qO /root/panel/app.py https://raw.githubusercontent.com/phosting58-maker/pyrunnercloud54/main/app.py
# Kalo app.py belum ada di repo, pake fallback minimal
if [! -s /root/panel/app.py ]; then
echo "app.py di repo kosong, pake fallback..."
cat > /root/panel/app.py << 'PYEOF'
from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse,JSONResponse,RedirectResponse
import os,psutil,subprocess,hashlib,time,glob,pathlib,zipfile,shutil
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
MAIN='''<html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>*{box-sizing:border-box;font-family:Inter,system-ui}body{margin:0;background:#08070e;color:#cbd5e1;padding-bottom:110px}body::before{content:'';position:fixed;inset:0;background:radial-gradient(900px at 50% 0%,rgba(120,60,255,.25),transparent 70%);pointer-events:none}.wrap{position:relative;z-index:1;max-width:480px;margin:0 auto;padding:14px}.h{display:flex;justify-content:space-between;padding:14px 18px;background:rgba(8,10,18,.9);border-bottom:1px solid rgba(255,255,255,.08);margin:-14px -14px 14px -14px}.logo{font-weight:900;font-size:19px;color:#fff}.logo span{color:#a78bfa}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:rgba(255,255,255,.08);border-radius:22px;overflow:hidden;margin-bottom:18px}.stat{background:rgba(15,15,28,.9);padding:16px}.stat b{font-size:22px;color:#fff;display:block;margin-top:4px}.sec{background:rgba(15,15,28,.75);border:1px solid rgba(255,255,255,.08);border-radius:26px;padding:18px}.bot{display:flex;justify-content:space-between;align-items:center;padding:14px;background:rgba(10,10,18,.6);border-radius:18px;margin-top:10px}.bottom{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);width:92%;max-width:400px;background:rgba(15,15,28,.95);border:1px solid rgba(255,255,255,.12);border-radius:26px;display:flex;padding:6px;z-index:9999}.bottom div{flex:1;text-align:center;padding:14px 6px;border-radius:18px;font-size:12px;font-weight:800;color:#6b7280;cursor:pointer}.bottom div.on{background:rgba(255,255,255,.1);color:#5eead4}.logbox{background:rgba(0,0,0,.4);border-radius:12px;padding:12px;font-family:monospace;font-size:11px;max-height:300px;overflow:auto;color:#5eead4;white-space:pre-wrap;margin-top:12px}.inp{width:100%;padding:12px;background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.08);border-radius:12px;color:#fff;margin-bottom:10px}</style></head><body><div class=wrap><div class=h><div class=logo>Cloud<span>Pusat54</span></div><a href="/logout" style="color:#64748b;text-decoration:none;font-size:12px">Logout</a></div><div class=grid><div class=stat><label>CPU</label><b id="cpu">-</b></div><div class=stat><label>RAM</label><b id="ram">-</b></div><div class=stat><label>DISK</label><b id="disk">-</b></div></div><div id="p1"><div class=sec><b>MY BOTS</b><div id="bots">Loading...</div><div id="rlog" class=logbox style="display:none"></div></div></div><div id="p2" style="display:none"><div class=sec><span id="cur">/root/apps</span><div id="fl"></div></div></div><div id="p3" style="display:none"><div class=sec><b>Deploy</b><input id="n" class=inp placeholder="Nama bot"><input id="cmd" class=inp value="python3 main.py"><input type="file" id="z"><button style="width:100%;padding:13px;background:#fff;color:#000;border-radius:12px" onclick="dp()">Deploy</button><div id="dl" class=logbox style="display:none"></div></div></div></div><div class=bottom><div id="b1" class="on" onclick="sh(1)">Monitor</div><div id="b2" onclick="sh(2)">Files</div><div id="b3" onclick="sh(3)">Deploy</div></div><script>let cur='/root/apps',sel=null;function sh(x){document.getElementById('p1').style.display=x==1?'block':'none';document.getElementById('p2').style.display=x==2?'block':'none';document.getElementById('p3').style.display=x==3?'block':'none';document.getElementById('b1').className=x==1?'on':'';document.getElementById('b2').className=x==2?'on':'';document.getElementById('b3').className=x==3?'on':'';if(x==2)lf(cur);if(x==1)lm()}function lm(){fetch('/api/s').then(r=>r.json()).then(d=>{document.getElementById('cpu').innerText=d.c+'%';document.getElementById('ram').innerText=d.m+'GB';document.getElementById('disk').innerText=d.d+'GB'});fetch('/api/b').then(r=>r.json()).then(d=>{let h='';for(let x of d){h+='<div class=bot><div><b>'+x[0]+'</b> '+x[1]+'</div><div><button onclick="rb(\\''+x[0]+'\\')">Run</button> <button onclick="sb(\\''+x[0]+'\\')">Stop</button></div></div>'}document.getElementById('bots').innerHTML=h||'No bots'})}function rb(n){fetch('/api/bot/'+n+'/start',{method:'POST'}).then(r=>r.json()).then(d=>{document.getElementById('rlog').style.display='block';document.getElementById('rlog').innerText=d.log;lm()})}function sb(n){fetch('/api/bot/'+n+'/stop',{method:'POST'}).then(()=>lm())}function lf(p){cur=p;fetch('/api/ls?path='+encodeURIComponent(p)).then(r=>r.json()).then(d=>{let h='';for(let x of d){h+='<div onclick="sl(\\''+x.p+'\\','+x.d+')">'+x.n+'</div>'}document.getElementById('fl').innerHTML=h})}function sl(p,d){sel=p;if(d)lf(p)}function dp(){let n=document.getElementById('n').value;let fd=new FormData();fd.append('name',n);fd.append('command',document.getElementById('cmd').value);fd.append('file',document.getElementById('z').files[0]);fetch('/api/dp',{method:'POST',body:fd}).then(r=>r.json()).then(d=>{document.getElementById('dl').style.display='block';document.getElementById('dl').innerText=d.log;lm();sh(1)})}lm();setInterval(lm,3000)</script></body></html>'''
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
   run,pid=is_run(p,n)
   o.append([n,'running' if run else 'stopped',pid])
 return JSONResponse(sorted(o))
@app.post('/api/bot/{name}/start')
async def f(name: str):
 bp=os.path.join(B,name);import pathlib;cf=os.path.join(bp,'.command');cmd=pathlib.Path(cf).read_text().strip() if os.path.exists(cf) else 'python3 main.py'
 for pr in psutil.process_iter(['pid']):
  try:
   if pr.cwd()==bp:pr.kill()
  except:pass
 time.sleep(0.5)
 full=f"cd {bp} && nohup {cmd} > bot.log 2>&1 & echo $!"
 r=subprocess.run(full,shell=True,capture_output=True,text=True,timeout=10)
 open(os.path.join(bp,'.pid'),'w').write(r.stdout.strip())
 return JSONResponse({'log':f'Started {name}'})
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
@app.get('/api/ls')
async def h(path: str):
 if not path.startswith('/root/'):path=B
 o=[]
 for nm in sorted(os.listdir(path)):
  if nm.startswith('.'):continue
  fp=os.path.join(path,nm);o.append({'n':nm,'p':fp,'d':os.path.isdir(fp)})
 return JSONResponse(o)
@app.post('/api/dp')
async def n(request: Request):
 f=await request.form();na=f.get('name');fi=f.get('file');de=os.path.join(B,na);os.makedirs(de,exist_ok=True)
 if fi:
  da=await fi.read();zp=os.path.join(de,'a.zip');open(zp,'wb').write(da)
  try:
   with zipfile.ZipFile(zp,'r') as z:z.extractall(de)
  except:pass
  try:os.remove(zp)
  except:pass
 open(os.path.join(de,'.command'),'w').write(f.get('command') or 'python3 main.py')
 return JSONResponse({'ok':True,'log':f'Deployed {na}'})
@app.get('/api/s')
async def o():
 return JSONResponse({'c':round(psutil.cpu_percent(),1),'m':round(psutil.virtual_memory().used/1024/1024/1024,1),'d':round(psutil.disk_usage('/').used/1024/1024/1024,1)})
PYEOF
fi
cat > /etc/systemd/system/cloud54.service << 'SVC'
[Unit]
Description=CloudPusat54
After=network.target
[Service]
User=root
WorkingDirectory=/root/panel
ExecStart=/root/panel-venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
SVC
systemctl daemon-reload
systemctl enable cloud54
systemctl restart cloud54
IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
echo ""
echo "=================================="
echo "✅ INSTALLED!"
echo "Panel: http://$IP:8000"
echo "Login: admin / cloud54"
echo "Repo: https://github.com/phosting58-maker/pyrunnercloud54.git"
echo "=================================="
