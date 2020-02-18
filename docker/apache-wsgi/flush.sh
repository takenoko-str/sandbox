#!/bin/bash

IMAGE_NAME="$1"
IMAGE_TAG=latest
PORT=80

[ -z "$IMAGE_NAME" ] && echo "image name not found" && exit
CONTAINER_ID=$(docker ps | grep "$IMAGE_NAME" | awk '{print $1}')
[ -n "$CONTAINER_ID" ] && docker rm -f "$CONTAINER_ID"
lsof -i:"$PORT"
[ $? -eq 0 ] && echo "port is already allocated" && exit
docker build -t "$IMAGE_NAME:$IMAGE_TAG" .
docker run -p "$PORT:$PORT" -itd "$IMAGE_NAME:$IMAGE_TAG"
docker exec -it "$(docker ps | grep "$IMAGE_NAME" | awk '{print $1}')" /bin/bash

