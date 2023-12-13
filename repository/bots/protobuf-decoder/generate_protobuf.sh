#!/bin/bash

set -x

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <path_to_proto_file> <output_directory>"
    exit 1
fi

# Assign arguments to variables
PROTO_FILE_PATH=$1
OUTPUT_DIR_PATH=$2

# Get the absolute path of the .proto file and its directory
ABS_PROTO_PATH=$(realpath "$PROTO_FILE_PATH")
ABS_PROTO_DIR=$(dirname "$ABS_PROTO_PATH")
PROTO_FILE_NAME=$(basename "$ABS_PROTO_PATH")

mkdir -p "${OUTPUT_DIR_PATH}"

# Get the absolute path of the output directory
ABS_OUTPUT_PATH=$(realpath "$OUTPUT_DIR_PATH")

# Run the Docker container with the necessary volumes mounted
docker run -it --rm \
    -v "$ABS_PROTO_DIR":/code/proto \
    -v "$ABS_OUTPUT_PATH":/code/protobuf_module \
    protobuf-decoder python proto_decoder.py generate /code/proto/"$PROTO_FILE_NAME" /code/protobuf_module