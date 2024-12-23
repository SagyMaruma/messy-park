import socket
import struct


def start_client(host="127.0.0.1", port=443):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((host, port))

    packed_data = client_socket.recv(1024)

    unpacked_data = struct.unpack("!10s I f", packed_data)

    name = unpacked_data[0].decode("utf-8").strip("\x00")
    age = unpacked_data[1]
    balance = unpacked_data[2]

    print(f"Name: {name}, Age: {age}, Balance: {balance}")

    while True:
        message = input(
            "Enter a message to send to the server (or 'exit' to disconnect): "
        )

        if message.lower() == "exit":
            print("Disconnecting from server...")
            break

        client_socket.sendall(message.encode("utf-8"))

        response = client_socket.recv(1024)
        print(f"Server response: {response.decode('utf-8')}")

    client_socket.close()
    print("Connection closed.")


if __name__ == "__main__":
    start_client()
