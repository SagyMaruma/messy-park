import socket
import threading
import struct
import time


data = {
    "player1": {"x": 500, "y": 300},
    "player2": {"x": 300, "y": 200},
    "player3": {"x": 350, "y": 600},
}


def send_data(client_socket: socket.socket):
    global data

    while True:
        flattened_data = (
            data["player1"]["x"],
            data["player1"]["y"],
            data["player2"]["x"],
            data["player2"]["y"],
            data["player3"]["x"],
            data["player3"]["y"],
        )
        packed_data = struct.pack("6i", *flattened_data)

        client_socket.sendall(packed_data)

        time.sleep(0.1)


def update_data(client_socket: socket.socket):
    global data

    while True:
        client_message = client_socket.recv(16)

        player_to_update, increment_x, increment_y = struct.unpack(
            "7sii", client_message
        )

        if not client_message:
            break

        data[bytes(player_to_update).decode()]["x"] += increment_x
        data[bytes(player_to_update).decode()]["y"] += increment_y

        print(
            f"Updated {bytes(player_to_update).decode()} with x: {increment_x} and y: {increment_y}"
        )


def start_server(host="0.0.0.0", port=443):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server started on {host}:{port}. Waiting for connections...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        send_thread = threading.Thread(target=send_data, args=(client_socket,))
        send_thread.start()

        update_thread = threading.Thread(target=update_data, args=(client_socket,))
        update_thread.start()


if __name__ == "__main__":
    start_server()
