import socket
import threading
import struct
import time
import keyboard


player_to_update = "player1"


def receive_data(client_socket: socket.socket):
    while True:
        packed_data = client_socket.recv(24)
        if not packed_data:
            break

        flattened_data = struct.unpack("6i", packed_data)

        print("Received player data:")
        print(f"Player 1: ({flattened_data[0]}, {flattened_data[1]})")
        print(f"Player 2: ({flattened_data[2]}, {flattened_data[3]})")
        print(f"Player 3: ({flattened_data[4]}, {flattened_data[5]})")

        time.sleep(0.1)


def send_update(client_socket: socket.socket):
    global player_to_update

    while True:
        if keyboard.is_pressed("up"):
            print(f"Up arrow pressed. Updating {player_to_update} y-coordinate.")

            flattened_data = ("player1".encode(), 10, 20)

            packed_data = struct.pack("7sii", *flattened_data)

            client_socket.sendall(packed_data)

            time.sleep(0.1)


def start_client(host="127.0.0.1", port=443):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((host, port))
    print(f"Connected to server at {host}:{port}")

    receive_thread = threading.Thread(target=receive_data, args=(client_socket,))
    receive_thread.start()

    update_thread = threading.Thread(target=send_update, args=(client_socket,))
    update_thread.start()


if __name__ == "__main__":
    start_client()
