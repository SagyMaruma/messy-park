import pygame

class Button:
    def __init__(self, x, y, width=40, height=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.activated = False

    def update(self, players):
        self.activated = any(self.rect.colliderect(player.rect) for player in players)

    def draw(self, screen):
        color = (0, 255, 0) if self.activated else (100, 100, 100)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)  # Border
