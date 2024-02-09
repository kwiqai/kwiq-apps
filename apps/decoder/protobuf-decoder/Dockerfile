# Use Python 3.10 image as a base
FROM python:3.10

# Set the working directory in the container
WORKDIR /code

# Install protobuf compiler
RUN apt-get update && apt-get install -y protobuf-compiler

# Install Python dependencies
RUN pip install protobuf

# Copy the Python script into the container
COPY proto_decoder.py .

# Set the default command (can be overridden)
CMD ["python", "./proto_decoder.py"]
