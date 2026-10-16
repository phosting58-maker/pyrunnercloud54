#!/bin/bash
set -e
echo "=== PyRunnerCloud54 V12 FINAL ==="
if [ "$EUID" -ne 0 ]; then echo "harus root"; exit 1; fi
apt-get update -y -q
apt-get install -y -q python3 python3-venv python3-pip git curl zip unzip -q || true
rm -rf /root/apps/__pycache__ /root/apps/FILE_PO* /root/panel/bots.db* 2>/dev/null || true
mkdir -p /root/panel/logs /root/apps
cp -f./app.py./index.html./requirements.txt./autostart.py /root/panel/ 2>/dev/null || cp -f./* /root/panel/ 2>/dev/null || true
cd /root/panel
rm -rf panel-venv
python3 -m venv panel-venv
./panel-venv/bin/pip install -r requirements.txt -q
cat > /etc/systemd/system/cloud54.service << 'SVC'
[Unit]
Description=PyRunnerCloud54 Panel
After=network.target
[Service]
Type=simple
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=2
User=root
[Install]
WantedBy=multi-user.target
SVC
cat > /etc/systemd/system/cloud54-bots.service << 'SVC2'
[Unit]
Description=Bot Autostart
After=cloud54.service
[Service]
Type=oneshot
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/python /root/panel/autostart.py
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target
SVC2
systemctl daemon-reload
systemctl enable cloud54 cloud54-bots -q
systemctl restart cloud54
sleep 2
systemctl restart cloud54-bots || true
IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
echo "DONE V12 - Panel: http://$IP:8000 admin/cloud54"
