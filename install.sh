#!/bin/bash
set -e
apt-get update -y -q && apt-get install -y -q python3 python3-venv python3-pip curl zip unzip -q
mkdir -p /root/panel/logs /root/apps
rm -rf /root/panel/panel-venv 2>/dev/null; true
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
 ap=APPS_DIR/name; main=ap/"main.py"; log=LOGS_DIR/f"{name}.log"; pidf=ap/"bot.pid"; reqf=ap/"requirements.txt"
 if not main.exists(): raise HTTPException(400,"main.py not found")
 if pidf.exists():
  try: os.kill(int(pidf.read_text()),9)
  except: pass
  pidf.unlink(missing_ok=True)
 # FIX PERMANEN TELEGRAM: auto install requirements + lib telegram umum
 if reqf.exists():
  try: subprocess.run(["/root/panel/panel-venv/bin/pip","install","-r",str(reqf),"-q"],timeout=120)
  except: pass
 else:
  # kalo gak ada requirements.txt, install lib telegram standar biar gak ModuleNotFoundError
  try: subprocess.run(["/root/panel/panel-venv/bin/pip","install","telebot","pyTelegramBotAPI","python-telegram-bot==13.15","telethon","pyrogram","tgcrypto","requests","python-dotenv","-q"],timeout=120)
  except: pass
 with open(log,"a") as lf:
  lf.write(f"\n--- START {datetime.now()} ---\n")
  proc=subprocess.Popen(["/root/panel/panel-venv/bin/python","-u",str(main)],cwd=str(ap),stdout=lf,stderr=subprocess.STDOUT,start_new_session=True)
 pidf.write_text(str(proc.pid)); (ap/".should_run").write_text("1")
 time.sleep(2.5)
 # VALIDASI BENERAN JALAN ATAU CRASH
 if not is_running(name):
  err=open(log).read()[-3000:] if log.exists() else "crash no log"
  raise HTTPException(500, err)
 return {"ok":True,"pid":proc.pid}
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
 if p.is_file(): return {"type":"file","path":str(p),"content":p.read_text(errors="ignore")[-15000:]}
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
while True:
 for bot in APPS_DIR.iterdir():
  if not bot.is_dir() or not (bot/"main.py").exists(): continue
  if (bot/".should_run").exists() and not is_running(bot/"bot.pid"):
   try:
    with open(LOGS_DIR/f"{bot.name}.log","a") as lf:
     lf.write(f"\n--- AUTO RESTART {time.ctime()} ---\n")
     proc=subprocess.Popen(["/root/panel/panel-venv/bin/python","-u",str(bot/"main.py")],cwd=str(bot),stdout=lf,stderr=subprocess.STDOUT,start_new_session=True)
    (bot/"bot.pid").write_text(str(proc.pid))
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
PY
cat > /root/panel/requirements.txt << 'PY'
fastapi
uvicorn
psutil
python-multipart
PY
curl -sSL https://raw.githubusercontent.com/phosting58-maker/pyrunnercloud54/main/index.html -o /root/panel/index.html
cd /root/panel
python3 -m venv panel-venv
./panel-venv/bin/pip install -r requirements.txt -q
./panel-venv/bin/pip install telebot pyTelegramBotAPI python-telegram-bot==13.15 telethon pyrogram tgcrypto requests python-dotenv -q
cat > /etc/systemd/system/cloud54.service << 'SVC'
[Unit]
Description=Cloud54
After=network.target
[Service]
Type=simple
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
User=root
[Install]
WantedBy=multi-user.target
SVC
cat > /etc/systemd/system/cloud54-watchdog.service << 'SVC2'
[Unit]
Description=Watchdog
After=cloud54.service
[Service]
Type=simple
ExecStart=/root/panel/panel-venv/bin/python /root/panel/watchdog.py
Restart=always
User=root
[Install]
WantedBy=multi-user.target
SVC2
cat > /etc/systemd/system/cloud54-bots.service << 'SVC3'
[Unit]
Description=Bots
After=cloud54.service
[Service]
Type=oneshot
ExecStart=/root/panel/panel-venv/bin/python /root/panel/autostart.py
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target
SVC3
systemctl daemon-reload
systemctl enable cloud54 cloud54-watchdog cloud54-bots -q
systemctl restart cloud54; sleep 2; systemctl restart cloud54-watchdog; systemctl restart cloud54-bots || true
echo "DONE PERMANEN http://$(curl -s ifconfig.me):8000 admin/cloud54"
