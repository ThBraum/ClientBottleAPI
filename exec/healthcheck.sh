#!/bin/bash

APP=$(echo "$APP" | awk '{print tolower($0)}')
MODE=${MODE^^}

if [ "$MODE" == "LOCAL" ]; then
    curl -f http://localhost:7071/api/server/ping/ || exit 1
else
    echo "Unknown APP: $APP"
    exit 1
fi