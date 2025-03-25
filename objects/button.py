import pygame
# button.py
class Button:
    def __init__(self, x, y, elevator):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.elevator = elevator

    def update(self, players):
        self.elevator.active = any(player.rect.colliderect(self.rect) for player in players)

    def draw(self, screen):
        color = (0, 255, 0) if self.elevator.active else (255, 0, 0)
        pygame.draw.rect(screen, color, self.rect)