import pygame
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
        # Each particle: [x, y, size, speed_x, speed_y, color]
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
                if self.velocity_y > 0:
                    self.rect.bottom = floor.rect.top
                    self.velocity_y = 0
                    self.is_jumping = False
            if self.rect.colliderect(floor.rect):
                if self.velocity_y < 0:
                    self.rect.top = floor.rect.bottom
                    self.velocity_y = 0
                    self.is_jumping = False

    def draw(self, screen):
        self.update_particles()

        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(screen, particle[5], (int(particle[0]), int(particle[1])), int(particle[2]))

        # Draw player rectangle
        pygame.draw.rect(screen, self.color, self.rect)

        # Draw player name
        name_surface = self.font.render(self.name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(self.rect.centerx, self.rect.top - 10))
        screen.blit(name_surface, name_rect)
