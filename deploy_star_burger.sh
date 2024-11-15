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
echo "Деплой завершен успешен"
