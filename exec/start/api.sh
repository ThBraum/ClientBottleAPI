#!/bin/bash

HOST="0.0.0.0"
PORT=7071
APP_NAME="server.__main__:app"

GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}


MODE=${MODE^^}


if [ "$MODE" == "PROD" ]; then
    echo "Running in PROD mode"
    exec gunicorn \
        --bind "$HOST:$PORT" \
        --max-requests 400 \
        --max-requests-jitter 40 \
        --workers $GUNICORN_WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        "$APP_NAME"
else
    echo "Running in DEV mode"
    echo "INFO- Host: $HOST, Port: $PORT, App: $APP_NAME, Mode: $MODE"
    exec uvicorn --host "$HOST" --port "$PORT" --reload "$APP_NAME"
fi
