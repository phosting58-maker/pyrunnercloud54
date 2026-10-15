from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os, psutil, subprocess, json

BASE_DIR = Path(__file__).parent
APPS_DIR = Path("/root/apps")
APPS_DIR.mkdir(exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_index():
    index_path = BASE_DIR / "index.html"
    if not index_path.exists():
        return "<h1>index.html not found in /root/panel</h1><p>cp /tmp/p/index.html /root/panel/</p>"
    return index_path.read_text(encoding="utf-8")

@app.get("/", response_class=HTMLResponse)
async def root():
    return get_index()

@app.get("/api/status")
async def status():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "apps": len(list(APPS_DIR.iterdir()))
    }

@app.get("/api/apps")
async def list_apps():
    apps = []
    for d in APPS_DIR.iterdir():
        if d.is_dir():
            apps.append({"name": d.name, "path": str(d)})
    return apps

@app.post("/api/login")
async def login(req: Request):
    data = await req.json()
    if data.get("username") == "admin" and data.get("password") == "cloud54":
        return {"ok": True, "token": "cloud54-token"}
    raise HTTPException(status_code=401, detail="Login salah")

@app.get("/health")
async def health():
    return {"ok": True}
