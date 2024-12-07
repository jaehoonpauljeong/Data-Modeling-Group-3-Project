#!/bin/bash

# Set working directory
cd $(dirname "$0")

echo

# Check if docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo " [ERROR] Docker is not installed!" >&2
  exit 1
fi

# Remove existing docker containers
echo " [INFO] Removing existing docker containers..."
docker compose down > /dev/null 2>&1

# Build and run the docker containers
echo " [INFO] Building and running the docker containers..."
docker compose up -d --build > /dev/null 2>&1

# Give the user some information
echo " [INFO] Docker containers are up and running!"
echo "        OpenDaylight needs around a minute to fully start up."
echo "        Please start the application by executing 'src/run_application.sh'."

echo
