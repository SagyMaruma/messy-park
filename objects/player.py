import pygame
class Player:
    def __init__(self, player_id, name, role, color, start_x, start_y):
        self.player_id = player_id  # Unique player ID
        self.name = name  # Player's name
        self.role = role  # Player's role (Fire or Water)
        self.color = color  # Player's color (red for Fire, blue for Water)
        self.rect = pygame.Rect(start_x, start_y, 25, 25)  # Player's rectangle for collision detection
        self.velocity_y = 0  # Vertical velocity for gravity
        self.is_jumping = False  # Whether the player is jumping
        self.gravity = 0.8  # Gravity constant
        self.jump_speed = -15  # Jump speed
        self.speed = 5  # Horizontal movement speed
        self.facing_right = True  # Whether the player is facing right
        self.font = pygame.font.SysFont(None, 24)  # Font for player name

    def handle_input(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed  # Move left
            self.facing_right = False  # Facing left
        if keys[pygame.K_d]:
            self.rect.x += self.speed  # Move right
            self.facing_right = True  # Facing right
        if keys[pygame.K_w] and not self.is_jumping:
            self.is_jumping = True  # Start jumping
            self.velocity_y = self.jump_speed  # Apply jump speed

    def apply_gravity(self):
        self.velocity_y += self.gravity  # Apply gravity to vertical velocity
        self.rect.y += self.velocity_y  # Move the player based on the velocity

    def check_floor_collision(self, floors):
        self.is_jumping = True  # Assume player is jumping
        for floor in floors:  # Check collision with each floor
            if self.rect.colliderect(floor.rect):
                if self.velocity_y > 0:  # Falling down
                    self.rect.bottom = floor.rect.top  # Stop falling when hitting the floor
                    self.velocity_y = 0  # Reset vertical velocity
                    self.is_jumping = False  # Player is no longer jumping
            if self.rect.colliderect(floor.rect):  # Handle collision with the floor from above
                if self.velocity_y < 0:
                    self.rect.top = floor.rect.bottom  # Stop when hitting the ceiling
                    self.velocity_y = 0
                    self.is_jumping = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)  # Draw player as a rectangle
        
        # Draw player name above the character
        name_surface = self.font.render(self.name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(self.rect.centerx, self.rect.top - 10))
        screen.blit(name_surface, name_rect)
