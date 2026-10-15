#!/bin/bash
set -e
SRC="$(pwd)"
mkdir -p /root/panel /root/apps
cp -vf $SRC/app.py $SRC/index.html /root/panel/
cp -vf $SRC/requirements.txt /root/panel/ 2>/dev/null || true
cd /root/panel
apt update -y
apt install -y python3-venv python3.10-venv python3-pip git curl ufw
rm -rf panel-venv
python3 -m venv panel-venv
./panel-venv/bin/pip install --upgrade pip
./panel-venv/bin/pip install -r requirements.txt
cat > /etc/systemd/system/cloud54.service << 'SVC'
[Unit]
Description=CloudPusat54 Panel
After=network.target
[Service]
Type=simple
User=root
WorkingDirectory=/root/panel
ExecStart=/root/panel/panel-venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1
[Install]
WantedBy=multi-user.target
SVC
ufw allow 8000/tcp 2>/dev/null || true
iptables -I INPUT -p tcp --dport 8000 -j ACCEPT 2>/dev/null || true
systemctl daemon-reload
systemctl enable cloud54
systemctl restart cloud54
sleep 2
echo "DONE: http://$(curl -s ifconfig.me):8000"
