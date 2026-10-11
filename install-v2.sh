#!/bin/bash
# PyRunner Cloud54 - Anti Kumat Installer V2 - Port 80
set -e
echo ">>> [1/6] Install deps..."
apt update -y
apt install -y python3-venv python3-pip curl ufw

echo ">>> [2/6] Clean old..."
systemctl stop cloud54 2>/dev/null || true
rm -rf /root/panel-venv /root/panel
mkdir -p /root/panel /root/apps

echo ">>> [3/6] Download app.py..."
curl -sL https://raw.githubusercontent.com/phosting58-maker/pyrunnercloud54/main/app.py -o /root/panel/app.py

echo ">>> [4/6] Create venv..."
python3 -m venv /root/panel-venv
/root/panel-venv/bin/pip install --upgrade pip -q
/root/panel-venv/bin/pip install fastapi uvicorn psutil python-multipart -q

echo ">>> [5/6] Create service port 80..."
cat > /etc/systemd/system/cloud54.service <<'EOF'
[Unit]
Description=Cloud54 Panel - Anti Kumat
After=network.target
[Service]
WorkingDirectory=/root/panel
ExecStart=/root/panel-venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 80
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now cloud54
ufw allow 80/tcp 2>/dev/null || true
iptables -I INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || true

echo ">>> [6/6] Check..."
sleep 3
systemctl status cloud54 --no-pager || true
IP=$(curl -s4 ifconfig.me || hostname -I | awk '{print $1}')
echo ""
echo "=========================================="
echo " PANEL CLOUDPUSAT54! ✅"
echo " URL: http://$IP"
echo " Login: admin / cloud54"
echo " Port: 80 (Anti tabrakan bot)"
echo "=========================================="
