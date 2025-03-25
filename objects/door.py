# objects/door.py
import pygame

class Door:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 255, 0)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def check_win(self, players):
        return all(player.is_inside_door for player in players)