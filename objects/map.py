import pygame
from objects.floor import Floor
from objects.door import Door
from objects.coin import Coin

class Map:
    def __init__(self, level):
        self.level = level
        self.floors = []
        self.door = None
        self.coins = []
        self.load_level()

    def load_level(self):
        if self.level == 1:
            self.floors = [
                Floor(0, 600, 2000, 800, "normal"),
                Floor(200, 450, 100, 20, "fire"),
                Floor(300, 450, 100, 20, "water"),
            ]
            self.door = Door(1700, 550, 50, 50)
            self.coins = [Coin(250, 400), Coin(350, 400), Coin(450, 400)]
        elif self.level == 2:
            self.floors = [
                Floor(0, 600, 2000, 800, "normal"),
                Floor(400, 400, 100, 20, "fire"),
                Floor(500, 400, 100, 20, "water"),
            ]
            self.door = Door(1800, 550, 50, 50)
            self.coins = [Coin(450, 350), Coin(550, 350)]

    def update_from_server(self, level, coins_data):
        """Update map state from server data."""
        if self.level != level:
            self.level = level
            self.load_level()
        self.coins = [Coin(coins_data[i], coins_data[i+1]) for i in range(0, len(coins_data), 2)]

    def draw(self, screen):
        for floor in self.floors:
            floor.draw(screen)
        self.door.draw(screen)
        for coin in self.coins:
            coin.draw(screen)