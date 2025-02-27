import socket
import struct
import threading

# store the game state for all players
player_positions = {1: (0, 0), 2: (0, 0), 3: (0, 0)}
player_names = ["P1", "P2", "P3"]

def broadcast_positions(clients):
    """
    Sends all players' positions to all connected clients.
    """
    try:
        # Prepare the data to send: 3 players, each with x, y
        positions_data = struct.pack(
            "6i", 
            *player_positions[1], 
            *player_positions[2], 
            *player_positions[3]
        )

        # Send the player names (each name is 20 bytes long)
        names_data = "".join([name.ljust(20) for name in player_names]).encode()

        # Calculate total data size
        total_data = names_data + positions_data
        data_size = struct.pack("i", len(total_data))  # 4 bytes for size

        # Send the size first, then the actual data
        for client_socket in clients.values():
            if client_socket:
                client_socket.sendall(data_size + total_data)
    except Exception as e:
        print(f"Error broadcasting positions: {e}")


def handle_client(client_socket, player_id, clients):
    """
    Handle the client connection, update the positions, and names.
    """
    try:
        # Get name from the client
        name_data = client_socket.recv(20)  # Receive 20 bytes for the player's name
        player_name = name_data.decode().strip()
        player_names[player_id - 1] = player_name  # Update the names in the list

        print(f"Player {player_id} connected as {player_name}")

        while True:
            # Receive player position (12 bytes: 3 integers)
            data = client_socket.recv(12)
            if not data:
                break
            
            received_id, x, y = struct.unpack("3i", data)

            if received_id == player_id:
                player_positions[player_id] = (x, y)
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
    server.listen(3)
    print("Server listening on port 5555...")

    clients = {}
    player_id = 1

    while player_id <= 3:
        client_socket, client_address = server.accept()
        print(f"Player {player_id} connected from {client_address}")

        # First, send the player_id to the client
        client_socket.sendall(struct.pack("i", player_id))

        # Save the client_socket in the clients dictionary with the player_id as the key
        clients[player_id] = client_socket

        # Create a new thread for this player
        threading.Thread(target=handle_client, args=(client_socket, player_id, clients)).start()
        player_id += 1

if __name__ == "__main__":
    main()
