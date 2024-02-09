#!/bin/bash

set -x

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <path_to_protobuf_python_module> <message_class_name> <hex_encoded_data>"
    exit 1
fi

# Assign arguments to variables
PROTOBUF_MODULE_DIR=$1
MESSAGE_CLASS=$2
HEX_DATA=$3

# Absolute path is required for mounting the protobuf module
ABS_MODULE_PATH=$(realpath "$PROTOBUF_MODULE_DIR")
ABS_MODULE_DIR=$(dirname "$ABS_MODULE_PATH")
MODULE_NAME=$(basename "$ABS_MODULE_PATH" .py)

# Run the Docker container with the protobuf module volume mounted
docker run -it --rm \
    -v "$ABS_MODULE_DIR":/code/protobuf_module \
    protobuf-decoder python proto_decoder.py decode -m "protobuf_module.$MODULE_NAME" -c "$MESSAGE_CLASS" -d "$HEX_DATA" --grpc
