#!/bin/bash
set -e
TARGET_DIR="/app/star-burger/"
cd "$TARGET_DIR"
git pull
source .venv/bin/activate
pip install -r requirements.txt
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundle>
python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput
systemctl reload nginx
curl -X POST "https://api.rollbar.com/api/1/deploy/" \
     -H "Content-Type: application/json" \
     -H "X-Rollbar-Access-Token: a0b492b873cb4cd482ac15880d4c8c4c" \
     -d "{
           \"environment\": \"production\",
           \"revision\": \"$(git rev-parse HEAD)\",
           \"local_username\": \"$(whoami)\",
           \"comment\": \"Deployment completed\"
         }"
echo "Деплой завершен успешен"
