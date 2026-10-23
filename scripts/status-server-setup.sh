#!/usr/bin/env bash
# One-time setup of the server status on the Lightsail box (user, 2026-10-23:
# "add a server status ... monitor our arma server"): a systemd timer runs
# scripts/arma-status.mjs every minute and writes /var/lib/jmsb-status/arma.json,
# which nginx serves as https://jmsb.info/status/arma.json for the home page.
#
#   cd /var/www/jmsb.info && sudo ./scripts/status-server-setup.sh
#
# Safe to run again: it rewrites the units and the nginx location and restarts
# the timer. Needs node 22 (the site's own requirement) and the checkout at
# /var/www/jmsb.info.
set -euo pipefail

SITE=/var/www/jmsb.info
OUT=/var/lib/jmsb-status
NODE=$(command -v node-22 || command -v node22 || command -v node)
CONF=/etc/nginx/conf.d/jmsb-info.conf

mkdir -p "$OUT"
chmod 755 "$OUT"

cat > /etc/systemd/system/jmsb-status.service <<EOF
[Unit]
Description=jmsb.info - Arma server status (A2S query, one JSON file)
After=network-online.target

[Service]
Type=oneshot
ExecStart=$NODE $SITE/scripts/arma-status.mjs $OUT/arma.json
EOF

cat > /etc/systemd/system/jmsb-status.timer <<EOF
[Unit]
Description=jmsb.info - Arma server status every minute

[Timer]
OnBootSec=30s
OnUnitActiveSec=60s
AccuracySec=5s

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now jmsb-status.timer
systemctl start jmsb-status.service || true

# nginx: /status/ is the status folder, never cached, inside the 443 server.
if ! grep -q "location /status/" "$CONF"; then
    cp "$CONF" "/root/jmsb-info.conf.before_status_$(date +%Y%m%d_%H%M%S)"
    sed -i "s#^    location /_astro/#    location /status/ { alias $OUT/; add_header Cache-Control \"no-cache\"; }\n    location /_astro/#" "$CONF"
    nginx -t && systemctl reload nginx
fi

echo "timer: $(systemctl is-active jmsb-status.timer)"
ls -la "$OUT"
