import socket
import threading
import struct

# save the game state for all players. The keys are player_ids and the values are tuples of (x, y) coordinates. 1-indexed. 3 players maximum. 6 integers for each
player_positions = {1: (0, 0), 2: (0, 0), 3: (0, 0)}

def broadcast_positions(clients):
    """
    sent the all players' positions to all connected clients.
    """
    for client_socket in clients.values():
        if client_socket:
            data = struct.pack(
                "6i", 
                *player_positions[1], 
                *player_positions[2], 
                *player_positions[3]
            )
            client_socket.sendall(data)

def handle_client(client_socket, player_id, clients):
    """
    handle the client and update the postions.
    """
    try:
        while True:
            # Getting the postion from the client (sends 3 values: player_id, x, y)
            data = client_socket.recv(12)  # 12 bytes for 3 integers
            if not data:
                break
            
            # Data decomposition
            received_id, x, y = struct.unpack("3i", data)
            
            # check that the received id matches the current player_id
            if received_id == player_id:
                player_positions[player_id] = (x, y)
                print(f"Player {player_id} updated position to: {x}, {y}")
                
                # sharing the new positions to all connected clients except the sender
                broadcast_positions(clients)
    except Exception as e:
        print(f"Error with player {player_id}: {e}")
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

        # first send the player_id to the client (1-3)
        client_socket.sendall(struct.pack("i", player_id))

        # save the client_socket in the clients dictionary with the player_id as the key
        clients[player_id] = client_socket

        # create the rope thread for this player
        threading.Thread(target=handle_client, args=(client_socket, player_id, clients)).start()
        player_id += 1

if __name__ == "__main__":
    main()
