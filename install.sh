cd /root/panel
cat > install.sh << 'SH'
#!/bin/bash
set -e
echo "========================================="
echo " Pyrunnercloud54 Installer FINAL"
echo " WELCOME TO Pyrunnercloud54"
echo "========================================="

# 0. Cek root
if [ "$EUID" -ne 0 ]; then
  echo "Harus jalan sebagai root! sudo su dulu"
  exit 1
fi

# 1. System deps
echo "[1/6] Install system deps..."
apt update -y
apt install -y python3 python3-venv python3-pip zip unzip git curl psmisc lsof

# 2. Folder
echo "[2/6] Buat folder..."
mkdir -p /root/apps
mkdir -p /root/panel
cd /root/panel

# 3. Venv
echo "[3/6] Buat venv..."
if [! -d "panel-venv" ]; then
  python3 -m venv panel-venv
fi
./panel-venv/bin/pip install --upgrade pip -q

# 4. Requirements - FINAL LENGKAP
echo "[4/6] Install python deps..."
cat > requirements.txt << 'REQ'
fastapi
uvicorn[standard]
psutil
httpx
telethon
requests
aiohttp
pyrogram
tgcrypto
python-multipart
REQ

./panel-venv/bin/pip install -r requirements.txt -q

# 5. Cek app.py & index.html ada gak - kalau gak ada, warning
if [! -f "app.py" ]; then
  echo "WARNING: app.py tidak ada! Pastikan lu clone repo lengkap."
  echo "Repo harus berisi app.py + index.html"
  exit 1
fi
if [! -f "index.html" ]; then
  echo "WARNING: index.html tidak ada!"
  exit 1
fi

# 6. Bersihkan sampah & buat isolated DB per bot (FIX sqlite unable to open)
echo "[5/6] Fix isolated DB & bersihkan sampah..."
rm -rf /root/apps/__pycache__ /root/apps/__pycache__* 2>/dev/null
for d in /root/apps/*; do
  if [ -d "$d" ]; then
    mkdir -p "$d/data" "$d/sessions"
    chmod 777 "$d" "$d/data" "$d/sessions" 2>/dev/null
  fi
done

# 7. Systemd service - FINAL
echo "[6/6] Setup systemd service cloud54..."
cat > /etc/systemd/system/cloud54.service << 'SERVICE'
[Unit]
Description=CloudPusat54 - Pyrunnercloud54 Panel FINAL
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --log-level info
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONPATH=/root/panel

[Install]
WantedBy=multi-user.target
SERVICE

chmod +x app.py
chmod +x install.sh

systemctl daemon-reload
systemctl enable cloud54
systemctl restart cloud54
sleep 2

# 8. Status
echo ""
echo "========================================="
echo " INSTALL SELESAI - FINAL"
echo "========================================="
IP=$(curl -s ifconfig.me || echo "IP-VPS-MU")
echo "Panel: http://$IP:8000"
echo "Login: admin / cloud54"
echo ""
echo "Fitur FINAL yang terinstall:"
echo "✅ Hapus tulisan V10 di header & login"
echo "✅ Running text WELCOME TO Pyrunnercloud54"
echo "✅ COPYRIGHT CLOUDPUSAT54 di bawah LOGIN"
echo "✅ Database isolated per bot (fix sqlite error)"
echo "✅ Bot OFF -> LIVE ikut OFF (psutil cwd check)"
echo "✅ Delete bot dari Files & Monitor"
echo "✅ Auto fix httpx/telethon saat Run"
echo ""
systemctl status cloud54 --no-pager -l | head -30
echo ""
echo "Log panel: journalctl -u cloud54 -f"
echo "Log bot: /root/apps/NAMA_BOT/bot.log"
SH

chmod +x install.sh
cat install.sh
echo ""
echo "--- install.sh LENGKAP SUDAH SIAP ---"
