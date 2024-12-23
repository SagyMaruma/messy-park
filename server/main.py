import socket
import threading
import struct


def handle_client(client_socket: socket, client_address: str):
    try:
        print(f"Connection established with {client_address}")

        data_to_send = {"name": "Alice", "age": 25, "balance": 1234.56}

        packed_data = struct.pack(
            "!10s I f",
            data_to_send["name"].encode("utf-8"),
            data_to_send["age"],
            data_to_send["balance"],
        )

        client_socket.sendall(packed_data)

        while True:
            try:
                client_message = client_socket.recv(1024)

                if not client_message:
                    print(f"Client {client_address} disconnected.")
                    break

                print(
                    f"Received message from {client_address}: {client_message.decode('utf-8')}"
                )

                client_socket.sendall(b"Message received")

            except Exception as e:
                print(f"Error with client {client_address}: {e}")
                break

    finally:
        client_socket.close()
        print(f"Connection closed with {client_address}")


def start_server(host="0.0.0.0", port=443):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((host, port))

    server_socket.listen(5)
    print(f"Server started on {host}:{port}. Waiting for connections...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        client_thread = threading.Thread(
            target=handle_client, args=(client_socket, client_address)
        )
        client_thread.start()


if __name__ == "__main__":
    start_server()
