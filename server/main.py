import socket
import struct
import threading

# Store the game state for all players
player_positions = {1: (0, 0), 2: (0, 0)}  # Only two players
player_names = ["Fireboy", "Watergirl"]  # Default names, updated by client
player_roles = {1: "Fire", 2: "Water"}  # Role assignment
player_animations = {1: {"facing_right": True, "walk_frame": 0}, 2: {"facing_right": True, "walk_frame": 0}}  # Animation state

def broadcast_positions(clients):
    """
    Sends all players' positions and animations to all connected clients.
    """
    try:
        # Prepare the data: 2 players, each with x, y, facing_right, walk_frame
        positions_data = struct.pack(
            "4i", 
            *player_positions[1], 
            *player_positions[2]
        )
        names_data = "".join([name.ljust(20) for name in player_names]).encode()
        anim_data = struct.pack(
            "2?2i",
            player_animations[1]["facing_right"], player_animations[2]["facing_right"],
            player_animations[1]["walk_frame"], player_animations[2]["walk_frame"]
        )
        total_data = names_data + positions_data + anim_data
        data_size = struct.pack("i", len(total_data))  # 4 bytes for size
        for client_socket in clients.values():
            if client_socket:
                client_socket.sendall(data_size + total_data)
    except Exception as e:
        print(f"Error broadcasting positions: {e}")

def handle_client(client_socket, player_id, clients):
    """
    Handle the client connection, update positions, names, and animations.
    """
    try:
        # Get name from the client
        name_data = client_socket.recv(20)  # Receive 20 bytes for the player's name
        player_name = name_data.decode().strip()
        player_names[player_id - 1] = player_name  # Update the names in the list
        print(f"Player {player_id} ({player_roles[player_id]}) connected as {player_name}")

        while True:
            # Receive player data (20 bytes: id, x, y, facing_right, walk_frame)
            data = client_socket.recv(20)
            if not data:
                break
            received_id, x, y, facing_right, walk_frame = struct.unpack("3i?1i", data)
            if received_id == player_id:
                player_positions[player_id] = (x, y)
                player_animations[player_id] = {"facing_right": facing_right, "walk_frame": walk_frame}
                print(f"{player_names[player_id - 1]} (Player {player_id}) moved to: {x}, {y}")
                broadcast_positions(clients)
    except Exception as e:
        print(f"Error with {player_names[player_id - 1]} (Player {player_id}): {e}")
    finally:
        client_socket.close()
        del clients[player_id]

def main():
    """
    Main function for the server.
    Starts the server, listens for clients, and handles each client's connection.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(2)  # Only two players
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