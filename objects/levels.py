# levels.py
from floor import Floor
from door import Door
from button import Button
from elevator import Elevator
from gun import Gun

class LevelManager:
    def __init__(self):
        self.levels = self._load_levels()

    def _load_levels(self):
        return [
            {
                "start_positions": {"Fire": (10,750), "Water": (10, 650)},
                "floors": [
                    Floor(0, 780, 1000, 20, "normal"),
                    Floor(0, 700, 180, 20, "normal"),
                    Floor(850, 700, 150, 20, "normal"),
                    Floor(0, 620, 700, 20, "normal"),
                    Floor(0, 380, 680, 20, "normal"),
                    Floor(0, 380, 680, 20, "normal"),
                    Floor(380, 250, 1000, 20, "normal"),
                    Floor(0, 150, 250, 20, "normal"),
                    Floor(800, 150, 200, 20, "normal"),
                    Floor(250, 779.9, 200, 20, "water"),
                    Floor(450, 779.9, 200, 20, "fire"),
                    Floor(250, 619.9, 200, 20, "fire"),
                    Floor(400, 379.9, 200, 20, "water")
                ],
                "doors": [
                    Door(40, 90, (255, 0, 0)),
                    Door(840, 90, (0, 0, 255))
                ],
                "buttons": [Button(70, 610), Button(70, 370)],
                "elevators": [Elevator(800, 620, 120, 20, 140)]
            },
            {
                "start_positions": {"Fire": (0, 750), "Water": (40, 750)},
                "floors": [
                    Floor(0, 780, 1000, 20, "normal"),
                    Floor(0, 700, 180, 20, "water"),
                    Floor(700, 700, 100, 20, "normal"),
                    Floor(0, 600, 100, 20, "normal"),
                    Floor(0, 450, 750, 20, "normal"),
                    Floor(600, 449.9, 100, 20, "water"),
                    Floor(250, 320, 200, 20, "normal"),
                    Floor(550, 320, 200, 20, "normal"),
                    Floor(250, 319, 200, 20, "water"),
                    Floor(550, 319, 200, 20, "fire"),
                    Floor(350, 250, 300, 20, "normal"),
                    Floor(450, 249, 100, 20, "green"),
                    Floor(0, 150, 250, 20, "normal"),
                    Floor(750, 150, 250, 20, "normal")
                ],
                "doors": [Door(40, 90, (255, 0, 0)), Door(840, 90, (0, 0, 255))],
                "buttons": [Button(50, 440), Button(50, 690)],
                "elevators": [Elevator(840, 400, 1000, 20, 500)],
                "guns": [Gun(150, 410, direction=1), Gun(20, 560, direction=1)]
            },
            {
                "start_positions": {"Fire": (200, 300), "Water": (750, 300)},
                "floors": [Floor(0, 600, 1000, 20, "normal"), Floor(200, 400, 600, 20, "normal")],
                "doors": [Door(150, 570, (255, 0, 0)), Door(780, 570, (0, 0, 255))],
                "buttons": [Button(300, 560)],
                "elevators": [Elevator(300, 600, 80, 20, 100)]
            }
        ]

    def get_level(self, index):
        return self.levels[index]

    def get_total_levels(self):
        return len(self.levels)
