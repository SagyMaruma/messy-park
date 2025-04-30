import pygame
import time

class Player:
    def __init__(self, player_id, name, role, color, start_x, start_y):
        self.player_id = player_id
        self.name = name
        self.role = role
        self.color = color
        self.rect = pygame.Rect(start_x, start_y, 25, 25)
        self.velocity_y = 0
        self.is_jumping = False
        self.gravity = 0.8
        self.jump_speed = -15
        self.speed = 5
        self.facing_right = True
        self.font = pygame.font.SysFont(None, 24)
        self.particles = []
        self.respawn_time = None
        self.is_respawning = False

    def respawn(self, start_x, start_y):
        self.rect.x, self.rect.y = start_x, start_y
        self.velocity_y = 0
        self.is_jumping = False
        self.is_respawning = True
        self.respawn_time = time.time()

    def update_respawn(self):
        if self.is_respawning:
            if time.time() - self.respawn_time < 0.5:
                if int(time.time() * 10) % 2 == 0:
                    self.color = (255, 255, 255)
                else:
                    self.color = (255, 0, 0) if self.role == "Fire" else (0, 0, 255)
            else:
                self.is_respawning = False

    def handle_input(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_right = False
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True
        if keys[pygame.K_w] and not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = self.jump_speed

    def apply_gravity(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

    def check_floor_collision(self, floors, start_positions):
        self.is_jumping = True
        for floor in floors:
            if self.rect.colliderect(floor.rect):
                if not floor.can_stand(self.role):
                    start_x, start_y = start_positions[self.role]
                    self.respawn(start_x, start_y)
                    return
                if self.velocity_y > 0:
                    self.rect.bottom = floor.rect.top
                    self.velocity_y = 0
                    self.is_jumping = False
                elif self.velocity_y < 0:
                    self.rect.top = floor.rect.bottom
                    self.velocity_y = 0
                    self.is_jumping = False

    def draw(self, screen):
        self.update_respawn()
        pygame.draw.rect(screen, self.color, self.rect)
        name_surface = self.font.render(self.name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(self.rect.centerx, self.rect.top - 10))
        screen.blit(name_surface, name_rect)
