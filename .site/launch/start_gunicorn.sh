#!/bin/bash
echo "GUNICORN_PORT: ${GUNICORN_PORT}"
echo "GUNICORN_WORKERS: ${GUNICORN_WORKERS}"

if [ $ENABLE_GEVENT = true ] || [ $ENABLE_GEVENT = '1' ] || [ $ENABLE_GEVENT = 1 ]; then
    exec /app/launch/start_gunicorn_with_gevent.sh
else
    exec /app/launch/start_gunicorn_without_gevent.sh
fi
