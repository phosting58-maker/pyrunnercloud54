from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import os, psutil, subprocess, hashlib, pathlib, json

app = FastAPI(docs_url=None, redoc_url=None)
BASE='/root/apps'
os.makedirs(BASE, exist_ok=True)
SECRET='cloudpusat54'
PH=hashlib.sha256(('cloud54'+SECRET).encode()).hexdigest()
def is_auth(r: Request): return r.cookies.get('auth','')==PH

LOGIN_HTML = """<!DOCTYPE html><html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>Cloud54</title><style>body{background:#0a0a12;color:#fff;font-family:system-ui;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}.box{background:#121224;border:1px solid #1e1e32;border-radius:20px;padding:28px;width:90%;max-width:380px}.logo{font-weight:900;font-style:italic;font-size:30px;text-align:center}.logo span{color:#22d3ee}input{width:100%;padding:14px;border-radius:12px;border:1px solid #2a2a44;background:#0e0e1e;color:#fff;margin-top:10px;box-sizing:border-box}button{width:100%;background:#00e676;color:#000;border:0;padding:14px;border-radius:12px;font-weight:900;margin-top:18px;cursor:pointer}</style></head><body><div class=box><div class=logo>PyRunner<span>Cloud54</span> Python+NodeJS</div><form method=post action=/login><input name=user placeholder="admin"><input name=pass type=password placeholder="cloud54"><button>LOGIN</button></form></div></body></html>"""

MAIN_HTML = """<!DOCTYPE html><html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>Cloud54</title><style>*{box-sizing:border-box}body{margin:0;background:#0a0a12;color:#e8e8ff;font-family:system-ui}.header{display:flex;justify-content:space-between;padding:14px 18px;background:#111125;border-bottom:1px solid #22223a}.logo{font-weight:900;font-style:italic;font-size:22px}.logo span{color:#22d3ee}.card{margin:14px;background:#151528;border:1px solid #1f1f3a;border-radius:16px;padding:16px}table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #22223a;text-align:left;font-size:13px}.btn{padding:8px 14px;border:0;border-radius:9px;font-weight:800;cursor:pointer}.btn-g{background:#00e676;color:#000}.btn-r{background:#ff3b5c;color:#fff}#log{white-space:pre-wrap;background:#0a0a12;padding:10px;border-radius:10px;max-height:400px;overflow:auto;font-size:12px;margin-top:10px}</style></head><body><div class=header><div class=logo>PyRunner<span>Cloud54</span> ✅ Py+Node</div><a href=/logout style=color:#ff5b7f;text-decoration:none;font-weight:700>Logout</a></div><div class=card><h3>Bot Manager - Auto Python/NodeJS</h3><div id=bots>Loading...</div></div><div class=card><h3>Log Output</h3><div id=log>klik Log di bot</div></div><script>function loadBots(){fetch('/api/bots').then(r=>r.json()).then(d=>{let h='<table><tr><th>Name</th><th>Type</th><th>Status</th><th>Log</th><th>Action</th></tr>';d.forEach(b=>{h+='<tr><td>'+b[0]+'</td><td>'+b[2]+'</td><td>'+b[1]+'</td><td><button class=btn onclick="showLog(\\''+b[0]+'\\')">Log</button></td><td><button class=btn btn-g onclick="runBot(\\''+b[0]+'\\')">Run</button> <button class=btn btn-r onclick="stopBot(\\''+b[0]+'\\')">Stop</button></td></tr>';});h+='</table>';document.getElementById('bots').innerHTML=h;});}function runBot(n){fetch('/api/bot/'+n+'/start',{method:'POST'}).then(r=>r.json()).then(d=>{alert(JSON.stringify(d));setTimeout(()=>showLog(n),1000);loadBots()})}function stopBot(n){fetch('/api/bot/'+n+'/stop',{method:'POST'}).then(()=>loadBots())}function showLog(n){fetch('/api/bot/'+n+'/log').then(r=>r.text()).then(t=>{document.getElementById('log').innerText=t})}loadBots();setInterval(loadBots,5000);</script></body></html>"""

@app.get('/login', response_class=HTMLResponse)
async def login_page(): return HTMLResponse(LOGIN_HTML)
@app.post('/login')
async def login_post(user: str = Form(...), pass_: str = Form(..., alias='pass')):
    if user=='admin' and hashlib.sha256((pass_+SECRET).encode()).hexdigest()==PH:
        resp=RedirectResponse('/',302); resp.set_cookie('auth',PH,max_age=86400*30,httponly=True); return resp
    return HTMLResponse(LOGIN_HTML, status_code=401)
@app.get('/logout')
async def logout():
    r=RedirectResponse('/login',302); r.delete_cookie('auth'); return r
@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    if not is_auth(request): return RedirectResponse('/login',302)
    return HTMLResponse(MAIN_HTML)

def detect_type(bot_path):
    if os.path.exists(os.path.join(bot_path,'package.json')): return 'NodeJS'
    if os.path.exists(os.path.join(bot_path,'bot.js')): return 'NodeJS'
    if os.path.exists(os.path.join(bot_path,'index.js')): return 'NodeJS'
    if os.path.exists(os.path.join(bot_path,'main.js')): return 'NodeJS'
    return 'Python'

def get_bots():
    out=[]
    for name in os.listdir(BASE):
        p=os.path.join(BASE,name)
        if not os.path.isdir(p) or name.startswith('.'): continue
        running=False
        for proc in psutil.process_iter(['cmdline']):
            try:
                cmd=' '.join(proc.info['cmdline'] or [])
                if BASE in cmd and name in cmd: running=True; break
            except: pass
        out.append([name,'running' if running else 'stopped', detect_type(p)])
    return sorted(out)

@app.get('/api/bots')
async def api_bots(request: Request):
    if not is_auth(request): return JSONResponse([],401)
    return JSONResponse(get_bots())

@app.post('/api/bot/{name}/start')
async def api_start(name: str, request: Request):
    if not is_auth(request): return JSONResponse({'err':'auth'},401)
    bot_path=os.path.join(BASE,name)
    entry=None
    if os.path.exists(os.path.join(bot_path,'package.json')):
        subprocess.run(['npm','install'], cwd=bot_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        entry='index.js'
        try:
            pkg=json.load(open(os.path.join(bot_path,'package.json')))
            entry=pkg.get('main','index.js')
        except: pass
        for f in ['bot.js','main.js','index.js','app.js']:
            if os.path.exists(os.path.join(bot_path,f)):
                entry=f
                break
        cmd=f"nohup node {entry} > bot.log 2>&1 &"
    else:
        for f in ['main.py','bot.py','app.py','run.py','index.js','bot.js','main.js']:
            if os.path.exists(os.path.join(bot_path,f)):
                entry=f; break
        if not entry:
            pys=list(pathlib.Path(bot_path).glob('*.py'))
            if pys: entry=pys[0].name
            else:
                jss=list(pathlib.Path(bot_path).glob('*.js'))
                if jss: entry=jss[0].name
        if not entry: return JSONResponse({'err':'no entry found'})
        if entry.endswith('.js'):
            subprocess.run(['npm','install'], cwd=bot_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            cmd=f"nohup node {entry} > bot.log 2>&1 &"
        else:
            req=os.path.join(bot_path,'requirements.txt')
            if os.path.exists(req):
                subprocess.run(['pip3','install','-r',req,'-q'], cwd=bot_path)
            cmd=f"nohup python3 {entry} > bot.log 2>&1 &"

    for proc in psutil.process_iter(['pid','cmdline']):
        try:
            c=' '.join(proc.info['cmdline'] or [])
            if BASE in c and name in c: psutil.Process(proc.info['pid']).kill()
        except: pass
    subprocess.Popen(cmd, cwd=bot_path, shell=True)
    return JSONResponse({'ok':True,'type':detect_type(bot_path),'entry':entry,'cmd':cmd})

@app.post('/api/bot/{name}/stop')
async def api_stop(name: str, request: Request):
    if not is_auth(request): return JSONResponse({'err':'auth'},401)
    for proc in psutil.process_iter(['pid','cmdline']):
        try:
            c=' '.join(proc.info['cmdline'] or [])
            if BASE in c and name in c: psutil.Process(proc.info['pid']).kill()
        except: pass
    return JSONResponse({'ok':True})

@app.get('/api/bot/{name}/log')
async def api_log(name: str, request: Request):
    if not is_auth(request): return HTMLResponse('auth',401)
    logf=os.path.join(BASE,name,'bot.log')
    if not os.path.exists(logf): return HTMLResponse('no log yet - click Run first')
    return HTMLResponse(open(logf, errors='ignore').read()[-8000:])
