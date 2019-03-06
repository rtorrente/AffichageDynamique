#!/bin/sh
yes yes | cp -f scripts/nginx/default.conf /script/nginx/prod && python3 manage.py migrate && python3 manage.py collectstatic --noinput && python3 manage.py crontab add && gunicorn AffichageDynamique.wsgi -b 0.0.0.0:8000 --log-file -
