#!/bin/bash

VERSION=0.0.1

cat banner.txt
echo "version $VERSION"

is_server_up () {
  aws --profile=$SMOL_AWS_PROFILE ec2 describe-instances
  return 1
}

