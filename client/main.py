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

    # יצירת שחקנים ורצפה
    colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0)]  # צבעים לכל שחקן
    players = [Player(i, 100 * i, 400, colors[i - 1]) for i in range(1, 4)]
    local_player = players[player_id - 1]
    floors = [Floor(0, 500, 800, 100), Floor(0,400,100,100)]  # ריצפה אחת פלוס ריצפה שהוספתי

    #לעשות בדיקה גם בצדדים של הריצפות כדי להיתקע בהם ולהעביר אותן דרך השרת ככה שהשחקנים יראו את אותו הדבר

    # חוט לקבלת מיקומים משרת
    threading.Thread(target=receive_positions, args=(client, players)).start()

    # לולאת המשחק
    running = True
    while running:
        screen.fill(WHITE)  # רקע לבן

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # קלט מהמשתמש
        keys = pygame.key.get_pressed()
        local_player.update(keys, floors, players)  # עדכון השחקן המקומי
        local_player.send_position(client)  # שליחת מיקום לשרת

        # ציור הרצפה והשחקנים
        for floor in floors:
            floor.draw(screen)
        for player in players:
            player.draw(screen)

        # עדכון המסך
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    client.close()

if __name__ == "__main__":
    main()
