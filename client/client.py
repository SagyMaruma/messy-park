
import sys
import os
import socket
import pygame
import struct
import threading
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'objects'))
from player import Player
from floor import Floor
from door import Door
from button import Button
from elevator import Elevator

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
start_time = None
running_game = False
waiting_for_players = True
game_over = False
elevator_y = 600

pygame.init()
screen = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("Fire and Water Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

colors = {"Fire": (255, 0, 0), "Water": (0, 0, 255)}

levels = [
    {
        "start_positions": {"Fire": (10,750), "Water": (10, 650)},
        "floors": [
            Floor(0, 780, 1000, 20, "normal"),#ריצפה ראשית
            Floor(0, 700, 180, 20, "normal"),#ריצפה צד ימין קטנה
            Floor(850, 700, 150, 20, "normal"),#רצפה צד שמאל קטנה
            Floor(0, 620, 700, 20, "normal"),#ריצפה ארוכה מעל ריצות קטנות
            Floor(0, 380, 680, 20, "normal"),#ריצפה מעל 
            Floor(0, 380, 680, 20, "normal"),#ריצפה מעל 
            Floor(380, 250, 1000, 20, "normal"),#ריצפה מעל 
            Floor(0, 150, 250, 20, "normal"),#ריצפה מעל 
            Floor(800, 150, 200, 20, "normal"),#ריצפה מעל 
            Floor(250, 779.9, 200, 20, "water"),
            Floor(450, 779.9, 200, 20, "fire"),
            Floor(250, 619.9, 200, 20, "fire"),
            Floor(400, 379.9, 200, 20, "water")
        ],
        "doors": [
            Door(40, 90, (255, 0, 0)),
            Door(840, 90, (0, 0, 255))
        ],
        "buttons": [Button(70, 610),Button(70, 370)],#כפתורים
        
        "elevators": [Elevator(800, 620, 120, 20, 140)]
    },
    {
        "start_positions": {"Fire": (150, 300), "Water": (700, 300)},
        "floors": [Floor(0, 600, 1000, 20, "normal"), Floor(300, 450, 400, 20, "water")],
        "doors": [Door(120, 570, (255, 0, 0)), Door(850, 570, (0, 0, 255))],
        "buttons": [Button(500, 560)],
        "elevators": [Elevator(500, 600, 80, 20, 100)]
    },
    {
        "start_positions": {"Fire": (200, 300), "Water": (750, 300)},
        "floors": [Floor(0, 600, 1000, 20, "normal"), Floor(200, 400, 600, 20, "normal")],
        "doors": [Door(150, 570, (255, 0, 0)), Door(780, 570, (0, 0, 255))],
        "buttons": [Button(300, 560)],
        "elevators": [Elevator(300, 600, 80, 20, 100)]
    }
]

def receive_data():
    global player_id, role, players, my_player, waiting_for_players, running_game, current_level, start_time, game_over, elevator_y
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)
            message = data.decode()

            if message.startswith("LEVEL:"):
                current_level = int(message.split(":")[1])
                if my_player:
                    pos = levels[current_level]["start_positions"][my_player.role]
                    my_player.respawn(*pos)
                continue

            if message.startswith("GAME_OVER:"):
                total_time = float(message.split(":")[1])
                game_over = True
                start_time = time.time() - total_time
                continue

            if message.startswith("ELEVATOR:"):
                elevator_y = int(float(message.split(":")[1]))
                for elevator in levels[current_level]["elevators"]:
                    elevator.update_position(elevator_y)
                continue

            if "," in message:
                player_id, role = message.split(",")
                player_id = int(player_id)
                start_pos = levels[current_level]["start_positions"][role]
                my_player = Player(player_id, name, role, colors[role], *start_pos)
            else:
                for p_data in message.split(";"):
                    pid, pname, prole, x, y, facing_right = p_data.split("|")
                    pid = int(pid)
                    players[pid] = {"name": pname, "role": prole, "x": int(x), "y": int(y), "facing_right": bool(int(facing_right))}

                if len(players) >= 2:
                    waiting_for_players = False
                    if start_time is None:
                        start_time = time.time()
                        running_game = True
        except:
            continue

threading.Thread(target=receive_data, daemon=True).start()

running = True
font_small = pygame.font.Font(None, 24)

while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))

    if waiting_for_players:
        screen.blit(font.render("Waiting for players...", True, (255, 255, 255)), (350, 300))
        pygame.display.flip()
        continue

    if game_over:
        total_time = time.time() - start_time
        screen.fill((0, 0, 0))
        screen.blit(font.render("Game Finished!", True, (0, 255, 0)), (400, 300))
        screen.blit(font.render(f"Total Time: {int(total_time // 60):02}:{int(total_time % 60):02}", True, (0, 255, 0)), (400, 350))
        pygame.display.flip()
        continue

    if my_player:
        my_player.handle_input(keys)
        my_player.apply_gravity()
        my_player.check_floor_collision(levels[current_level]["floors"] + levels[current_level]["elevators"], levels[current_level]["start_positions"])

    for button in levels[current_level]["buttons"]:
        button.update([my_player])

    standing_status = {}
    for pid, pdata in players.items():
        door = levels[current_level]["doors"][pid - 1]
        rect = pygame.Rect(pdata["x"], pdata["y"], 25, 25)
        if rect.colliderect(door.rect):
            standing_status[pid] = pdata["role"]

    door = levels[current_level]["doors"][my_player.player_id - 1]
    if my_player.rect.colliderect(door.rect):
        standing_status[my_player.player_id] = my_player.role

    button_pressed = any(button.activated for button in levels[current_level]["buttons"])
    i_am_standing = my_player.rect.colliderect(door)
    data = struct.pack("2i?b?", my_player.rect.x, my_player.rect.y, my_player.facing_right, i_am_standing, button_pressed)
    client_socket.sendto(data, (SERVER_IP, SERVER_PORT))

    for floor in levels[current_level]["floors"]:
        floor.draw(screen)
    for elevator in levels[current_level]["elevators"]:
        elevator.draw(screen)
    for button in levels[current_level]["buttons"]:
        button.draw(screen)
    for door in levels[current_level]["doors"]:
        door.draw(screen)
    if my_player:
        my_player.draw(screen)

    for pid, pdata in players.items():
        if pid != my_player.player_id:
            color = colors[pdata["role"]]
            rect = pygame.Rect(pdata["x"], pdata["y"], 25, 25)
            pygame.draw.rect(screen, color, rect)
            screen.blit(font_small.render(pdata["name"], True, (255, 255, 255)), (pdata["x"], pdata["y"] - 20))

    y_offset = 20
    for pid, role in standing_status.items():
        text = f"{role} is standing on their door!"
        color = (173, 216, 230) if role == "Water" else (255, 0, 0)
        screen.blit(font.render(text, True, color), (20, y_offset))
        y_offset += 40

    if start_time:
        elapsed_time = time.time() - start_time
        timer_text = font.render(f"Time: {int(elapsed_time // 60):02}:{int(elapsed_time % 60):02}", True, (255, 255, 255))
        screen.blit(timer_text, (450, 30))

    pygame.display.flip()
    print(pygame.mouse.get_pos())

pygame.quit()