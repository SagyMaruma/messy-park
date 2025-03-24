import pygame
import socket
import struct
import threading
import os
import sys

# Set direction for every file, in this case I need the objects file.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from objects.player import Player
from objects.map import Map

# Window size
WIDTH, HEIGHT = 1800, 920
FPS = 60
WHITE = (255, 255, 255)
pygame.display.set_caption("Fireboy and Watergirl")

def receive_full_data(sock, expected_size):
    """Helper function to receive a fixed amount of data."""
    data = b""
    while len(data) < expected_size:
        packet = sock.recv(expected_size - len(data))
        if not packet:
            return None  # Connection lost
        data += packet
    return data

def receive_data(client_socket, players, player_names):
    """Receives positions, names, and animations from the server."""
    try:
        while True:
            size_data = receive_full_data(client_socket, 4)
            if not size_data:
                print("Disconnected from server.")
                break
            data_size = struct.unpack("i", size_data)[0]
            full_data = receive_full_data(client_socket, data_size)
            name_data = full_data[:40]  # Two players, 20 bytes each
            positions_data = full_data[40:56]  # 4 integers (x, y for each)
            anim_data = full_data[56:]  # Animation data (facing_right, walk_frame)
            names = [name_data[i:i+20].decode().strip() for i in range(0, 40, 20)]
            player_names.clear()
            player_names.extend(names)
            positions = struct.unpack("4i", positions_data)
            anim = struct.unpack("2?2i", anim_data)
            for i, player in enumerate(players):
                idx = i * 2
                player.update_position(positions[idx], positions[idx+1], anim[i], anim[i+2])
    except Exception as e:
        print(f"Error receiving data: {e}")
    finally:
        client_socket.close()

def run_game(player_id, client_socket):
    # Starts Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Font for displaying text
    font = pygame.font.SysFont("Arial", 15)

    # Create players
    players = [
        Player(1, 100, 400, (255, 0, 0), "assets/fireboy_still.png", "Fire"),
        Player(2, 200, 400, (0, 0, 255), "assets/watergirl_still.png", "Water")
    ]
    local_player = players[player_id - 1]

    # Initialize map
    current_level = 1
    game_map = Map(current_level)

    # Store player names
    player_names = []
    threading.Thread(target=receive_data, args=(client_socket, players, player_names)).start()

    # Game variables
    start_time = pygame.time.get_ticks()
    collected_coins = 0
    running = True
    while running:
        screen.fill(WHITE)  # Background fill (this case white)

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_n and game_map.door.check_win(players):
                current_level += 1
                game_map = Map(current_level)
                for player in players:
                    player.reset_position()
                collected_coins = 0
                start_time = pygame.time.get_ticks()

        # Check input
        keys = pygame.key.get_pressed()
        local_player.update(keys, game_map.floors, players, game_map.door, client_socket)  # Pass door to update

        # Draw map elements
        game_map.draw(screen)
        
        # Draw players and names
        for i, player in enumerate(players):
            player.draw(screen)
            if not player.is_inside_door:  # Only show name if not inside door
                name_text = font.render(player_names[i] if i < len(player_names) else f"Player {i+1}", True, (255, 255, 255), (176, 176, 176))
                if len(player_names) > i and len(player_names[i]) > 10:
                    name_text = font.render(player_names[i][:10] + "...", True, (255, 255, 255), (176, 176, 176))
                text_x = player.rect.centerx - name_text.get_width() // 2.1
                text_y = player.rect.top - 40
                screen.blit(name_text, (text_x, text_y))

        # Handle coins
        for coin in game_map.coins[:]:
            if coin.collect(local_player):
                game_map.coins.remove(coin)
                collected_coins += 1

        # Display timer and coins
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        time_text = font.render(f"Time: {elapsed_time}s", True, (0, 0, 0))
        coin_text = font.render(f"Coins: {collected_coins}", True, (0, 0, 0))
        screen.blit(time_text, (10, 10))
        screen.blit(coin_text, (10, 30))

        # Check win condition (both players inside door)
        if all(player.is_inside_door for player in players):
            score = collected_coins * 100 - elapsed_time
            from pymongo import MongoClient
            client = MongoClient("mongodb://localhost:27017/")
            db = client["fire_water_game"]
            db.scores.insert_one({
                "name": player_names[player_id - 1] if player_id - 1 < len(player_names) else f"Player {player_id}",
                "score": score,
                "coins": collected_coins,
                "time": elapsed_time,
                "level": current_level,
                "date": pygame.time.get_ticks()
            })
            win_text = font.render(f"You Win! Score: {score} - Press N for Next Level", True, (0, 255, 0))
            screen.blit(win_text, (WIDTH // 2 - 100, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    client_socket.close()