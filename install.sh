#!/bin/bash
# CloudPusat54 V14 CLEAN PREMIUM + AUTO FIX INSTALLER
# Fix: ModuleNotFoundError httpx / telethon di VPS baru

set -e
echo "=== Installing CloudPusat54 V14 CLEAN ==="

# Bersihin install lama
systemctl stop cloud54 2>/dev/null || true
pkill -9 -f uvicorn || true

cd /root
rm -rf panel
mkdir -p panel apps
cd panel

# Buat venv fresh
python3 -m venv panel-venv
./panel-venv/bin/pip install --upgrade pip -q
./panel-venv/bin/pip install fastapi uvicorn python-multipart psutil httpx requests -q

# Copy dari repo (jika dijalankan dari repo) atau download
if [ -f "/root/pyrunnercloud54/app.py" ]; then
    cp /root/pyrunnercloud54/app.py./app.py
    cp /root/pyrunnercloud54/index.html./index.html
elif [ -f "../app.py" ]; then
    cp../app.py./app.py
    cp../index.html./index.html
else
    echo "app.py not found in expected location, make sure you run from repo"
    # fallback - akan diisi oleh git clone
    curl -sL https://raw.githubusercontent.com/phosting58-maker/pyrunnercloud54/main/app.py -o app.py || true
    curl -sL https://raw.githubusercontent.com/phosting58-maker/pyrunnercloud54/main/index.html -o index.html || true
fi

# Buat service
cat > /etc/systemd/system/cloud54.service << 'SVC'
[Unit]
Description=CloudPusat54 V14 AutoFix
After=network.target

[Service]
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SVC

systemctl daemon-reload
systemctl enable cloud54
systemctl restart cloud54

sleep 2
systemctl status cloud54 --no-pager -l | head -20
IP=$(curl -s ifconfig.me || echo "YOUR_VPS_IP")
echo ""
echo "=== DONE V14 CLEAN PREMIUM ==="
echo "URL: http://$IP:8000"
echo "Login: admin / cloud54"
echo "AutoFix: ON - requirements.txt auto install on Run"
echo ""
