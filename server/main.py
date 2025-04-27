import socket
import threading
import struct
import time

# Server settings
IP = "0.0.0.0"  
PORT = 5555  
BUFFER_SIZE = 1024  # Size of the buffer for receiving data

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create UDP socket
server_socket.bind((IP, PORT))  # Bind the socket to the server IP and port
print(f"Server started on {IP}:{PORT}")

players = {}  # Dictionary to store player information by their address
roles = ["Fire", "Water"]  # List of roles (Fire and Water)

def handle_clients():
    while True:
        try:
            data, addr = server_socket.recvfrom(BUFFER_SIZE)  # Wait for data from clients

            if len(data) == struct.calcsize("2i?"):  # If the data is for movement update (x, y, facing_right)
                x, y, facing_right = struct.unpack("2i?", data)  # Unpack the data
                if addr in players:  # Update player position if already in the game
                    players[addr]["x"] = x
                    players[addr]["y"] = y
                    players[addr]["facing_right"] = facing_right
            else:  # Handle a new player joining the game
                message = data.decode()  # Decode the player's name
                if addr not in players and len(players) < 2:  # If not already in the game and max 2 players
                    player_id = len(players) + 1  # Assign ID (1 or 2)
                    role = roles[player_id - 1]  # Assign Fire or Water role
                    start_x = 100 if player_id == 1 else 600  # Initial position (different for each player)
                    start_y = 300
                    players[addr] = {  # Store the player's info
                        "id": player_id,
                        "name": message,
                        "role": role,
                        "x": start_x,
                        "y": start_y,
                        "facing_right": True
                    }
                    print(f"{message} joined as {role}")  # Print when a player joins
                    server_socket.sendto(f"{player_id},{role}".encode(), addr)  # Send player ID and role back to client
        except Exception as e:
            print(f"Error: {e}")  # Catch any errors

def send_positions():
    while True:
        if len(players) == 2:  # If both players are in the game
            all_data = []  # Prepare a message containing info of all players
            for p in players.values():
                player_info = f"{p['id']}|{p['name']}|{p['role']}|{p['x']}|{p['y']}|{int(p['facing_right'])}"
                all_data.append(player_info)  # Gather all players' info in a list
            message = ";".join(all_data)  # Join the player data into one message

            for addr in players:  # Send the message to both players
                server_socket.sendto(message.encode(), addr)
        time.sleep(0.033)  # Send data 30 times per second for smooth updates

# Start threads for handling clients and sending positions
threading.Thread(target=handle_clients, daemon=True).start()
threading.Thread(target=send_positions, daemon=True).start()

while True:
    time.sleep(1)  # Main loop to keep server running
