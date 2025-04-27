import pygame

class Floor:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (200, 200, 200)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
