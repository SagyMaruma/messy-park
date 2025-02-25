import pygame
import socket
import struct
import threading
import os
import sys

# set drication for evry file in this case I need the objects file.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from objects.player import Player
from objects.floor import Floor

# window size
WIDTH, HEIGHT = 1800, 920
FPS = 60
WHITE = (255, 255, 255)
pygame.display.set_caption("Game")


def receive_positions(client_socket, players):
    """gets positions from the server"""
    try:
        while True:
            data = client_socket.recv(24)  # 24 בתים (6 מספרים שלמים)
            if not data:
                break
            positions = struct.unpack("6i", data)
            for i, player in enumerate(players, start=1):
                player.update_position(
                    positions[(i - 1) * 2], positions[(i - 1) * 2 + 1]
                )
    except Exception as e:
        print(f"Error receiving positions: {e}")
    finally:
        client_socket.close()


def run_game(player_id, client_socket):
    # starts Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    #font for displaying text    
    font = pygame.font.SysFont('Arial', 15)

    # color, in case thier is no assets/images.
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

    # חוט לקבלת מיקומים משרת
    threading.Thread(target=receive_positions, args=(client_socket, players)).start()

    running = True
    while running:
        screen.fill(WHITE)  # background fill(this case white)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # check input.
        keys = pygame.key.get_pressed()

        # Player physics
        if player_id == 1:  # player 2 stuck to player 2.
            rope_data = (players[1], 200)  # length 200px.
            local_player.update(keys, floors, players, rope_data)
        elif player_id == 2:  # player 2 stuck to player 1.
            rope_data = (players[0], 200)
            local_player.update(keys, floors, players, rope_data)
        else:  # player 3 beeing player 3.
            local_player.update(keys, floors, players)

        # sent position to the server.
        local_player.send_position(client_socket)

        # drawing the floors
        for floor in floors:
            floor.draw(screen)
        for player in players:
            player.draw(screen)

        for player in players:
            player.draw(screen)

            # Draw text above each player 
            player_text = font.render(f"Player {player_id}", True, (255, 255, 255), (176, 176, 176))  # color white, background gray.

            # position of the text above the player.
            text_x = player.rect.centerx - player_text.get_width() // 2.3
            text_y = player.rect.top - 40  # 40 pixels above the player.
            
            # Draw the text on the screen at the calculated position
            screen.blit(player_text, (text_x, text_y))




        # drawing the rope bet player 1 to player 2.
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
