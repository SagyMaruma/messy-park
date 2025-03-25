import pygame
from pymongo import MongoClient

class Coin:
    def __init__(self, x, y, coin_type="fire"):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.type = coin_type  # "fire" or "water"
        self.color = (255, 165, 0) if coin_type == "fire" else (0, 191, 255)
        self.collected_by = None

    def draw(self, screen):
        if self.collected_by is None:
            pygame.draw.circle(screen, self.color, self.rect.center, 10)

    def collect(self, player):
        if self.collected_by is None and self.rect.colliderect(player.rect):
            self.collected_by = player.player_id
            client = MongoClient("mongodb://localhost:27017/")
            db = client["fire_water_game"]
            db.coins.insert_one({
                "level": 1,  # Default to level 1, updated later if needed
                "type": self.type,
                "collected_by": player.player_id,
                "timestamp": pygame.time.get_ticks()
            })
            return True
        return False