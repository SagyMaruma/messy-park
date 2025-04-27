import pygame

class Floor:
    def __init__(self, x, y, width, height, floor_type="normal"):
        """
        floor_type: can be "normal", "fire", or "water"
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.type = floor_type
        self.color = self.get_color_by_type(floor_type)

    def get_color_by_type(self, floor_type):
        if floor_type == "fire":
            return (255, 100, 100)  # reddish for fire-only
        elif floor_type == "water":
            return (100, 100, 255)  # bluish for water-only
        return (200, 200, 200)     # gray for normal

    def can_stand(self, role):
        """
        Check if a player with the given role can stand on this floor.
        """
        return (
            self.type == "normal" or
            (self.type == "fire" and role == "Fire") or
            (self.type == "water" and role == "Water")
        )

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
