import time, subprocess, psutil
from pathlib import Path
APPS_DIR=Path("/root/apps"); LOGS_DIR=Path("/root/panel/logs")
def is_running(p):
 if not p.exists(): return False
 try: return psutil.pid_exists(int(p.read_text().strip()))
 except: return False
print("WATCHDOG START - AUTO RESTART AKTIF")
while True:
 for bot in APPS_DIR.iterdir():
  if not bot.is_dir() or not (bot/"main.py").exists(): continue
  should=bot/".should_run"; pidf=bot/"bot.pid"; log=LOGS_DIR/f"{bot.name}.log"
  if should.exists() and not is_running(pidf):
   try:
    with open(log,"a") as lf:
     lf.write(f"\n--- AUTO RESTART {time.ctime()} ---\n")
     proc=subprocess.Popen(["/root/panel/panel-venv/bin/python","-u",str(bot/"main.py")],cwd=str(bot),stdout=lf,stderr=subprocess.STDOUT,start_new_session=True)
    pidf.write_text(str(proc.pid))
   except: pass
 time.sleep(10)