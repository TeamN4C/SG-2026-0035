#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
NAME=node2shell-official
IMAGE=node2shell-official:24.22.0

docker build -t "$IMAGE" "$ROOT"

if docker container inspect "$NAME" >/dev/null 2>&1; then
  docker rm -f "$NAME" >/dev/null
fi

docker run -d \
  --name "$NAME" \
  --restart always \
  --network host \
  "$IMAGE" >/dev/null

echo "official Node.js target: http://127.0.0.1:31338/upload"
echo "container: $NAME (continues running after this log view exits)"
echo "stop with: docker rm -f $NAME"
exec docker logs -f "$NAME"
