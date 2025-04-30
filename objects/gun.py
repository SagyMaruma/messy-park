import pygame

class Bullet:
    def __init__(self, x, y, direction, owner_id):
        self.rect = pygame.Rect(x, y, 8, 4)
        self.speed = 8 * direction
        self.owner_id = owner_id
        self.active = True

    def update(self):
        self.rect.x += self.speed
        if self.rect.x < 0 or self.rect.x > 800:
            self.active = False

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 0), self.rect)
