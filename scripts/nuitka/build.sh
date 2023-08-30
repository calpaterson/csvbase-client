#!/usr/bin/env bash

set -xe

# Build the Docker image using the Dockerfile (from root)
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
repo_root="$script_dir/../.."
cd $repo_root
docker build -f scripts/nuitka/Dockerfile.nuitka . -t csvbase-client-build:latest

# Create a temporary container from the built image
container_id=$(docker create csvbase-client-build:latest)

# Copy the binary from the container to your local machine
docker cp "$container_id":"csvbase-client" "dist/csvbase-client"

# Clean up: remove the temporary container
docker rm "$container_id"
