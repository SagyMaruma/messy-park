import pygame

class Door:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
