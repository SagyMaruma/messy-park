import pygame
from objects.floor import Floor
from objects.door import Door
from objects.coin import Coin
from objects.gun import Gun
from objects.elevator import Elevator

class Map:
    def __init__(self, level):
        self.level = level
        self.floors = []
        self.door = None
        self.coins = []
        self.guns = []
        self.elevators = []
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
            self.guns = [Gun(500, 500, 1)]
            self.elevators = [Elevator(600, 500, 100, 20, 700, 400, 300)]
        elif self.level == 2:
            self.floors = [
                Floor(0, 600, 2000, 800, "normal"),
                Floor(400, 400, 100, 20, "fire"),
                Floor(500, 400, 100, 20, "water"),
                Floor(800, 300, 200, 20, "normal"),
            ]
            self.door = Door(1800, 550, 50, 50)
            self.coins = [Coin(450, 350), Coin(550, 350)]
            self.guns = [Gun(700, 350, -1)]
            self.elevators = [Elevator(900, 400, 100, 20, 900, 500, 200)]
        elif self.level == 3:
            self.floors = [
                Floor(0, 600, 2500, 900, "normal"),
                Floor(400, 400, 100, 20, "fire"),
                Floor(500, 400, 100, 20, "water"),
                Floor(800, 300, 200, 20, "normal"),
            ]
            self.door = Door(1800, 550, 50, 50)
            self.coins = [Coin(450, 350), Coin(550, 350)]
            self.guns = [Gun(700, 350, -1)]
            self.elevators = [Elevator(900, 400, 100, 20, 900, 500, 200)]

    def update(self, screen):
        for gun in self.guns:
            gun.update(screen)
        for elevator in self.elevators:
            elevator.update()

    def draw(self, screen):
        for floor in self.floors:
            floor.draw(screen)
        self.door.draw(screen)
        for coin in self.coins:
            coin.draw(screen)
        for gun in self.guns:
            gun.draw(screen)
        for elevator in self.elevators:
            elevator.draw(screen)

    def check_win(self, players):
        return all(player.is_inside_door for player in players)