import pygame

class Elevator:
    def __init__(self, x, y, width, height, max_up_distance):
        self.rect = pygame.Rect(x, y, width, height)
        self.start_y = y
        self.max_up_distance = max_up_distance

    def update_position(self, new_y):
        self.rect.y = new_y

    def draw(self, screen):
        pygame.draw.rect(screen, (150, 150, 150), self.rect)

    def can_stand(self, role):
        return True  # anyone can stand on elevator
