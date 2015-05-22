#!/bin/bash
echo "starting runserver"
exec python manage.py runserver 0.0.0.0:${GUNICORN_PORT:-80}
