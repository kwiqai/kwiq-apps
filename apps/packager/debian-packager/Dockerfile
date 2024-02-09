# Use an Ubuntu base image
FROM ubuntu:latest

# Install dpkg-dev and other essential build tools
RUN apt-get update && \
    apt-get install -y dpkg-dev build-essential

# Set a working directory (optional)
WORKDIR /workspace

# By default, run a shell. You can change this to your build script
CMD ["/bin/bash"]
