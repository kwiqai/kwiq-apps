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


def decode_hex(proto_class, hex_data):
    print("Decoding: ", proto_class, hex_data)

    byte_data = binascii.unhexlify(hex_data)
    print("Byte Data: ", byte_data)
    message = proto_class()
    print("Message Empty Class: ", message)

    message.ParseFromString(byte_data)
    return message


def main():
    parser = argparse.ArgumentParser(description='Protobuf Utilities')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Subparser for generating protobuf classes
    parser_generate = subparsers.add_parser('generate', help='Generate Python classes from .proto files.')
    parser_generate.add_argument('proto_file', type=str, help='The .proto file to generate Python classes from.')
    parser_generate.add_argument('output_dir', type=str, help='The output directory for the generated Python classes.')

    # Subparser for decoding hex data
    parser_decode = subparsers.add_parser('decode', help='Decode Protobuf Hex Data.')
    parser_decode.add_argument('proto_module', type=str,
                               help='The location of the protobuf Python module (without .py extension).')
    parser_decode.add_argument('message_class', type=str, help='The name of the target message class.')
    parser_decode.add_argument('hex_data', type=str, help='The encoded protobuf data in hex format.')

    args = parser.parse_args()

    try:
        if args.command == 'generate':
            generate_protobuf_classes(args.proto_file, args.output_dir)
        elif args.command == 'decode':
            try:
                proto_module = importlib.import_module(args.proto_module)
                proto_class = getattr(proto_module, args.message_class)
                decoded_message = decode_hex(proto_class, args.hex_data)
                print(decoded_message)
            except ImportError:
                print(f"Error: Unable to import module {args.proto_module}. Ensure the module path is correct and the module is in your Python path.", file=sys.stderr)
            except AttributeError:
                print(f"Error: The class {args.message_class} was not found in module {args.proto_module}.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
