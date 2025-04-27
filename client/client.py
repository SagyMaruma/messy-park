import sys
import os
# Add the path to the objects folder
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'objects'))
import socket
import pygame
import struct
import threading
from player import Player
from floor import Floor
from door import Door

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5555
BUFFER_SIZE = 4096

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setblocking(False)

name = input("Enter your player name: ")
client_socket.sendto(name.encode(), (SERVER_IP, SERVER_PORT))

player_id, role = None, None
players = {}
my_player = None
current_level = 0
doors = []

pygame.init()
screen = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("Fire and Water Game")
clock = pygame.time.Clock()

# Define levels
levels = [
    {
        "floors": [Floor(0, 600, 1000, 1000), Floor(400, 500, 200, 20)],
        "doors": [Door(100, 570, (255, 0, 0)), Door(800, 570, (0, 0, 255))]
    },
    {
        "floors": [Floor(0, 600, 1000, 1000), Floor(300, 450, 400, 20)],
        "doors": [Door(120, 570, (255, 0, 0)), Door(850, 570, (0, 0, 255))]
    },
    {
        "floors": [Floor(0, 600, 1000, 1000), Floor(200, 400, 600, 20)],
        "doors": [Door(150, 570, (255, 0, 0)), Door(780, 570, (0, 0, 255))]
    },
]

colors = {"Fire": (255, 0, 0), "Water": (0, 0, 255)}

def receive_data():
    global player_id, role, players, my_player, current_level
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            if data.startswith(b"LEVEL"):
                current_level = int(data.decode().split(":")[1])
                continue
            message = data.decode()
            if "," in message:
                player_id, role = message.split(",")
                player_id = int(player_id)
                print(f"Assigned ID: {player_id}, Role: {role}")
                my_player = Player(player_id, name, role, colors[role], 100 if player_id == 1 else 600, 300)
            else:
                existing_ids = set()
                for p_data in message.split(";"):
                    pid, pname, prole, x, y, facing_right = p_data.split("|")
                    pid = int(pid)
                    players[pid] = {
                        "name": pname,
                        "role": prole,
                        "x": int(x),
                        "y": int(y),
                        "facing_right": bool(int(facing_right))
                    }
                    existing_ids.add(pid)

                for pid in list(players.keys()):
                    if pid not in existing_ids:
                        del players[pid]

        except:
            continue

threading.Thread(target=receive_data, daemon=True).start()

running = True
while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if my_player:
        my_player.handle_input(keys)
        my_player.apply_gravity()
        my_player.check_floor_collision(levels[current_level]["floors"])

        # Check if player is on their door
        door = levels[current_level]["doors"][my_player.player_id - 1]
        standing_on_door = my_player.rect.colliderect(door.rect)

        # Send position + standing on door info
        data = struct.pack("2i?b", my_player.rect.x, my_player.rect.y, my_player.facing_right, standing_on_door)
        client_socket.sendto(data, (SERVER_IP, SERVER_PORT))

    screen.fill((30, 30, 30))

    for floor in levels[current_level]["floors"]:
        floor.draw(screen)

    for door in levels[current_level]["doors"]:
        door.draw(screen)

    if my_player:
        my_player.draw(screen)

    for pid, pdata in players.items():
        if pid != my_player.player_id:
            color = colors[pdata["role"]]
            rect = pygame.Rect(pdata["x"], pdata["y"], 25, 25)
            pygame.draw.rect(screen, color, rect)
            font = pygame.font.Font(None, 24)
            text = font.render(pdata["name"], True, (255, 255, 255))
            screen.blit(text, (pdata["x"], pdata["y"] - 20))

    pygame.display.flip()

pygame.quit()
