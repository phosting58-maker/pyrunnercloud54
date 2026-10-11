#!/bin/bash
rm -rf /root/panel /root/panel-venv 2>/dev/null
mkdir -p /root/panel /root/apps
python3 -m venv /root/panel-venv
/root/panel-venv/bin/pip install fastapi uvicorn psutil python-multipart -q
curl -sL https://raw.githubusercontent.com/phosting58-maker/pyrunnercloud54/main/app.py -o /root/panel/app.py
cat > /etc/systemd/system/cloud54.service << 'SVC'
[Unit]
Description=PyRunnerCloud54 Panel
After=network.target
[Service]
Type=simple
User=root
WorkingDirectory=/root/panel
ExecStart=/root/panel-venv/bin/uvicorn app:app --host 0.0.0.0 --port 2121 --workers 1
Restart=always
RestartSec=2
[Install]
WantedBy=multi-user.target
SVC
systemctl daemon-reload
systemctl enable cloud54 --now
systemctl restart cloud54
sleep 2
IP=$(curl -4 -s ifconfig.me)
echo "======================================"
echo "✅ PYRUNNER CLOUD54 READY!"
echo "LINK: http://$IP:2121/login"
echo "USER: admin"
echo "PASS: cloud54"
echo "======================================"