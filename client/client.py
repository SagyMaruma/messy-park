
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
from gun import Gun

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5555
BUFFER_SIZE = 4096

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setblocking(False)

name = input("Enter your player name: ")
client_socket.sendto(name.encode(), (SERVER_IP, SERVER_PORT))
remote_bullets = []  # List of pygame.Rect
player_id, role = None, None
players = {}
my_player = None
current_level = 1
start_time = None
running_game = False
waiting_for_players = True
game_over = False
elevator_y = 600
last_hit_time = 0
hit_cooldown = 1.0  # seconds

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
    #level2
    {
        "start_positions": {"Fire": (0, 750), "Water": (40, 750)},
        
        "floors": [
                Floor(0, 780, 1000, 20, "normal"),#ריצפה ראשית
            Floor(0, 700, 180, 20, "water"),#ריצפה צד ימין קטנה
            Floor(700, 700, 100, 20, "normal"),#ריצפה צד ימין שמאל

            Floor(0, 600, 100, 20, "normal"),#ריצפה מעל ריצפה קטה צד ימין
            

            Floor(0, 450, 750, 20, "normal"),#ריצפה מעל 
            Floor(600, 449.9, 100, 20, "water"),
            Floor(250, 320, 200, 20, "normal"),
            Floor(550, 320, 200, 20, "normal"),
            Floor(250, 319, 200, 20, "water"),
            Floor(550, 319, 200, 20, "fire"),
            
            Floor(350, 250, 300, 20, "normal"),#ריצפה מעל 
            
            Floor(450, 249, 100, 20, "green"),

            #ריצפות של דלתות
            Floor(0, 150, 250, 20, "normal"),#ריצפה מעל 
            Floor(750, 150, 250, 20, "normal"),#ריצפה מעל 

                    
                    
            ],
        "doors": [Door(40, 90, (255, 0, 0)),Door(840, 90, (0, 0, 255))],
        "buttons": [Button(50, 440),Button(50, 690)],
        "elevators": [Elevator(840, 400, 1000, 20, 500)],
        "guns": [  # <-- Add this section
            Gun(150, 410, direction=1),  # Slower gun from the server
            Gun(20, 560, direction=1)    # Faster gun from the server
        ]
        
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

            if message.startswith("BULLETS:"):
                bullet_strs = message[len("BULLETS:"):].split(";")
                remote_bullets.clear()
                for b_str in bullet_strs:
                    if b_str.strip() == "":
                        continue
                    bx, by = map(int, b_str.split(","))
                    remote_bullets.append(pygame.Rect(bx, by, 10, 5))
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
                    players[pid] = {
                        "name": pname,
                        "role": prole,
                        "x": int(x),
                        "y": int(y),
                        "facing_right": bool(int(facing_right))
                    }

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

                # הגבלת מיקום השחקן במסך כך שלא יוכל לצאת מעבר לגבולות
        if my_player.rect.x < 0:
            my_player.rect.x = 0
        elif my_player.rect.x > screen.get_width() - my_player.rect.width:
            my_player.rect.x = screen.get_width() - my_player.rect.width

        if my_player.rect.y < 0:
            my_player.rect.y = 0
        elif my_player.rect.y > screen.get_height() - my_player.rect.height:
            my_player.rect.y = screen.get_height() - my_player.rect.height

            
    for button in levels[current_level]["buttons"]:
        button.update([my_player])

    standing_status = {}
    for pid, pdata in players.items():
        door = levels[current_level]["doors"][pid - 1]
        rect = pygame.Rect(pdata["x"], pdata["y"], 25, 25)
        if rect.colliderect(door.rect):
            standing_status[pid] = pdata["role"]
    # ציור כדורים מהשרת ובדיקה אם פוגעים בי
    for bullet in remote_bullets:
        pygame.draw.rect(screen, (255, 0, 0), bullet)
        if my_player and bullet.colliderect(my_player.rect):
            start_x, start_y = levels[current_level]["start_positions"][my_player.role]
            my_player.respawn(start_x, start_y)
    
        # ציור רובים (רק ויזואלית)
    if "guns" in levels[current_level]:
        for gun in levels[current_level]["guns"]:
            gun.draw(screen)


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