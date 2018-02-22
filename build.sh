#!/bin/sh

docker login -u $DOCKER_USER -p $DOCKER_PASS

docker build . -f Dockerfile.fc26 -t fridex/thoth-solver-fc26
docker build . -f Dockerfile.fc27 -t fridex/thoth-solver-fc27

docker push fridex/thoth-solver-fc26
docker push fridex/thoth-solver-fc27
