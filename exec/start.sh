#!/bin/bash

if [ -f /app/.env ]; then
    export $(cat /app/.env | xargs)
fi

exec bash /app/exec/start/api.sh
