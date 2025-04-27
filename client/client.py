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

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5555
BUFFER_SIZE = 2048

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setblocking(False)

name = input("Enter your player name: ")
client_socket.sendto(name.encode(), (SERVER_IP, SERVER_PORT))

player_id, role = None, None
players = {}
my_player = None

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Fire and Water Game")
clock = pygame.time.Clock()

floors = [Floor(0, 550, 800, 50)]
colors = {"Fire": (255, 0, 0), "Water": (0, 0, 255)}

def receive_data():
    global player_id, role, players, my_player
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
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

                # Optional: remove disconnected players
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
        my_player.check_floor_collision(floors)

        # Send position and direction
        data = struct.pack("2i?", my_player.rect.x, my_player.rect.y, my_player.facing_right)
        client_socket.sendto(data, (SERVER_IP, SERVER_PORT))

    screen.fill((30, 30, 30))

    for floor in floors:
        floor.draw(screen)

    if my_player:
        my_player.draw(screen)

    for pid, pdata in players.items():
        if pid != my_player.player_id:
            color = colors[pdata["role"]]
            rect = pygame.Rect(pdata["x"], pdata["y"], 50, 50)
            pygame.draw.rect(screen, color, rect)
            # Draw player name above their character
            font = pygame.font.Font(None, 24)
            text = font.render(pdata["name"], True, (255, 255, 255))
            screen.blit(text, (pdata["x"], pdata["y"] - 20))

    pygame.display.flip()

pygame.quit()
