import pygame
import socket
import struct
import threading
import os
import sys

# set direction for every file in this case I need the objects file.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from objects.player import Player
from objects.floor import Floor

# window size
WIDTH, HEIGHT = 1800, 920
FPS = 60
WHITE = (255, 255, 255)
pygame.display.set_caption("Game")

def receive_data(client_socket, players, player_names):
    """Receives positions and player names from the server"""
    try:
        # First, receive player names
        name_data = client_socket.recv(60)  # Assuming max 3 players, 20 bytes each
        names = [name_data[i:i+20].decode().strip() for i in range(0, 60, 20)]
        player_names.extend(names)
        
        while True:
            data = client_socket.recv(24)  # 24 bytes (6 integers for positions)
            if not data:
                break
            positions = struct.unpack("6i", data)
            for i, player in enumerate(players, start=1):
                player.update_position(
                    positions[(i - 1) * 2], positions[(i - 1) * 2 + 1]
                )
    except Exception as e:
        print(f"Error receiving data: {e}")
    finally:
        client_socket.close()

def run_game(player_id, client_socket):
    # starts Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # font for displaying text    
    font = pygame.font.SysFont('Arial', 15)

    # color, in case there are no assets/images.
    colors = [
        (255, 0, 0),
        (0, 0, 255),
        (0, 255, 0),
    ]
    # create players.
    players = [
        Player(i, 100 * i, 400, colors[i - 1], "assets/player1.png")
        for i in range(1, 4)
    ]
    local_player = players[player_id - 1]

    # create floors
    floors = [
        Floor(0, 600, 2000, 800),  # main floor
        Floor(200, 450, 100, 20),
        Floor(300, 380, 100, 20),  # middle floor
        Floor(400, 350, 500, 20),  # the floor above
    ]
    
    # Store player names
    player_names = []
    threading.Thread(target=receive_data, args=(client_socket, players, player_names)).start()

    running = True
    while running:
        screen.fill(WHITE)  # background fill(this case white)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # check input.
        keys = pygame.key.get_pressed()

        # Player physics
        if player_id == 1:  # player 1 stuck to player 2.
            rope_data = (players[1], 200)  # length 200px.
            local_player.update(keys, floors, players, rope_data)
        elif player_id == 2:  # player 2 stuck to player 1.
            rope_data = (players[0], 200)
            local_player.update(keys, floors, players, rope_data)
        else:  # player 3 being player 3.
            local_player.update(keys, floors, players)

        # send position to the server.
        local_player.send_position(client_socket)

        # drawing the floors
        for floor in floors:
            floor.draw(screen)
        for player in players:
            player.draw(screen)

        for i, player in enumerate(players):
            player.draw(screen)

            # Draw text above each player with their name if available
            player_text = font.render(player_names[i] if i < len(player_names) else f"Player {i+1}", True, (255, 255, 255), (176, 176, 176))

            # position of the text above the player.
            text_x = player.rect.centerx - player_text.get_width() // 2.3
            text_y = player.rect.top - 40  # 40 pixels above the player.

            # Draw the text on the screen at the calculated position
            screen.blit(player_text, (text_x, text_y))

        # drawing the rope between player 1 and player 2.
        if len(players) >= 2:
            pygame.draw.line(
                screen,
                (0, 0, 0),  # rope color(black).
                players[0].rect.center,
                players[1].rect.center,
                2,  # thickness of the rope.
            )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    client_socket.close()
