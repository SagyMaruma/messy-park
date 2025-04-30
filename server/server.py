# --- server.py ---
import socket
import threading
import struct
import time
import logging
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
IP = "127.0.0.1"
PORT = 5555
BUFFER_SIZE = 4096

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP, PORT))
logging.info(f"Server started on {IP}:{PORT}")

bullets = []  # Each bullet is a dict: {"x": int, "y": int, "dir": int}
players = {}
roles = ["Fire", "Water"]
standing_on_doors = {}
last_seen = {}
current_level = 1
max_levels = 3
start_time = None
game_over = False
button_active = False

# Elevator state per level
elevator_states = {
    0: {"y": 600, "max_up": 480, "base_y": 600},
    1: {"y": 600, "max_up": 500, "base_y": 600},
    2: {"y": 600, "max_up": 500, "base_y": 600}
}
elevator_speed = 2

client = MongoClient("mongodb://localhost:27017/")
db = client["fire_and_water_game"]
results_collection = db["game_results"]

def handle_clients():
    global start_time, button_active
    while True:
        try:
            data, addr = server_socket.recvfrom(BUFFER_SIZE)
            last_seen[addr] = time.time()

            if len(data) == struct.calcsize("2i?b?"):
                x, y, facing_right, on_door, button = struct.unpack("2i?b?", data)
                if addr in players:
                    players[addr]["x"] = x
                    players[addr]["y"] = y
                    players[addr]["facing_right"] = facing_right
                    standing_on_doors[addr] = bool(on_door)
                    if button:
                        button_active = True
            else:
                message = data.decode()
                if addr not in players and len(players) < 2:
                    pid = len(players) + 1
                    role = roles[pid - 1]
                    players[addr] = {"id": pid, "name": message, "role": role, "x": 100 if role == "Fire" else 600, "y": 300, "facing_right": True}
                    standing_on_doors[addr] = False
                    server_socket.sendto(f"{pid},{role}".encode(), addr)
                    if len(players) == 2:
                        start_time = time.time()
        except:
            continue

def send_positions():
    global current_level, game_over, button_active
    bullet_timer = 0
    while True:
        if len(players) == 2:
            e = elevator_states[current_level]
            if button_active and e["y"] > e["max_up"]:
                e["y"] -= elevator_speed
            elif not button_active and e["y"] < e["base_y"]:
                e["y"] += elevator_speed
            button_active = False

            # Update bullets
            bullet_timer += 1
            if bullet_timer >= 20:  # spawn bullet every ~20 frames (~3 times/sec)
                bullet_timer = 0
                bullets.append({"x": 150, "y": 410, "dir": 1})  # Example position/direction

            for bullet in bullets[:]:
                bullet["x"] += bullet["dir"] * 5
                if bullet["x"] < 0 or bullet["x"] > 1000:
                    bullets.remove(bullet)

            # Format bullet positions
            bullet_data = ";".join(f'{b["x"]},{b["y"]}' for b in bullets)

            data_lines = []
            for p in players.values():
                data_lines.append(f"{p['id']}|{p['name']}|{p['role']}|{p['x']}|{p['y']}|{int(p['facing_right'])}")
            message = ";".join(data_lines)

            for addr in players:
                server_socket.sendto(message.encode(), addr)
                server_socket.sendto(f"ELEVATOR:{e['y']}".encode(), addr)
                server_socket.sendto(f"BULLETS:{bullet_data}".encode(), addr)

            if all(standing_on_doors.values()) and not game_over:
                if current_level < max_levels - 1:
                    current_level += 1
                    for addr in players:
                        server_socket.sendto(f"LEVEL:{current_level}".encode(), addr)
                    for addr in standing_on_doors:
                        standing_on_doors[addr] = False
                else:
                    total_time = round(time.time() - start_time, 2)
                    for addr in players:
                        server_socket.sendto(f"GAME_OVER:{total_time}".encode(), addr)
                    results_collection.insert_one({
                        "player1": list(players.values())[0]["name"],
                        "player2": list(players.values())[1]["name"],
                        "total_time_seconds": total_time,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    game_over = True
        time.sleep(0.033)

threading.Thread(target=handle_clients, daemon=True).start()
threading.Thread(target=send_positions, daemon=True).start()

while True:
    time.sleep(1)

