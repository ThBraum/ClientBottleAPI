#!/bin/bash

APP=$(echo "$APP" | awk '{print tolower($0)}')

if [ "$APP" = "api" ]; then
    exec bash /app/exec/start/api.sh
    curl -f http://localhost:7071/api/server/ping/ || exit 1
elif [ "$APP" = "healthcheck" ]; then
    exec bash /app/exec/start/healthcheck.sh
else
    echo "Unknown APP: $APP"
    exit 1
fi