#!/bin/bash
cd "$(dirname "$0")"
PORT=8088
while lsof -i :$PORT >/dev/null 2>&1; do PORT=$((PORT+1)); done
echo "Nephélé  →  http://localhost:$PORT   (Ctrl-C pour arrêter)"
( sleep 1; open "http://localhost:$PORT" ) &
python3 -m http.server $PORT
