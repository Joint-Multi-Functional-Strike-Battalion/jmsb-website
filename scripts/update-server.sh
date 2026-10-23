#!/usr/bin/env bash
# Update jmsb.info from git, on the Lightsail box (user, 2026-10-23: "fix that
# so it pulls from git"). The site is a checkout at /var/www/jmsb.info that
# nginx serves from its dist/, the way the PAC sites are checkouts that pull -
# except that this site has to be built, so the box needs node 22 (Astro 7).
#
# One-time setup, done 2026-10-23 (as ec2-user, sudo without password):
#   sudo dnf install -y nodejs22
#   sudo git clone https://github.com/Joint-Multi-Functional-Strike-Battalion/jmsb-website.git /var/www/jmsb.info
#   cd /var/www/jmsb.info && sudo git config pull.ff only
#   sudo ./scripts/update-server.sh
#   in /etc/nginx/conf.d/jmsb-info.conf the 443 server's root is /var/www/jmsb.info/dist
#   (the port-80 acme-challenge root is /var/www/jmsb.info, the checkout itself),
#   then  sudo nginx -t && sudo systemctl reload nginx
#
# Every update after that, once main is pushed:
#   cd /var/www/jmsb.info && sudo ./scripts/update-server.sh
set -euo pipefail

cd "$(dirname "$0")/.."

NODE=$(command -v node-22 || command -v node22 || command -v node)
NPM=$(command -v npm-22 || command -v npm22 || command -v npm)
"$NODE" --version | grep -qE '^v(2[2-9]|[3-9][0-9])\.' || { echo "node 22 or newer is needed (sudo dnf install -y nodejs22); have $("$NODE" --version)"; exit 1; }

echo "== pull"
git pull --ff-only
echo "== install"
"$NPM" ci --no-audit --no-fund --loglevel=error
echo "== build"
"$NODE" node_modules/astro/bin/astro.mjs build
test -f dist/index.html
chmod -R a+rX dist
echo "== done: $(git log --oneline -1)"
