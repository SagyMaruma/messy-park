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

        # Particle effects
        self.particles = []

        # Respawn properties
        self.respawn_time = None
        self.is_respawning = False

    def respawn(self):
        if self.player_id == 1:
            self.rect.x, self.rect.y = 100, 300  # Fire player start
        else:
            self.rect.x, self.rect.y = 600, 300  # Water player start

        self.velocity_y = 0
        self.is_jumping = False
        self.is_respawning = True
        self.respawn_time = time.time()

    def update_respawn(self):
        # Handle the respawn flash effect
        if self.is_respawning:
            if time.time() - self.respawn_time < 0.5:  # Flashing for half a second
                if int(time.time() * 10) % 2 == 0:
                    self.color = (255, 255, 255)  # Flash white
                else:
                    self.color = (255, 0, 0) if self.role == "Fire" else (0, 0, 255)  # Fire/Water color
            else:
                self.is_respawning = False  # Stop respawn flash

    def handle_input(self, keys):
        moving = False
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_right = False
            moving = True
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True
            moving = True
        if keys[pygame.K_w] and not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = self.jump_speed

        # Create particles if moving
        if moving or self.is_jumping:
            self.create_particles()

    def create_particles(self):
        if self.role == "Fire":
            color = (255, 100, 0)
        else:
            color = (0, 150, 255)

        particle = [
            self.rect.centerx,
            self.rect.centery,
            5,
            (pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() % 360) * 2).x,
            -1,
            color
        ]
        self.particles.append(particle)

    def update_particles(self):
        for particle in self.particles:
            particle[0] += particle[3]  # x move
            particle[1] += particle[4]  # y move
            particle[2] -= 0.1  # shrink
        self.particles = [p for p in self.particles if p[2] > 0]

    def apply_gravity(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

    def check_floor_collision(self, floors):
        self.is_jumping = True
        for floor in floors:
            if self.rect.colliderect(floor.rect):
                if not floor.can_stand(self.role):
                    # Player is on a forbidden floor — respawn!
                    self.respawn()
                    return  # Skip rest of collision
                if self.velocity_y > 0:
                    self.rect.bottom = floor.rect.top
                    self.velocity_y = 0
                    self.is_jumping = False
                elif self.velocity_y < 0:
                    self.rect.top = floor.rect.bottom
                    self.velocity_y = 0
                    self.is_jumping = False

    def draw(self, screen):
        self.update_particles()
        self.update_respawn()  # Check for respawn effect

        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(screen, particle[5], (int(particle[0]), int(particle[1])), int(particle[2]))

        # Draw player rectangle
        pygame.draw.rect(screen, self.color, self.rect)

        # Draw player name
        name_surface = self.font.render(self.name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(self.rect.centerx, self.rect.top - 10))
        screen.blit(name_surface, name_rect)
