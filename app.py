import os, subprocess, pathlib, shutil, zipfile, psutil
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, PlainTextResponse
app=FastAPI()
APPS_DIR="/root/apps"
os.makedirs(APPS_DIR,exist_ok=True)
VENV_PY="/root/panel/panel-venv/bin/python"
VENV_PIP="/root/panel/panel-venv/bin/pip"

@app.get("/", response_class=HTMLResponse)
def home():
    return pathlib.Path("index.html").read_text(encoding='utf-8', errors='ignore')

@app.get("/api/stats")
def stats():
    cpu=psutil.cpu_percent(interval=0.5)
    ram=psutil.virtual_memory()
    disk=psutil.disk_usage("/")
    return {"cpu":f"{cpu:.1f}%","ram":f"{ram.used/1024/1024/1024:.1f}GB","disk":f"{disk.used/1024/1024/1024:.1f}GB","ram_p":ram.percent,"disk_p":disk.percent}

@app.post("/api/login")
async def login(r:Request):
    d=await r.json()
    return {"ok": d.get("u")=="admin" and d.get("p")=="cloud54"}

def is_bot_live(name):
    for proc in psutil.process_iter(['pid','cmdline','cwd']):
        try:
            cmd=' '.join(proc.info['cmdline'] or [])
            cwd=(proc.info['cwd'] or '')
            if f"/root/apps/{name}" in cwd or f"/root/apps/{name}" in cmd:
                if "main.py" in cmd:
                    return True
        except: continue
    return False

@app.get("/api/bots")
def bots():
    res=[]
    for n in os.listdir(APPS_DIR):
        if n.startswith("__"): continue
        p=os.path.join(APPS_DIR,n)
        if os.path.isdir(p):
            res.append({"name":n,"status":"LIVE" if is_bot_live(n) else "OFF"})
    return res

@app.post("/run/{name}")
def runb(name:str):
    bp=f"{APPS_DIR}/{name}"
    req=f"{bp}/requirements.txt"
    if os.path.exists(req):
        subprocess.run([VENV_PIP,"install","-r",req],timeout=300)
    mp=f"{bp}/main.py"
    if os.path.exists(mp):
        txt=open(mp,errors="ignore").read().lower()
        for lib in ["httpx","telethon","requests","aiohttp","pyrogram","tgcrypto"]:
            if lib in txt:
                subprocess.run([VENV_PIP,"install",lib],timeout=90)
    os.makedirs(f"{bp}/data",exist_ok=True)
    os.makedirs(f"{bp}/sessions",exist_ok=True)
    subprocess.run(f"pkill -9 -f '/root/apps/{name}'",shell=True)
    subprocess.Popen(f"nohup {VENV_PY} main.py > bot.log 2>&1 &",shell=True,cwd=bp)
    return {"ok":True}

@app.post("/stop/{name}")
def stopb(name:str):
    subprocess.run(f"pkill -9 -f '/root/apps/{name}'",shell=True)
    for proc in psutil.process_iter(['pid','cmdline','cwd']):
        try:
            cwd=proc.info['cwd'] or ''
            if f"/root/apps/{name}" in cwd:
                proc.kill()
        except: pass
    return {"ok":True}

@app.get("/log/{name}", response_class=PlainTextResponse)
def logb(name:str):
    p=f"{APPS_DIR}/{name}/bot.log"
    return pathlib.Path(p).read_text()[-7000:] if os.path.exists(p) else "no log"

@app.get("/api/files")
def files(path:str="/root/apps"):
    items=[]
    if os.path.exists(path):
        for f in os.listdir(path):
            full=os.path.join(path,f)
            items.append({"name":f,"isDir":os.path.isdir(full),"size":os.path.getsize(full) if os.path.isfile(full) else 0})
        items=sorted(items,key=lambda x:(not x["isDir"], x["name"].lower()))
    return {"path":path,"files":items}

@app.get("/api/read")
def readf(path:str):
    try: return {"content":pathlib.Path(path).read_text()[:80000]}
    except Exception as e: return {"content":str(e)}

@app.post("/api/save")
async def save(r:Request):
    d=await r.json()
    pathlib.Path(d["path"]).write_text(d["content"])
    return {"ok":True}

@app.post("/api/mkdir")
async def mkdir(r:Request):
    d=await r.json()
    os.makedirs(d["path"],exist_ok=True)
    return {"ok":True}

@app.post("/api/delete")
async def delete(r:Request):
    d=await r.json()
    p=d["path"]
    try:
        name=os.path.basename(p.rstrip('/'))
        subprocess.run(f"pkill -9 -f '/root/apps/{name}'",shell=True)
        if os.path.isdir(p): shutil.rmtree(p,ignore_errors=True)
        else: os.remove(p)
    except: pass
    return {"ok":True}

@app.post("/api/upload")
async def upload(file: UploadFile = File(...), dest: str = Form("/root/apps")):
    os.makedirs(dest,exist_ok=True)
    fpath=os.path.join(dest,file.filename)
    with open(fpath,"wb") as out: out.write(await file.read())
    if fpath.endswith(".zip"):
        try:
            with zipfile.ZipFile(fpath,'r') as z: z.extractall(dest)
            os.remove(fpath)
        except: pass
    return {"ok":True}

@app.post("/api/extract")
async def extract(r:Request):
    d=await r.json()
    p=d.get("path")
    try:
        with zipfile.ZipFile(p,'r') as z: z.extractall(os.path.dirname(p))
        return {"ok":True}
    except Exception as e:
        return {"ok":False,"msg":str(e)}

@app.post("/api/deploy")
async def deploy(name: str = Form(...), cmd: str = Form("python3 main.py"), file: UploadFile = File(None)):
    bp=f"{APPS_DIR}/{name.strip()}"
    os.makedirs(bp,exist_ok=True)
    os.makedirs(f"{bp}/data",exist_ok=True)
    os.makedirs(f"{bp}/sessions",exist_ok=True)
    if file and file.filename:
        fpath=os.path.join(bp,file.filename)
        with open(fpath,"wb") as out: out.write(await file.read())
        if fpath.endswith(".zip"):
            try:
                with zipfile.ZipFile(fpath,'r') as z: z.extractall(bp)
                os.remove(fpath)
            except: pass
    else:
        pathlib.Path(f"{bp}/main.py").write_text("# bot ready")
    return {"ok":True,"name":name}
