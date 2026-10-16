from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import psutil, subprocess, os, shutil, zipfile, time
from datetime import datetime

BASE_DIR = Path(__file__).parent
APPS_DIR = Path("/root/apps")
APPS_DIR.mkdir(exist_ok=True)
LOGS_DIR = Path("/root/panel/logs")
LOGS_DIR.mkdir(exist_ok=True)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def is_running(name):
    p = APPS_DIR / name / "bot.pid"
    if p.exists():
        try:
            pid = int(p.read_text().strip())
            if psutil.pid_exists(pid):
                return True
        except:
            pass
    return False

def get_pid(name):
    p = APPS_DIR / name / "bot.pid"
    try:
        return int(p.read_text().strip())
    except:
        return 0

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse((BASE_DIR / "index.html").read_text(encoding="utf-8"))

@app.get("/api/status")
async def status():
    return {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "disk": psutil.disk_usage("/").percent}

@app.post("/api/login")
async def login(req: Request):
    d = await req.json()
    if d.get("username") == "admin" and d.get("password") == "cloud54":
        return {"ok": True}
    raise HTTPException(status_code=401, detail="salah")

@app.get("/api/apps")
async def list_apps():
    out = []
    for d in APPS_DIR.iterdir():
        if not d.is_dir(): continue
        if d.name.startswith("."): continue
        if d.name.startswith("__"): continue
        if d.name.startswith("FILE"): continue
        if "__pycache__" in d.name: continue
        if not (d / "main.py").exists():
            # cek ada.py lain
            if not list(d.glob("*.py")): continue
        out.append({"name": d.name, "running": is_running(d.name), "pid": get_pid(d.name)})
    return out

@app.post("/api/apps/{name}/start")
async def start_app(name: str):
    ap = APPS_DIR / name
    main = ap / "main.py"
    if not main.exists():
        pys = list(ap.glob("*.py"))
        if pys: main = pys[0]
        else: raise HTTPException(400, "main.py not found")
    log = LOGS_DIR / f"{name}.log"
    pidf = ap / "bot.pid"
    if pidf.exists():
        try: os.kill(int(pidf.read_text()), 9)
        except: pass
        pidf.unlink(missing_ok=True)
    # kill sisa proses lama
    try:
        for proc in psutil.process_iter(['cmdline']):
            try:
                if f"/root/apps/{name}" in " ".join(proc.info['cmdline'] or []):
                    os.kill(proc.info['pid'], 9)
            except: continue
    except: pass
    with open(log, "a") as lf:
        lf.write(f"\n--- START {datetime.now()} ---\n")
        proc = subprocess.Popen(["/root/panel/panel-venv/bin/python", "-u", str(main)], cwd=str(ap), stdout=lf, stderr=subprocess.STDOUT, start_new_session=True, preexec_fn=os.setpgrp)
    pidf.write_text(str(proc.pid))
    time.sleep(1)
    return {"ok": True, "pid": proc.pid, "running": True}

@app.post("/api/apps/{name}/stop")
async def stop_app(name: str):
    pidf = APPS_DIR / name / "bot.pid"
    if pidf.exists():
        try: os.kill(int(pidf.read_text()), 9)
        except: pass
        pidf.unlink(missing_ok=True)
    try:
        for proc in psutil.process_iter(['cmdline']):
            try:
                if f"/root/apps/{name}" in " ".join(proc.info['cmdline'] or []):
                    os.kill(proc.info['pid'], 9)
            except: continue
    except: pass
    return {"ok": True}

@app.get("/api/apps/{name}/logs")
async def logs(name: str):
    p = LOGS_DIR / f"{name}.log"
    if not p.exists(): return {"logs": "no log yet"}
    return {"logs": p.read_text(encoding="utf-8", errors="ignore")[-12000:]}

@app.get("/api/files")
async def files(path: str = "/root/apps"):
    p = Path(path)
    if not p.exists(): raise HTTPException(404, "not found")
    if p.is_file():
        return {"type": "file", "path": str(p), "content": p.read_text(encoding="utf-8", errors="ignore")[-15000:]}
    items = []
    for c in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        items.append({"name": c.name, "path": str(c), "is_dir": c.is_dir(), "size": c.stat().st_size if c.is_file() else 0})
    return {"type": "dir", "path": str(p), "items": items}

@app.post("/api/files/write")
async def write(req: Request):
    d = await req.json()
    Path(d["path"]).write_text(d["content"], encoding="utf-8")
    return {"ok": True}

@app.post("/api/files/delete")
async def deletef(req: Request):
    d = await req.json()
    p = Path(d["path"])
    if p.is_dir(): shutil.rmtree(p, ignore_errors=True)
    else: p.unlink(missing_ok=True)
    return {"ok": True}

@app.post("/api/files/extract")
async def extract(req: Request):
    d = await req.json()
    p = Path(d["path"])
    with zipfile.ZipFile(p) as z:
        z.extractall(p.parent)
    return {"ok": True}

@app.post("/api/files/upload")
async def upload(path: str = "/root/apps", file: UploadFile = File(...)):
    dest = Path(path) / file.filename
    if dest.is_file(): dest = dest.parent / file.filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(await file.read())
    if dest.suffix == ".zip":
        with zipfile.ZipFile(dest) as z: z.extractall(dest.parent)
        dest.unlink()
    return {"ok": True}

@app.post("/api/deploy")
async def deploy(req: Request):
    d = await req.json()
    name = d.get("name", "pusat").strip().replace(" ", "_")
    p = APPS_DIR / name
    p.mkdir(exist_ok=True)
    (p / "main.py").write_text(d.get("code", ""), encoding="utf-8")
    return {"ok": True, "name": name}

@app.post("/api/deploy/upload")
async def deploy_upload(name: str = Form(...), file: UploadFile = File(...)):
    name = name.strip().replace(" ", "_") or "pusat"
    bd = APPS_DIR / name
    bd.mkdir(exist_ok=True)
    dst = bd / file.filename
    dst.write_bytes(await file.read())
    if dst.suffix == ".zip":
        with zipfile.ZipFile(dst) as z: z.extractall(bd)
        dst.unlink()
        # kalau zip ada folder di dalam, naikkan
        subs = [d for d in bd.iterdir() if d.is_dir()]
        if len(subs) == 1 and not (bd / "main.py").exists():
            inner = subs[0]
            for it in inner.iterdir(): shutil.move(str(it), str(bd / it.name))
            shutil.rmtree(inner, ignore_errors=True)
    elif dst.suffix == ".py" and dst.name!= "main.py":
        if (bd / "main.py").exists(): (bd / "main.py").unlink()
        dst.rename(bd / "main.py")
    return {"ok": True, "name": name}
