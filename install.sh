#!/bin/bash
set -e
echo "=== PyRunnerCloud54 V10.3 FINAL ==="
[ "$EUID" -ne 0 ] && echo "run as root" && exit 1
mkdir -p /root/panel/logs /root/apps
cp -r. /root/panel/ 2>/dev/null || cp index.html app.py autostart.py requirements.txt /root/panel/ 2>/dev/null || true
cd /root/panel
python3 -m venv panel-venv
./panel-venv/bin/pip install --upgrade pip -q
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
RestartSec=3
User=root
[Install]
WantedBy=multi-user.target
SVC
cat > /etc/systemd/system/cloud54-bots.service << 'SVC2'
[Unit]
Description=PyRunner Bot Autostart
After=network.target cloud54.service
[Service]
Type=oneshot
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/python /root/panel/autostart.py
RemainAfterExit=yes
User=root
[Install]
WantedBy=multi-user.target
SVC2
systemctl daemon-reload
systemctl enable cloud54 cloud54-bots
systemctl restart cloud54
systemctl restart cloud54-bots || true
echo "DONE http://$(curl -s ifconfig.me):8000 - WELCOME TO PYRUNNERCLOUD54"
