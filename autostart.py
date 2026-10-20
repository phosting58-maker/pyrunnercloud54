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
