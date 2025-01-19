import pygame
import struct  # ייבוא struct

class Player:
    def __init__(self, player_id, start_x, start_y, color):
        """
        אתחול השחקן.
        :param player_id: מזהה השחקן
        :param start_x: מיקום התחלתי ב-X
        :param start_y: מיקום התחלתי ב-Y
        :param color: צבע הריבוע המייצג את השחקן
        """
        self.player_id = player_id
        self.rect = pygame.Rect(start_x, start_y, 50, 50)  # ריבוע בגודל 50x50
        self.color = color
        self.speed = 5

    def handle_input(self, keys):
        """מטפל בקלט מהשחקן לתנועה."""
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  # תנועה שמאלה
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:  # תנועה ימינה
            self.rect.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:  # תנועה למעלה
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  # תנועה למטה
            self.rect.y += self.speed

    def draw(self, screen):
        """מצייר את השחקן על המסך."""
        pygame.draw.rect(screen, self.color, self.rect)

    def send_position(self, client_socket):
        """שולח את המיקום הנוכחי לשרת."""
        data = struct.pack("3i", self.player_id, self.rect.x, self.rect.y)
        client_socket.sendall(data)

    def update_position(self, x, y):
        """מעודכן לפי מיקום שהתקבל מהשרת."""
        self.rect.x = x
        self.rect.y = y
