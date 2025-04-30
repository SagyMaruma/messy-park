# objects/gun.py
import pygame

class Gun:
    def __init__(self, x, y, direction, shoot_interval=60):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.direction = direction
        self.shoot_timer = 0
        self.shoot_interval = shoot_interval  # Custom shoot speed
        self.bullets = []

    def update(self, screen):
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            self.bullets.append(pygame.Rect(self.rect.centerx, self.rect.centery, 10, 5))
        for bullet in self.bullets[:]:
            bullet.x += self.direction * 5
            if bullet.x < 0 or bullet.x > 1800:
                self.bullets.remove(bullet)
            pygame.draw.rect(screen, (255, 0, 0), bullet)

    def shoot(self, player):
        for bullet in self.bullets:
            if bullet.colliderect(player.rect):
                self.bullets.remove(bullet)
                return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.rect)
