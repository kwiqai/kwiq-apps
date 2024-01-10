import sys


def main():
    # Check if there are enough command line arguments
    if len(sys.argv) < 3:
        print("Usage: python script.py <number_of_bytes_to_ignore> <comma_separated_bytes>")
        sys.exit(1)

    # Parse the number of bytes to ignore
    try:
        bytes_to_ignore = int(sys.argv[1])
    except ValueError:
        print("Invalid number for bytes to ignore. Please enter a valid integer.")
        sys.exit(1)

    # Get the byte string from the command line argument
    byte_string = sys.argv[2]

    # Convert the byte string to a list of integers
    try:
        bytes_list = [int(b) for b in byte_string.split(',')]
    except ValueError:
        print("Invalid input. Please ensure you have entered a comma-separated list of bytes.")
        sys.exit(1)

    # Ignore the first N bytes
    if bytes_to_ignore > len(bytes_list):
        print("The number of bytes to ignore is greater than the length of the byte array.")
        sys.exit(1)

    bytes_list = bytes_list[bytes_to_ignore:]

    # Convert remaining bytes to hexadecimal
    hex_string = ''.join(f'{b:02x}' for b in bytes_list)
    print(f"Hexadecimal representation: {hex_string}")

    # Try to decode the remaining bytes to a string
    try:
        decoded_string = bytes(bytes_list).decode('utf-8')
        print(f"Decoded string: {decoded_string}")
    except UnicodeDecodeError:
        print("Unable to decode the byte array to a string using UTF-8 encoding.")


if __name__ == "__main__":
    main()
