import sqlite3, subprocess, time
from pathlib import Path
DB = Path("/root/panel/bots.db")
APPS = Path("/root/apps")
LOGS = Path("/root/panel/logs")
if not DB.exists(): exit(0)
conn = sqlite3.connect(DB); cur = conn.cursor()
cur.execute("SELECT name FROM bots WHERE auto_start=1")
for (name,) in cur.fetchall():
    print(f"[autostart] {name}")
    main = APPS / name / "main.py"
    if not main.exists():
        pys = list((APPS / name).glob("*.py"))
        if pys: main = pys[0]
        else: continue
    log = LOGS / f"{name}.log"
    try:
        subprocess.Popen(["systemd-run", f"--unit=bot-{name}", "--scope", "--quiet", "/root/panel/panel-venv/bin/python", str(main)], cwd=str(APPS/name), stdout=open(log,"a"), stderr=subprocess.STDOUT, start_new_session=True)
    except:
        subprocess.Popen(["nohup", "/root/panel/panel-venv/bin/python", str(main)], cwd=str(APPS/name), stdout=open(log,"a"), stderr=subprocess.STDOUT, start_new_session=True)
    time.sleep(1)