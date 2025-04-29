import sys
import os
import socket
import pygame
import struct
import threading
import time

# הוספת תיקיית האובייקטים
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'objects'))
from player import Player
from floor import Floor
from door import Door

# הגדרות רשת
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5555
BUFFER_SIZE = 4096

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setblocking(False)

# התחברות ראשונית
name = input("Enter your player name: ")
client_socket.sendto(name.encode(), (SERVER_IP, SERVER_PORT))

# משתנים כלליים
player_id, role = None, None
players = {}
my_player = None
current_level = 0
start_time = None
running_game = False
waiting_for_players = True
game_over = False

# Pygame
pygame.init()
screen = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("Fire and Water Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# שלבים עם מיקומי התחלה
levels = [
    {
        "start_positions": {
            "Fire": (100, 300),
            "Water": (600, 300),
        },
        "floors": [
            Floor(0, 600, 1000, 1000, "normal"),
            Floor(400, 500, 200, 20, "fire"),
            Floor(500, 500, 200, 20, "green")
        ],
        "doors": [
            Door(100, 570, (255, 0, 0)),
            Door(800, 570, (0, 0, 255))
        ]
    },
    {
        "start_positions": {
            "Fire": (150, 300),
            "Water": (700, 300),
        },
        "floors": [
            Floor(0, 600, 1000, 1000, "normal"),
            Floor(300, 450, 400, 20, "water")
        ],
        "doors": [
            Door(120, 570, (255, 0, 0)),
            Door(850, 570, (0, 0, 255))
        ]
    },
    {
        "start_positions": {
            "Fire": (200, 300),
            "Water": (750, 300),
        },
        "floors": [
            Floor(0, 600, 1000, 1000, "normal"),
            Floor(200, 400, 600, 20, "normal")
        ],
        "doors": [
            Door(150, 570, (255, 0, 0)),
            Door(780, 570, (0, 0, 255))
        ]
    },
]

colors = {"Fire": (255, 0, 0), "Water": (0, 0, 255)}
standing_status = {}

# קבלת מידע מהשרת
def receive_data():
    global player_id, role, players, my_player, waiting_for_players, running_game, current_level, start_time, game_over
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            message = data.decode()

            if message.startswith("LEVEL:"):
                current_level = int(message.split(":")[1])
                print(f"Level changed to {current_level}")
                if my_player:
                    pos = levels[current_level]["start_positions"][my_player.role]
                    my_player.respawn(*pos)
                continue

            if message.startswith("GAME_OVER:"):
                total_time = float(message.split(":")[1])
                game_over = True
                start_time = time.time() - total_time
                print("Game Over received from server.")
                continue

            if "," in message:
                player_id, role = message.split(",")
                player_id = int(player_id)
                print(f"Assigned ID: {player_id}, Role: {role}")
                start_pos = levels[current_level]["start_positions"][role]
                my_player = Player(player_id, name, role, colors[role], *start_pos)
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

                if len(players) >= 2:
                    waiting_for_players = False
                    if start_time is None:
                        start_time = time.time()
                        running_game = True
        except:
            continue

# התחלת thread
threading.Thread(target=receive_data, daemon=True).start()

# לולאת המשחק
running = True
while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))

    if waiting_for_players:
        text = font.render("Waiting for players...", True, (255, 255, 255))
        screen.blit(text, (350, 300))
        pygame.display.flip()
        continue

    if game_over:
        screen.fill((0, 0, 0))
        total_time = time.time() - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        screen.blit(font.render("Game Finished!", True, (0, 255, 0)), (400, 300))
        screen.blit(font.render(f"Total Time: {minutes:02}:{seconds:02}", True, (0, 255, 0)), (400, 350))
        pygame.display.flip()
        continue

    if my_player:
        my_player.handle_input(keys)
        my_player.apply_gravity()
        my_player.check_floor_collision(levels[current_level]["floors"], levels[current_level]["start_positions"])

        standing_status = {}
        for pid, pdata in players.items():
            door = levels[current_level]["doors"][pid - 1]
            rect = pygame.Rect(pdata["x"], pdata["y"], 25, 25)
            if rect.colliderect(door.rect):
                standing_status[pid] = pdata["role"]

        door = levels[current_level]["doors"][my_player.player_id - 1]
        if my_player.rect.colliderect(door.rect):
            standing_status[my_player.player_id] = my_player.role

        i_am_standing = my_player.rect.colliderect(door)
        data = struct.pack("2i?b", my_player.rect.x, my_player.rect.y, my_player.facing_right, i_am_standing)
        client_socket.sendto(data, (SERVER_IP, SERVER_PORT))

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
            font_small = pygame.font.Font(None, 24)
            text = font_small.render(pdata["name"], True, (255, 255, 255))
            screen.blit(text, (pdata["x"], pdata["y"] - 20))

    y_offset = 20
    for pid, role in standing_status.items():
        msg = f"{role} is standing on their door!"
        color = (173, 216, 230) if role == "Water" else (255, 0, 0)
        screen.blit(font.render(msg, True, color), (20, y_offset))
        y_offset += 40

    if start_time:
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        timer = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        screen.blit(timer, timer.get_rect(center=(500, 30)))

    pygame.display.flip()

pygame.quit()
