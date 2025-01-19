import pygame
import socket
import struct
import threading
import os
import sys

# הוספת נתיב לתיקיית assets
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from assets.player import Player
from assets.floor import Floor

# הגדרות מסך
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)

def receive_positions(client_socket, players):
    """מקבל עדכוני מיקומים מהשרת ומעדכן את כל השחקנים."""
    try:
        while True:
            data = client_socket.recv(24)  # 24 בתים (6 מספרים שלמים)
            if not data:
                break
            positions = struct.unpack("6i", data)
            for i, player in enumerate(players, start=1):
                player.update_position(positions[(i - 1) * 2], positions[(i - 1) * 2 + 1])
    except Exception as e:
        print(f"Error receiving positions: {e}")
    finally:
        client_socket.close()

def main():
    # אתחול Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # חיבור לשרת
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5555))  # כתובת IP מקומית

    # קבלת מזהה שחקן מהשרת
    player_id = struct.unpack("i", client.recv(4))[0]

    # יצירת שחקנים
    colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0)]  # צבעים לכל שחקן
    players = [Player(i, 100 * i, 400, colors[i - 1]) for i in range(1, 4)]
    local_player = players[player_id - 1]

    # יצירת רצפות
    floors = [
        Floor(0, 500, 800, 50),  # רצפה תחתונה
        Floor(200, 350, 200, 20),  # רצפה אמצעית
        Floor(400, 250, 200, 20),  # רצפה עליונה
    ]

    # חוט לקבלת מיקומים משרת
    threading.Thread(target=receive_positions, args=(client, players)).start()

    running = True
    while running:
        screen.fill(WHITE)  # רקע לבן

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # קלט מהמשתמש
        keys = pygame.key.get_pressed()

        # עדכון פיזיקה לשחקנים
        if player_id == 1:  # שחקן 1 מחובר לשחקן 2
            rope_data = (players[1], 200)  # חבל באורך 200 פיקסלים
            local_player.update(keys, floors, players, rope_data)
        elif player_id == 2:  # שחקן 2 מחובר לשחקן 1
            rope_data = (players[0], 200)
            local_player.update(keys, floors, players, rope_data)
        else:  # שחקן 3 אינו מחובר
            local_player.update(keys, floors, players)

        # שליחת מיקום לשרת
        local_player.send_position(client)

        # ציור רצפה ושחקנים
        for floor in floors:
            floor.draw(screen)
        for player in players:
            player.draw(screen)

        # ציור חבל בין שחקן 1 ל-2
        if len(players) >= 2:
            pygame.draw.line(
                screen,
                (0, 0, 0),  # צבע החבל: שחור
                players[0].rect.center,
                players[1].rect.center,
                2,  # עובי החבל
            )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    client.close()

if __name__ == "__main__":
    main()
