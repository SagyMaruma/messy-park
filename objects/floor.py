import pygame

class Floor:
    def __init__(self, x, y, width, height, floor_type="normal"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = floor_type
        self.color = (255, 127, 50) if floor_type == "normal" else (255, 0, 0) if floor_type == "fire" else (0, 0, 255)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)