import socket
import struct
import threading
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["fire_water_game"]

# Game state
player_positions = {1: (0, 0), 2: (0, 0)}
player_names = ["Fireboy", "Watergirl"]
player_roles = {1: "Fire", 2: "Water"}
player_animations = {1: {"facing_right": True, "walk_frame": 0}, 2: {"facing_right": True, "walk_frame": 0}}
player_approvals = {1: False, 2: False}  # Approval for next level
current_level = 1

def broadcast_positions(clients):
    """Sends all players' positions and animations to all connected clients."""
    try:
        positions_data = struct.pack("4i", *player_positions[1], *player_positions[2])
        names_data = "".join([name.ljust(20) for name in player_names]).encode()
        anim_data = struct.pack("2?2i", player_animations[1]["facing_right"], player_animations[2]["facing_right"],
                                player_animations[1]["walk_frame"], player_animations[2]["walk_frame"])
        total_data = names_data + positions_data + anim_data
        data_size = struct.pack("i", len(total_data))
        for client_socket in clients.values():
            if client_socket:
                client_socket.sendall(data_size + total_data)
    except Exception as e:
        print(f"Error broadcasting positions: {e}")

def handle_client(client_socket, player_id, clients):
    """Handle client connection, update positions, names, animations, and approvals."""
    global current_level
    try:
        name_data = client_socket.recv(20)
        player_name = name_data.decode().strip()
        player_names[player_id - 1] = player_name
        print(f"Player {player_id} ({player_roles[player_id]}) connected as {player_name}")

        while True:
            data = client_socket.recv(20)  # Original size: id, x, y, facing_right, walk_frame
            if not data:
                break
            received_id, x, y, facing_right, walk_frame = struct.unpack("3i?1i", data)
            if received_id == player_id:
                player_positions[player_id] = (x, y)
                player_animations[player_id] = {"facing_right": facing_right, "walk_frame": walk_frame}
                if x == -100 and y == -100:
                    player_approvals[player_id] = True
                else:
                    player_approvals[player_id] = False
                
                if all(player_approvals.values()):
                    current_level += 1
                    player_approvals[1] = player_approvals[2] = False
                    print(f"Both players approved, moving to level {current_level}")
                
                broadcast_positions(clients)
    except Exception as e:
        print(f"Error with {player_names[player_id - 1]} (Player {player_id}): {e}")
    finally:
        client_socket.close()
        del clients[player_id]

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(2)
    print("Server listening on port 5555...")
    clients = {}
    player_id = 1
    while player_id <= 2:
        client_socket, client_address = server.accept()
        print(f"Player {player_id} ({player_roles[player_id]}) connected from {client_address}")
        client_socket.sendall(struct.pack("i", player_id))
        clients[player_id] = client_socket
        threading.Thread(target=handle_client, args=(client_socket, player_id, clients)).start()
        player_id += 1

if __name__ == "__main__":
    main()