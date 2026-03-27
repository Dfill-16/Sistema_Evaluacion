# !/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

npm ci
npm run build

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py createsuperuser --no-input || true