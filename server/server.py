import socket
import threading
import struct
import time
from pymongo import MongoClient

# Server configuration
IP = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 4096

# Create and bind the UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP, PORT))
print(f"Server started on {IP}:{PORT}")

# Data structures to store player info and game state
players = {}  # key: address, value: player data
roles = ["Fire", "Water"]  # predefined roles
standing_on_doors = {}  # key: address, value: bool
current_level = 0
max_levels = 3
start_time = None
game_over = False

# MongoDB connection to store game results
client = MongoClient("mongodb://localhost:27017/")
db = client["fire_and_water_game"]
results_collection = db["game_results"]


# Function to handle incoming messages from clients
def handle_clients():
    global start_time
    while True:
        try:
            data, addr = server_socket.recvfrom(BUFFER_SIZE)

            # Print received data for debugging
            print(f"Received data: {data} from {addr}")  # Debug print statement

            # Player position and status update
            if len(data) == struct.calcsize("2i?b"):
                x, y, facing_right, on_door = struct.unpack("2i?b", data)
                if addr in players:
                    players[addr]["x"] = x
                    players[addr]["y"] = y
                    players[addr]["facing_right"] = facing_right
                    standing_on_doors[addr] = bool(on_door)
            else:
                # Initial player connection (expecting the name as a string)
                message = data.decode()
                print(
                    f"Decoded message: {message}"
                )  # Debug print statement for the player name

                if addr not in players and len(players) < 2:
                    player_id = len(players) + 1
                    role = roles[player_id - 1]
                    start_x = 100 if player_id == 1 else 600
                    start_y = 300
                    players[addr] = {
                        "id": player_id,
                        "name": message,
                        "role": role,
                        "x": start_x,
                        "y": start_y,
                        "facing_right": True,
                    }
                    standing_on_doors[addr] = False
                    print(f"{message} joined as {role}")
                    # Print the names of players joining
                    print(
                        f"Player {message} has joined the game."
                    )  # This will print to terminal when a player joins
                    # Send assigned role and ID to the player
                    server_socket.sendto(f"{player_id},{role}".encode(), addr)

                    # If both players are connected, start the game timer
                    if len(players) == 2:
                        start_time = time.time()
                        print("Both players connected. Starting timer!")
        except Exception as e:
            print(f"Error: {e}")


# Function to continuously broadcast player positions and handle level progression
def send_positions():
    global current_level, game_over
    while True:
        if len(players) == 2:
            all_data = []
            for p in players.values():
                # Serialize player data for broadcast
                player_info = f"{p['id']}|{p['name']}|{p['role']}|{p['x']}|{p['y']}|{int(p['facing_right'])}"
                all_data.append(player_info)
            message = ";".join(all_data)

            # Send to all clients
            for addr in players:
                server_socket.sendto(message.encode(), addr)

            # Check if both players are standing on their doors
            if all(standing_on_doors.values()) and len(standing_on_doors) == 2:
                if current_level < max_levels - 1:
                    # Move to next level
                    current_level += 1
                    print(f"Loading Level {current_level}")
                    time.sleep(1)
                    for addr in players:
                        server_socket.sendto(f"LEVEL:{current_level}".encode(), addr)
                    for addr in standing_on_doors:
                        standing_on_doors[addr] = False
                else:
                    # Game finished, record results
                    if not game_over:
                        end_time = time.time()
                        total_time = round(end_time - start_time, 2)
                        print(f"Game finished! Total time: {total_time} seconds.")
                        for addr in players:
                            server_socket.sendto(
                                f"GAME_OVER:{total_time}".encode(), addr
                            )

                        result = {
                            "player1": list(players.values())[0]["name"],
                            "player2": list(players.values())[1]["name"],
                            "total_time_seconds": total_time,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        results_collection.insert_one(result)
                        print("Saved game result to MongoDB.")
                        game_over = True
        time.sleep(0.033)  # approx 30 FPS update rate


# Start server threads
threading.Thread(target=handle_clients, daemon=True).start()
threading.Thread(target=send_positions, daemon=True).start()

# Keep the server running
while True:
    time.sleep(1)
