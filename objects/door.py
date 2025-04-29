import pygame

class Door:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.color = color
        self.outline_color = (0, 0, 0)  # black outline
        self.knob_color = (255, 255, 0)  # yellow/golden knob

    def draw(self, screen):
        # Draw black outline slightly bigger than the door
        outline_rect = self.rect.inflate(4, 4)
        pygame.draw.rect(screen, self.outline_color, outline_rect)

        # Draw the door
        pygame.draw.rect(screen, self.color, self.rect)

        # Draw a simple round doorknob
        knob_x = self.rect.right - 8
        knob_y = self.rect.centery
        pygame.draw.circle(screen, self.knob_color, (knob_x, knob_y), 3)
