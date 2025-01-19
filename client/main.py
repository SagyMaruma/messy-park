import socket
import struct
import threading
import pygame
import sys
import os

# הוספת נתיב לתיקיית assets
sys.path.append(os.path.join(os.path.dirname(__file__), '../assets'))
from player import Player

# הגדרות Pygame
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)

def receive_positions(client_socket, players):
    """
    מקבל עדכונים מהשרת ומעדכן את מיקומי השחקנים.
    """
    try:
        while True:
            data = client_socket.recv(24)  # 24 בתים לכל השחקנים
            if not data:
                break
            positions = struct.unpack("6i", data)

            # עדכון מיקומי השחקנים
            for i, player in enumerate(players, start=1):
                player.update_position(positions[(i - 1) * 2], positions[(i - 1) * 2 + 1])
    except Exception as e:
        print(f"Error receiving positions: {e}")
    finally:
        client_socket.close()

def main():
    # חיבור לשרת
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5555))
    print("Connected to the server!")

    # קבלת מזהה שחקן
    player_id_data = client.recv(4)
    player_id = struct.unpack("i", player_id_data)[0]
    print(f"Your player ID is: {player_id}")

    # יצירת שחקנים
    colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0)]
    players = [Player(i, 100 * i, HEIGHT - 100, colors[i - 1]) for i in range(1, 4)]

    # השחקן המקומי
    local_player = players[player_id - 1]

    # הפעלת חוט לקבלת מיקומים
    threading.Thread(target=receive_positions, args=(client, players)).start()

    # התחלת Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # קלט תנועה לשחקן המקומי
        keys = pygame.key.get_pressed()
        local_player.handle_input(keys)

        # שליחת מיקום לשרת
        local_player.send_position(client)

        # ציור כל השחקנים
        for player in players:
            player.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    client.close()

if __name__ == "__main__":
    main()
