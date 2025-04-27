import socket
import threading
import struct
import time

IP = "0.0.0.0"
PORT = 5555
BUFFER_SIZE = 4096

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP, PORT))
print(f"Server started on {IP}:{PORT}")

players = {}
roles = ["Fire", "Water"]
standing_on_doors = {}
current_level = 0
max_levels = 3

def handle_clients():
    while True:
        try:
            data, addr = server_socket.recvfrom(BUFFER_SIZE)

            if len(data) == struct.calcsize("2i?b"):
                x, y, facing_right, on_door = struct.unpack("2i?b", data)
                if addr in players:
                    players[addr]["x"] = x
                    players[addr]["y"] = y
                    players[addr]["facing_right"] = facing_right
                    standing_on_doors[addr] = bool(on_door)
            else:
                message = data.decode()
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
                        "facing_right": True
                    }
                    standing_on_doors[addr] = False
                    print(f"{message} joined as {role}")
                    server_socket.sendto(f"{player_id},{role}".encode(), addr)
        except Exception as e:
            print(f"Error: {e}")

def send_positions():
    global current_level
    while True:
        if len(players) == 2:
            all_data = []
            for p in players.values():
                player_info = f"{p['id']}|{p['name']}|{p['role']}|{p['x']}|{p['y']}|{int(p['facing_right'])}"
                all_data.append(player_info)
            message = ";".join(all_data)

            for addr in players:
                server_socket.sendto(message.encode(), addr)

            if all(standing_on_doors.values()) and len(standing_on_doors) == 2:
                current_level += 1
                if current_level >= max_levels:
                    current_level = max_levels - 1  # Stay at last level
                print(f"Loading Level {current_level}")
                time.sleep(1)
                for addr in players:
                    server_socket.sendto(f"LEVEL:{current_level}".encode(), addr)

        time.sleep(0.033)

threading.Thread(target=handle_clients, daemon=True).start()
threading.Thread(target=send_positions, daemon=True).start()

while True:
    time.sleep(1)
