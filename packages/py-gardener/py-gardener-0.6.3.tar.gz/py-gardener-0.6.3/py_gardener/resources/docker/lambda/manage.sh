#!/bin/sh

sudo docker build -t lambda-environment-python -f docker/Dockerfile . &&
sudo docker run \
  -u=$UID:$(id -g $USER) \
  -v $(pwd):/user/project \
  -v ~/.aws:/user/.aws \
  -v ~/.npmrc:/user/.npmrc \
  -it lambda-environment-python
