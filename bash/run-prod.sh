#!/bin/sh
yes yes | service cron start && cp -f scripts/nginx/default.conf scripts/nginx/prod && python3 manage.py migrate && python3 manage.py collectstatic --noinput && python3 manage.py crontab add && gunicorn AffichageDynamique.wsgi -b 0.0.0.0:8000 --log-file -
