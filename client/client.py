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
BUFFER_SIZE = 2048  # Buffer size for receiving data

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create UDP socket
client_socket.setblocking(False)  # Non-blocking socket to avoid freezing the game

name = input("Enter your player name: ")  # Get player name from input
client_socket.sendto(name.encode(), (SERVER_IP, SERVER_PORT))  # Send the name to the server

player_id, role = None, None  # Player's ID and role will be set later
players = {}  # Dictionary to store other players' info
my_player = None  # The local player object

pygame.init()  # Initialize Pygame
screen = pygame.display.set_mode((1000, 800))  # Set up the game window
pygame.display.set_caption("Fire and Water Game")  # Set the window title
clock = pygame.time.Clock()  # Create the game clock for FPS control

floors = [Floor(0, 600, 1000, 1000), Floor(500, 550, 200, 20)]  # Game floor setup
colors = {"Fire": (255, 0, 0), "Water": (0, 0, 255)}  # Colors for Fire and Water roles

def receive_data():
    global player_id, role, players, my_player
    while True:
        try:
            data, _ = client_socket.recvfrom(BUFFER_SIZE)  # Receive data from the server
            message = data.decode()

            if "," in message:  # New player info (ID and role)
                player_id, role = message.split(",")
                player_id = int(player_id)
                print(f"Assigned ID: {player_id}, Role: {role}")
                my_player = Player(player_id, name, role, colors[role], 100 if player_id == 1 else 600, 300)
            else:
                existing_ids = set()
                for p_data in message.split(";"):  # Parse the list of players
                    pid, pname, prole, x, y, facing_right = p_data.split("|")
                    pid = int(pid)
                    players[pid] = {  # Store player data in dictionary
                        "name": pname,
                        "role": prole,
                        "x": int(x),
                        "y": int(y),
                        "facing_right": bool(int(facing_right))
                    }
                    existing_ids.add(pid)

                # Remove disconnected players (if any)
                for pid in list(players.keys()):
                    if pid not in existing_ids:
                        del players[pid]

        except:
            continue

# Start a thread to receive data from the server
threading.Thread(target=receive_data, daemon=True).start()

# Game loop
running = True
while running:
    clock.tick(60)  # Limit the frame rate to 60 FPS
    keys = pygame.key.get_pressed()  # Get the current key presses

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Close the game window
            running = False

    if my_player:
        my_player.handle_input(keys)  # Handle player movement input
        my_player.apply_gravity()  # Apply gravity
        my_player.check_floor_collision(floors)  # Check if player collides with the floor

        # Send the player's position and movement data to the server
        data = struct.pack("2i?", my_player.rect.x, my_player.rect.y, my_player.facing_right)
        client_socket.sendto(data, (SERVER_IP, SERVER_PORT))

    screen.fill((30, 30, 30))  # Fill the screen with a background color

    # Draw the floors
    for floor in floors:
        floor.draw(screen)

    if my_player:
        my_player.draw(screen)  # Draw the local player's character

    # Draw the other players
    for pid, pdata in players.items():
        if pid != my_player.player_id:  # Don't draw the local player twice
            color = colors[pdata["role"]]
            rect = pygame.Rect(pdata["x"], pdata["y"], 25, 25)
            pygame.draw.rect(screen, color, rect)  # Draw the player's rectangle
            # Draw player name above their character
            font = pygame.font.Font(None, 24)
            text = font.render(pdata["name"], True, (255, 255, 255))
            screen.blit(text, (pdata["x"], pdata["y"] - 20))

    pygame.display.flip()  # Update the display

pygame.quit()  # Quit Pygame when the game loop ends
