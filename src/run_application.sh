#!/bin/bash

# Set working directory
cd $(dirname "$0")

echo

# Check if docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo " [ERROR] Docker is not installed!" >&2
  exit 1
fi

# Check if the container "opendaylight" is running
if ! docker ps | grep -q "opendaylight"; then
  echo " [ERROR] OpenDaylight container is not running!" >&2
  exit 1
fi

# Check if the container "mininet" is running
if ! docker ps | grep -q "mininet"; then
  echo " [ERROR] Mininet container is not running!" >&2
  exit 1
fi

# Start the application
docker exec -it mininet sudo python3 mininet_data/main.py
