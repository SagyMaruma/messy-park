import pygame

class Floor:
    def __init__(self, x, y, width, height, floor_type="normal"):
        """
        floor_type: can be "normal", "fire", "water", or "green" (forbidden)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.type = floor_type
        self.color = self.get_color_by_type(floor_type)

    def get_color_by_type(self, floor_type):
        if floor_type == "fire":
            return (255, 100, 100)  # red
        elif floor_type == "water":
            return (100, 100, 255)  # blue
        elif floor_type == "green":
            return (0, 255, 0)      # green
        return (200, 200, 200)     # gray for normal

    def can_stand(self, role):
        """
        Only allow standing if the floor is normal or matches the role.
        Green floor blocks both.
        """
        return (
            self.type == "normal" or
            (self.type == "fire" and role == "Fire") or
            (self.type == "water" and role == "Water")
        )

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
