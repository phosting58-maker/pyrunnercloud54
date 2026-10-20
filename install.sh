#!/bin/bash
set -e
echo "=== PyRunnerCloud54 V14 PERMANEN ==="
if [ "$EUID" -ne 0 ]; then echo "Harus root"; exit 1; fi
apt-get update -y -q
apt-get install -y -q python3 python3-venv python3-pip git curl zip unzip -q || true
mkdir -p /root/panel/logs /root/apps
rm -rf /root/panel/panel-venv /root/panel/__pycache__ 2>/dev/null || true

cat > /root/panel/app.py << 'PY'
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import subprocess, os, shutil, zipfile, time, psutil
from datetime import datetime
BASE_DIR=Path(__file__).parent
APPS_DIR=Path("/root/apps"); APPS_DIR.mkdir(exist_ok=True)
LOGS_DIR=Path("/root/panel/logs"); LOGS_DIR.mkdir(parents=True,exist_ok=True)
app=FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
def is_running(n):
 p=APPS_DIR/n/"bot.pid"
 if p.exists():
  try: return psutil.pid_exists(int(p.read_text().strip()))
  except: return False
 return False
def get_pid(n):
 try: return int((APPS_DIR/n/"bot.pid").read_text().strip())
 except: return 0
@app.get("/",response_class=HTMLResponse)
async def root(): return HTMLResponse((BASE_DIR/"index.html").read_text(encoding="utf-8"))
@app.get("/api/status")
async def status(): return {"cpu":psutil.cpu_percent(),"ram":psutil.virtual_memory().percent,"disk":psutil.disk_usage("/").percent}
@app.post("/api/login")
async def login(req:Request):
 d=await req.json()
 if d.get("username")=="admin" and d.get("password")=="cloud54": return {"ok":True}
 raise HTTPException(401,"salah")
@app.get("/api/apps")
async def list_apps():
 out=[]
 for d in APPS_DIR.iterdir():
  if not d.is_dir() or d.name.startswith("."): continue
  if not (d/"main.py").exists(): continue
  out.append({"name":d.name,"running":is_running(d.name),"pid":get_pid(d.name)})
 return out
@app.post("/api/apps/{name}/start")
async def start_app(name:str):
 ap=APPS_DIR/name; main=ap/"main.py"; log=LOGS_DIR/f"{name}.log"; pidf=ap/"bot.pid"
 if not main.exists(): raise HTTPException(400,"main.py not found")
 if pidf.exists():
  try: os.kill(int(pidf.read_text()),9)
  except: pass
  pidf.unlink(missing_ok=True)
 with open(log,"a") as lf:
  lf.write(f"\n--- START {datetime.now()} ---\n")
  proc=subprocess.Popen(["/root/panel/panel-venv/bin/python","-u",str(main)],cwd=str(ap),stdout=lf,stderr=subprocess.STDOUT,start_new_session=True)
 pidf.write_text(str(proc.pid)); (ap/".should_run").write_text("1")
 time.sleep(1); return {"ok":True,"pid":proc.pid}
@app.post("/api/apps/{name}/stop")
async def stop_app(name:str):
 pidf=APPS_DIR/name/"bot.pid"; should=APPS_DIR/name/".should_run"
 if pidf.exists():
  try: os.kill(int(pidf.read_text()),9)
  except: pass
  pidf.unlink(missing_ok=True)
 if should.exists(): should.unlink()
 return {"ok":True}
@app.get("/api/apps/{name}/logs")
async def logs(name:str):
 p=LOGS_DIR/f"{name}.log"
 return {"logs":p.read_text(errors="ignore")[-8000:] if p.exists() else "no log"}
@app.get("/api/files")
async def files(path:str="/root/apps"):
 p=Path(path)
 if p.is_file(): return {"type":"file","path":str(p),"content":p.read_text(errors="ignore")[-10000:]}
 return {"type":"dir","path":str(p),"items":[{"name":c.name,"path":str(c),"is_dir":c.is_dir()} for c in p.iterdir()]}
@app.post("/api/files/write")
async def wr(req:Request):
 d=await req.json(); Path(d["path"]).write_text(d["content"]); return {"ok":True}
@app.post("/api/files/delete")
async def dl(req:Request):
 d=await req.json(); p=Path(d["path"]); shutil.rmtree(p,ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True); return {"ok":True}
@app.post("/api/files/upload")
async def up(path:str="/root/apps",file:UploadFile=File(...)):
 dest=Path(path)/file.filename; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(await file.read())
 if dest.suffix==".zip":
  with zipfile.ZipFile(dest) as z: z.extractall(dest.parent)
  dest.unlink()
 return {"ok":True}
@app.post("/api/deploy")
async def dep(req:Request):
 d=await req.json(); n=d.get("name","pusat").replace(" ","_"); p=APPS_DIR/n; p.mkdir(exist_ok=True); (p/"main.py").write_text(d.get("code","")); return {"ok":True,"name":n}
@app.post("/api/deploy/upload")
async def depu(name:str=Form(...),file:UploadFile=File(...)):
 bd=APPS_DIR/name; bd.mkdir(exist_ok=True); dst=bd/file.filename; dst.write_bytes(await file.read())
 if dst.suffix==".zip":
  with zipfile.ZipFile(dst) as z: z.extractall(bd)
  dst.unlink()
 elif dst.suffix==".py" and dst.name!="main.py": dst.rename(bd/"main.py")
 return {"ok":True,"name":name}
@app.post("/api/files/extract")
async def ex(req:Request):
 d=await req.json(); p=Path(d["path"])
 with zipfile.ZipFile(p) as z: z.extractall(p.parent); return {"ok":True}
PY

cat > /root/panel/watchdog.py << 'PY'
import time, subprocess, psutil
from pathlib import Path
APPS_DIR=Path("/root/apps"); LOGS_DIR=Path("/root/panel/logs")
def is_running(p):
 if not p.exists(): return False
 try: return psutil.pid_exists(int(p.read_text().strip()))
 except: return False
print("WATCHDOG START")
while True:
 for bot in APPS_DIR.iterdir():
  if not bot.is_dir() or not (bot/"main.py").exists(): continue
  should=bot/".should_run"; pidf=bot/"bot.pid"; log=LOGS_DIR/f"{bot.name}.log"
  if should.exists() and not is_running(pidf):
   try:
    with open(log,"a") as lf:
     lf.write(f"\n--- AUTO RESTART {time.ctime()} ---\n")
     proc=subprocess.Popen(["/root/panel/panel-venv/bin/python","-u",str(bot/"main.py")],cwd=str(bot),stdout=lf,stderr=subprocess.STDOUT,start_new_session=True)
    pidf.write_text(str(proc.pid))
   except: pass
 time.sleep(10)
PY

cat > /root/panel/autostart.py << 'PY'
import subprocess
from pathlib import Path
APPS=Path("/root/apps"); LOGS=Path("/root/panel/logs"); LOGS.mkdir(parents=True,exist_ok=True)
for d in APPS.iterdir():
 if d.is_dir() and (d/"main.py").exists():
  try:
   with open(LOGS/f"{d.name}.log","a") as lf:
    subprocess.Popen(["/root/panel/panel-venv/bin/python","-u",str(d/"main.py")],cwd=str(d),stdout=lf,stderr=subprocess.STDOUT,start_new_session=True)
  except: pass
print("autostart done")
PY

cat > /root/panel/requirements.txt << 'PY'
fastapi
uvicorn
psutil
python-multipart
PY

cat > /root/panel/index.html << 'HTML'
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CloudPusat54</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;800&display=swap" rel="stylesheet">
<style>*{box-sizing:border-box}body{margin:0;background:#0d0a1a;color:#fff;font-family:Inter,sans-serif}
.header{padding:16px;text-align:center;border-bottom:1px solid #1e1a32;position:sticky;top:0;background:#0d0a1a;z-index:10}
.logo{font-weight:800;font-size:26px}.logo span{color:#8b7cf7}.welcome{margin-top:6px;background:linear-gradient(90deg,#8b7cf7,#3dc5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:13px;letter-spacing:2px}
.stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:0;padding:12px}
.scard{padding:16px 14px}.scard:first-child{background:linear-gradient(135deg,#13232e,#12131f);border-radius:20px 0 0 20px;border:1px solid #1c2a33;border-right:0}
.scard:nth-child(2){background:linear-gradient(135deg,#2a2050,#1a1830);border:1px solid #2d2655;border-left:0;border-right:0}
.scard:last-child{background:linear-gradient(135deg,#1e2f4a,#181c2f);border-radius:0 20px 20px 0;border:1px solid #22405f;border-left:0}
.scard small{color:#7a758f;font-size:11px}.scard b{font-size:22px;display:block;margin:6px 0 10px}.bar{height:4px;background:#1f1b33;border-radius:10px;overflow:hidden}.bar i{display:block;height:100%}
.bots-wrap{margin:10px 12px;background:#151121;border:1px solid #23203a;border-radius:20px;padding:14px}
.bot{background:#1c1830;border:1px solid #2a2645;border-radius:22px;padding:14px;display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.live{background:#0d2a1e;color:#00ff88;border:1px solid #1a4d33;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}.off{background:#2a1a1a;color:#ff4d4d;border:1px solid #4a1f1f;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}
.btn{border:0;border-radius:20px;padding:10px 18px;font-weight:800;font-size:14px;cursor:pointer;touch-action:manipulation}
.run{background:#fff;color:#000}.stop{background:#211821;color:#ff4d4d;border:1px solid #3a1f2a}.log{background:#211e32;color:#9a96b5;border:1px solid #2e2b4a}
.tabs{display:flex;gap:8px;padding:0 12px 12px}.tab{padding:8px 14px;border-radius:20px;background:#1a1730;border:1px solid #2a2645;color:#7a758f;font-size:13px;cursor:pointer}.tab.active{background:#8b7cf7;color:#fff}
.file{padding:10px;border-bottom:1px solid #1e1a32;display:flex;justify-content:space-between;align-items:center}
input,textarea{width:100%;padding:10px;border-radius:12px;border:1px solid #2a2645;background:#0f0c1c;color:#fff;margin:5px 0}
pre{background:#000;color:#0f0;padding:10px;border-radius:12px;max-height:320px;overflow:auto;white-space:pre-wrap}
.login{position:fixed;inset:0;background:#0d0a1a;z-index:999;display:flex;align-items:center;justify-content:center}
.uploadBox{border:1px dashed #3a3560;background:#0f0c1c;border-radius:16px;padding:14px;text-align:center;margin:10px 0}
</style></head><body>
<div class="login" id="loginPage"><div style="background:#151121;border:1px solid #23203a;border-radius:20px;padding:24px;width:90%;max-width:320px;text-align:center"><div style="font-weight:800;font-size:24px">Cloud<span style="color:#8b7cf7">Pusat54</span></div><div class="welcome">WELCOME TO PYRUNNERCLOUD54</div><input id="u" value="admin"><input id="p" type="password" value="cloud54"><button class="btn run" style="width:100%;margin-top:10px" onclick="doLogin()">LOGIN</button></div></div>
<div class="header"><div class="logo">Cloud<span>Pusat54</span></div><div class="welcome">WELCOME TO PYRUNNERCLOUD54</div><div style="display:flex;justify-content:center;gap:10px;margin-top:6px"><small id="clock" style="color:#5a5672"></small><small onclick="logout()" style="color:#8b7cf7;cursor:pointer">Logout</small></div></div>
<div class="stats"><div class="scard"><small>CPU</small><b id="cpu">0%</b><div class="bar"><i id="cpuBar" style="background:#00ff88;width:10%"></i></div></div><div class="scard"><small>RAM</small><b id="ram">0%</b><div class="bar"><i id="ramBar" style="background:#8b7cf7;width:10%"></i></div></div><div class="scard"><small>DISK</small><b id="disk">0%</b><div class="bar"><i id="diskBar" style="background:#3dc5ff;width:10%"></i></div></div></div>
<div class="bots-wrap"><div style="display:flex;justify-content:space-between"><b>MY BOTS</b><small id="botCount"></small></div><div id="bots" style="margin-top:10px"></div></div>
<div class="tabs"><div class="tab active" id="t-apps" onclick="show('apps')">Bots</div><div class="tab" id="t-fm" onclick="show('fm')">File Manager</div><div class="tab" id="t-deploy" onclick="show('deploy')">Deploy</div></div>
<div id="fm" style="display:none;margin:12px;background:#151121;border:1px solid #23203a;border-radius:20px;padding:12px"><div style="display:flex;gap:6px"><input id="fmPath" value="/root/apps" style="flex:1"><button class="btn log" onclick="loadFM()">Go</button></div><div id="fmList" style="margin-top:10px"></div><div id="ed" style="display:none;margin-top:12px;border-top:1px solid #23203a;padding-top:12px"><b id="edPath" style="font-size:12px;color:#8b7cf7"></b><textarea id="edCode" rows="14"></textarea><div style="display:flex;gap:6px"><button class="btn run" onclick="saveF()">Save</button><button class="btn log" onclick="cancelEdit()">Batal</button><button class="btn stop" onclick="doDel()">Hapus</button></div></div></div>
<div id="deploy" style="display:none;margin:12px;background:#151121;border:1px solid #23203a;border-radius:20px;padding:12px"><input id="bName" placeholder="nama bot: pusat"><textarea id="bCode" rows="8" placeholder="paste kode main.py"></textarea><button class="btn run" style="width:100%" onclick="doDeploy()">DEPLOY & RUN</button><div class="uploadBox"><b style="font-size:13px">ATAU UPLOAD SCRIPT</b><br><small style="color:#7a758f">.py atau.zip</small><input type="file" id="deployFile" accept=".py,.zip" style="margin-top:10px"><button class="btn edit" style="width:100%;margin-top:8px" onclick="doDeployUpload()">UPLOAD & DEPLOY</button><small id="upStatus" style="display:block;color:#3dc5ff;margin-top:8px"></small></div><pre id="logOut" style="display:none;margin-top:10px"></pre></div>
<script>
function doLogin(){fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u.value,password:p.value})}).then(r=>{if(r.ok){localStorage.setItem('login','1');loginPage.style.display='none'}else alert('salah')})}
if(localStorage.getItem('login')=='1')loginPage.style.display='none'
function logout(){localStorage.removeItem('login');location.reload()}
function show(t){document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));document.getElementById('t-'+t).classList.add('active');fm.style.display=t=='fm'?'block':'none';deploy.style.display=t=='deploy'?'block':'none';document.querySelector('.bots-wrap').style.display=t=='apps'?'block':'none';if(t=='fm')loadFM()}
function loadStat(){fetch('/api/status').then(r=>r.json()).then(d=>{cpu.innerText=d.cpu+'%';cpuBar.style.width=d.cpu+'%';ram.innerText=d.ram+'%';ramBar.style.width=d.ram+'%';disk.innerText=d.disk+'%';diskBar.style.width=d.disk+'%'})}
function loadBots(){fetch('/api/apps').then(r=>r.json()).then(arr=>{botCount.innerText=arr.length+' bots';bots.innerHTML=arr.length?arr.map(b=>`<div class=bot><div style="display:flex;align-items:center;gap:10px"><div style="width:12px;height:12px;border-radius:50%;background:${b.running?'#00ff88':'#ff4d4d'}"></div><div><div style="font-weight:700">${b.name}</div><div style="margin-top:4px"><span class="${b.running?'live':'off'}">${b.running?'LIVE':'OFF'}</span> <small style="color:#5a5672">#${b.pid||'--'}</small></div></div></div><div style="display:flex;gap:5px"><button class="btn run" onclick="runBot('${b.name}')">Run</button><button class="btn stop" onclick="stopBot('${b.name}')">Stop</button><button class="btn log" onclick="viewLog('${b.name}')">Log</button></div></div>`).join(''):`<div style="text-align:center;color:#5a5672;padding:20px">Belum ada bot</div>`})}
async function runBot(n){let r=await fetch('/api/apps/'+n+'/start',{method:'POST'});if(!r.ok){let t=await r.text();alert('Gagal: '+t.slice(0,300))}setTimeout(loadBots,900)}
async function stopBot(n){await fetch('/api/apps/'+n+'/stop',{method:'POST'});setTimeout(loadBots,600)}
function viewLog(n){show('deploy');fetch('/api/apps/'+n+'/logs').then(r=>r.json()).then(d=>{logOut.style.display='block';logOut.innerText=d.logs})}
function loadFM(){fetch('/api/files?path='+encodeURIComponent(fmPath.value)).then(r=>r.json()).then(d=>{if(d.type=='file'){edPath.innerText=d.path;edCode.value=d.content;ed.style.display='block';return}fmList.innerHTML=d.items.map(i=>`<div class=file onclick="clickFM('${i.path}',${i.is_dir})"><span>${i.is_dir?'📁':'📄'} ${i.name}</span></div>`).join('')})}
function clickFM(p,isDir){if(isDir){fmPath.value=p;loadFM()}else{fetch('/api/files?path='+encodeURIComponent(p)).then(r=>r.json()).then(d=>{edPath.innerText=d.path;edCode.value=d.content;ed.style.display='block'})}}
function saveF(){fetch('/api/files/write',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:edPath.innerText,content:edCode.value})}).then(()=>{alert('Saved');loadFM()})}
function cancelEdit(){ed.style.display='none'}
function doDel(){fetch('/api/files/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:edPath.innerText})}).then(()=>{ed.style.display='none';loadFM();loadBots()})}
function doDeploy(){let n=bName.value||'pusat';let c=bCode.value;if(!c)return alert('paste kode');fetch('/api/deploy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,code:c})}).then(()=>{fetch('/api/apps/'+n+'/start',{method:'POST'}).then(()=>{show('apps');loadBots()})})}
function doDeployUpload(){let n=bName.value||'pusat';let f=deployFile.files[0];if(!f)return alert('Pilih file');let fd=new FormData();fd.append('name',n);fd.append('file',f);upStatus.innerText='Uploading...';fetch('/api/deploy/upload',{method:'POST',body:fd}).then(r=>r.json()).then(d=>{upStatus.innerText='Deployed '+d.name;fetch('/api/apps/'+d.name+'/start',{method:'POST'}).then(()=>{show('apps');loadBots()})})}
setInterval(()=>clock.innerText=new Date().toLocaleTimeString(),1000);loadStat();loadBots();setInterval(()=>{loadStat();loadBots()},3000)
</script></body></html>
HTML

cd /root/panel
python3 -m venv panel-venv
./panel-venv/bin/pip install -r requirements.txt -q

cat > /etc/systemd/system/cloud54.service << 'SVC'
[Unit]
Description=PyRunnerCloud54 Panel
After=network.target
[Service]
Type=simple
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=2
User=root
[Install]
WantedBy=multi-user.target
SVC

cat > /etc/systemd/system/cloud54-watchdog.service << 'SVC2'
[Unit]
Description=Watchdog Auto Fix
After=cloud54.service
[Service]
Type=simple
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/python /root/panel/watchdog.py
Restart=always
User=root
[Install]
WantedBy=multi-user.target
SVC2

cat > /etc/systemd/system/cloud54-bots.service << 'SVC3'
[Unit]
Description=Bot Autostart
After=cloud54.service
[Service]
Type=oneshot
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/python /root/panel/autostart.py
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target
SVC3

systemctl daemon-reload
systemctl enable cloud54 cloud54-watchdog cloud54-bots -q
systemctl restart cloud54
sleep 2
systemctl restart cloud54-watchdog
systemctl restart cloud54-bots || true
IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
echo ""
echo "=========================================="
echo "DONE V14 PERMANEN - PANEL HIDUP"
echo "Panel: http://$IP:8000"
echo "Login: admin / cloud54"
echo "=========================================="
