import pygame
import struct

class Player:
    def __init__(self, player_id, start_x, start_y, color):
        """
        אתחול שחקן.
        :param player_id: מזהה השחקן
        :param start_x: מיקום התחלתי ב-X
        :param start_y: מיקום התחלתי ב-Y
        :param color: צבע הריבוע של השחקן
        """
        self.player_id = player_id
        self.rect = pygame.Rect(start_x, start_y, 50, 50)  # ריבוע בגודל 50x50
        self.color = color
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_speed = -15
        self.is_jumping = False
        self.is_double_jumping = False  # דגל לדאבל קפיצה

    def handle_input(self, keys):
        """מטפל בקלט מהשחקן לתנועה וקפיצה."""
        self.velocity_x = 0
        if keys[pygame.K_a]:  # תנועה שמאלה
            self.velocity_x = -5
        if keys[pygame.K_d]:  # תנועה ימינה
            self.velocity_x = 5

        # קפיצה ראשונה (W)
        if keys[pygame.K_w] and not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = self.jump_speed

        # דאבל קפיצה (SPACE)
        if keys[pygame.K_SPACE] and self.is_jumping and not self.is_double_jumping:
            self.is_double_jumping = True
            self.velocity_y = self.jump_speed

    def apply_gravity(self):
        """מוסיף כוח משיכה לשחקן."""
        self.velocity_y += self.gravity

    def check_horizontal_collision(self, floors, players):
        """בודק התנגשות אופקית עם הרצפה והשחקנים האחרים."""
        for floor in floors:
            if self.rect.colliderect(floor.rect):
                if self.velocity_x > 0:  # תנועה ימינה
                    self.rect.right = floor.rect.left
                elif self.velocity_x < 0:  # תנועה שמאלה
                    self.rect.left = floor.rect.right
                self.velocity_x = 0  # עצירה בהתנגשות

        for player in players:
            if player != self and self.rect.colliderect(player.rect):  # לא בודק את עצמו
                if self.velocity_x > 0:  # תנועה ימינה
                    self.rect.right = player.rect.left
                elif self.velocity_x < 0:  # תנועה שמאלה
                    self.rect.left = player.rect.right
                self.velocity_x = 0  # עצירה בהתנגשות

    def check_vertical_collision(self, floors, players):
        """בודק התנגשות אנכית עם הרצפה והשחקנים האחרים."""
        self.is_jumping = True
        for floor in floors:
            if self.rect.colliderect(floor.rect):
                if self.velocity_y > 0:  # נופל ופוגע ברצפה
                    self.rect.bottom = floor.rect.top
                    self.velocity_y = 0
                    self.is_jumping = False
                    self.is_double_jumping = False  # מאתחל דאבל קפיצה
                elif self.velocity_y < 0:  # קופץ ופוגע בתקרה
                    self.rect.top = floor.rect.bottom
                    self.velocity_y = 0

        for player in players:
            if player != self and self.rect.colliderect(player.rect):  # לא בודק את עצמו
                if self.velocity_y > 0:  # נופל ופוגע בשחקן אחר
                    self.rect.bottom = player.rect.top
                    self.velocity_y = 0
                    self.is_jumping = False
                    self.is_double_jumping = False  # מאתחל דאבל קפיצה
                elif self.velocity_y < 0:  # קופץ ופוגע בתחתית שחקן אחר
                    self.rect.top = player.rect.bottom
                    self.velocity_y = 0

    def update(self, keys, floors, players):
        """מעדכן את המיקום, הפיזיקה וההתנגשויות של השחקן."""
        self.handle_input(keys)
        self.rect.x += self.velocity_x
        self.check_horizontal_collision(floors, players)  # בדיקת התנגשות אופקית
        self.apply_gravity()
        self.rect.y += self.velocity_y
        self.check_vertical_collision(floors, players)  # בדיקת התנגשות אנכית

    def draw(self, screen):
        """מצייר את השחקן על המסך."""
        pygame.draw.rect(screen, self.color, self.rect)

    def send_position(self, client_socket):
        """שולח את המיקום הנוכחי לשרת."""
        data = struct.pack("3i", self.player_id, self.rect.x, self.rect.y)
        client_socket.sendall(data)

    def update_position(self, x, y):
        """מעדכן את מיקום השחקן לפי נתוני שרת."""
        self.rect.x = x
        self.rect.y = y
