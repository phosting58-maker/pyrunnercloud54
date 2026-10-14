import os, subprocess, pathlib, shutil, zipfile
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, PlainTextResponse

app = FastAPI()
APPS_DIR = "/root/apps"
os.makedirs(APPS_DIR, exist_ok=True)

# Path venv panel - sesuaikan sama install.sh
VENV_PY = "/root/panel/panel-venv/bin/python"
VENV_PIP = "/root/panel/panel-venv/bin/pip"

@app.get("/", response_class=HTMLResponse)
def home():
    try:
        return pathlib.Path("index.html").read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return f"<h2>Panel Running - index.html error: {e}</h2>"

@app.post("/api/login")
async def login(r: Request):
    d = await r.json()
    # Login clean - default admin/cloud54
    return {"ok": d.get("u") == "admin" and d.get("p") == "cloud54"}

@app.get("/api/bots")
def bots():
    res = []
    if not os.path.exists(APPS_DIR):
        return res
    for n in os.listdir(APPS_DIR):
        p = os.path.join(APPS_DIR, n)
        if os.path.isdir(p):
            running = subprocess.getoutput(f"pgrep -f 'apps/{n}/main.py'")!= ""
            res.append({"name": n, "status": "LIVE" if running else "OFF"})
    return res

@app.post("/run/{name}")
def runb(name: str):
    # === AUTO FIX CORE - Ini yang fix issue httpx di VPS baru ===
    bp = f"{APPS_DIR}/{name}"
    req = f"{bp}/requirements.txt"
    if os.path.exists(req):
        # Auto install requirements.txt setiap Run
        subprocess.run([VENV_PIP, "install", "-r", req], timeout=300)

    main = f"{bp}/main.py"
    if os.path.exists(main):
        txt = open(main, errors="ignore").read()
        # Auto scan import yang sering kepake
        for lib in ["httpx", "telethon", "requests", "aiohttp", "pyrogram", "tgcrypto", "python-telegram-bot"]:
            if lib in txt:
                subprocess.run([VENV_PIP, "install", lib], timeout=90)

    subprocess.run(f"pkill -9 -f 'apps/{name}/main.py'", shell=True)
    subprocess.Popen(f"nohup {VENV_PY} {bp}/main.py > {bp}/bot.log 2>&1 &", shell=True)
    return {"status": "LIVE"}

@app.post("/stop/{name}")
def stopb(name: str):
    # FIX: tombol Off sekarang beneran kill
    subprocess.run(f"pkill -9 -f 'apps/{name}/main.py'", shell=True)
    return {"status": "OFF"}

@app.get("/log/{name}", response_class=PlainTextResponse)
def logb(name: str):
    p = f"{APPS_DIR}/{name}/bot.log"
    return pathlib.Path(p).read_text()[-8000:] if os.path.exists(p) else "no log yet"

# === FILE MANAGER PREMIUM - edit/save/extract ===
@app.get("/api/files")
def files(path: str = "/root/apps"):
    items = []
    if os.path.exists(path):
        for f in os.listdir(path):
            full = os.path.join(path, f)
            items.append({
                "name": f,
                "isDir": os.path.isdir(full),
                "size": os.path.getsize(full) if os.path.isfile(full) else 0
            })
        items = sorted(items, key=lambda x: (not x["isDir"], x["name"].lower()))
    return {"path": path, "files": items}

@app.get("/api/read")
def readf(path: str):
    try:
        return {"content": pathlib.Path(path).read_text()[:80000]}
    except Exception as e:
        return {"content": f"Error: {e}"}

@app.post("/api/save")
async def save(r: Request):
    d = await r.json()
    pathlib.Path(d["path"]).write_text(d["content"])
    return {"ok": True}

@app.post("/api/mkdir")
async def mkdir(r: Request):
    d = await r.json()
    os.makedirs(d["path"], exist_ok=True)
    return {"ok": True}

@app.post("/api/delete")
async def delete(r: Request):
    d = await r.json()
    p = d["path"]
    try:
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        else:
            os.remove(p)
    except:
        pass
    return {"ok": True}

@app.post("/api/upload")
async def upload(file: UploadFile = File(...), dest: str = Form("/root/apps")):
    os.makedirs(dest, exist_ok=True)
    fpath = os.path.join(dest, file.filename)
    with open(fpath, "wb") as out:
        out.write(await file.read())
    if fpath.endswith(".zip"):
        try:
            with zipfile.ZipFile(fpath, 'r') as z:
                z.extractall(dest)
            os.remove(fpath)
        except:
            pass
    return {"ok": True}

@app.post("/api/deploy")
async def deploy(r: Request):
    d = await r.json()
    bp = f"{APPS_DIR}/{d.get('name')}"
    os.makedirs(bp, exist_ok=True)
    pathlib.Path(f"{bp}/main.py").write_text(d.get("main", ""))
    if d.get("req"):
        pathlib.Path(f"{bp}/requirements.txt").write_text(d.get("req"))
    return {"ok": True}
