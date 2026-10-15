from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import psutil, subprocess, os, shutil, zipfile, sqlite3, time, signal
from datetime import datetime

BASE_DIR = Path(__file__).parent
APPS_DIR = Path("/root/apps"); APPS_DIR.mkdir(exist_ok=True)
LOGS_DIR = Path("/root/panel/logs"); LOGS_DIR.mkdir(exist_ok=True)
DB_PATH = BASE_DIR / "bots.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS bots (name TEXT PRIMARY KEY, auto_start INTEGER DEFAULT 1, created_at TEXT, last_pid INTEGER DEFAULT 0, status TEXT DEFAULT 'stopped')""")
    conn.commit(); conn.close()
init_db()
def db_q(q, args=(), fetch=False):
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    cur = conn.cursor(); cur.execute(q, args)
    res = cur.fetchall() if fetch else None
    conn.commit(); conn.close()
    return res

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def is_running(name):
    pidf = APPS_DIR / name / "bot.pid"
    if pidf.exists():
        try:
            pid = int(pidf.read_text().strip())
            if pid>0 and psutil.pid_exists(pid):
                # cek masih hidup beneran
                p = psutil.Process(pid)
                if p.status()!= psutil.STATUS_ZOMBIE: return True
        except: pass
    # fallback cari proses dengan path
    try:
        for proc in psutil.process_iter(['pid','cmdline']):
            try:
                cmd = " ".join(proc.info['cmdline'] or [])
                if f"/root/apps/{name}" in cmd and "python" in cmd: return True
            except: continue
    except: pass
    return False

def get_pid(name):
    pidf = APPS_DIR / name / "bot.pid"
    try:
        if pidf.exists(): return int(pidf.read_text().strip())
    except: pass
    try:
        for proc in psutil.process_iter(['pid','cmdline']):
            try:
                if f"/root/apps/{name}" in " ".join(proc.info['cmdline'] or []):
                    return proc.info['pid']
            except: continue
    except: pass
    return 0

def safe_read(p: Path):
    try:
        if not p.exists(): return "no logs yet"
        if p.stat().st_size > 500000: return p.read_text(encoding="utf-8", errors="ignore")[-15000:]
        return p.read_text(encoding="utf-8", errors="ignore")[-15000:]
    except Exception as e: return f"[error: {e}]"

@app.get("/", response_class=HTMLResponse)
async def root(): return HTMLResponse((BASE_DIR / "index.html").read_text(encoding="utf-8", errors="ignore"))
@app.get("/api/status")
async def status(): return {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "disk": psutil.disk_usage("/").percent}
@app.post("/api/login")
async def login(req: Request):
    d = await req.json()
    if d.get("username")=="admin" and d.get("password")=="cloud54": return {"ok": True}
    raise HTTPException(status_code=401, detail="salah")

@app.get("/api/apps")
async def list_apps():
    db_rows = {r['name']: dict(r) for r in db_q("SELECT * FROM bots", fetch=True)}
    out=[]; IGNORE = {"__pycache__", "FILE_PO", ".git", "venv", "panel-venv", "logs"}
    for d in APPS_DIR.iterdir():
        if not d.is_dir(): continue
        if d.name in IGNORE or d.name.startswith(".") or d.name.startswith("__") or d.name.startswith("FILE_"): continue
        has_py = (d / "main.py").exists() or any(f.suffix==".py" for f in d.iterdir() if f.is_file())
        if not has_py: continue
        out.append({"name": d.name, "running": is_running(d.name), "pid": get_pid(d.name), "auto_start": db_rows.get(d.name,{}).get('auto_start',1)})
    return out

@app.post("/api/apps/{name}/start")
async def start_app(name: str):
    app_path = APPS_DIR / name
    if not app_path.exists(): raise HTTPException(404, "app not found")
    main = app_path / "main.py"
    if not main.exists():
        pys = list(app_path.glob("*.py"))
        if not pys: raise HTTPException(400, "main.py not found - upload.py dulu")
        main = pys[0]
        shutil.copy(pys[0], app_path / "main.py")
        main = app_path / "main.py"
    log = LOGS_DIR / f"{name}.log"
    pidf = app_path / "bot.pid"
    # STOP dulu yang lama
    if pidf.exists():
        try:
            old_pid = int(pidf.read_text())
            if psutil.pid_exists(old_pid): os.kill(old_pid, 9)
        except: pass
        pidf.unlink(missing_ok=True)
    # Kill sisa proses
    try:
        for proc in psutil.process_iter(['pid','cmdline']):
            try:
                if f"/root/apps/{name}" in " ".join(proc.info['cmdline'] or []): os.kill(proc.info['pid'], 9)
            except: continue
    except: pass

    # START PAKE NOHUP LANGSUNG - INI YANG FIX RUN BUTTON
    log.parent.mkdir(exist_ok=True, parents=True)
    with open(log, "a") as lf:
        lf.write(f"\n--- START {datetime.now()} ---\n")
        proc = subprocess.Popen(["/root/panel/panel-venv/bin/python", "-u", str(main)], cwd=str(app_path), stdout=lf, stderr=subprocess.STDOUT, preexec_fn=os.setpgrp, start_new_session=True)
    pidf.write_text(str(proc.pid))
    time.sleep(0.8)
    # cek hidup gak
    alive = psutil.pid_exists(proc.pid)
    db_q("UPDATE bots SET status=?, last_pid=? WHERE name=?", ("running" if alive else "failed", proc.pid, name))
    if not alive:
        raise HTTPException(500, f"bot crash, cek log: {safe_read(log)[:500]}")
    return {"ok": True, "pid": proc.pid, "running": True}

@app.post("/api/apps/{name}/stop")
async def stop_app(name: str):
    pidf = APPS_DIR / name / "bot.pid"
    killed=False
    if pidf.exists():
        try:
            pid = int(pidf.read_text())
            if psutil.pid_exists(pid): os.kill(pid, 9); killed=True
        except: pass
        pidf.unlink(missing_ok=True)
    try:
        for proc in psutil.process_iter(['pid','cmdline']):
            try:
                if f"/root/apps/{name}" in " ".join(proc.info['cmdline'] or []): os.kill(proc.info['pid'], 9); killed=True
            except: continue
    except: pass
    db_q("UPDATE bots SET status='stopped' WHERE name=?", (name,))
    return {"ok": True, "killed": killed}

@app.delete("/api/apps/{name}")
async def del_app(name: str):
    await stop_app(name)
    shutil.rmtree(APPS_DIR / name, ignore_errors=True)
    (LOGS_DIR / f"{name}.log").unlink(missing_ok=True)
    db_q("DELETE FROM bots WHERE name=?", (name,))
    return {"ok": True}
@app.get("/api/apps/{name}/logs")
async def logs(name: str): return {"logs": safe_read(LOGS_DIR / f"{name}.log")}
@app.get("/api/files")
async def files(path: str = "/root/apps"):
    p = Path(path)
    if not p.exists(): raise HTTPException(404)
    if p.is_file(): return {"type": "file", "path": str(p), "content": safe_read(p)}
    items=[]
    for child in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        try: sz = child.stat().st_size if child.is_file() else 0
        except: sz=0
        items.append({"name": child.name, "path": str(child), "is_dir": child.is_dir(), "size": sz})
    return {"type": "dir", "path": str(p), "items": items}
@app.post("/api/files/write")
async def write(req: Request):
    d = await req.json(); p = Path(d["path"]); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(d["content"], encoding="utf-8"); return {"ok": True}
@app.post("/api/files/delete")
async def deletef(req: Request):
    d = await req.json(); p = Path(d["path"])
    if p.is_dir(): shutil.rmtree(p, ignore_errors=True)
    else: p.unlink(missing_ok=True)
    return {"ok": True}
@app.post("/api/files/upload")
async def upload(path: str = "/root/apps", file: UploadFile = File(...)):
    dest_dir = Path(path);
    if dest_dir.is_file(): dest_dir = dest_dir.parent
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / file.filename; dest.write_bytes(await file.read())
    if dest.suffix == ".zip":
        try:
            with zipfile.ZipFile(dest) as z: z.extractall(dest_dir); dest.unlink()
        except: pass
    return {"ok": True}
@app.post("/api/files/extract")
async def extract(req: Request):
    d = await req.json(); p = Path(d["path"]);
    if not p.exists(): raise HTTPException(404)
    if p.suffix!= ".zip": raise HTTPException(400, "bukan zip")
    with zipfile.ZipFile(p) as z: z.extractall(p.parent)
    return {"ok": True}
@app.post("/api/deploy")
async def deploy(req: Request):
    d = await req.json(); name = d.get("name","pusat").replace(" ","_").strip()
    p = APPS_DIR / name; p.mkdir(exist_ok=True)
    (p / "main.py").write_text(d.get("code",""), encoding="utf-8")
    db_q("INSERT OR REPLACE INTO bots (name, auto_start, created_at, status) VALUES (?,?,?,?)", (name, 1, datetime.now().isoformat(), "stopped"))
    return {"ok": True}
@app.post("/api/deploy/upload")
async def deploy_upload(name: str = Form(...), file: UploadFile = File(...)):
    name = name.replace(" ","_").strip() or "pusat"
    bot_dir = APPS_DIR / name; bot_dir.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    dest = bot_dir / file.filename; dest.write_bytes(content)
    count=1
    if dest.suffix == ".zip":
        try:
            with zipfile.ZipFile(dest) as z: z.extractall(bot_dir); count=len(z.namelist())
            dest.unlink()
            subdirs = [d for d in bot_dir.iterdir() if d.is_dir()]
            if len(subdirs)==1 and not (bot_dir / "main.py").exists():
                inner = subdirs[0]
                for item in inner.iterdir(): shutil.move(str(item), str(bot_dir / item.name))
                shutil.rmtree(inner, ignore_errors=True)
        except Exception as e: raise HTTPException(500, f"extract gagal: {e}")
    elif dest.suffix == ".py":
        if dest.name!= "main.py":
            if (bot_dir / "main.py").exists(): (bot_dir / "main.py").unlink()
            dest.rename(bot_dir / "main.py")
    db_q("INSERT OR REPLACE INTO bots (name, auto_start, created_at, status) VALUES (?,?,?,?)", (name, 1, datetime.now().isoformat(), "stopped"))
    return {"ok": True, "name": name, "files": count}
