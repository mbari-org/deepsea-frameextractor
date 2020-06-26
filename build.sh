#!/usr/bin/env bash
docker build -t mbari/deepsea-frameextractor --build-arg DOCKER_GID=`id -u` --build-arg DOCKER_UID=`id -g` .
