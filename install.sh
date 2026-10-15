#!/bin/bash
set -e
echo "=== PyRunnerCloud54 V10.7 UNIVERSAL FIX ==="

# 1. WAJIB ROOT
if [ "$EUID" -ne 0 ]; then echo "Harus root: sudo su -"; exit 1; fi

# 2. AUTO INSTALL DEPENDENCY DI VPS FRESH
export DEBIAN_FRONTEND=noninteractive
apt-get update -y -q
apt-get install -y -q python3 python3-venv python3-pip git curl zip unzip psmisc systemd > /dev/null 2>&1 || true

# 3. BERSIHIN SAMPAH LAMA YANG BIKIN ERROR
echo "[1/6] Cleaning old junk..."
systemctl stop cloud54 cloud54-bots 2>/dev/null || true
systemctl stop bot-*.scope 2>/dev/null || true
rm -rf /root/apps/__pycache__ /root/apps/FILE_PO* /root/apps/FILE_* /root/apps/.pycache 2>/dev/null || true
find /root/apps -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /root/apps -type f -name "*.pyc" -delete 2>/dev/null || true

# 4. SIAPIN FOLDER
mkdir -p /root/panel/logs /root/apps
# Copy file dari repo ke /root/panel (handle 2 posisi)
if [ -f "./index.html" ]; then cp -f ./index.html ./app.py ./autostart.py ./requirements.txt /root/panel/ 2>/dev/null || true
else cp -f ./pyrunnercloud54/* /root/panel/ 2>/dev/null || true
fi
cd /root/panel

# 5. FIX DATABASE RUSAK
if [ -f "./bots.db" ]; then
  sqlite3 ./bots.db "SELECT 1" > /dev/null 2>&1 || rm -f ./bots.db
fi
rm -f ./bots.db-journal ./bots.db-wal ./bots.db-shm 2>/dev/null || true

# 6. VENV + REQUIREMENTS (ANTI ERROR)
echo "[2/6] Setup venv..."
rm -rf panel-venv 2>/dev/null || true
python3 -m venv panel-venv
./panel-venv/bin/pip install --upgrade pip -q
./panel-venv/bin/pip install -r requirements.txt -q

# 7. SYSTEMD SERVICE BARU YANG KUAT
echo "[3/6] Setup systemd..."
cat > /etc/systemd/system/cloud54.service << 'SVC'
[Unit]
Description=PyRunnerCloud54 Panel
After=network.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=2
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
SVC

cat > /etc/systemd/system/cloud54-bots.service << 'SVC2'
[Unit]
Description=PyRunner Bot Autostart
After=network.target cloud54.service
Wants=cloud54.service

[Service]
Type=oneshot
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/python /root/panel/autostart.py
RemainAfterExit=yes
User=root

[Install]
WantedBy=multi-user.target
SVC2

# 8. RELOAD & START
echo "[4/6] Starting panel..."
systemctl daemon-reload
systemctl enable cloud54 cloud54-bots > /dev/null 2>&1 || true
systemctl restart cloud54
sleep 2
systemctl restart cloud54-bots || true

# 9. FIX PERMISSION
chmod -R 755 /root/apps /root/panel/logs 2>/dev/null || true

# 10. CEK STATUS
echo "[5/6] Check status..."
systemctl is-active --quiet cloud54 && echo "✅ Panel OK" || echo "❌ Panel gagal, cek: journalctl -u cloud54 -n 20"
IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo ""
echo "=== DONE V10.7 UNIVERSAL ==="
echo "Panel: http://$IP:8000"
echo "Login: admin / cloud54"
echo "Bots: $(ls -1 /root/apps 2>/dev/null | wc -l) bot terdeteksi"
echo ""
echo "Command backup: tar -czf /root/backup-pyrunner-\$(date +%F).tar.gz /root/apps /root/panel/bots.db /root/panel/logs"
