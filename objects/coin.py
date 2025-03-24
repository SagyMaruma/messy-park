import pygame

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.color = (255, 215, 0)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, 10)

    def collect(self, player):
        """Checks if the player collects the coin."""
        return self.rect.colliderect(player.rect)