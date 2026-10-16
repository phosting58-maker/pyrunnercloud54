import time, subprocess, os
from pathlib import Path
APPS=Path("/root/apps")
for d in APPS.iterdir():
    if d.is_dir() and (d/"main.py").exists():
        log=Path(f"/root/panel/logs/{d.name}.log")
        log.parent.mkdir(exist_ok=True,parents=True)
        with open(log,"a") as lf:
            subprocess.Popen(["/root/panel/panel-venv/bin/python","-u",str(d/"main.py")],cwd=str(d),stdout=lf,stderr=subprocess.STDOUT,start_new_session=True)
print("autostart done")
