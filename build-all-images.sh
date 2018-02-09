#!/usr/bin/env bash

set -ex

docker build . -f Dockerfile.fc26 -t fridex/thoth-solver-fc26 && docker push fridex/thoth-solver-fc26

