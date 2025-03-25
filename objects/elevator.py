import pygame

class Elevator:
    def __init__(self, x, y, width, height, button_x, button_y, max_height):
        self.rect = pygame.Rect(x, y, width, height)
        self.button_rect = pygame.Rect(button_x, button_y, 20, 20)
        self.max_height = max_height
        self.min_height = y
        self.is_active = False
        self.speed = 2
        self.direction = 0  # 0: stopped, 1: up

    def activate(self):
        """Start elevator movement when a player steps on the button."""
        if not self.is_active:
            self.is_active = True
            self.direction = 1  # Move up

    def update(self):
        """Update elevator position based on activation."""
        if self.is_active and self.direction == 1:
            if self.rect.y > self.max_height:
                self.rect.y -= self.speed
            else:
                self.is_active = False  # Stop when reaching max height
                self.direction = 0

    def is_moving_up(self):
        return self.direction == 1

    def draw(self, screen):
        pygame.draw.rect(screen, (150, 150, 150), self.rect)
        pygame.draw.rect(screen, (0, 255, 255), self.button_rect)