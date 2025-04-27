import socket
import threading
import struct
import time

# Server settings
IP = "0.0.0.0"
PORT = 5555
BUFFER_SIZE = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP, PORT))
print(f"Server started on {IP}:{PORT}")

players = {}
roles = ["Fire", "Water"]

def handle_clients():
    while True:
        try:
            data, addr = server_socket.recvfrom(BUFFER_SIZE)

            if len(data) == struct.calcsize("2i?"):  # Movement update
                x, y, facing_right = struct.unpack("2i?", data)
                if addr in players:
                    players[addr]["x"] = x
                    players[addr]["y"] = y
                    players[addr]["facing_right"] = facing_right
            else:  # New player joining
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
                    print(f"{message} joined as {role}")
                    server_socket.sendto(f"{player_id},{role}".encode(), addr)
        except Exception as e:
            print(f"Error: {e}")

def send_positions():
    while True:
        if len(players) == 2:
            all_data = []
            for p in players.values():
                # Send all player info
                player_info = f"{p['id']}|{p['name']}|{p['role']}|{p['x']}|{p['y']}|{int(p['facing_right'])}"
                all_data.append(player_info)
            message = ";".join(all_data)

            for addr in players:
                server_socket.sendto(message.encode(), addr)
        time.sleep(0.033)  # 30 times per second (smoother)

threading.Thread(target=handle_clients, daemon=True).start()
threading.Thread(target=send_positions, daemon=True).start()

while True:
    time.sleep(1)
