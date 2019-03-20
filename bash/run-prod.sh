#!/bin/sh
yes yes | export -p > /tmp/env.txt  && cp -f scripts/nginx/default.conf scripts/nginx/prod && python3 manage.py migrate && python3 manage.py collectstatic --noinput && python3 manage.py crontab add && service cron start && gunicorn AffichageDynamique.wsgi -b 0.0.0.0:8000 --log-file -
