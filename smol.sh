#!/bin/bash

source smol.properties

if [ "$SMOL_HOSTING" = "aws" ]; then
  source remote/aws/smol-aws.sh
fi

if is_server_up; then
  echo "up"
else
  echo "down"
fi