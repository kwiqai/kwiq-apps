import argparse
import importlib
import binascii
import subprocess
import sys
import os


def generate_protobuf_classes(proto_file, output_dir):
    # Get the directory of the proto file
    proto_dir = os.path.dirname(proto_file)
    proto_file_name = os.path.basename(proto_file)

    try:
        subprocess.run(["protoc", "-I", proto_dir, f"--python_out={output_dir}", proto_file_name], check=True)
        print(f"Protobuf classes generated in {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate Protobuf classes: {e}", file=sys.stderr)
        sys.exit(1)


def decode_hex(proto_class, hex_data, grpc: bool):
    print(f"Decoding with {proto_class}: ", hex_data)

    byte_data = binascii.unhexlify(hex_data)
    if grpc:
        # Extract the length of the data from the first 5 bytes
        length = int.from_bytes(byte_data[:5], byteorder='big')
        print(f"(debug) length: {length}")
        # Use only the data of the specified length
        byte_data = byte_data[5:5+length]

    message = proto_class()
    message.ParseFromString(byte_data)
    return message


def main():
    parser = argparse.ArgumentParser(description='Protobuf Utilities')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Subparser for generating protobuf classes
    parser_generate = subparsers.add_parser('generate', help='Generate Python classes from .proto files.')
    parser_generate.add_argument('--proto-file', '-p', type=str, required=True,
                                 help='The .proto file to generate Python classes from.')
    parser_generate.add_argument('--output-dir', '-o', type=str, required=True,
                                 help='The output directory for the generated Python classes.')

    # Subparser for decoding hex data
    parser_decode = subparsers.add_parser('decode', help='Decode Protobuf Hex Data.')
    parser_decode.add_argument('--proto-module', '-m', type=str, required=True,
                               help='The location of the protobuf Python module (without .py extension).')
    parser_decode.add_argument('--message-class', '-c', type=str, required=True,
                               help='The name of the target message class.')
    parser_decode.add_argument('--hex-data', '-d', type=str, required=True,
                               help='The encoded protobuf data in hex format.')
    parser_decode.add_argument('--grpc', action='store_true',
                               help='Include gRPC support (optional).')

    # Example of how to use the parser

    args = parser.parse_args()

    try:
        if args.command == 'generate':
            generate_protobuf_classes(args.proto_file, args.output_dir)
        elif args.command == 'decode':
            try:
                proto_module = importlib.import_module(args.proto_module)
                proto_class = getattr(proto_module, args.message_class)
                decoded_message = decode_hex(proto_class, args.hex_data, args.grpc)
                print(f"→ {decoded_message}")
            except ImportError:
                print(
                    f"Error: Unable to import module {args.proto_module}. Ensure the module path is correct and the module is in your Python path.",
                    file=sys.stderr)
            except AttributeError:
                print(f"Error: The class {args.message_class} was not found in module {args.proto_module}.",
                      file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
